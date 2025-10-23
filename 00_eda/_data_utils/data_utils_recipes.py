from .data_utils_common import *

# =============================================================================
# �📦 CHARGEMENT DES DONNÉES
# =============================================================================

def load_recipes_raw(limit: Optional[int] = None) -> pl.DataFrame:
    """
    Charge les données de recettes depuis la table RAW_recipes sur S3.
    
    Args:
        limit: Nombre maximum de lignes à charger (optionnel)
        
    Returns:
        pl.DataFrame: DataFrame Polars avec les données brutes
    """
    # Charger depuis S3
    conn = get_s3_duckdb_connection()
    
    # Attacher la base DuckDB depuis S3 puis requêter la table
    conn.execute("ATTACH 's3://mangetamain/mangetamain.duckdb' AS s3_db")
    sql = "SELECT * FROM s3_db.RAW_recipes"
    
    if limit:
        sql += f" LIMIT {limit}"
    
    df = conn.execute(sql).pl()
    conn.close()

    print(f"✅ Recettes chargées depuis S3 : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
    return df


def save_recipes_to_s3(df: pl.DataFrame, s3_path: str, format: str = "parquet") -> None:
    """
    Sauvegarde un DataFrame de recettes vers S3 (fichier indépendant, pas dans DuckDB).
    
    Args:
        df: DataFrame Polars à sauvegarder
        s3_path: Chemin S3 (ex: 's3://mangetamain/final_recipes.parquet')
        format: Format de fichier ('parquet' ou 'csv')
        
    Example:
        >>> df_clean = clean_recipes(df_raw)
        >>> save_recipes_to_s3(df_clean, 's3://mangetamain/final_recipes.parquet')
        ✅ Sauvegardé vers s3://mangetamain/final_recipes.parquet (123,456 lignes)
    """
    import boto3
    from io import BytesIO
    from configparser import ConfigParser
    
    # Extraire bucket et key du chemin S3
    if not s3_path.startswith("s3://"):
        raise ValueError(f"Le chemin doit commencer par 's3://': {s3_path}")
    
    # Parse s3://bucket/path/to/file.parquet
    s3_parts = s3_path.replace("s3://", "").split("/", 1)
    bucket = s3_parts[0]
    key = s3_parts[1] if len(s3_parts) > 1 else ""
    
    # Charger les credentials depuis 96_keys/credentials
    creds_path = get_s3_credentials_path()
    config = ConfigParser()
    config.read(creds_path)
    
    if 's3fast' not in config:
        raise ValueError("Profil [s3fast] introuvable dans 96_keys/credentials")
    
    s3_config = config['s3fast']
    endpoint_url = s3_config.get('endpoint_url', 'http://s3fast.lafrance.io')
    access_key = s3_config.get('aws_access_key_id')
    secret_key = s3_config.get('aws_secret_access_key')
    region = s3_config.get('region', 'garage-fast')
    
    # Créer le client S3 avec les credentials chargés
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        use_ssl=False  # Pour s3fast.lafrance.io
    )
    
    # Sauvegarder selon le format
    if format.lower() == "parquet":
        # Écrire en mémoire puis uploader
        buffer = BytesIO()
        df.write_parquet(buffer)
        buffer.seek(0)
        s3_client.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
        
    elif format.lower() == "csv":
        # Écrire CSV en mémoire puis uploader
        buffer = BytesIO()
        df.write_csv(buffer)
        buffer.seek(0)
        s3_client.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
        
    else:
        raise ValueError(f"Format non supporté: {format}. Utilisez 'parquet' ou 'csv'")
    
    print(f"✅ Sauvegardé vers {s3_path} ({df.shape[0]:,} lignes, format={format})")

# =============================================================================
# 🧹 HELPERS INTERNES - PARSING
# =============================================================================

def _parse_list_column(df: pl.DataFrame, col_name: str, clean_quotes: bool = True) -> pl.DataFrame:
    """
    Parse une colonne texte de type "[item1, item2, ...]" en liste Python.
    
    Args:
        df: DataFrame Polars
        col_name: Nom de la colonne à parser
        clean_quotes: Si True, nettoie les guillemets autour des éléments
        
    Returns:
        DataFrame avec la colonne parsée en liste
    """
    if col_name not in df.columns:
        return df
    
    # Nettoyer et parser la colonne
    df_parsed = df.with_columns([
        pl.col(col_name)
        .str.strip_chars()
        .str.replace("'", '"')  # Remplacer quotes simples par doubles
        .str.strip_chars("[]")
        .str.split(", ")
        .alias(col_name)
    ])
    
    # Nettoyer les guillemets dans chaque élément de la liste si demandé
    if clean_quotes:
        df_parsed = df_parsed.with_columns([
            pl.col(col_name)
            .list.eval(pl.element().str.strip_chars('"\''))
            .alias(col_name)
        ])
    
    return df_parsed


