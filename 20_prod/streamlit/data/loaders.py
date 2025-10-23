"""Module de chargement et validation des données DuckDB"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple


def validate_db_path(db_path: str) -> bool:
    """
    Valide l'existence d'un fichier DuckDB.

    Args:
        db_path: Chemin vers le fichier DuckDB

    Returns:
        True si le fichier existe, False sinon
    """
    return Path(db_path).exists()


def get_file_size_mb(file_path: str) -> float:
    """
    Retourne la taille d'un fichier en MB.

    Args:
        file_path: Chemin vers le fichier

    Returns:
        Taille en MB
    """
    if not Path(file_path).exists():
        return 0.0

    return Path(file_path).stat().st_size / (1024 * 1024)


def calculate_rating_stats(ratings_df: pd.DataFrame) -> dict:
    """
    Calcule les statistiques sur les ratings.

    Args:
        ratings_df: DataFrame avec colonnes 'rating' et 'count'

    Returns:
        Dict avec statistiques (total, moyenne, mode, pct_5_stars)
    """
    if ratings_df.empty:
        return {}

    total_ratings = ratings_df["count"].sum()
    avg_rating = (ratings_df["rating"] * ratings_df["count"]).sum() / total_ratings
    most_common_rating = ratings_df.loc[ratings_df["count"].idxmax(), "rating"]

    # Pourcentage de 5 étoiles
    pct_5_stars = 0.0
    if 5 in ratings_df["rating"].values:
        count_5 = ratings_df[ratings_df["rating"] == 5]["count"].iloc[0]
        pct_5_stars = (count_5 / total_ratings) * 100

    return {
        "total": int(total_ratings),
        "average": float(avg_rating),
        "mode": int(most_common_rating),
        "pct_5_stars": float(pct_5_stars),
    }


def categorize_table(table_name: str) -> str:
    """
    Catégorise une table selon son nom.

    Args:
        table_name: Nom de la table

    Returns:
        Catégorie de la table
    """
    if table_name.startswith("RAW_"):
        return "Données brutes"
    elif table_name.startswith("PP_"):
        return "Données préprocessées"
    elif "interactions_" in table_name:
        return "Datasets ML"
    else:
        return "Autres"


def validate_rating_range(rating: float) -> bool:
    """
    Valide qu'un rating est dans la plage [0, 5].

    Args:
        rating: Note à valider

    Returns:
        True si valide, False sinon
    """
    return 0 <= rating <= 5


def filter_valid_ratings(df: pd.DataFrame, rating_col: str = "rating") -> pd.DataFrame:
    """
    Filtre un DataFrame pour ne garder que les ratings valides.

    Args:
        df: DataFrame source
        rating_col: Nom de la colonne rating

    Returns:
        DataFrame filtré
    """
    if rating_col not in df.columns:
        return df

    return df[(df[rating_col] >= 0) & (df[rating_col] <= 5)]


def get_table_stats(tables_info: List[Tuple[str, int, int]]) -> dict:
    """
    Calcule les statistiques globales sur un ensemble de tables.

    Args:
        tables_info: Liste de tuples (nom_table, nb_lignes, nb_colonnes)

    Returns:
        Dict avec statistiques
    """
    if not tables_info:
        return {"total_tables": 0, "total_rows": 0, "avg_columns": 0.0}

    total_rows = sum(rows for _, rows, _ in tables_info)
    total_columns = sum(cols for _, _, cols in tables_info)

    return {
        "total_tables": len(tables_info),
        "total_rows": total_rows,
        "avg_columns": total_columns / len(tables_info) if tables_info else 0.0,
    }
