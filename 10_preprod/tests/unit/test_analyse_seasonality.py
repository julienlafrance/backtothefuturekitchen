"""Tests unitaires pour le module analyse_seasonality.

Teste les fonctions d'analyse de saisonnalité.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch
import polars as pl

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from visualization.analyse_seasonality import (
    analyse_seasonality_volume,
    analyse_seasonality_duree,
    analyse_seasonality_complexite,
    analyse_seasonality_nutrition,
    analyse_seasonality_ingredients,
    analyse_seasonality_tags,
)


@pytest.fixture
def mock_recipes_data():
    """Fixture pour créer des données de test simulées."""
    data = {
        "id": list(range(1000)),
        "season": ["Winter", "Spring", "Summer", "Autumn"] * 250,
        "minutes": [30 + (i % 50) for i in range(1000)],
        "n_steps": [5 + i % 10 for i in range(1000)],
        "n_ingredients": [8 + i % 15 for i in range(1000)],
        "complexity_score": [2.0 + (i % 10) * 0.1 for i in range(1000)],
        "calories": [300 + i % 200 for i in range(1000)],
        "carb_pct": [40 + (i % 30) for i in range(1000)],
        "total_fat_pct": [25 + (i % 25) for i in range(1000)],
        "sat_fat_pct": [8 + (i % 12) for i in range(1000)],
        "protein_pct": [20 + (i % 20) for i in range(1000)],
        "sugar_pct": [10 + (i % 15) for i in range(1000)],
        "sodium_pct": [15 + (i % 20) for i in range(1000)],
        "ingredients": [["salt", "pepper", "olive oil"] for _ in range(1000)],
        "tags": [["dinner", "main-dish", "quick"] for _ in range(1000)],
    }
    return pl.DataFrame(data)


def setup_st_mocks(mock_st):
    """Configure tous les mocks Streamlit nécessaires."""
    mock_st.plotly_chart = Mock()
    # MagicMock supporte le context manager protocol pour `with col:`
    # Retourne une liste de MagicMock de la longueur demandée
    mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])
    mock_st.metric = Mock()
    mock_st.write = Mock()
    mock_st.markdown = Mock()
    return mock_st


@patch("visualization.analyse_seasonality.st")
@patch("visualization.analyse_seasonality.load_recipes_clean")
def test_analyse_seasonality_volume(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_seasonality_volume."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_seasonality_volume()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_seasonality.st")
@patch("visualization.analyse_seasonality.load_recipes_clean")
def test_analyse_seasonality_duree(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_seasonality_duree."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_seasonality_duree()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_seasonality.st")
@patch("visualization.analyse_seasonality.load_recipes_clean")
def test_analyse_seasonality_complexite(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_seasonality_complexite."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_seasonality_complexite()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_seasonality.st")
@patch("visualization.analyse_seasonality.load_recipes_clean")
def test_analyse_seasonality_nutrition(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_seasonality_nutrition."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_seasonality_nutrition()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_seasonality.st")
@patch("visualization.analyse_seasonality.load_recipes_clean")
def test_analyse_seasonality_ingredients(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_seasonality_ingredients."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_seasonality_ingredients()

    mock_load_recipes.assert_called_once()


@patch("visualization.analyse_seasonality.st")
@patch("visualization.analyse_seasonality.load_recipes_clean")
def test_analyse_seasonality_tags(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_seasonality_tags."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_seasonality_tags()

    mock_load_recipes.assert_called_once()
