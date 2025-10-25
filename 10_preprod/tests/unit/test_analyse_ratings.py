"""Tests unitaires pour le module analyse_ratings.

Teste les fonctions d'analyse des ratings.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch
import polars as pl
import pandas as pd

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from visualization.analyse_ratings import (
    analyse_ratings_validation_ponderee,
    analyse_ratings_tendance_temporelle,
    analyse_ratings_distribution,
    analyse_ratings_seasonality_1,
    analyse_ratings_seasonality_2,
)


@pytest.fixture
def mock_interactions_data():
    """Fixture pour créer des données d'interactions simulées."""
    # For seasonality tests (raw interactions)
    data = {
        "recipe_id": list(range(1000)),
        "user_id": list(range(1000)),
        "rating": [3.0 + (i % 3) for i in range(1000)],
        "date": pd.date_range("2010-01-01", periods=1000, freq="D"),
        "year": [2010 + i % 10 for i in range(1000)],
        "season": ["Winter", "Spring", "Summer", "Autumn"] * 250,
        "n_interactions": [10 + i % 50 for i in range(1000)],
    }
    return pl.DataFrame(data)


@pytest.fixture
def mock_monthly_stats():
    """Fixture pour créer des statistiques mensuelles agrégées."""
    # For validation_ponderee, tendance_temporelle, distribution tests
    data = {
        "date": pd.date_range("2010-01-01", periods=100, freq="MS"),
        "mean_rating": [3.5 + (i % 10) * 0.1 for i in range(100)],
        "std_rating": [0.5 + (i % 5) * 0.05 for i in range(100)],
        "n_interactions": [100 + i * 10 for i in range(100)],
        "n_recipes": [50 + i * 2 for i in range(100)],
        "n_users": [80 + i * 3 for i in range(100)],
    }
    return pd.DataFrame(data)


def setup_st_mocks(mock_st):
    """Configure tous les mocks Streamlit nécessaires."""
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()
    mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])
    mock_st.slider = Mock(return_value=(2010, 2020))
    mock_st.radio = Mock(return_value="Linéaire")
    mock_st.selectbox = Mock(return_value="Moyenne")
    mock_st.multiselect = Mock(return_value=[])
    mock_st.checkbox = Mock(return_value=False)
    mock_st.metric = Mock()
    mock_st.write = Mock()
    mock_st.markdown = Mock()
    mock_st.subheader = Mock()
    mock_st.divider = Mock()
    return mock_st


@patch("visualization.analyse_ratings.st")
@patch("visualization.analyse_ratings.load_ratings_for_longterm_analysis")
def test_analyse_ratings_validation_ponderee(
    mock_load_ratings, mock_st, mock_monthly_stats
):
    """Test de la fonction analyse_ratings_validation_ponderee."""
    # Return tuple (df, metadata) as expected by the function
    mock_load_ratings.return_value = (mock_monthly_stats, {"count": 100})
    setup_st_mocks(mock_st)

    analyse_ratings_validation_ponderee()

    mock_load_ratings.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_ratings.st")
@patch("visualization.analyse_ratings.load_ratings_for_longterm_analysis")
def test_analyse_ratings_tendance_temporelle(
    mock_load_ratings, mock_st, mock_monthly_stats
):
    """Test de la fonction analyse_ratings_tendance_temporelle."""
    # Return tuple (df, metadata) as expected by the function
    mock_load_ratings.return_value = (mock_monthly_stats, {"count": 100})
    setup_st_mocks(mock_st)

    analyse_ratings_tendance_temporelle()

    mock_load_ratings.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_ratings.st")
@patch("visualization.analyse_ratings.load_ratings_for_longterm_analysis")
def test_analyse_ratings_distribution(
    mock_load_ratings, mock_st, mock_monthly_stats
):
    """Test de la fonction analyse_ratings_distribution."""
    # Return tuple (df, metadata) as expected by the function
    mock_load_ratings.return_value = (mock_monthly_stats, {"count": 100})
    setup_st_mocks(mock_st)

    analyse_ratings_distribution()

    mock_load_ratings.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_ratings.st")
@patch("visualization.analyse_ratings.load_clean_interactions")
def test_analyse_ratings_seasonality_1(
    mock_load_interactions, mock_st, mock_interactions_data
):
    """Test de la fonction analyse_ratings_seasonality_1."""
    mock_load_interactions.return_value = mock_interactions_data
    setup_st_mocks(mock_st)

    analyse_ratings_seasonality_1()

    mock_load_interactions.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_ratings.st")
@patch("visualization.analyse_ratings.load_clean_interactions")
def test_analyse_ratings_seasonality_2(
    mock_load_interactions, mock_st, mock_interactions_data
):
    """Test de la fonction analyse_ratings_seasonality_2."""
    mock_load_interactions.return_value = mock_interactions_data
    setup_st_mocks(mock_st)

    analyse_ratings_seasonality_2()

    mock_load_interactions.assert_called_once()
    mock_st.plotly_chart.assert_called()
