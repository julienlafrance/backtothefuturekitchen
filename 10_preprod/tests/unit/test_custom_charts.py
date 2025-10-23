#!/usr/bin/env python3
"""Tests unitaires pour le module custom_charts"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Ajouter le chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# Mock Streamlit avant l'import
sys.modules['streamlit'] = MagicMock()

from mangetamain_analytics.visualization import custom_charts


class TestCreateCorrelationHeatmap:
    """Tests pour create_correlation_heatmap"""

    def test_correlation_heatmap_with_valid_data(self):
        """Test heatmap avec données valides"""
        # Mock de la connexion DuckDB
        mock_conn = Mock()
        mock_df = pd.DataFrame({
            'rating': [1, 2, 3, 4, 5],
            'user_count': [10, 20, 30, 40, 50],
            'recipe_count': [5, 15, 25, 35, 45]
        })
        mock_conn.execute.return_value.fetchdf.return_value = mock_df

        # Pas d'exception levée
        custom_charts.create_correlation_heatmap(mock_conn, "test_table")

        # Vérifier que la requête SQL est exécutée
        mock_conn.execute.assert_called_once()
        assert "test_table" in str(mock_conn.execute.call_args)

    def test_correlation_heatmap_with_no_numeric_cols(self):
        """Test heatmap avec aucune colonne numérique"""
        mock_conn = Mock()
        mock_df = pd.DataFrame({
            'name': ['a', 'b', 'c']
        })
        mock_conn.execute.return_value.fetchdf.return_value = mock_df

        # Ne doit pas lever d'exception
        custom_charts.create_correlation_heatmap(mock_conn, "test_table")


class TestCreateDistributionPlot:
    """Tests pour create_distribution_plot"""

    def test_distribution_plot_with_valid_data(self):
        """Test distribution plot avec données valides"""
        mock_conn = Mock()
        mock_df = pd.DataFrame({
            'rating': [1, 2, 3, 4, 5, 3, 4, 5]
        })
        mock_conn.execute.return_value.fetchdf.return_value = mock_df

        # Pas d'exception
        custom_charts.create_distribution_plot(mock_conn, "test_table", "rating")

        # Vérifier que la requête utilise la bonne colonne
        call_args = str(mock_conn.execute.call_args)
        assert "rating" in call_args
        assert "test_table" in call_args


class TestCreateTimeSeriesPlot:
    """Tests pour create_time_series_plot"""

    def test_time_series_plot_with_valid_data(self):
        """Test time series avec données valides"""
        mock_conn = Mock()
        mock_df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'value': [10, 20, 30, 40, 50]
        })
        mock_conn.execute.return_value.fetchdf.return_value = mock_df

        # Pas d'exception
        custom_charts.create_time_series_plot(mock_conn, "test_table", "date", "value")

        # Vérifier l'appel SQL
        call_args = str(mock_conn.execute.call_args)
        assert "date" in call_args
        assert "value" in call_args


class TestCreateCustomScatterPlot:
    """Tests pour create_custom_scatter_plot"""

    def test_scatter_plot_without_color(self):
        """Test scatter plot sans colonne de couleur"""
        mock_conn = Mock()
        mock_df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10]
        })
        mock_conn.execute.return_value.fetchdf.return_value = mock_df

        # Pas d'exception
        custom_charts.create_custom_scatter_plot(mock_conn, "test_table", "x", "y")

    def test_scatter_plot_with_color(self):
        """Test scatter plot avec colonne de couleur"""
        mock_conn = Mock()
        mock_df = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [2, 4, 6, 8, 10],
            'category': ['A', 'B', 'A', 'B', 'A']
        })
        mock_conn.execute.return_value.fetchdf.return_value = mock_df

        # Pas d'exception
        custom_charts.create_custom_scatter_plot(
            mock_conn, "test_table", "x", "y", color_col="category"
        )

        # Vérifier que category est inclus dans la requête
        call_args = str(mock_conn.execute.call_args)
        assert "category" in call_args


class TestErrorHandling:
    """Tests de gestion des erreurs"""

    def test_correlation_heatmap_handles_sql_error(self):
        """Test gestion erreur SQL dans heatmap"""
        mock_conn = Mock()
        mock_conn.execute.side_effect = Exception("SQL Error")

        # Ne doit pas lever d'exception (erreur gérée par streamlit)
        custom_charts.create_correlation_heatmap(mock_conn, "bad_table")

    def test_distribution_plot_handles_sql_error(self):
        """Test gestion erreur SQL dans distribution"""
        mock_conn = Mock()
        mock_conn.execute.side_effect = Exception("SQL Error")

        # Ne doit pas lever d'exception
        custom_charts.create_distribution_plot(mock_conn, "bad_table", "col")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