def _extract_nutrition_fields(df: pl.DataFrame, validate: bool = True) -> pl.DataFrame:
    """
    Format attendu: [calories, total_fat_pct, sugar_pct, sodium_pct, 
                     protein_pct, sat_fat_pct, carb_pct]
    
    Args:
        df: DataFrame avec colonne 'nutrition'
        validate: Si True, valide les valeurs (calories >= 0, pourcentages valides)
        
    Returns:
        DataFrame avec 7 nouvelles colonnes nutritionnelles
    """
    if "nutrition" not in df.columns:
        return df

    # Vérifier le type de la colonne nutrition
    nutrition_dtype = df["nutrition"].dtype
    
    # Si nutrition est déjà une liste, on l'utilise directement
    if nutrition_dtype == pl.List:
        df_parsed = df.with_columns([
            pl.col("nutrition").alias("_nutrition_list")
        ])
    # Sinon, parser la nutrition (format string "[val1, val2, ...]")
    elif nutrition_dtype in (pl.Utf8, pl.String):
        df_parsed = df.with_columns([
            pl.col("nutrition")
            .str.strip_chars("[]")
            .str.split(", ")
            .alias("_nutrition_list")
        ])
    else:
        # Type inattendu, essayer de caster en string puis parser
        df_parsed = df.with_columns([
            pl.col("nutrition")
            .cast(pl.Utf8)
            .str.strip_chars("[]")
            .str.split(", ")
            .alias("_nutrition_list")
        ])
    
    # Extraire les 7 valeurs
    df_result = df_parsed.with_columns([
        pl.col("_nutrition_list").list.get(0).cast(pl.Float64, strict=False).alias("calories"),
        pl.col("_nutrition_list").list.get(1).cast(pl.Float64, strict=False).alias("total_fat_pct"),
        pl.col("_nutrition_list").list.get(2).cast(pl.Float64, strict=False).alias("sugar_pct"),
        pl.col("_nutrition_list").list.get(3).cast(pl.Float64, strict=False).alias("sodium_pct"),
        pl.col("_nutrition_list").list.get(4).cast(pl.Float64, strict=False).alias("protein_pct"),
        pl.col("_nutrition_list").list.get(5).cast(pl.Float64, strict=False).alias("sat_fat_pct"),
        pl.col("_nutrition_list").list.get(6).cast(pl.Float64, strict=False).alias("carb_pct")
    ]).drop("_nutrition_list")
    
    if validate:
        # Remplacer les calories négatives par null (détecté dans l'audit)
        df_result = df_result.with_columns([
            pl.when(pl.col("calories") < 0)
            .then(None)
            .otherwise(pl.col("calories"))
            .alias("calories")
        ])
        
    return df_result


def _cast_submitted_to_date(df: pl.DataFrame) -> pl.DataFrame:
    """
    Cast la colonne 'submitted' en type Date (pl.Date).
    
    Args:
        df: DataFrame avec colonne 'submitted'
        
    Returns:
        DataFrame avec 'submitted' en type pl.Date
    """
    if "submitted" not in df.columns:
        return df
    
    submitted_dtype = df["submitted"].dtype
    
    # Déjà une date ou datetime
    if submitted_dtype in (pl.Date, pl.Datetime):
        return df.with_columns([
            pl.col("submitted").cast(pl.Date).alias("submitted")
        ])
    
    # String à parser
    elif submitted_dtype in (pl.Utf8, pl.String):
        return df.with_columns([
            pl.col("submitted").str.strptime(pl.Date, "%Y-%m-%d", strict=False)
        ])
    
    # Autre type : tentative de cast direct
    else:
        return df.with_columns([
            pl.col("submitted").cast(pl.Date, strict=False)
        ])


# =============================================================================
# 🧹 NETTOYAGE DES DONNÉES
# =============================================================================

