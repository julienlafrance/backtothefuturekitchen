
from .data_utils_common import *

# =============================================================================
# LOADING
# =============================================================================

def load_interactions_raw(db_path: Optional[Path] = None) -> pl.DataFrame:
    """Charge la table RAW_interactions avec filtrage de base - EXCLUT les ratings à 0."""
    if db_path is None:
        db_path = get_db_path()
    
    sql = """
    SELECT *
    FROM RAW_interactions
    WHERE rating BETWEEN 1 AND 5
      AND date IS NOT NULL
    """
    
    with duckdb.connect(database=str(db_path), read_only=True) as conn:
        return conn.execute(sql).pl()

def load_enriched_interactions(db_path: Optional[Path] = None) -> pl.DataFrame:
    """Charge interactions enrichies avec les données de recettes - EXCLUT les ratings à 0."""
    if db_path is None:
        db_path = get_db_path()
    
    sql = """
    SELECT 
        i.user_id,
        i.recipe_id,
        i.date,
        i.rating,
        i.review,
        r.name as recipe_name,
        r.ingredients,
        r.tags,
        r.nutrition,
        r.n_steps,
        r.n_ingredients
    FROM RAW_interactions i
    LEFT JOIN RAW_recipes r ON i.recipe_id = r.id
    WHERE i.rating BETWEEN 1 AND 5
      AND i.date IS NOT NULL
    """
    
    with duckdb.connect(database=str(db_path), read_only=True) as conn:
        return conn.execute(sql).pl()
    
# =============================================================================
# TRANSFORMATIONS
# =============================================================================

def add_rating_features(df: pl.DataFrame, rating_col: str = "rating") -> pl.DataFrame:
    """Ajoute les features dérivées du rating (z-score normalisé, catégories)."""
    rating_mean = df[rating_col].mean()
    rating_std = df[rating_col].std()
    
    return df.with_columns([
        ((pl.col(rating_col) - rating_mean) / rating_std).alias("normalized_rating"),
        pl.when(pl.col(rating_col) <= 2).then(pl.lit("Low"))
          .when(pl.col(rating_col) <= 3).then(pl.lit("Medium"))
          .when(pl.col(rating_col) <= 4).then(pl.lit("High"))
          .otherwise(pl.lit("Excellent")).alias("rating_category"),
    ])

def clean_and_enrich_interactions(df: pl.DataFrame) -> pl.DataFrame:
    """Pipeline complet de nettoyage et enrichissement - EXCLUT les ratings à 0 - retourne une copie transformée."""
    # Nettoyage de base (copie pour ne pas modifier l'original)
    # IMPORTANT: Exclut les ratings à 0 car ils correspondent à des interactions sans note
    cleaned = df.filter(
        (pl.col("rating").is_between(1, 5, closed="both")) &
        (pl.col("date").is_not_null())
    )
    
    # Suppression des duplicatas exacts
    cleaned = cleaned.unique()
    
    # Ajout des features
    enriched = add_calendar_features(cleaned)
    enriched = add_rating_features(enriched)
    
    return enriched

def load_clean_interactions(db_path: Optional[Path] = None) -> pl.DataFrame:
    """Charge et nettoie les interactions en une seule fois - version transformée prête à l'emploi."""
    raw_interactions = load_interactions_raw(db_path)
    return clean_and_enrich_interactions(raw_interactions)

# =============================================================================
# FONCTIONS INGRÉDIENTS - NOUVELLES
# =============================================================================

def extract_ingredients_from_string(ingredients_str: str) -> List[str]:
    """Extrait les ingrédients d'une string format "['ing1', 'ing2', ...]"."""
    if not ingredients_str or ingredients_str == 'null':
        return []
    
    # Supprime les crochets et guillemets, puis split sur les virgules
    cleaned = ingredients_str.strip("[]").replace("'", "").replace('"', '')
    ingredients = [ing.strip() for ing in cleaned.split(",")]
    
    # Filtre les éléments vides et normalise
    return [ing.lower().strip() for ing in ingredients if ing.strip()]

