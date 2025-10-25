"""Tests unitaires pour le module chart_theme.

Teste les fonctions d'application de thème aux graphiques Plotly.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock
import plotly.graph_objects as go

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from utils import chart_theme, colors


@pytest.fixture
def sample_figure():
    """Fixture pour créer une figure Plotly de test."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode="lines", name="test"))
    return fig


def test_apply_chart_theme_basic(sample_figure):
    """Test de l'application du thème de base."""
    result = chart_theme.apply_chart_theme(sample_figure)

    assert result is not None
    assert result.layout.plot_bgcolor == "rgba(0,0,0,0)"
    assert result.layout.paper_bgcolor == "rgba(0,0,0,0)"
    assert result.layout.font.color == colors.TEXT_PRIMARY


def test_apply_chart_theme_with_title(sample_figure):
    """Test de l'application du thème avec titre."""
    result = chart_theme.apply_chart_theme(sample_figure, title="Test Chart")

    assert result.layout.title.text == "Test Chart"
    assert result.layout.title.font.color == colors.PRIMARY
    assert result.layout.title.x == 0.5
    assert result.layout.title.xanchor == "center"


def test_apply_chart_theme_axes(sample_figure):
    """Test de la configuration des axes."""
    result = chart_theme.apply_chart_theme(sample_figure)

    assert result.layout.xaxis.showgrid is True
    assert result.layout.xaxis.gridcolor == "#444444"
    assert result.layout.xaxis.gridwidth == 1

    assert result.layout.yaxis.showgrid is True
    assert result.layout.yaxis.gridcolor == "#444444"
    assert result.layout.yaxis.gridwidth == 1


def test_apply_chart_theme_legend(sample_figure):
    """Test de la configuration de la légende."""
    result = chart_theme.apply_chart_theme(sample_figure)

    assert result.layout.legend.bgcolor == "rgba(42, 42, 42, 0.8)"
    assert result.layout.legend.bordercolor == "#666666"
    assert result.layout.legend.borderwidth == 1


def test_apply_chart_theme_hoverlabel(sample_figure):
    """Test de la configuration des hover labels."""
    result = chart_theme.apply_chart_theme(sample_figure)

    assert result.layout.hoverlabel.bgcolor == colors.BACKGROUND_CARD
    assert result.layout.hoverlabel.font.color == colors.TEXT_WHITE
    assert result.layout.hoverlabel.bordercolor == colors.PRIMARY


def test_get_bar_color():
    """Test de la couleur pour les barres."""
    bar_color = chart_theme.get_bar_color()

    assert bar_color == colors.CHART_COLORS[0]
    assert bar_color == "#FF8C00"


def test_get_line_colors():
    """Test de la palette de couleurs pour lignes."""
    line_colors = chart_theme.get_line_colors()

    assert isinstance(line_colors, list)
    assert line_colors == colors.CHART_COLORS
    assert len(line_colors) == 8


def test_get_scatter_color():
    """Test de la couleur pour scatter plots."""
    scatter_color = chart_theme.get_scatter_color()

    assert scatter_color == colors.CHART_COLORS[1]


def test_get_reference_line_color():
    """Test de la couleur pour lignes de référence."""
    ref_color = chart_theme.get_reference_line_color()

    assert ref_color == colors.ERROR
    assert ref_color == "#DC3545"


def test_apply_subplot_theme():
    """Test de l'application du thème à des subplots."""
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=1, cols=2)
    fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
    fig.add_trace(go.Scatter(x=[1, 2], y=[5, 6]), row=1, col=2)

    result = chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)

    assert result is not None
    assert result.layout.plot_bgcolor == "rgba(0,0,0,0)"
    assert result.layout.paper_bgcolor == "rgba(0,0,0,0)"