def _compute_outlier_thresholds(df: pl.DataFrame, percentile: float = 0.05) -> dict:
    """
    Calcule les seuils pour détecter les valeurs aberrantes (IQ 90% par défaut).

    Args:
        df: DataFrame avec colonnes 'n_steps' et 'n_ingredients'
        percentile: Percentile inférieur (défaut: 0.05 pour Q5%-Q95%)
        
    Returns:
        {
            'n_steps': {'min': x, 'max': y, 'q_low': 0.05, 'q_high': 0.95},
            'n_ingredients': {'min': x, 'max': y, 'q_low': 0.05, 'q_high': 0.95}
        }
    """
    thresholds = {}
    
    if "n_steps" in df.columns:
        q_low = df["n_steps"].quantile(percentile)
        q_high = df["n_steps"].quantile(1 - percentile)
        thresholds["n_steps"] = {
            "min": int(q_low),
            "max": int(q_high),
            "q_low": percentile,
            "q_high": 1 - percentile,
            "median": df["n_steps"].median(),
            "mean": df["n_steps"].mean()
        }
    
    if "n_ingredients" in df.columns:
        q_low = df["n_ingredients"].quantile(percentile)
        q_high = df["n_ingredients"].quantile(1 - percentile)
        thresholds["n_ingredients"] = {
            "min": int(q_low),
            "max": int(q_high),
            "q_low": percentile,
            "q_high": 1 - percentile,
            "median": df["n_ingredients"].median(),
            "mean": df["n_ingredients"].mean()
        }
    
    return thresholds

# =============================================================================
# 📊 CLEAN RECIPES 
# =============================================================================

def add_recipe_time_features(df: pl.DataFrame) -> pl.DataFrame:
    """Ajoute des features temporelles à partir de la date de soumission (réutilise add_calendar_features)."""
    if "submitted" not in df.columns:
        return df

    # Vérifier si submitted est déjà de type Date, sinon le parser
    submitted_dtype = df["submitted"].dtype
    
    # DuckDB retourne souvent Date directement, ou parfois Datetime
    if submitted_dtype in (pl.Date, pl.Datetime):
        # Déjà une date, juste caster en Date si besoin et renommer
        df = df.with_columns([
            pl.col("submitted").cast(pl.Date).alias("date")
        ])
    elif submitted_dtype in (pl.Utf8, pl.String):
        # C'est une string, parser en date
        df = df.with_columns([
            pl.col("submitted").str.strptime(pl.Date, "%Y-%m-%d", strict=False).alias("date")
        ])
    else:
        # Autre type, essayer de caster
        df = df.with_columns([
            pl.col("submitted").cast(pl.Date).alias("date")
        ])

    # Réutiliser la fonction commune pour les features calendaires
    return add_calendar_features(df, date_col="date")

def compute_recipe_complexity(df: pl.DataFrame) -> pl.DataFrame:
    """Crée un score de complexité basé sur minutes, n_steps, n_ingredients."""
    if not all(c in df.columns for c in ["minutes", "n_steps", "n_ingredients"]):
        return df

    return df.with_columns([
        ((pl.col("minutes").fill_null(0) / 10) +
         pl.col("n_steps").fill_null(0) +
         (pl.col("n_ingredients").fill_null(0) * 0.5)).alias("complexity_score")
    ])

def clean_and_enrich_recipes(df: pl.DataFrame) -> pl.DataFrame:
    """Pipeline complet pour nettoyer et enrichir les recettes."""
    # Cast submitted en Date AVANT drop_nulls
    df = _cast_submitted_to_date(df)
    
    # Nettoyage de base
    cleaned = df.drop_nulls(subset=["name", "submitted"])
    cleaned = cleaned.unique()
    
    # Filtrer les recettes avec minutes invalides (avant d'enrichir)
    if "minutes" in cleaned.columns:
        before = cleaned.height
        cleaned = cleaned.filter((pl.col("minutes") > 0) & (pl.col("minutes") <= 180))
        removed = before - cleaned.height
        if removed > 0:
            print(f"🧹 Filtrage minutes : {removed:,} recettes retirées (<=0 ou >180 min)")

    # Enrichissement avec features
    enriched = (
        cleaned
        .pipe(_extract_nutrition_fields)
        .pipe(add_recipe_time_features)
        .pipe(compute_recipe_complexity)
    )
    print(f"✅ Recettes nettoyées et enrichies : {enriched.shape}")
    return enriched

