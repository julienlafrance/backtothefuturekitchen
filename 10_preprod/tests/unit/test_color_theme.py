"""Tests unitaires pour la classe ColorTheme.

Ce module teste l'encapsulation POO des couleurs de la charte graphique.
"""

import pytest

from mangetamain_analytics.utils.color_theme import ColorTheme


class TestColorThemeConstants:
    """Tests pour les constantes de couleur."""

    def test_background_colors(self):
        """Vérifie les couleurs de fond."""
        assert ColorTheme.BACKGROUND == "#1E1E1E"
        assert ColorTheme.SECONDARY_BACKGROUND == "#333333"
        assert ColorTheme.BACKGROUND_MAIN == "#1E1E1E"
        assert ColorTheme.BACKGROUND_SIDEBAR == "#000000"
        assert ColorTheme.BACKGROUND_FOOTER == "#1a1a1a"
        assert ColorTheme.BACKGROUND_CARD == "#333333"

    def test_text_colors(self):
        """Vérifie les couleurs de texte."""
        assert ColorTheme.TEXT == "#F0F0F0"
        assert ColorTheme.TEXT_PRIMARY == "#F0F0F0"
        assert ColorTheme.TEXT_SECONDARY == "#888888"
        assert ColorTheme.TEXT_WHITE == "#ffffff"

    def test_primary_colors(self):
        """Vérifie les couleurs primaires."""
        assert ColorTheme.PRIMARY == "#FF8C00"
        assert ColorTheme.SECONDARY_ACCENT == "#FFD700"
        assert ColorTheme.ORANGE_PRIMARY == "#FF8C00"
        assert ColorTheme.ORANGE_SECONDARY == "#E24E1B"
        assert ColorTheme.ORANGE_LIGHT == "#FFA07A"

    def test_state_colors(self):
        """Vérifie les couleurs d'état."""
        assert ColorTheme.SUCCESS == "#28A745"
        assert ColorTheme.WARNING == "#FFC107"
        assert ColorTheme.ERROR == "#DC3545"
        assert ColorTheme.INFO == "#17A2B8"

    def test_chart_colors_list(self):
        """Vérifie la palette graphique."""
        assert isinstance(ColorTheme.CHART_COLORS, list)
        assert len(ColorTheme.CHART_COLORS) == 8
        assert ColorTheme.CHART_COLORS[0] == "#FF8C00"
        assert ColorTheme.CHART_COLORS[1] == "#FFD700"
        assert ColorTheme.CHART_COLORS[2] == "#E24E1B"

    def test_steelblue_palette(self):
        """Vérifie la palette steelblue."""
        assert isinstance(ColorTheme.STEELBLUE_PALETTE, list)
        assert len(ColorTheme.STEELBLUE_PALETTE) == 3
        assert ColorTheme.STEELBLUE_PALETTE[0] == "#4682b4"


class TestColorThemeToRgba:
    """Tests pour la méthode to_rgba()."""

    def test_to_rgba_basic(self):
        """Conversion HEX vers RGBA basique."""
        result = ColorTheme.to_rgba("#FF8C00")
        assert result == "rgba(255, 140, 0, 1.0)"

    def test_to_rgba_with_alpha(self):
        """Conversion HEX vers RGBA avec transparence."""
        result = ColorTheme.to_rgba("#FF8C00", 0.5)
        assert result == "rgba(255, 140, 0, 0.5)"

    def test_to_rgba_alpha_zero(self):
        """Conversion avec alpha = 0."""
        result = ColorTheme.to_rgba("#FF8C00", 0.0)
        assert result == "rgba(255, 140, 0, 0.0)"

    def test_to_rgba_white(self):
        """Conversion blanc."""
        result = ColorTheme.to_rgba("#FFFFFF", 1.0)
        assert result == "rgba(255, 255, 255, 1.0)"

    def test_to_rgba_black(self):
        """Conversion noir."""
        result = ColorTheme.to_rgba("#000000", 1.0)
        assert result == "rgba(0, 0, 0, 1.0)"

    def test_to_rgba_invalid_format_no_hash(self):
        """Validation: format sans #."""
        with pytest.raises(ValueError, match="Couleur hex invalide"):
            ColorTheme.to_rgba("FF8C00")

    def test_to_rgba_invalid_format_not_string(self):
        """Validation: type non-string."""
        with pytest.raises(ValueError, match="Couleur hex invalide"):
            ColorTheme.to_rgba(123456)

    def test_to_rgba_invalid_length(self):
        """Validation: longueur invalide."""
        with pytest.raises(ValueError, match="Couleur hex doit avoir 6 caractères"):
            ColorTheme.to_rgba("#FF8C")

    def test_to_rgba_invalid_hex_chars(self):
        """Validation: caractères invalides."""
        with pytest.raises(ValueError, match="Couleur hex invalide"):
            ColorTheme.to_rgba("#GGGGGG")

    def test_to_rgba_alpha_negative(self):
        """Validation: alpha négatif."""
        with pytest.raises(ValueError, match="Alpha doit être entre 0 et 1"):
            ColorTheme.to_rgba("#FF8C00", -0.1)

    def test_to_rgba_alpha_too_high(self):
        """Validation: alpha > 1."""
        with pytest.raises(ValueError, match="Alpha doit être entre 0 et 1"):
            ColorTheme.to_rgba("#FF8C00", 1.5)


