from .data_utils_common import *
from typing import Union, Tuple, Dict, List, Optional
import pandas as pd
import boto3
from io import BytesIO

# =============================================================================
# LOADING - RAW (données brutes, sans filtrage)
# =============================================================================

def load_interactions_raw(limit: Optional[int] = None) -> pl.DataFrame:
    """
    Charge les données d'interactions BRUTES depuis S3.
    
    ⚠️ ATTENTION: Cette fonction charge TOUTES les données, y compris:
        - Ratings à 0
        - Dates nulles
        - Doublons éventuels
    
    Args:
        limit: Nombre maximum de lignes à charger (optionnel, utile pour tests)
        
    Returns:
        pl.DataFrame: Interactions brutes non filtrées
        
    Example:
        >>> df = load_interactions_raw()
        >>> df_sample = load_interactions_raw(limit=10000)
    """
    conn = get_s3_duckdb_connection()
    
    sql = "SELECT * FROM 's3://mangetamain/interactions_train.csv'"
    
    if limit:
        sql += f" LIMIT {limit}"
    
    df = conn.execute(sql).pl()
    conn.close()
    
    limit_info = f" (limité à {limit:,})" if limit else ""
    print(f"✅ Interactions RAW chargées depuis S3{limit_info} : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
    return df


def load_ingredient_ratings(limit: Optional[int] = None) -> pl.DataFrame:
    """
    Charge interactions enrichies avec les données de recettes depuis S3.
    EXCLUT les ratings à 0 et les dates nulles.
    
    Args:
        limit: Nombre maximum de lignes à charger (optionnel)
        
    Returns:
        pl.DataFrame: Interactions enrichies avec colonnes recette
    """
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
    FROM read_csv('s3://mangetamain/interactions_train.csv') i
    LEFT JOIN read_csv('s3://mangetamain/PP_recipes.csv') r ON i.recipe_id = r.id
    WHERE i.rating BETWEEN 1 AND 5
      AND i.date IS NOT NULL
    """
    
    if limit:
        sql += f" LIMIT {limit}"
    
    df = conn.execute(sql).pl()
    conn.close()
    
    limit_info = f" (limité à {limit:,})" if limit else ""
    print(f"✅ Interactions enrichies chargées depuis S3{limit_info} : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
    return df


def get_s3_credentials_path():
    from pathlib import Path
    return Path.cwd() / '96_keys' / 'credentials'



# =============================================================================
# LOADING - CLEAN (données pré-nettoyées depuis Parquet)
# =============================================================================

def load_interactions_clean(limit: Optional[int] = None) -> pl.DataFrame:
    """
    Charge les interactions nettoyées depuis le fichier Parquet final sur S3.
    
    Le fichier Parquet contient les données déjà filtrées et enrichies:
        - Ratings BETWEEN 1 AND 5
        - Dates non-nulles
        - Features calendaires ajoutées
        - Normalized ratings
    
    Args:
        limit: Nombre maximum de lignes à charger (optionnel)
        
    Returns:
        pl.DataFrame: Interactions nettoyées et enrichies
        
    Example:
        >>> df = load_interactions_clean()
        >>> df_sample = load_interactions_clean(limit=5000)
    """
    conn = get_s3_duckdb_connection()
    
    sql = "SELECT * FROM read_parquet('s3://mangetamain/final_interactions.parquet')"
    
    if limit:
        sql += f" LIMIT {limit}"
    
    df = conn.execute(sql).pl()
    conn.close()
    
    limit_info = f" (limité à {limit:,})" if limit else ""
    print(f"✅ Interactions CLEAN chargées depuis S3{limit_info} : {df.shape[0]:,} lignes × {df.shape[1]} colonnes")
    return df


# =============================================================================
# SAUVEGARDE S3
# =============================================================================

def save_ratings_to_s3(df, s3_path, format="parquet"):
    """
    Save a ratings DataFrame to S3 (independent file, not in DuckDB).

    Args:
        df: DataFrame (pandas or polars) to save
        s3_path: S3 path (e.g., 's3://mangetamain/final_ratings.parquet')
        format: 'parquet' or 'csv'
    """
    import boto3
    from io import BytesIO
    from configparser import ConfigParser

    # Parse S3 path
    if not s3_path.startswith("s3://"):
        raise ValueError(f"Path must start with 's3://': {s3_path}")
    s3_parts = s3_path.replace("s3://", "").split("/", 1)
    bucket = s3_parts[0]
    key = s3_parts[1] if len(s3_parts) > 1 else ""

    # Load credentials
    creds_path = get_s3_credentials_path()
    config = ConfigParser()
    config.read(str(creds_path))  # ✅ Convertir Path en string
    if 's3fast' not in config:
        raise ValueError("Profile [s3fast] not found in credentials file")
    s3_config = config['s3fast']
    endpoint_url = s3_config.get('endpoint_url', 'http://s3fast.lafrance.io')
    access_key = s3_config.get('aws_access_key_id')
    secret_key = s3_config.get('aws_secret_access_key')
    region = s3_config.get('region', 'garage-fast')

    # Create S3 client
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        use_ssl=False
    )

    # Save DataFrame
    buffer = BytesIO()
    if format.lower() == "parquet":
        df.write_parquet(buffer)  # For polars DataFrame
    elif format.lower() == "csv":
        df.write_csv(buffer)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'parquet' or 'csv'")
    buffer.seek(0)
    s3_client.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
    print(f"✅ Saved to {s3_path} ({df.shape[0]:,} rows, format={format})")

# =============================================================================
# PIPELINE COMPLET
# =============================================================================

def load_clean_interactions(limit: Optional[int] = None, save_to_s3: bool = False) -> pl.DataFrame:
    """
    Pipeline complet : charge, nettoie et enrichit les interactions.
    
    Étapes:
        1️⃣ Chargement RAW depuis S3
        2️⃣ Nettoyage et enrichissement
        3️⃣ [Optionnel] Sauvegarde du résultat final sur S3
    
    Args:
        limit: Nombre de lignes à charger (None = toutes)
        save_to_s3: Si True, sauvegarde le résultat en Parquet
        
    Returns:
        pl.DataFrame: Interactions prêtes pour l'analyse
    """
    print("1️⃣ Chargement des données brutes...")
    df_raw = load_interactions_raw(limit)
    
    print("\n2️⃣ Nettoyage et enrichissement...")
    df_clean = clean_and_enrich_interactions(df_raw)
    
    if save_to_s3:
        print("\n3️⃣ Sauvegarde sur S3...")
        s3_path = "s3://mangetamain/final_interactions.parquet"
        save_interactions_to_s3(df_clean, s3_path)
        print(f"💾 Dataset sauvegardé : {s3_path}")
    
    print("\n✅ Pipeline terminé !")
    return df_clean



# =============================================================================
# FONCTIONS POUR ANALYSES TEMPORELLES - RATINGS GLOBAUX
# =============================================================================

def load_ratings_for_longterm_analysis(
    min_interactions: int = 100,
    return_metadata: bool = True,
    verbose: bool = True
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict]]:
    import polars as pl
    import pandas as pd

    if verbose:
        print(f"🔄 Chargement avec seuil de robustesse: {min_interactions}")

    # 1. Charger les interactions nettoyées directement depuis S3 Parquet
    conn = get_s3_duckdb_connection()
    sql = "SELECT * FROM read_parquet('s3://mangetamain/final_interactions.parquet')"
    df_clean = conn.execute(sql).pl()
    conn.close()

    # 2. Agrégation mensuelle
    monthly_raw = df_clean.group_by(["year", "month"]).agg([
        pl.col("rating").mean().alias("mean_rating"),
        pl.col("rating").median().alias("median_rating"),
        pl.col("rating").std().alias("std_rating"),
        pl.len().alias("n_interactions")
    ]).sort(["year", "month"]).to_pandas()

    monthly_raw['date'] = pd.to_datetime(monthly_raw[['year', 'month']].assign(day=1))

    # 3. Filtrage de robustesse
    monthly_filtered = monthly_raw[monthly_raw['n_interactions'] >= min_interactions].copy()

    # 4. Métadonnées
    n_exclus = len(monthly_raw) - len(monthly_filtered)
    pct_exclus = (n_exclus / len(monthly_raw)) * 100 if len(monthly_raw) > 0 else 0

    if len(monthly_filtered) > 0:
        periode_avant = f"{monthly_raw['date'].min().strftime('%Y-%m')} → {monthly_raw['date'].max().strftime('%Y-%m')}"
        periode_apres = f"{monthly_filtered['date'].min().strftime('%Y-%m')} → {monthly_filtered['date'].max().strftime('%Y-%m')}"
        dates_complete = pd.date_range(monthly_filtered['date'].min(), monthly_filtered['date'].max(), freq='MS')
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

    if return_metadata:
        return monthly_filtered, metadata
    else:
        return monthly_filtered