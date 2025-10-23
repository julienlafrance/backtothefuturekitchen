#!/usr/bin/env python3
"""Tests unitaires pour streamlit/data/loaders.py"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

# Ajouter le chemin streamlit pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "streamlit"))

from data.loaders import (
    validate_db_path,
    get_file_size_mb,
    calculate_rating_stats,
    categorize_table,
    validate_rating_range,
    filter_valid_ratings,
    get_table_stats
)


class TestValidateDbPath:
    """Tests pour validate_db_path"""

    def test_path_exists(self):
        """Test fichier qui existe"""
        with tempfile.NamedTemporaryFile() as tmp:
            assert validate_db_path(tmp.name) is True

    def test_path_not_exists(self):
        """Test fichier qui n'existe pas"""
        assert validate_db_path("/nonexistent/path/file.db") is False


class TestGetFileSizeMb:
    """Tests pour get_file_size_mb"""

    def test_file_size(self):
        """Test taille de fichier"""
        with tempfile.NamedTemporaryFile() as tmp:
            # Écrire 1 MB de données
            tmp.write(b"x" * (1024 * 1024))
            tmp.flush()

            size = get_file_size_mb(tmp.name)

            assert size >= 1.0
            assert size < 1.1  # ~1 MB

    def test_file_not_exists(self):
        """Test fichier inexistant"""
        size = get_file_size_mb("/nonexistent/file.db")
        assert size == 0.0


class TestCalculateRatingStats:
    """Tests pour calculate_rating_stats"""

    def test_rating_stats_basic(self):
        """Test calcul statistiques basiques"""
        df = pd.DataFrame({
            'rating': [1, 2, 3, 4, 5],
            'count': [10, 20, 30, 40, 100]
        })

        stats = calculate_rating_stats(df)

        assert stats['total'] == 200
        assert 'average' in stats
        assert stats['mode'] == 5  # Le plus fréquent
        assert stats['pct_5_stars'] == 50.0  # 100/200

    def test_rating_stats_empty(self):
        """Test avec DataFrame vide"""
        df = pd.DataFrame(columns=['rating', 'count'])

        stats = calculate_rating_stats(df)

        assert stats == {}

    def test_rating_stats_no_5_stars(self):
        """Test sans notes à 5 étoiles"""
        df = pd.DataFrame({
            'rating': [1, 2, 3],
            'count': [30, 40, 30]
        })

        stats = calculate_rating_stats(df)

        assert stats['pct_5_stars'] == 0.0

    def test_rating_stats_average_calculation(self):
        """Test calcul de la moyenne pondérée"""
        df = pd.DataFrame({
            'rating': [1, 5],
            'count': [50, 50]
        })

        stats = calculate_rating_stats(df)

        # (1*50 + 5*50) / 100 = 3.0
        assert stats['average'] == pytest.approx(3.0, rel=1e-2)


class TestCategorizeTable:
    """Tests pour categorize_table"""

    def test_categorize_raw(self):
        """Test catégorisation table RAW"""
        assert categorize_table("RAW_interactions") == "Données brutes"
        assert categorize_table("RAW_users") == "Données brutes"

    def test_categorize_preprocessed(self):
        """Test catégorisation table PP"""
        assert categorize_table("PP_interactions") == "Données préprocessées"
        assert categorize_table("PP_recipes") == "Données préprocessées"

    def test_categorize_ml(self):
        """Test catégorisation tables ML"""
        assert categorize_table("interactions_train") == "Datasets ML"
        assert categorize_table("interactions_test") == "Datasets ML"
        assert categorize_table("interactions_validation") == "Datasets ML"

    def test_categorize_other(self):
        """Test catégorisation autres tables"""
        assert categorize_table("custom_table") == "Autres"
        assert categorize_table("metadata") == "Autres"


class TestValidateRatingRange:
    """Tests pour validate_rating_range"""

    def test_valid_ratings(self):
        """Test ratings valides"""
        assert validate_rating_range(0) is True
        assert validate_rating_range(2.5) is True
        assert validate_rating_range(5) is True

    def test_invalid_ratings(self):
        """Test ratings invalides"""
        assert validate_rating_range(-1) is False
        assert validate_rating_range(6) is False
        assert validate_rating_range(10) is False


class TestFilterValidRatings:
    """Tests pour filter_valid_ratings"""

    def test_filter_valid(self):
        """Test filtrage ratings valides"""
        df = pd.DataFrame({
            'rating': [-1, 0, 2, 3, 5, 6, 10],
            'user_id': [1, 2, 3, 4, 5, 6, 7]
        })

        result = filter_valid_ratings(df)

        # Seuls 0, 2, 3, 5 sont valides
        assert len(result) == 4
        assert (result['rating'] >= 0).all()
        assert (result['rating'] <= 5).all()

    def test_filter_no_rating_column(self):
        """Test avec DataFrame sans colonne rating"""
        df = pd.DataFrame({
            'user_id': [1, 2, 3],
            'value': [10, 20, 30]
        })

        result = filter_valid_ratings(df)

        # Devrait retourner le DataFrame tel quel
        assert len(result) == len(df)

    def test_filter_custom_column(self):
        """Test avec nom de colonne personnalisé"""
        df = pd.DataFrame({
            'score': [-1, 2, 6],
            'user_id': [1, 2, 3]
        })

        result = filter_valid_ratings(df, rating_col='score')

        # Seul 2 est valide
        assert len(result) == 1
        assert result['score'].iloc[0] == 2


class TestGetTableStats:
    """Tests pour get_table_stats"""

    def test_stats_basic(self):
        """Test statistiques basiques"""
        tables_info = [
            ('table1', 1000, 5),
            ('table2', 2000, 10),
            ('table3', 3000, 15)
        ]

        stats = get_table_stats(tables_info)

        assert stats['total_tables'] == 3
        assert stats['total_rows'] == 6000
        assert stats['avg_columns'] == 10.0  # (5+10+15)/3

    def test_stats_empty(self):
        """Test avec liste vide"""
        stats = get_table_stats([])

        assert stats['total_tables'] == 0
        assert stats['total_rows'] == 0
        assert stats['avg_columns'] == 0.0

    def test_stats_single_table(self):
        """Test avec une seule table"""
        tables_info = [('single_table', 500, 8)]

        stats = get_table_stats(tables_info)

        assert stats['total_tables'] == 1
        assert stats['total_rows'] == 500
        assert stats['avg_columns'] == 8.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