def load_clean_recipes(db_path: Optional[Path] = None) -> pl.DataFrame:
    """Charge les recettes nettoyées et enrichies prêtes à l’analyse."""
    df_raw = load_recipes_raw(db_path)
    return clean_and_enrich_recipes(df_raw)


def clean_recipes(df: pl.DataFrame) -> pl.DataFrame:
    """
    Nettoie et prépare les données de la table RAW_RECIPES.
    
    Args: df: DataFrame Polars brut depuis DuckDB
        
    Returns: DataFrame nettoyé et structuré
    """
    print("🧹 Nettoyage des recettes...")
    initial_rows = df.height
    
    # 1. Supprimer les doublons basés sur 'id' ou combinaison name+submitted
    df = df.unique(subset=["id"]) if "id" in df.columns else df.unique()
    duplicates_removed = initial_rows - df.height
    if duplicates_removed > 0:
        print(f"   ✓ {duplicates_removed:,} doublons supprimés")
    
    # 2. Filtrer les minutes aberrantes
    if "minutes" in df.columns:
        before = df.height
        df = df.filter(
            (pl.col("minutes") >= 1) & (pl.col("minutes") <= 180)
        )
        removed = before - df.height
        if removed > 0:
            print(f"   ✓ {removed:,} recettes avec minutes invalides (<1 ou >180)")
    
    # 2b. Filtrer les valeurs aberrantes de n_steps et n_ingredients (IQ 90%)
    # Calcul automatique des seuils à partir de la distribution réelle
    if "n_steps" in df.columns and "n_ingredients" in df.columns:
        # Calculer les seuils basés sur les quantiles
        thresholds = _compute_outlier_thresholds(df, percentile=0.025)
        
        # Afficher les seuils calculés pour traçabilité
        print(f"   ℹ️  Seuils calculés (IQ 90% = Q5%-Q95%):")
        for col, bounds in thresholds.items():
            print(f"      • {col}: [{bounds['min']}, {bounds['max']}] "
                  f"(médiane={bounds['median']:.0f}, moyenne={bounds['mean']:.1f})")
        
        # Appliquer le filtrage
        before = df.height
        df = df.filter(
            (pl.col("n_steps") >= thresholds["n_steps"]["min"]) & 
            (pl.col("n_steps") <= thresholds["n_steps"]["max"]) &
            (pl.col("n_ingredients") >= thresholds["n_ingredients"]["min"]) & 
            (pl.col("n_ingredients") <= thresholds["n_ingredients"]["max"])
        )
        removed = before - df.height
        if removed > 0:
            print(f"   ✓ {removed:,} recettes avec n_steps ou n_ingredients aberrants (hors IQ 90%)")
    
    # 3. Cast submitted en Date AVANT drop_nulls
    df = _cast_submitted_to_date(df)
    
    # 4. Supprimer les lignes sans submitted ou name
    df = df.drop_nulls(subset=["submitted", "name"])
    
    # 5. Parser les colonnes de type liste/JSON avec nettoyage des guillemets
    df = _parse_list_column(df, "tags", clean_quotes=True)
    df = _parse_list_column(df, "ingredients", clean_quotes=True)
    df = _parse_list_column(df, "steps")
    
    # 6. Extraire les champs nutrition avec validation
    df = _extract_nutrition_fields(df, validate=True)
    
    # 7. Supprimer les recettes sans nutrition ou sans ingrédients
    before = df.height
    df = df.filter(
        pl.col("calories").is_not_null() &
        (pl.col("n_ingredients") > 0)
    )
    removed = before - df.height
    if removed > 0:
        print(f"   ✓ {removed:,} recettes sans nutrition ou ingrédients")
    
    final_rows = df.height
    print(f"✅ Nettoyage terminé : {final_rows:,} recettes conservées ({initial_rows - final_rows:,} supprimées)")
    
    return df


# =============================================================================
# ⚙️ ENRICH RECIPES - FEATURES ENGINEERING
# =============================================================================