def explore_ingredients_format(db_path: Optional[Path] = None, n_samples: int = 10) -> Dict:
    """Fonction de test pour comprendre le format des ingrédients."""
    if db_path is None:
        db_path = get_db_path()
    
    # Charge quelques recettes avec ingrédients
    sql = """
    SELECT id as recipe_id, name, ingredients, n_ingredients
    FROM RAW_recipes 
    WHERE ingredients IS NOT NULL 
    LIMIT ?
    """
    
    with duckdb.connect(database=str(db_path), read_only=True) as conn:
        df_sample = conn.execute(sql, [n_samples]).pl()
    
    # Analyse du format
    analysis = {
        "sample_count": len(df_sample),
        "ingredients_samples": [],
        "format_analysis": {},
    }
    
    for row in df_sample.iter_rows(named=True):
        ingredients_str = row["ingredients"]
        extracted = extract_ingredients_from_string(ingredients_str)
        
        analysis["ingredients_samples"].append({
            "recipe_id": row["recipe_id"],
            "name": row["name"][:50] + "..." if len(row["name"]) > 50 else row["name"],
            "n_ingredients": row["n_ingredients"],
            "raw_string": ingredients_str[:100] + "..." if len(str(ingredients_str)) > 100 else ingredients_str,
            "extracted_count": len(extracted),
            "extracted_sample": extracted[:3]  # Premiers 3 ingrédients
        })
    
    # Stats globales
    all_extracted = []
    for sample in analysis["ingredients_samples"]:
        recipe_ingredients = extract_ingredients_from_string(
            df_sample.filter(pl.col("recipe_id") == sample["recipe_id"])["ingredients"][0]
        )
        all_extracted.extend(recipe_ingredients)
    
    analysis["format_analysis"] = {
        "total_ingredients_extracted": len(all_extracted),
        "unique_ingredients": len(set(all_extracted)),
        "most_common": pd.Series(all_extracted).value_counts().head(10).to_dict(),
        "avg_ingredients_per_recipe": len(all_extracted) / n_samples if n_samples > 0 else 0
    }
    
    return analysis

def load_ingredient_ratings(target_ingredients: List[str], db_path: Optional[Path] = None) -> pl.DataFrame:
    """
    Charge les ratings pour recettes contenant des ingrédients spécifiques.
    
    SCHÉMA DU DATASET FINAL:
    - recipe_id: ID de la recette
    - user_id: ID utilisateur  
    - date: Date de l'interaction
    - rating: Note donnée (1-5)
    - ingredient_name: Nom de l'ingrédient trouvé
    - recipe_name: Nom de la recette (pour debug)
    - n_ingredients: Nombre total ingrédients recette
    
    Une ligne par (recette × ingrédient_cible_trouvé × interaction)
    """
    df_enriched = load_enriched_interactions(db_path)
    
    # Explode les ingrédients - chaque recette devient N lignes (1 par ingrédient)
    df_with_ingredients = (df_enriched
        .with_columns([
            # Extraction des ingrédients individuels  
            pl.col("ingredients").map_elements(
                lambda x: extract_ingredients_from_string(str(x)) if x else [],
                return_dtype=pl.List(pl.Utf8)
            ).alias("ingredient_list")
        ])
        .explode("ingredient_list")  # Explose la liste = 1 ligne par ingrédient
        .rename({"ingredient_list": "ingredient_name"})
        .filter(pl.col("ingredient_name") != "")  # Supprime les vides
    )
    
    # Filtre sur les ingrédients cibles seulement
    df_filtered = df_with_ingredients.filter(
        pl.col("ingredient_name").is_in([ing.lower().strip() for ing in target_ingredients])
    )
    
    # Sélectionne les colonnes finales
    return df_filtered.select([
        "recipe_id", 
        "user_id", 
        "date", 
        "rating",
        "ingredient_name",
        "recipe_name",
        "n_ingredients"
    ])

