"""Tests unitaires pour le module analyse_weekend.

Teste les fonctions d'analyse weekend vs weekday.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch
import polars as pl

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from visualization.analyse_weekend import (
    analyse_weekend_volume,
    analyse_weekend_duree,
    analyse_weekend_complexite,
    analyse_weekend_nutrition,
    analyse_weekend_ingredients,
    analyse_weekend_tags,
)


@pytest.fixture
def mock_recipes_data():
    """Fixture pour créer des données de test simulées."""
    data = {
        "id": list(range(1000)),
        "is_weekend": [i % 2 == 0 for i in range(1000)],
        "day_of_week": [i % 7 for i in range(1000)],
        "weekday": [(i % 7) + 1 for i in range(1000)],  # 1-7 pour Lun-Dim
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
    mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])
    mock_st.metric = Mock()
    mock_st.write = Mock()
    mock_st.markdown = Mock()
    return mock_st


@patch("visualization.analyse_weekend.st")
@patch("visualization.analyse_weekend.load_recipes_clean")
def test_analyse_weekend_volume(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_weekend_volume."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_weekend_volume()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_weekend.st")
@patch("visualization.analyse_weekend.load_recipes_clean")
def test_analyse_weekend_duree(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_weekend_duree."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_weekend_duree()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_weekend.st")
@patch("visualization.analyse_weekend.load_recipes_clean")
def test_analyse_weekend_complexite(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_weekend_complexite."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_weekend_complexite()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_weekend.st")
@patch("visualization.analyse_weekend.load_recipes_clean")
def test_analyse_weekend_nutrition(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_weekend_nutrition."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_weekend_nutrition()

    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_weekend.st")
@patch("visualization.analyse_weekend.load_recipes_clean")
def test_analyse_weekend_ingredients(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_weekend_ingredients."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    # Cette fonction affiche un tableau, pas forcément un graphique
    analyse_weekend_ingredients()

    mock_load_recipes.assert_called_once()


@patch("visualization.analyse_weekend.st")
@patch("visualization.analyse_weekend.load_recipes_clean")
def test_analyse_weekend_tags(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_weekend_tags."""
    mock_load_recipes.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    # Cette fonction affiche un tableau, pas forcément un graphique
    analyse_weekend_tags()

    mock_load_recipes.assert_called_once()
