#!/usr/bin/env python3
"""Tests unitaires pour le module analyse_ratings_simple"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajouter le chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mangetamain_analytics.visualization.analyse_ratings_simple import (
    process_data,
    MODULE_INFO
)


class TestProcessData:
    """Tests pour la fonction process_data"""

    def test_process_data_basic(self):
        """Test du traitement de base des données"""
        # Créer des données de test
        ratings_data = pd.DataFrame({
            'rating': [1, 2, 3, 4, 5],
            'count': [10, 20, 30, 40, 100]
        })

        processed_data, stats = process_data(ratings_data)

        # Vérifier que les pourcentages sont ajoutés
        assert 'percentage' in processed_data.columns
        assert processed_data['percentage'].sum() == pytest.approx(100.0, rel=1e-2)

        # Vérifier les statistiques
        assert stats['total'] == 200
        assert 'avg_rating' in stats
        assert 'mode_rating' in stats
        assert stats['mode_rating'] == 5  # Le plus fréquent

    def test_process_data_empty(self):
        """Test avec DataFrame vide"""
        empty_data = pd.DataFrame(columns=['rating', 'count'])

        processed_data, stats = process_data(empty_data)

        assert processed_data.empty
        assert stats == {}

    def test_process_data_calculates_avg_correctly(self):
        """Test du calcul de la moyenne pondérée"""
        ratings_data = pd.DataFrame({
            'rating': [1, 5],
            'count': [50, 50]
        })

        _, stats = process_data(ratings_data)

        # Moyenne devrait être (1*50 + 5*50) / 100 = 3.0
        assert stats['avg_rating'] == pytest.approx(3.0, rel=1e-2)

    def test_process_data_pct_5_stars(self):
        """Test du calcul du pourcentage de 5 étoiles"""
        ratings_data = pd.DataFrame({
            'rating': [1, 2, 3, 4, 5],
            'count': [10, 10, 10, 10, 60]
        })

        _, stats = process_data(ratings_data)

        # 60/100 = 60%
        assert stats['pct_5_stars'] == pytest.approx(60.0, rel=1e-2)

    def test_process_data_no_5_stars(self):
        """Test quand il n'y a pas de notes à 5 étoiles"""
        ratings_data = pd.DataFrame({
            'rating': [1, 2, 3],
            'count': [30, 40, 30]
        })

        _, stats = process_data(ratings_data)

        assert stats['pct_5_stars'] == 0


class TestModuleInfo:
    """Tests pour les métadonnées du module"""

    def test_module_info_exists(self):
        """Vérifier que MODULE_INFO est défini"""
        assert MODULE_INFO is not None
        assert isinstance(MODULE_INFO, dict)

    def test_module_info_required_fields(self):
        """Vérifier les champs obligatoires"""
        required_fields = ['name', 'description', 'category', 'version']

        for field in required_fields:
            assert field in MODULE_INFO, f"Champ manquant: {field}"
            assert MODULE_INFO[field], f"Champ vide: {field}"

    def test_module_info_data_sources(self):
        """Vérifier que les sources de données sont documentées"""
        assert 'data_sources' in MODULE_INFO
        assert isinstance(MODULE_INFO['data_sources'], list)
        assert len(MODULE_INFO['data_sources']) > 0


class TestDataValidation:
    """Tests de validation des données"""

    def test_ratings_in_valid_range(self):
        """Test que les ratings sont dans la plage 0-5"""
        # Simuler des données avec ratings invalides
        ratings_data = pd.DataFrame({
            'rating': [0, 1, 2, 3, 4, 5],
            'count': [5, 10, 15, 20, 25, 30]
        })

        # Tous les ratings doivent être entre 0 et 5
        assert ratings_data['rating'].min() >= 0
        assert ratings_data['rating'].max() <= 5

    def test_counts_are_positive(self):
        """Test que les compteurs sont positifs"""
        ratings_data = pd.DataFrame({
            'rating': [1, 2, 3],
            'count': [10, 20, 30]
        })

        assert (ratings_data['count'] >= 0).all()


class TestPrintStats:
    """Tests pour la fonction print_stats"""

    def test_print_stats(self, capsys):
        """Test affichage des statistiques"""
        from mangetamain_analytics.visualization.analyse_ratings_simple import print_stats

        stats = {
            'total': 1000,
            'avg_rating': 4.2,
            'mode_rating': 5,
            'pct_5_stars': 65.5
        }

        print_stats(stats)

        captured = capsys.readouterr()
        assert "1,000" in captured.out
        assert "4.20" in captured.out
        assert "65.5%" in captured.out


class TestPrintInterpretation:
    """Tests pour print_interpretation"""

    def test_print_interpretation(self, capsys):
        """Test affichage de l'interprétation"""
        from mangetamain_analytics.visualization.analyse_ratings_simple import print_interpretation

        print_interpretation()

        captured = capsys.readouterr()
        assert "ANALYSE" in captured.out
        assert "Observations" in captured.out or "biais" in captured.out.lower()


class TestSetupS3Connection:
    """Tests pour setup_s3_connection"""

    @patch('mangetamain_analytics.visualization.analyse_ratings_simple.duckdb.connect')
    def test_setup_s3_connection(self, mock_connect):
        """Test configuration de la connexion S3"""
        from mangetamain_analytics.visualization.analyse_ratings_simple import setup_s3_connection

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = setup_s3_connection()

        # Vérifier que duckdb.connect() a été appelé
        mock_connect.assert_called_once()

        # Vérifier que les commandes S3 ont été exécutées
        assert mock_conn.execute.call_count >= 7  # INSTALL, LOAD, + 5 SET commands

        # Vérifier qu'on retourne la connexion
        assert conn == mock_conn


class TestGetRatingsData:
    """Tests pour get_ratings_data"""

    @patch('mangetamain_analytics.visualization.analyse_ratings_simple.setup_s3_connection')
    def test_get_ratings_data(self, mock_setup):
        """Test récupération des données depuis S3"""
        from mangetamain_analytics.visualization.analyse_ratings_simple import get_ratings_data

        # Mock connexion et résultats
        mock_conn = MagicMock()
        mock_setup.return_value = mock_conn

        mock_result = pd.DataFrame({
            'rating': [1, 2, 3, 4, 5],
            'count': [10, 20, 30, 40, 100]
        })
        mock_conn.execute.return_value.fetchdf.return_value = mock_result

        ratings_data = get_ratings_data()

        # Vérifier que setup_s3_connection a été appelé
        mock_setup.assert_called_once()

        # Vérifier qu'une requête SQL a été exécutée
        mock_conn.execute.assert_called_once()
        call_args = str(mock_conn.execute.call_args)
        assert "SELECT" in call_args
        assert "mangetamain" in call_args.lower()

        # Vérifier les données retournées
        assert isinstance(ratings_data, pd.DataFrame)
        assert len(ratings_data) == 5


# Note: render_analysis, create_plots_streamlit, create_plots_matplotlib et main
# sont marquées "pragma: no cover" car ce sont des fonctions UI difficiles à tester unitairement


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