# =============================================================================
# FONCTIONS D'ANALYSE SPÉCIALISÉES
# =============================================================================

def prepare_volume_analysis(df: pl.DataFrame) -> Dict[str, pd.DataFrame]:
    """Prépare les DataFrames pour l'analyse de volume (graphiques)."""
    return {
        "by_year": df.group_by("year").agg(pl.len().alias("n_interactions")).sort("year").to_pandas(),
        "by_month": df.group_by("month").agg(pl.len().alias("n_interactions")).sort("month").to_pandas(),
        "by_weekend": df.group_by("is_weekend").agg(pl.len().alias("n_interactions")).sort("is_weekend").to_pandas(),
        "by_season": df.group_by("season").agg(pl.len().alias("n_interactions")).to_pandas(),
    }

def prepare_rating_analysis(df: pl.DataFrame) -> Dict[str, pd.DataFrame]:
    """Prépare les DataFrames pour l'analyse des ratings."""
    return {
        "monthly_stats": df.group_by("year", "month").agg([
            pl.col("rating").mean().alias("mean_rating"),
            pl.col("rating").median().alias("median_rating"),
            pl.col("rating").std().alias("std_rating"),
            pl.len().alias("n_interactions")
        ]).sort(["year", "month"]).to_pandas(),
        
        "seasonal_stats": df.group_by("season").agg([
            pl.col("rating").mean().alias("mean_rating"),
            pl.col("rating").median().alias("median_rating"),
            pl.col("rating").std().alias("std_rating"),
            pl.len().alias("n_interactions")
        ]).to_pandas(),
        
        "weekend_stats": df.group_by("is_weekend").agg([
            pl.col("rating").mean().alias("mean_rating"),
            pl.col("rating").median().alias("median_rating"),
            pl.col("rating").std().alias("std_rating"),
            pl.len().alias("n_interactions")
        ]).to_pandas(),
    }

# =============================================================================
# FONCTIONS DE TEST
# =============================================================================

def show_transformed_sample(df: pl.DataFrame, n: int = 5):
    """Affiche un échantillon formaté des données transformées."""
    print(f"📊 Aperçu des données transformées ({n} premières lignes):")
    
    # Colonnes de base
    base_cols = ["user_id", "recipe_id", "date", "rating"]
    # Nouvelles colonnes ajoutées
    new_cols = [col for col in df.columns if col not in base_cols]
    
    print(f"🆕 Nouvelles colonnes ajoutées: {', '.join(new_cols)}")
    
    # Affichage avec sélection de colonnes importantes
    display_cols = base_cols + ["year", "month", "season", "is_weekend", "normalized_rating"]
    available_cols = [col for col in display_cols if col in df.columns]
    
    sample_df = df.select(available_cols).head(n)
    print(sample_df)
    
    return sample_df

def test_data_pipeline():
    """Test rapide du pipeline de données."""
    print("🧪 Test du pipeline de données...")
    
    # Test connexion
    db_path = get_db_path()
    print(f"✅ DB trouvée: {db_path}")
    
    # Test chargement RAW (original, non modifié)
    df_raw = load_interactions_raw(db_path)
    print(f"✅ RAW_interactions chargées: {df_raw.shape}")
    
    # Test qualité RAW
    report_raw = analyze_data_quality(df_raw, "RAW_interactions")
    print_quality_report(report_raw)
    
    # Test version transformée (copie enrichie)
    df_transformed = load_clean_interactions(db_path)
    print(f"\n✅ Interactions transformées: {df_transformed.shape}")
    
    # Test qualité transformée
    report_transformed = analyze_data_quality(df_transformed, "TRANSFORMED_interactions")
    print_quality_report(report_transformed)
    
    # Aperçu formaté de la version transformée
    show_transformed_sample(df_transformed, n=5)
    
    return df_raw, df_transformed