def _add_temporal_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Ajoute les features temporelles : year, month, weekday, is_weekend, season.
        
    Args:
        df: DataFrame avec colonne 'submitted' (type Date)
        
    Returns:
        DataFrame avec features temporelles ajoutées
    """
    if "submitted" not in df.columns:
        return df
    
    # Créer une colonne 'date' temporaire pour la fonction commune
    df = df.with_columns([
        pl.col("submitted").alias("date")
    ])
    
    # Utiliser la fonction commune
    df = add_calendar_features(df, date_col="date")
    
    # Supprimer la colonne temporaire 'date' si elle n'existait pas avant
    if "date" in df.columns:
        df = df.drop("date")
    
    return df


def _add_complexity_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Calcule le score de complexité des recettes.
    Formule: complexity_score = log1p(minutes) + n_steps + 0.5 * n_ingredients
    
    Args:
        df: DataFrame avec colonnes 'minutes', 'n_steps', 'n_ingredients'
        
    Returns:
        DataFrame avec colonne 'complexity_score' ajoutée
    """
    required_cols = ["minutes", "n_steps", "n_ingredients"]
    if not all(c in df.columns for c in required_cols):
        return df
    
    return df.with_columns([
        (
            pl.col("minutes").fill_null(0).log1p() +
            pl.col("n_steps").fill_null(0) +
            (pl.col("n_ingredients").fill_null(0) * 0.5)
        ).alias("complexity_score")
    ])


def _add_ingredient_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Ajoute des features liées aux ingrédients.    
    - Recalcule n_ingredients si manquant (depuis la liste ingredients)

    Args:
        df: DataFrame avec colonne 'ingredients'
        
    Returns:
        DataFrame avec features ingrédients ajoutées
    """
    if "ingredients" not in df.columns:
        return df
    
    # Recalculer n_ingredients si manquant ou incohérent
    df = df.with_columns([
        pl.when(pl.col("n_ingredients").is_null())
        .then(pl.col("ingredients").list.len())
        .otherwise(pl.col("n_ingredients"))
        .alias("n_ingredients")
    ])
    
    return df


def _add_textual_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Ajoute des features textuelles:
    
    - avg_step_length: longueur moyenne des étapes
    - description_length: longueur de la description
    
    Args:
        df: DataFrame avec colonnes 'steps', 'description'
        
    Returns:
        DataFrame avec features textuelles ajoutées
    """
    # Longueur moyenne des étapes
    if "steps" in df.columns:
        df = df.with_columns([
            pl.col("steps")
            .list.eval(pl.element().str.len_chars())
            .list.mean()
            .alias("avg_step_length")
        ])
    
    # Longueur de la description
    if "description" in df.columns:
        df = df.with_columns([
            pl.col("description").str.len_chars().alias("description_length")
        ])
    
    return df

def enrich_recipes(df: pl.DataFrame) -> pl.DataFrame:
    """
    Crée les features analytiques pour l'analyse des recettes.
    
    Features créées:
        🕐 Temporal: year, month, weekday, is_weekend, season
        ⚙️ Complexity: complexity_score (log1p(minutes) + n_steps + 0.5*n_ingredients)
        🍽️ Nutrition: 7 colonnes (calories, total_fat_pct, sugar_pct, etc.)
        🧾 Textual: avg_step_length, description_length
        
    Args:
        df: DataFrame nettoyé (sortie de clean_recipes)
        
    Returns:
        DataFrame enrichi avec toutes les features
    """
    print("⚙️ Enrichissement des recettes...")
    
    # Pipeline d'enrichissement
    df = (
        df
        .pipe(_add_temporal_features)
        .pipe(_add_complexity_features)
        .pipe(_add_ingredient_features)
        .pipe(_add_textual_features)
    )
    
    print(f"✅ Enrichissement terminé : {df.shape[1]} colonnes totales")
    
    return df

# =============================================================================
# 🚀 PIPELINE COMPLET
# =============================================================================

def load_clean_recipes(limit: Optional[int] = None, save_to_s3: bool = False) -> pl.DataFrame:
    """
    Pipeline complet : charge, nettoie et enrichit les recettes en une seule commande.
    Sauvegarde automatiquement le résultat sur S3.

    Args: 
        limit: Nombre maximum de lignes à charger (optionnel)
        save_to_s3: Si True, sauvegarde le DataFrame final sur S3
        
    Returns: 
        DataFrame prêt pour l'analyse
    """
    # 1️⃣ Chargement brut
    print("1️⃣ Chargement des données brutes...")
    df_raw = load_recipes_raw(limit)
    
    # 2️⃣ Nettoyage
    print("\n2️⃣ Nettoyage des données...")
    df_clean = clean_recipes(df_raw)
    
    # 3️⃣ Enrichissement
    print("\n3️⃣ Enrichissement des features...")
    df_final = enrich_recipes(df_clean)
    
    # 4️⃣ Sauvegarde sur S3
    if save_to_s3:
        print("\n4️⃣ Sauvegarde sur S3...")
        s3_path = "s3://mangetamain/final_recipes.parquet"
        save_recipes_to_s3(df_final, s3_path, format="parquet")
        print(f"💾 Dataset final sauvegardé : {s3_path}")
    
    print("\n✅ Pipeline complet terminé !")
    return df_final

