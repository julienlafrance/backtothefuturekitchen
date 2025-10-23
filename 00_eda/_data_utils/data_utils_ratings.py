
from .data_utils_common import *
from typing import Union, Tuple, Dict, List, Optional
import pandas as pd

# =============================================================================
# LOADING
# =============================================================================

def load_interactions_raw() -> pl.DataFrame:
    """
    Charge les données d'interactions depuis S3.
    EXCLUT les ratings à 0 et les dates nulles.
    
    Returns:
        pl.DataFrame: Interactions filtrées (rating 1-5, date non-null)
    """
    # Charger depuis S3
    conn = get_s3_duckdb_connection()
    sql = """
    SELECT *
    FROM 's3://mangetamain/interactions_train.csv'
    WHERE rating BETWEEN 1 AND 5
      AND date IS NOT NULL
    """
    df = conn.execute(sql).pl()
    conn.close()
    
    print(f"✅ Interactions chargées depuis S3 : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
    return df

def load_enriched_interactions() -> pl.DataFrame:
    """
    Charge interactions enrichies avec les données de recettes depuis S3.
    EXCLUT les ratings à 0 et les dates nulles.
    
    Returns:
        pl.DataFrame: Interactions enrichies avec colonnes recette
    """
    # Charger depuis S3 avec JOIN
    conn = get_s3_duckdb_connection()
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
    FROM 's3://mangetamain/interactions_train.csv' i
    LEFT JOIN 's3://mangetamain/PP_recipes.csv' r ON i.recipe_id = r.id
    WHERE i.rating BETWEEN 1 AND 5
      AND i.date IS NOT NULL
    """
    df = conn.execute(sql).pl()
    conn.close()
    
    print(f"✅ Interactions enrichies chargées depuis S3 : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
    return df
    

    
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

def load_clean_interactions() -> pl.DataFrame:
    """Charge et nettoie les interactions depuis S3 - version transformée prête à l'emploi."""
    raw_interactions = load_interactions_raw()
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
    """Test rapide du pipeline de données S3."""
    print("🧪 Test du pipeline de données S3...")
    
    # Test chargement RAW depuis S3
    df_raw = load_interactions_raw()
    print(f"✅ RAW_interactions chargées depuis S3: {df_raw.shape}")
    
    # Test qualité RAW
    report_raw = analyze_data_quality(df_raw, "RAW_interactions")
    print_quality_report(report_raw)
    
    # Test version transformée (copie enrichie)
    df_transformed = load_clean_interactions()
    print(f"\n✅ Interactions transformées: {df_transformed.shape}")
    
    # Test qualité transformée
    report_transformed = analyze_data_quality(df_transformed, "TRANSFORMED_interactions")
    print_quality_report(report_transformed)
    
    # Aperçu formaté de la version transformée
    show_transformed_sample(df_transformed, n=5)
    
    return df_raw, df_transformed

# =============================================================================
# FONCTIONS POUR ANALYSES TEMPORELLES - RATINGS GLOBAUX
# =============================================================================

def load_ratings_for_longterm_analysis(
    min_interactions: int = 100,
    return_metadata: bool = True,
    verbose: bool = True
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict]]:
    """
    Charge les statistiques mensuelles de ratings avec filtrage de robustesse statistique depuis S3.
    
    Conçue pour analyses de tendances long-terme (Mann-Kendall, régression linéaire).
    Élimine les mois avec volume insuffisant pour garantir la fiabilité statistique.
    
    Args:
        min_interactions: Seuil minimum d'interactions par mois (défaut: 100)
                         Recommandé: >=100 pour robustesse, >=50 minimum acceptable
        return_metadata: Si True, retourne aussi les métadonnées de filtrage
        verbose: Si True, affiche les logs de progression
        
    Returns:
        pd.DataFrame: Stats mensuelles filtrées avec colonnes:
            - year, month, date: identifiants temporels
            - mean_rating, median_rating, std_rating: statistiques de rating
            - n_interactions: volume mensuel (tous >= min_interactions)
        dict (optionnel): Métadonnées du filtrage:
            - seuil_applique, mois_total, mois_exclus, mois_conserves
            - pct_exclus, periode_avant, periode_apres
            - gaps_temporels (bool), volume_moyen_avant, volume_moyen_apres
    
    Example:
        >>> monthly_stats, meta = load_ratings_for_longterm_analysis(
        ...     min_interactions=100, return_metadata=True, verbose=False
        ... )
        >>> print(f"Période d'analyse: {meta['periode_apres']}")
        >>> print(f"Mois conservés: {meta['mois_conserves']}")
    """
    if verbose:
        print(f"🔄 Chargement avec seuil de robustesse: {min_interactions}")
    
    # 1. Chargement données de base depuis S3 (filtrées: rating 1-5, date non-null)
    df_clean = load_clean_interactions()
    
    # 2. Agrégation mensuelle complète (avant filtrage)
    monthly_raw = df_clean.group_by(["year", "month"]).agg([
        pl.col("rating").mean().alias("mean_rating"),
        pl.col("rating").median().alias("median_rating"),
        pl.col("rating").std().alias("std_rating"),
        pl.len().alias("n_interactions")
    ]).sort(["year", "month"]).to_pandas()
    
    # Ajout date pour continuité temporelle et visualisations
    monthly_raw['date'] = pd.to_datetime(monthly_raw[['year', 'month']].assign(day=1))
    
    # 3. FILTRAGE de robustesse statistique
    monthly_filtered = monthly_raw[monthly_raw['n_interactions'] >= min_interactions].copy()
    
    # 4. Calcul des métadonnées de filtrage
    n_exclus = len(monthly_raw) - len(monthly_filtered)
    pct_exclus = (n_exclus / len(monthly_raw)) * 100 if len(monthly_raw) > 0 else 0
    
    # Analyse de la continuité temporelle
    if len(monthly_filtered) > 0:
        periode_avant = f"{monthly_raw['date'].min().strftime('%Y-%m')} → {monthly_raw['date'].max().strftime('%Y-%m')}"
        periode_apres = f"{monthly_filtered['date'].min().strftime('%Y-%m')} → {monthly_filtered['date'].max().strftime('%Y-%m')}"
        
        # Détection de gaps temporels (mois manquants dans la séquence)
        dates_complete = pd.date_range(
            monthly_filtered['date'].min(), 
            monthly_filtered['date'].max(), 
            freq='MS'
        )
        gaps_detected = len(dates_complete) != len(monthly_filtered)
    else:
        periode_avant = periode_apres = "N/A"
        gaps_detected = True
    
    metadata = {
        "seuil_applique": min_interactions,
        "mois_total": len(monthly_raw),
        "mois_exclus": n_exclus,
        "mois_conserves": len(monthly_filtered),
        "pct_exclus": pct_exclus,
        "periode_avant": periode_avant,
        "periode_apres": periode_apres,
        "gaps_temporels": gaps_detected,
        "volume_moyen_avant": monthly_raw['n_interactions'].mean(),
        "volume_moyen_apres": monthly_filtered['n_interactions'].mean() if len(monthly_filtered) > 0 else 0
    }
    
    # 5. Logging automatique (si verbose)
    if verbose:
        print(f"📊 RÉSULTATS FILTRAGE:")
        print(f"   Mois exclus: {n_exclus} ({pct_exclus:.1f}%)")
        print(f"   Mois conservés: {len(monthly_filtered)}")
        print(f"   Période finale: {periode_apres}")
        print(f"   Volume moyen: {metadata['volume_moyen_avant']:.0f} → {metadata['volume_moyen_apres']:.0f}")
        
        if gaps_detected:
            print(f"   ⚠️ Gaps temporels détectés")
        else:
            print(f"   ✅ Continuité temporelle préservée")
    
    if return_metadata:
        return monthly_filtered, metadata
    else:
        return monthly_filtered

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
    
    Note:
        - Évite les ingrédients ubiquitaires (salt, eggs, onions) qui masquent les variations
        - Privilégie les ingrédients avec vraie volatilité temporelle ou saisonnière
    """
    
    if analysis_type == 'long_term':
        # Ingrédients VOLATILES dans le temps (tendances émergentes/déclinantes)
        # Stratégie: Détecter évolutions culturelles et tendances alimentaires
        return [
            # Emergent (santé)
            'quinoa',           # Superfood 2010+
            'kale',             # Health trend 2010+
            'avocado',          # Boom 2015+
            
            # Adoption culturelle
            'tofu',             # Végétarisme croissant
            'sriracha',         # Hot sauce trend
            
            # Phénomènes temporels
            'bacon',            # "Bacon craze" 2010-2015
            'butternut squash'  # Contrôle saisonnier
        ]
    
    elif analysis_type == 'seasonality':
        # Ingrédients avec SAISONNALITÉ NATURELLE forte
        # Stratégie: Légumes/fruits avec variations liées aux saisons
        return [
            # 🌱 Printemps
            'asparagus',        # Pic avril-mai
            'peas',             # Pic printemps
            'strawberries',     # Pic printemps/été
            'rhubarb',          # Pic avril-mai
            
            # ☀️ Été
            'tomatoes',         # Pic juillet-août
            'zucchini',         # Pic été
            'basil',            # Herbe d'été
            'corn',             # Pic juillet-août
            
            # 🍂 Automne
            'butternut squash', # Pic octobre-novembre
            'pumpkin',          # Pic automne
            'brussels sprouts', # Pic automne/hiver
            'sweet potato',     # Pic automne
            
            # ❄️ Hiver
            'kale',             # Résistant au froid
            'cabbage',          # Légume d'hiver
            'cranberries',      # Pic novembre-décembre
            'lemon'             # Agrumes hiver
        ]
    
    elif analysis_type == 'weekend':
        # Mix d'ingrédients pour analyser comportements weekend vs semaine
        # Stratégie: Ingrédients variés (comfort food + healthy + saisonniers)
        return [
            # Comfort food (weekend)
            'bacon',
            'cheese',
            'butter',
            
            # Healthy (semaine?)
            'kale',
            'quinoa',
            'avocado',
            
            # Saisonniers (contrôle)
            'butternut squash',
            'asparagus',
            'tomatoes',
            
            # Basiques
            'olive oil',
            'garlic'
        ]
    
    else:
        raise ValueError(f"Type d'analyse non supporté: {analysis_type}. "
                        f"Utilisez 'long_term', 'seasonality', ou 'weekend'.")

def load_ingredient_ratings(target_ingredients: List[str]) -> pl.DataFrame:
    """
    Charge les données de ratings filtrées par ingrédients cibles depuis S3.
    
    Args:
        target_ingredients: Liste des ingrédients à analyser
    
    Returns:
        DataFrame Polars avec les ratings des ingrédients sélectionnés
    """
    # Charger depuis S3 avec connexion
    conn = get_s3_duckdb_connection()
    
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
    
    # Remplacer les noms de tables par les chemins S3
    query_s3 = query.replace("RAW_interactions", "'s3://mangetamain/interactions_train.csv'")
    query_s3 = query_s3.replace("RAW_recipes", "'s3://mangetamain/PP_recipes.csv'")
    
    df = conn.execute(query_s3).pl()
    conn.close()
    
    print(f"✅ Données chargées depuis S3: {df.shape[0]:,} interactions pour {len(target_ingredients)} ingrédients")
    
    return df

# =============================================================================
# POINT D'ENTRÉE PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    # Exécution du test si ce module est lancé directement
    test_data_pipeline()