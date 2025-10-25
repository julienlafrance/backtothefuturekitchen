"""Tests unitaires pour le module analyse_trendlines_v2.

Teste les fonctions d'analyse de tendances temporelles (version 2).
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock, patch
import polars as pl

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from visualization.analyse_trendlines_v2 import (
    analyse_trendline_volume,
    analyse_trendline_duree,
    analyse_trendline_duree_old_intervals,
    analyse_trendline_duree_old,
    analyse_trendline_complexite,
    analyse_trendline_nutrition,
    analyse_trendline_ingredients,
    analyse_trendline_tags,
)


@pytest.fixture
def mock_recipes_data():
    """Fixture pour créer des données de test simulées."""
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


def setup_st_mocks(mock_st):
    """Configure tous les mocks Streamlit nécessaires."""
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()
    mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])
    mock_st.slider = Mock(
        side_effect=lambda *args, **kwargs: kwargs.get(
            "value", (1999, 2018) if isinstance(kwargs.get("value", ()), tuple) else 95
        )
    )
    mock_st.radio = Mock(return_value="Linéaire")
    # Return steelblue for color selections, Moyenne for metrics
    mock_st.selectbox = Mock(
        side_effect=lambda label, options, **kwargs: (
            options[kwargs.get("index", 0)] if options else "Moyenne"
        )
    )
    mock_st.multiselect = Mock(return_value=[])
    mock_st.checkbox = Mock(return_value=False)
    mock_st.metric = Mock()
    mock_st.write = Mock()
    mock_st.markdown = Mock()
    mock_st.subheader = Mock()
    mock_st.divider = Mock()
    return mock_st


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_volume(mock_load_data, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_volume."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_volume()

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_duree(mock_load_data, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_duree."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_duree()

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_duree_old_intervals(
    mock_load_data, mock_st, mock_recipes_data
):
    """Test de la fonction analyse_trendline_duree_old_intervals."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_duree_old_intervals()

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_duree_old(mock_load_data, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_duree_old."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_duree_old()

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_complexite(mock_load_data, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_complexite."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_complexite()

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_nutrition(mock_load_data, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_nutrition."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_nutrition()

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_ingredients(mock_load_data, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_ingredients."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_ingredients(top_n=5)

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()


@patch("visualization.analyse_trendlines_v2.st")
@patch("visualization.analyse_trendlines_v2.load_and_prepare_data")
def test_analyse_trendline_tags(mock_load_data, mock_st, mock_recipes_data):
    """Test de la fonction analyse_trendline_tags."""
    mock_load_data.return_value = mock_recipes_data
    setup_st_mocks(mock_st)

    analyse_trendline_tags(top_n=5)

    mock_load_data.assert_called_once()
    mock_st.plotly_chart.assert_called()