# =============================================================================
# 📊 ANALYSE DE QUALITÉ
# =============================================================================

def analyze_recipe_quality(df: pl.DataFrame) -> Dict[str, any]:
    """
    Génère un rapport synthétique de qualité des données.
    
    Informations incluses:
        - Nombre de lignes, colonnes, doublons
        - Valeurs nulles par colonne
        - Distribution des variables clés (minutes, n_steps, n_ingredients)
        - Période temporelle couverte (min/max de submitted)
        
    Args:
        df: DataFrame à analyser
        
    Returns:
        Dictionnaire avec métriques de qualité
    """
    print("📊 Analyse de qualité des données...")
    
    report = {
        "n_rows": df.height,
        "n_cols": df.width,
        "columns": df.columns,
        "duplicate_count": df.is_duplicated().sum(),
        "null_counts": {col: df[col].null_count() for col in df.columns if df[col].null_count() > 0}
    }
    
    # Statistiques sur minutes
    if "minutes" in df.columns:
        minutes_stats = df.select("minutes").describe()
        report["minutes_stats"] = {
            "mean": df["minutes"].mean(),
            "median": df["minutes"].median(),
            "min": df["minutes"].min(),
            "max": df["minutes"].max(),
            "q25": df["minutes"].quantile(0.25),
            "q75": df["minutes"].quantile(0.75)
        }
    
    # Statistiques sur n_steps
    if "n_steps" in df.columns:
        report["n_steps_stats"] = {
            "mean": df["n_steps"].mean(),
            "median": df["n_steps"].median(),
            "min": df["n_steps"].min(),
            "max": df["n_steps"].max()
        }
    
    # Statistiques sur n_ingredients
    if "n_ingredients" in df.columns:
        report["n_ingredients_stats"] = {
            "mean": df["n_ingredients"].mean(),
            "median": df["n_ingredients"].median(),
            "min": df["n_ingredients"].min(),
            "max": df["n_ingredients"].max()
        }
    
    # Période temporelle
    if "submitted" in df.columns:
        report["time_range"] = {
            "min_date": df["submitted"].min(),
            "max_date": df["submitted"].max(),
            "n_years": (df["submitted"].max().year - df["submitted"].min().year) if df["submitted"].min() else None
        }
    
    # Affichage du rapport
    print(f"\n{'='*70}")
    print(f"📋 RAPPORT DE QUALITÉ - RAW_RECIPES")
    print(f"{'='*70}")
    print(f"📦 Dimensions : {report['n_rows']:,} lignes × {report['n_cols']} colonnes")
    print(f"🔄 Doublons : {report['duplicate_count']:,}")
    
    if report['null_counts']:
        print(f"⚠️  Valeurs nulles :")
        for col, count in sorted(report['null_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
            pct = (count / report['n_rows']) * 100
            print(f"   • {col}: {count:,} ({pct:.1f}%)")
    
    if "minutes_stats" in report:
        print(f"⏱️ Minutes : médiane={report['minutes_stats']['median']:.0f}, "
              f"moyenne={report['minutes_stats']['mean']:.1f}, "
              f"max={report['minutes_stats']['max']:,}")

    if "n_steps_stats" in report:
        print(f"🔜 Steps : médiane={report['n_steps_stats']['median']:.0f}, "
              f"moyenne={report['n_steps_stats']['mean']:.1f}, "
              f"max={report['n_steps_stats']['max']}")
    else:
        print("There is no n_steps in this.")
            
    if "n_ingredients_stats" in report:
        print(f"🥕 Ingrédients : médiane={report['n_ingredients_stats']['median']:.0f}, "
              f"moyenne={report['n_ingredients_stats']['mean']:.1f}, "
              f"max={report['n_ingredients_stats']['max']}")
    
    if "time_range" in report and report['time_range']['min_date']:
        print(f"📅 Période : {report['time_range']['min_date']} → {report['time_range']['max_date']} "
              f"({report['time_range']['n_years']} ans)")
    
    print(f"{'='*70}\n")
    
    return report