class TestColorThemeGetPlotlyTheme:
    """Tests pour la méthode get_plotly_theme()."""

    def test_get_plotly_theme_structure(self):
        """Vérifie la structure du thème Plotly."""
        theme = ColorTheme.get_plotly_theme()
        assert isinstance(theme, dict)
        assert "layout" in theme

    def test_get_plotly_theme_layout(self):
        """Vérifie le contenu du layout."""
        theme = ColorTheme.get_plotly_theme()
        layout = theme["layout"]

        assert layout["plot_bgcolor"] == ColorTheme.BACKGROUND_MAIN
        assert layout["paper_bgcolor"] == ColorTheme.BACKGROUND_MAIN
        assert layout["font"]["color"] == ColorTheme.TEXT_PRIMARY

    def test_get_plotly_theme_axes(self):
        """Vérifie la configuration des axes."""
        theme = ColorTheme.get_plotly_theme()
        layout = theme["layout"]

        assert layout["xaxis"]["gridcolor"] == "#333333"
        assert layout["xaxis"]["linecolor"] == "#444444"
        assert layout["yaxis"]["gridcolor"] == "#333333"
        assert layout["yaxis"]["linecolor"] == "#444444"

    def test_get_plotly_theme_colorway(self):
        """Vérifie la palette de couleurs."""
        theme = ColorTheme.get_plotly_theme()
        layout = theme["layout"]

        assert layout["colorway"] == ColorTheme.CHART_COLORS
        assert len(layout["colorway"]) == 8


class TestColorThemeSeasonalColors:
    """Tests pour les méthodes de couleurs saisonnières."""

    def test_get_seasonal_colors_structure(self):
        """Vérifie la structure du mapping."""
        colors = ColorTheme.get_seasonal_colors()
        assert isinstance(colors, dict)
        assert len(colors) == 4

    def test_get_seasonal_colors_values(self):
        """Vérifie les valeurs du mapping."""
        colors = ColorTheme.get_seasonal_colors()
        assert colors["Printemps"] == "#90EE90"
        assert colors["Été"] == "#FFD700"
        assert colors["Automne"] == ColorTheme.ORANGE_PRIMARY
        assert colors["Hiver"] == "#4682B4"

    def test_get_seasonal_color_printemps(self):
        """Récupération couleur printemps."""
        color = ColorTheme.get_seasonal_color("Printemps")
        assert color == "#90EE90"

    def test_get_seasonal_color_ete(self):
        """Récupération couleur été."""
        color = ColorTheme.get_seasonal_color("Été")
        assert color == "#FFD700"

    def test_get_seasonal_color_automne(self):
        """Récupération couleur automne."""
        color = ColorTheme.get_seasonal_color("Automne")
        assert color == ColorTheme.ORANGE_PRIMARY

    def test_get_seasonal_color_hiver(self):
        """Récupération couleur hiver."""
        color = ColorTheme.get_seasonal_color("Hiver")
        assert color == "#4682B4"

    def test_get_seasonal_color_fallback(self):
        """Fallback pour saison inconnue."""
        color = ColorTheme.get_seasonal_color("Inconnu")
        assert color == ColorTheme.ORANGE_PRIMARY

    def test_get_seasonal_color_case_sensitive(self):
        """Vérification sensibilité à la casse."""
        # Doit retourner fallback si casse incorrecte
        color = ColorTheme.get_seasonal_color("printemps")
        assert color == ColorTheme.ORANGE_PRIMARY


class TestColorThemeButtonColors:
    """Tests pour les couleurs de boutons."""

    def test_button_primary_colors(self):
        """Vérifie les couleurs bouton primaire."""
        assert ColorTheme.BUTTON_PRIMARY_BG == ColorTheme.ORANGE_PRIMARY
        assert ColorTheme.BUTTON_PRIMARY_TEXT == ColorTheme.TEXT_WHITE
        assert ColorTheme.BUTTON_PRIMARY_HOVER == ColorTheme.ORANGE_LIGHT

    def test_button_secondary_colors(self):
        """Vérifie les couleurs bouton secondaire."""
        assert ColorTheme.BUTTON_SECONDARY_BG == "transparent"
        assert ColorTheme.BUTTON_SECONDARY_BORDER == ColorTheme.ORANGE_PRIMARY
        assert ColorTheme.BUTTON_SECONDARY_TEXT == ColorTheme.ORANGE_PRIMARY


class TestColorThemeEnvironmentBadges:
    """Tests pour les badges d'environnement."""

    def test_env_prod_colors(self):
        """Vérifie les couleurs badge PROD."""
        assert ColorTheme.ENV_PROD_BG == ColorTheme.SUCCESS
        assert ColorTheme.ENV_PROD_TEXT == ColorTheme.TEXT_WHITE

    def test_env_preprod_colors(self):
        """Vérifie les couleurs badge PREPROD."""
        assert ColorTheme.ENV_PREPROD_BG == ColorTheme.WARNING
        assert ColorTheme.ENV_PREPROD_TEXT == "#333333"

    def test_env_prod_dict(self):
        """Vérifie le dictionnaire ENV_PROD."""
        assert ColorTheme.ENV_PROD["bg"] == ColorTheme.SUCCESS
        assert ColorTheme.ENV_PROD["text"] == ColorTheme.TEXT_WHITE
        assert ColorTheme.ENV_PROD["icon"] == "🟢"

    def test_env_preprod_dict(self):
        """Vérifie le dictionnaire ENV_PREPROD."""
        assert ColorTheme.ENV_PREPROD["bg"] == ColorTheme.WARNING
        assert ColorTheme.ENV_PREPROD["text"] == "#333333"
        assert ColorTheme.ENV_PREPROD["icon"] == "🔍"
