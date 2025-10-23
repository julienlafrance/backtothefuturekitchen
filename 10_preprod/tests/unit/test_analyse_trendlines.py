"""Tests unitaires pour le module analyse_trendlines.

Teste les fonctions d'analyse de tendances temporelles.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch
import polars as pl

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from visualization.analyse_trendlines import (
    analyse_trendline_volume,
    analyse_trendline_duree,
    analyse_trendline_complexite,
    analyse_trendline_nutrition,
    analyse_trendline_ingredients,
    analyse_trendline_tags,
)


@pytest.fixture
def mock_recipes_data():
    """Fixture pour créer des données de test simulées."""
    # Création de données polars simulées
    data = {
        "id": list(range(1000)),
        "year": [1999 + i % 20 for i in range(1000)],
        "minutes": [30 + (i % 50) for i in range(1000)],
        "complexity_score": [2.0 + (i % 10) * 0.1 for i in range(1000)],
        "n_steps": [5 + i % 10 for i in range(1000)],
        "n_ingredients": [8 + i % 15 for i in range(1000)],
        "calories": [300 + i % 200 for i in range(1000)],
        "carb_pct": [40 + (i % 30) for i in range(1000)],
        "total_fat_pct": [25 + (i % 25) for i in range(1000)],
        "protein_pct": [20 + (i % 20) for i in range(1000)],
        "ingredients": [["salt", "pepper", "olive oil"] for _ in range(1000)],
        "tags": [["dinner", "main-dish", "quick"] for _ in range(1000)],
    }
    return pl.DataFrame(data)


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_volume(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_volume."""
    mock_load_recipes.return_value = mock_recipes_data

    # Mock Streamlit components
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()

    # Exécution
    analyse_trendline_volume()

    # Vérifications
    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called_once()
    mock_st.info.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_duree(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_duree."""
    mock_load_recipes.return_value = mock_recipes_data

    # Mock Streamlit components
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()

    # Exécution
    analyse_trendline_duree()

    # Vérifications
    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called_once()
    mock_st.info.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_complexite(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_complexite."""
    mock_load_recipes.return_value = mock_recipes_data

    # Mock Streamlit components
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()

    # Exécution
    analyse_trendline_complexite()

    # Vérifications
    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called_once()
    mock_st.info.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_nutrition(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_nutrition."""
    mock_load_recipes.return_value = mock_recipes_data

    # Mock Streamlit components
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()

    # Exécution
    analyse_trendline_nutrition()

    # Vérifications
    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called_once()
    mock_st.info.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_ingredients(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_ingredients."""
    mock_load_recipes.return_value = mock_recipes_data

    # Mock Streamlit components
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()

    # Exécution
    analyse_trendline_ingredients(top_n=5)

    # Vérifications
    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called_once()
    mock_st.info.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_tags(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_tags."""
    mock_load_recipes.return_value = mock_recipes_data

    # Mock Streamlit components
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()

    # Exécution
    analyse_trendline_tags(top_n=5)

    # Vérifications
    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called_once()
    mock_st.info.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_volume_no_data(mock_load_recipes, mock_st):
    """Test du comportement quand load_recipes_clean retourne None."""
    # Simuler l'échec du chargement
    with patch("visualization.analyse_trendlines.load_recipes_clean", None):
        mock_st.error = Mock()

        # Exécution
        analyse_trendline_volume()

        # Vérifications
        mock_st.error.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_duree_no_data(mock_load_recipes, mock_st):
    """Test du comportement quand load_recipes_clean retourne None."""
    # Simuler l'échec du chargement
    with patch("visualization.analyse_trendlines.load_recipes_clean", None):
        mock_st.error = Mock()

        # Exécution
        analyse_trendline_duree()

        # Vérifications
        mock_st.error.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_complexite_no_data(mock_load_recipes, mock_st):
    """Test du comportement quand load_recipes_clean retourne None."""
    # Simuler l'échec du chargement
    with patch("visualization.analyse_trendlines.load_recipes_clean", None):
        mock_st.error = Mock()

        # Exécution
        analyse_trendline_complexite()

        # Vérifications
        mock_st.error.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_nutrition_no_data(mock_load_recipes, mock_st):
    """Test du comportement quand load_recipes_clean retourne None."""
    # Simuler l'échec du chargement
    with patch("visualization.analyse_trendlines.load_recipes_clean", None):
        mock_st.error = Mock()

        # Exécution
        analyse_trendline_nutrition()

        # Vérifications
        mock_st.error.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_ingredients_no_data(mock_load_recipes, mock_st):
    """Test du comportement quand load_recipes_clean retourne None."""
    # Simuler l'échec du chargement
    with patch("visualization.analyse_trendlines.load_recipes_clean", None):
        mock_st.error = Mock()

        # Exécution
        analyse_trendline_ingredients()

        # Vérifications
        mock_st.error.assert_called_once()


@patch("visualization.analyse_trendlines.st")
@patch("visualization.analyse_trendlines.load_recipes_clean")
def test_analyse_trendline_tags_no_data(mock_load_recipes, mock_st):
    """Test du comportement quand load_recipes_clean retourne None."""
    # Simuler l'échec du chargement
    with patch("visualization.analyse_trendlines.load_recipes_clean", None):
        mock_st.error = Mock()

        # Exécution
        analyse_trendline_tags()

        # Vérifications
        mock_st.error.assert_called_once()
