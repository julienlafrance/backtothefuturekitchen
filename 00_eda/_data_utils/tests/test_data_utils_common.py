#!/usr/bin/env python3
"""Tests unitaires pour data_utils_common"""

import pytest
import polars as pl
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Ajouter le chemin parent pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_utils_common import (
    analyze_data_quality,
    print_quality_report,
    add_calendar_features,
    add_rating_features,
    clean_and_enrich_interactions
)


class TestAnalyzeDataQuality:
    """Tests pour analyze_data_quality"""

    def test_basic_quality_analysis(self):
        """Test analyse de qualité basique"""
        df = pl.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'value': [10, 20, None, 40, 50],
            'name': ['a', 'b', 'c', 'd', 'e']
        })

        report = analyze_data_quality(df, "test_df")

        assert report['name'] == "test_df"
        assert report['shape'] == (5, 3)
        assert 'null_counts' in report
        assert 'duplicate_count' in report

    def test_quality_with_ratings(self):
        """Test analyse avec colonne rating"""
        df = pl.DataFrame({
            'rating': [1, 2, 3, 4, 5, 0, 6],
            'count': [10, 20, 30, 40, 50, 5, 2]
        })

        report = analyze_data_quality(df, "ratings_df")

        assert 'rating_stats' in report
        assert 'mean' in report['rating_stats']
        assert 'std' in report['rating_stats']
        assert 'n_zero' in report['rating_stats']
        assert 'n_invalid' in report['rating_stats']

        # Vérifier les compteurs
        assert report['rating_stats']['n_zero'] == 1
        assert report['rating_stats']['n_invalid'] == 2  # 0 et 6

    def test_quality_with_dates(self):
        """Test analyse avec colonne date"""
        df = pl.DataFrame({
            'date': pl.date_range(
                pl.date(2024, 1, 1),
                pl.date(2024, 1, 5),
                "1d",
                eager=True
            ),
            'value': [1, 2, 3, 4, 5]
        })

        report = analyze_data_quality(df, "dates_df")

        assert 'date_stats' in report
        assert 'min_date' in report['date_stats']
        assert 'max_date' in report['date_stats']


class TestPrintQualityReport:
    """Tests pour print_quality_report"""

    def test_print_quality_report(self, capsys):
        """Test affichage du rapport"""
        report = {
            'name': 'test_data',
            'shape': (100, 5),
            'duplicate_count': 3,
            'rating_stats': {
                'mean': 4.2,
                'std': 0.8,
                'min': 1,
                'max': 5,
                'n_zero': 2,
                'n_invalid': 1
            },
            'date_stats': {
                'min_date': pl.date(2024, 1, 1),
                'max_date': pl.date(2024, 12, 31)
            }
        }

        print_quality_report(report)

        captured = capsys.readouterr()
        assert "test_data" in captured.out
        assert "(100, 5)" in captured.out
        assert "Ratings" in captured.out or "ratings" in captured.out.lower()


class TestAddCalendarFeatures:
    """Tests pour add_calendar_features"""

    def test_add_calendar_features(self):
        """Test ajout des features calendaires"""
        df = pl.DataFrame({
            'date': pl.date_range(
                pl.date(2024, 1, 1),
                pl.date(2024, 12, 31),
                "30d",
                eager=True
            ),
            'value': range(13)
        })

        result = add_calendar_features(df)

        # Vérifier les nouvelles colonnes
        assert 'year' in result.columns
        assert 'month' in result.columns
        assert 'day' in result.columns
        assert 'weekday' in result.columns
        assert 'is_weekend' in result.columns
        assert 'season' in result.columns

        # Vérifier les valeurs
        assert (result['year'] == 2024).all()
        assert result['month'].min() >= 1
        assert result['month'].max() <= 12

        # Vérifier les saisons
        seasons = result['season'].unique().to_list()
        assert len(seasons) > 0
        assert all(s in ["Winter", "Spring", "Summer", "Autumn"] for s in seasons)


class TestAddRatingFeatures:
    """Tests pour add_rating_features"""

    def test_add_rating_features(self):
        """Test ajout normalized_rating"""
        df = pl.DataFrame({
            'rating': [1.0, 2.0, 3.0, 4.0, 5.0]
        })

        result = add_rating_features(df)

        assert 'normalized_rating' in result.columns

        # La moyenne doit être proche de 0
        assert abs(result['normalized_rating'].mean()) < 0.1


class TestCleanAndEnrichInteractions:
    """Tests pour clean_and_enrich_interactions"""

    def test_clean_and_enrich(self):
        """Test pipeline complet"""
        df = pl.DataFrame({
            'rating': [0, 1, 2, 3, 4, 5, 6, 3],
            'date': [
                pl.date(2024, 1, 1),
                pl.date(2024, 1, 2),
                pl.date(2024, 1, 3),
                pl.date(2024, 1, 4),
                pl.date(2024, 1, 5),
                pl.date(2024, 1, 6),
                pl.date(2024, 1, 7),
                None  # Date nulle
            ],
            'user_id': [1, 2, 3, 4, 5, 6, 7, 8]
        })

        result = clean_and_enrich_interactions(df)

        # Vérifier le nettoyage
        # 0 exclu, 6 exclu, date None exclue
        assert len(result) < len(df)
        assert (result['rating'] >= 1).all()
        assert (result['rating'] <= 5).all()
        assert result['date'].null_count() == 0

        # Vérifier les enrichissements
        assert 'year' in result.columns
        assert 'month' in result.columns
        assert 'normalized_rating' in result.columns

    def test_clean_removes_duplicates(self):
        """Test suppression des duplicatas"""
        df = pl.DataFrame({
            'rating': [3, 3, 4, 4],
            'date': [
                pl.date(2024, 1, 1),
                pl.date(2024, 1, 1),  # Duplicata
                pl.date(2024, 1, 2),
                pl.date(2024, 1, 2)   # Duplicata
            ],
            'user_id': [1, 1, 2, 2]
        })

        result = clean_and_enrich_interactions(df)

        # Doit avoir supprimé les duplicatas
        assert len(result) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
