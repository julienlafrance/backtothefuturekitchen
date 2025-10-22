"""
Data Loading & Quality Utils

Module utilitaire contenant toutes les fonctions de chargement, nettoyage et transformation des données.
Extrait du notebook 00_data_utils.ipynb pour permettre un import Python classique.

Usage:
    from data_utils import *
    # ou
    import data_utils
    df_clean = data_utils.load_clean_interactions()
"""

# Imports de base
from pathlib import Path
import os
import duckdb
import polars as pl
import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Tuple, Union
from configparser import ConfigParser
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONNEXION S3 via DUCKDB
# =============================================================================

def get_s3_credentials_path() -> Path:
    """Localise le fichier de credentials S3 dans 96_keys/."""
    anchors = [Path.cwd().resolve(), *Path.cwd().resolve().parents]
    creds_candidate = next(
        (anchor / "96_keys" / "credentials"
         for anchor in anchors
         if (anchor / "96_keys" / "credentials").exists()),
        None,
    )
    if creds_candidate is None:
        raise FileNotFoundError("Impossible de localiser 96_keys/credentials")
    return creds_candidate

def get_s3_duckdb_connection():
    """
    Crée une connexion DuckDB en mémoire avec le secret S3 configuré.
    
    Returns:
        duckdb.DuckDBPyConnection: Connexion avec httpfs et secret S3 chargés
        
    Raises:
        FileNotFoundError: Si le fichier credentials n'est pas trouvé
        
    Example:
        >>> conn = get_s3_duckdb_connection()
        >>> df = conn.execute("SELECT * FROM 's3://mangetamain/PP_recipes.csv'").pl()
    """
    # Charger les credentials
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
    
    # Créer une connexion en mémoire
    conn = duckdb.connect(database=':memory:')
    
    # Installer et charger httpfs
    conn.execute("INSTALL httpfs;")
    conn.execute("LOAD httpfs;")
    
    # Configurer le secret S3
    conn.execute(f"""
        CREATE SECRET s3fast (
            TYPE s3,
            KEY_ID '{access_key}',
            SECRET '{secret_key}',
            ENDPOINT '{endpoint_url.replace('http://', '').replace('https://', '')}',
            REGION '{region}',
            URL_STYLE 'path',
            USE_SSL false
        );
    """)
    
    return conn

# =============================================================================
# DATA QUALITY & CLEANING
# =============================================================================

def analyze_data_quality(df: pl.DataFrame, name: str = "DataFrame") -> Dict[str, any]:
    """Analyse complète de la qualité des données."""
    report = {
        "name": name,
        "shape": df.shape,
        "schema": dict(df.schema),
        "null_counts": df.null_count().to_dict(),
        "duplicate_count": df.is_duplicated().sum(),
    }
    
    # Analyse spécifique ratings si présent
    if "rating" in df.columns:
        ratings = df["rating"]
        report["rating_stats"] = {
            "mean": ratings.mean(),
            "std": ratings.std(),
            "min": ratings.min(),
            "max": ratings.max(),
            "n_zero": df.filter(pl.col("rating") == 0).height,
            "n_invalid": df.filter((pl.col("rating") < 0) | (pl.col("rating") > 5)).height,
        }
    
    # Analyse dates si présent
    if "date" in df.columns:
        date_col = df["date"]
        report["date_stats"] = {
            "min_date": date_col.min(),
            "max_date": date_col.max(),
            "null_dates": date_col.null_count(),
        }
    
    return report

def print_quality_report(report: Dict[str, any]):
    """Affiche un rapport de qualité formaté."""
    print(f"📊 Rapport de qualité : {report['name']}")
    print(f"Shape: {report['shape']}")
    print(f"Duplicatas: {report['duplicate_count']}")
    
    if "rating_stats" in report:
        rs = report["rating_stats"]
        print(f"\n🌟 Ratings:")
        print(f"  Moyenne: {rs['mean']:.3f} ± {rs['std']:.3f}")
        print(f"  Range: [{rs['min']}, {rs['max']}]")
        print(f"  Zéros: {rs['n_zero']}, Invalides: {rs['n_invalid']}")
    
    if "date_stats" in report:
        ds = report["date_stats"]
        print(f"\n📅 Dates: {ds['min_date']} → {ds['max_date']}")

def check_data_quality(df: pl.DataFrame, name: str = "DataFrame") -> Dict[str, any]:
    """Alias pour analyze_data_quality (compatibilité)."""
    return analyze_data_quality(df, name)


# =============================================================================
# FEATURES ENGINEERING
# =============================================================================

def add_calendar_features(df: pl.DataFrame, date_col: str = "date") -> pl.DataFrame:
    """Ajoute les features calendaires (année, mois, jour, saison, weekend)."""
    return df.with_columns([
        pl.col(date_col).dt.year().alias("year"),
        pl.col(date_col).dt.month().alias("month"),
        pl.col(date_col).dt.day().alias("day"),
        pl.col(date_col).dt.weekday().alias("weekday"),
        (pl.col(date_col).dt.weekday() >= 5).cast(pl.Int8).alias("is_weekend"),
        pl.when(pl.col(date_col).dt.month().is_in([12, 1, 2])).then(pl.lit("Winter"))
          .when(pl.col(date_col).dt.month().is_in([3, 4, 5])).then(pl.lit("Spring"))
          .when(pl.col(date_col).dt.month().is_in([6, 7, 8])).then(pl.lit("Summer"))
          .otherwise(pl.lit("Autumn")).alias("season"),
    ])

def add_rating_features(df: pl.DataFrame, rating_col: str = "rating") -> pl.DataFrame:
    """Ajoute les features dérivées du rating (z-score normalisé)."""
    rating_mean = df[rating_col].mean()
    rating_std = df[rating_col].std()
    
    return df.with_columns([
        ((pl.col(rating_col) - rating_mean) / rating_std).alias("normalized_rating"),
    ])

def clean_and_enrich_interactions(df: pl.DataFrame) -> pl.DataFrame:
    """Pipeline complet de nettoyage et enrichissement - retourne une copie transformée."""
    # Nettoyage de base (copie pour ne pas modifier l'original)
    # ⚠️ EXCLUT les ratings à 0 (cohérent avec load_interactions_raw)
    cleaned = df.filter(
        (pl.col("rating").is_between(1, 5, closed="both")) &
        (pl.col("date").is_not_null())
    )
    
    # Suppression des duplicatas exacts
    cleaned = cleaned.unique()
    
    # Ajout des features calendaires et de rating
    enriched = add_calendar_features(cleaned)
    enriched = add_rating_features(enriched)
    
    return enriched

