from .data_utils_common import *

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

def load_recipes_raw(db_path: Optional[Path] = None, limit: Optional[int] = None) -> pl.DataFrame:
    """Charge la table RAW_recipes complète depuis DuckDB."""
    if db_path is None:
        db_path = get_db_path()

    sql = "SELECT * FROM RAW_recipes"
    if limit:
        sql += f" LIMIT {limit}"

    with duckdb.connect(database=str(db_path), read_only=True) as conn:
        df = conn.execute(sql).pl()

    print(f"✅ RAW_recipes chargée ({df.shape[0]} lignes, {df.shape[1]} colonnes)")
    return df

# =============================================================================
# QUALITÉ & NETTOYAGE
# =============================================================================

def analyze_recipe_quality(df: pl.DataFrame) -> Dict[str, any]:
    """Analyse de qualité spécifique aux recettes."""
    report = {
        "shape": df.shape,
        "columns": df.columns,
        "null_counts": df.null_count().to_dict(),
        "duplicate_count": df.is_duplicated().sum(),
    }

    # Statistiques basiques sur la durée
    if "minutes" in df.columns:
        report["minutes_stats"] = {
            "mean": df["minutes"].mean(),
            "median": df["minutes"].median(),
            "max": df["minutes"].max(),
            "min": df["minutes"].min()
        }

    # Sur le nombre d'ingrédients
    if "n_ingredients" in df.columns:
        report["ingredients_stats"] = {
            "mean": df["n_ingredients"].mean(),
            "median": df["n_ingredients"].median(),
            "max": df["n_ingredients"].max()
        }

    print(f"📊 Rapport de qualité des recettes ({df.shape[0]} lignes)")
    print(f"Colonnes : {', '.join(df.columns)}")
    print(f"Doublons : {report['duplicate_count']}")
    print(f"Valeurs manquantes principales :")
    print({k: v for k, v in report['null_counts'].items() if v > 0})

    return report

# =============================================================================
# PARSING & ENRICHISSEMENT
# =============================================================================

def parse_nutrition_column(df: pl.DataFrame) -> pl.DataFrame:
    """Décompose la colonne nutrition (liste de 7 éléments) en colonnes séparées."""
    if "nutrition" not in df.columns:
        return df

    return df.with_columns([
        pl.col("nutrition").str.strip_chars("[]").str.split(", ").alias("nutrition_list")
    ]).with_columns([
        pl.col("nutrition_list").list.get(0).cast(pl.Float64).alias("calories"),
        pl.col("nutrition_list").list.get(1).cast(pl.Float64).alias("total_fat_pct"),
        pl.col("nutrition_list").list.get(2).cast(pl.Float64).alias("sugar_pct"),
        pl.col("nutrition_list").list.get(3).cast(pl.Float64).alias("sodium_pct"),
        pl.col("nutrition_list").list.get(4).cast(pl.Float64).alias("protein_pct"),
        pl.col("nutrition_list").list.get(5).cast(pl.Float64).alias("sat_fat_pct"),
        pl.col("nutrition_list").list.get(6).cast(pl.Float64).alias("carb_pct")
    ]).drop("nutrition_list")

def add_recipe_time_features(df: pl.DataFrame) -> pl.DataFrame:
    """Ajoute des features temporelles à partir de la date de soumission."""
    if "submitted" not in df.columns:
        return df

    df = df.with_columns([
        pl.col("submitted").str.strptime(pl.Date, "%Y-%m-%d", strict=False).alias("date")
    ])

    return df.with_columns([
        pl.col("date").dt.year().alias("year"),
        pl.col("date").dt.month().alias("month"),
        (pl.col("date").dt.weekday() >= 5).cast(pl.Int8).alias("is_weekend"),
        pl.when(pl.col("date").dt.month().is_in([12, 1, 2])).then(pl.lit("Winter"))
          .when(pl.col("date").dt.month().is_in([3, 4, 5])).then(pl.lit("Spring"))
          .when(pl.col("date").dt.month().is_in([6, 7, 8])).then(pl.lit("Summer"))
          .otherwise(pl.lit("Autumn")).alias("season")
    ])

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
    cleaned = df.drop_nulls(subset=["name", "submitted"])
    cleaned = cleaned.unique()

    enriched = (
        cleaned
        .pipe(parse_nutrition_column)
        .pipe(add_recipe_time_features)
        .pipe(compute_recipe_complexity)
    )
    print(f"✅ Recettes nettoyées et enrichies : {enriched.shape}")
    return enriched

def load_clean_recipes(db_path: Optional[Path] = None) -> pl.DataFrame:
    """Charge les recettes nettoyées et enrichies prêtes à l’analyse."""
    df_raw = load_recipes_raw(db_path)
    return clean_and_enrich_recipes(df_raw)

# =============================================================================
# ANALYSES RAPIDES
# =============================================================================

def prepare_recipe_analysis(df: pl.DataFrame) -> Dict[str, pd.DataFrame]:
    """Prépare les datasets agrégés pour les analyses temporelles."""
    if "year" not in df.columns:
        df = add_recipe_time_features(df)

    return {
        "recipes_per_year": df.group_by("year").agg(pl.len().alias("n_recipes")).to_pandas(),
        "avg_duration_per_year": df.group_by("year").agg(pl.mean("minutes").alias("avg_minutes")).to_pandas(),
        "avg_complexity_per_season": df.group_by("season").agg(pl.mean("complexity_score").alias("mean_complexity")).to_pandas(),
        "avg_calories_per_year": df.group_by("year").agg(pl.mean("calories").alias("avg_calories")).to_pandas()
    }
