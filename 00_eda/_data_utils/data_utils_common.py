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
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONNEXION DUCKDB
# =============================================================================

def get_db_path() -> Path:
    """Localise automatiquement la base DuckDB dans la hiérarchie de dossiers."""
    anchors = [Path.cwd().resolve(), *Path.cwd().resolve().parents]
    db_candidate = next(
        (anchor / "00_preprod" / "data" / "mangetamain.duckdb"
         for anchor in anchors
         if (anchor / "00_preprod" / "data" / "mangetamain.duckdb").exists()),
        None,
    )
    if db_candidate is None:
        raise FileNotFoundError("Impossible de localiser 00_preprod/data/mangetamain.duckdb")
    return db_candidate

def get_table_overview(db_path: Path) -> pl.DataFrame:
    """Retourne un aperçu de toutes les tables avec leurs tailles."""
    with duckdb.connect(database=str(db_path), read_only=True) as conn:
        tables = conn.execute("SHOW TABLES").pl()
        table_list = [row[0] for row in tables.iter_rows()]
        
        row_counts = []
        for table in table_list:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            row_counts.append(count)
    
    return pl.DataFrame({
        "table": table_list,
        "row_count": row_counts,
    }).sort("row_count", descending=True)

# =============================================================================
# CHARGEMENT DES DONNÉES
# =============================================================================

def load_table(table_name: str, db_path: Optional[Path] = None, limit: Optional[int] = None) -> pl.DataFrame:
    """Charge une table depuis DuckDB."""
    if db_path is None:
        db_path = get_db_path()
    
    sql = f"SELECT * FROM {table_name}"
    if limit is not None:
        sql += f" LIMIT {limit}"
    
    with duckdb.connect(database=str(db_path), read_only=True) as conn:
        return conn.execute(sql).pl()


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