# =============================================================================
# FONCTIONS POUR ANALYSES TEMPORELLES D'INGRÉDIENTS
# =============================================================================

def get_ingredients_for_analysis(analysis_type: str) -> List[str]:
    """
    Retourne la liste des ingrédients cibles selon le type d'analyse temporelle.
    
    Args:
        analysis_type: Type d'analyse ('long_term', 'seasonality', 'weekend')
    
    Returns:
        Liste des ingrédients sélectionnés pour l'analyse
    """
    # Ingrédients CORE (présents dans toutes les analyses)
    core_ingredients = ['salt', 'ground beef', 'eggs', 'onions', 'garlic']
    
    # Ingrédients spécialisés par axe d'analyse
    if analysis_type == 'long_term':
        # Ingrédients avec >= 10 ans de données pour analyser les tendances long-terme
        specialized = ['butter', 'olive oil']
        return core_ingredients + specialized
    
    elif analysis_type == 'seasonality':
        # Ingrédients avec potentiel saisonnier fort
        specialized = ['butternut squash', 'asparagus', 'pumpkin']
        return core_ingredients + specialized
    
    elif analysis_type == 'weekend':
        # Tous les ingrédients disponibles (weekend a moins de contraintes)
        specialized = ['butternut squash', 'asparagus', 'pumpkin', 'butter', 'olive oil']
        return core_ingredients + specialized
    
    else:
        raise ValueError(f"Type d'analyse non supporté: {analysis_type}. "
                        f"Utilisez 'long_term', 'seasonality', ou 'weekend'.")

def load_ingredient_ratings(target_ingredients: List[str], db_path: Optional[Path] = None) -> pl.DataFrame:
    """
    Charge les données de ratings filtrées par ingrédients cibles.
    
    Args:
        target_ingredients: Liste des ingrédients à analyser
        db_path: Chemin vers la base DuckDB (auto-détecté si None)
    
    Returns:
        DataFrame Polars avec les ratings des ingrédients sélectionnés
    """
    if db_path is None:
        db_path = get_db_path()
    
    # Création de la clause WHERE pour les ingrédients
    ingredients_clause = "', '".join(target_ingredients)
    
    # Requête optimisée avec jointure et filtrage
    query = f"""
    SELECT 
        i.date,
        i.rating,
        i.user_id,
        i.recipe_id,
        r.name as recipe_name,
        r.n_ingredients,
        ingredient.value as ingredient_name
    FROM RAW_interactions i
    JOIN RAW_recipes r ON i.recipe_id = r.id
    JOIN (
        SELECT 
            id as recipe_id,
            UNNEST(string_split(TRIM(ingredients, '[]'), ', ')) as ingredient_value
        FROM RAW_recipes
    ) ingredient_table ON r.id = ingredient_table.recipe_id
    JOIN (
        SELECT DISTINCT
            TRIM(value, ''' "''') as value
        FROM (
            SELECT UNNEST(string_split(TRIM(ingredients, '[]'), ', ')) as value
            FROM RAW_recipes
        )
        WHERE TRIM(value, ''' "''') IN ('{ingredients_clause}')
    ) ingredient ON TRIM(ingredient_table.ingredient_value, ''' "''') = ingredient.value
    WHERE 
        i.rating IS NOT NULL
        AND i.rating BETWEEN 1 AND 5  -- 🛠️ CORRECTION: Exclut les ratings à 0
        AND i.date IS NOT NULL
        AND r.ingredients IS NOT NULL
        AND LENGTH(r.ingredients) > 2
    ORDER BY i.date, ingredient.value
    """
    
    with duckdb.connect(database=str(db_path), read_only=True) as conn:
        df = conn.execute(query).pl()
    
    print(f"✅ Données chargées: {df.shape[0]:,} interactions pour {len(target_ingredients)} ingrédients")
    
    return df

# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    # Exécution du test si ce module est lancé directement
    test_data_pipeline()