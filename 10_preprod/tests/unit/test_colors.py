"""Tests unitaires pour le module colors.

Teste les constantes et fonctions de gestion des couleurs.
"""

import sys
from pathlib import Path

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from utils import colors


def test_color_constants():
    """Test des constantes de couleur principales."""
    assert colors.PRIMARY == "#FF8C00"
    assert colors.BACKGROUND == "#1E1E1E"
    assert colors.TEXT == "#F0F0F0"
    assert colors.SUCCESS == "#28A745"
    assert colors.WARNING == "#FFC107"
    assert colors.ERROR == "#DC3545"


def test_chart_colors_palette():
    """Test de la palette de couleurs pour graphiques."""
    assert isinstance(colors.CHART_COLORS, list)
    assert len(colors.CHART_COLORS) == 8
    assert colors.CHART_COLORS[0] == "#FF8C00"  # Orange
    assert all(color.startswith("#") for color in colors.CHART_COLORS)


def test_get_rgba_full_opacity():
    """Test de la conversion HEX vers RGBA avec opacité complète."""
    result = colors.get_rgba("#FF8C00", 1.0)
    assert result == "rgba(255, 140, 0, 1.0)"


def test_get_rgba_half_opacity():
    """Test de la conversion HEX vers RGBA avec demi-opacité."""
    result = colors.get_rgba("#FF8C00", 0.5)
    assert result == "rgba(255, 140, 0, 0.5)"


def test_get_rgba_zero_opacity():
    """Test de la conversion HEX vers RGBA avec opacité nulle."""
    result = colors.get_rgba("#FF8C00", 0.0)
    assert result == "rgba(255, 140, 0, 0.0)"


def test_get_rgba_without_hash():
    """Test de la conversion HEX sans # initial."""
    result = colors.get_rgba("FF8C00", 1.0)
    assert result == "rgba(255, 140, 0, 1.0)"


def test_get_plotly_theme():
    """Test de la génération du thème Plotly."""
    theme = colors.get_plotly_theme()

    assert isinstance(theme, dict)
    assert "layout" in theme
    assert theme["layout"]["plot_bgcolor"] == colors.BACKGROUND_MAIN
    assert theme["layout"]["paper_bgcolor"] == colors.BACKGROUND_MAIN
    assert theme["layout"]["font"]["color"] == colors.TEXT_PRIMARY
    assert theme["layout"]["colorway"] == colors.CHART_COLORS


def test_env_badges():
    """Test des configurations de badges environnement."""
    assert colors.ENV_PROD["bg"] == colors.SUCCESS
    assert colors.ENV_PROD["text"] == colors.TEXT_WHITE
    assert colors.ENV_PROD["icon"] == "🟢"

    assert colors.ENV_PREPROD["bg"] == colors.WARNING
    assert colors.ENV_PREPROD["text"] == "#333333"
    assert colors.ENV_PREPROD["icon"] == "🔍"


def test_button_colors():
    """Test des couleurs de boutons."""
    assert colors.BUTTON_PRIMARY_BG == colors.ORANGE_PRIMARY
    assert colors.BUTTON_PRIMARY_TEXT == colors.TEXT_WHITE
    assert colors.BUTTON_SECONDARY_BG == "transparent"


def test_gradient_constants():
    """Test des constantes de dégradés."""
    assert "linear-gradient" in colors.GRADIENT_ORANGE
    assert colors.PRIMARY in colors.GRADIENT_ORANGE
    assert colors.ORANGE_SECONDARY in colors.GRADIENT_ORANGE
