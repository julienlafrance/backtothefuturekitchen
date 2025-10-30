"""Classe ColorTheme - Charte graphique Back to the Kitchen.

Ce module fournit une classe centralisée pour gérer toutes les couleurs
de l'application Mangetamain Analytics avec une approche POO.
"""


class ColorTheme:
    """Thème de couleurs 'Back to the Kitchen' avec accesseurs typés.

    Cette classe encapsule toutes les couleurs de la charte graphique
    dans une interface POO avec méthodes utilitaires.

    Examples:
        >>> # Accès direct aux couleurs
        >>> bar_color = ColorTheme.ORANGE_PRIMARY
        >>> text_color = ColorTheme.TEXT_PRIMARY

        >>> # Conversion en RGBA
        >>> rgba = ColorTheme.to_rgba(ColorTheme.ORANGE_PRIMARY, 0.5)
        >>> # 'rgba(255, 140, 0, 0.5)'

        >>> # Récupération thème Plotly
        >>> theme = ColorTheme.get_plotly_theme()
    """

    # ========================================================================
    # COULEURS PRINCIPALES
    # ========================================================================

    # Fond et surfaces
    BACKGROUND: str = "#1E1E1E"  # Fond sombre principal
    SECONDARY_BACKGROUND: str = "#333333"  # Fond widgets/cartes
    BACKGROUND_MAIN: str = "#1E1E1E"  # Gris foncé - zone principale
    BACKGROUND_SIDEBAR: str = "#000000"  # Noir pur - sidebar
    BACKGROUND_FOOTER: str = "#1a1a1a"  # Noir foncé - footer
    BACKGROUND_CARD: str = "#333333"  # Gris moyen - cards et widgets

    # Texte
    TEXT: str = "#F0F0F0"  # Texte clair principal
    TEXT_PRIMARY: str = "#F0F0F0"  # Gris clair - texte principal
    TEXT_SECONDARY: str = "#888888"  # Gris moyen - texte secondaire
    TEXT_WHITE: str = "#ffffff"  # Blanc pur - texte sur fond sombre

    # Orange primaire (accent principal) - COULEURS DU LOGO
    PRIMARY: str = "#FF8C00"  # Orange vif - couleur principale
    SECONDARY_ACCENT: str = "#FFD700"  # Jaune doré - accent secondaire
    ORANGE_PRIMARY: str = "#FF8C00"  # Orange vif (alias de PRIMARY)
    ORANGE_SECONDARY: str = "#E24E1B"  # Rouge/Orange profond du logo
    ORANGE_LIGHT: str = "#FFA07A"  # Saumon - teinte douce

    # ========================================================================
    # COULEURS D'ÉTAT
    # ========================================================================

    SUCCESS: str = "#28A745"  # Vert - succès, PROD badge
    WARNING: str = "#FFC107"  # Jaune - warnings, PREPROD badge
    ERROR: str = "#DC3545"  # Rouge - erreurs
    INFO: str = "#17A2B8"  # Cyan - informations

    # ========================================================================
    # PALETTE GRAPHIQUES (Plotly/Matplotlib)
    # ========================================================================

    CHART_COLORS: list[str] = [
        "#FF8C00",  # Base Orange (du milieu du dégradé du logo)
        "#FFD700",  # Base Jaune (du point lumineux du dégradé)
        "#E24E1B",  # Rouge/Orange Profond (de la base du dégradé)
        "#1E90FF",  # Bleu Vif (du contour et des effets de vitesse)
        "#00CED1",  # Cyan (accent technologique du logo)
        "#FFA07A",  # Saumon (teinte plus douce du dégradé)
        "#B0E0E6",  # Bleu Clair (teinte plus claire du contour)
        "#DAA520",  # Jaune Doré (variation riche du jaune)
    ]

    # Palette steelblue (comme dans les wireframes)
    STEELBLUE_PALETTE: list[str] = [
        "#4682b4",  # SteelBlue principal
        "#5a9bd5",  # SteelBlue clair
        "#3a6ba5",  # SteelBlue foncé
    ]

    # ========================================================================
    # DÉGRADÉS
    # ========================================================================

    @classmethod
    def gradient_orange(cls) -> str:
        """Dégradé orange (PRIMARY → ORANGE_SECONDARY)."""
        return (
            f"linear-gradient(135deg, {cls.PRIMARY} 0%, "
            f"{cls.ORANGE_SECONDARY} 100%)"
        )

    @classmethod
    def gradient_dark(cls) -> str:
        """Dégradé fond sombre (SIDEBAR → MAIN)."""
        return (
            f"linear-gradient(180deg, {cls.BACKGROUND_SIDEBAR} 0%, "
            f"{cls.BACKGROUND_MAIN} 100%)"
        )

    # ========================================================================
    # BADGES ENVIRONNEMENT
    # ========================================================================

    ENV_PROD: dict[str, str] = {
        "bg": SUCCESS,
        "text": TEXT_WHITE,
        "icon": "🟢",
    }

    ENV_PREPROD: dict[str, str] = {
        "bg": WARNING,
        "text": "#333333",  # Texte sombre sur jaune
        "icon": "🔍",
    }

    # Constantes séparées pour utilisation directe
    ENV_PROD_BG: str = SUCCESS
    ENV_PROD_TEXT: str = TEXT_WHITE
    ENV_PREPROD_BG: str = WARNING
    ENV_PREPROD_TEXT: str = "#333333"

    # ========================================================================
    # COMPOSANTS UI
    # ========================================================================

    # Boutons
    BUTTON_PRIMARY_BG: str = ORANGE_PRIMARY
    BUTTON_PRIMARY_TEXT: str = TEXT_WHITE
    BUTTON_PRIMARY_HOVER: str = ORANGE_LIGHT

    BUTTON_SECONDARY_BG: str = "transparent"
    BUTTON_SECONDARY_BORDER: str = ORANGE_PRIMARY
    BUTTON_SECONDARY_TEXT: str = ORANGE_PRIMARY

    # Cards et conteneurs
    CARD_BORDER: str = "#333333"
    CARD_SHADOW: str = "0 4px 6px rgba(0, 0, 0, 0.3)"
    CARD_SHADOW_ORANGE: str = "0 4px 6px rgba(255, 140, 66, 0.3)"

    # Inputs et contrôles
    INPUT_BORDER: str = "#444444"
    INPUT_FOCUS_BORDER: str = ORANGE_PRIMARY
    INPUT_BG: str = BACKGROUND_CARD

    # ========================================================================
    # MÉTHODES UTILITAIRES
    # ========================================================================

    @classmethod
    def to_rgba(cls, hex_color: str, alpha: float = 1.0) -> str:
        """Convertit une couleur HEX en RGBA avec validation.

        Args:
            hex_color: Couleur au format hex (#RRGGBB)
            alpha: Transparence (0.0 à 1.0)

        Returns:
            Couleur au format rgba(r, g, b, a)

        Raises:
            ValueError: Si hex_color invalide ou alpha hors range

        Examples:
            >>> ColorTheme.to_rgba("#FF8C00", 0.5)
            'rgba(255, 140, 0, 0.5)'

            >>> ColorTheme.to_rgba(ColorTheme.ORANGE_PRIMARY, 0.8)
            'rgba(255, 140, 0, 0.8)'
        """
        if not isinstance(hex_color, str) or not hex_color.startswith("#"):
            raise ValueError(f"Couleur hex invalide: {hex_color}")

        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"Alpha doit être entre 0 et 1, reçu: {alpha}")

        hex_color = hex_color.lstrip("#")

        if len(hex_color) != 6:
            raise ValueError(f"Couleur hex doit avoir 6 caractères, reçu: #{hex_color}")

        try:
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        except ValueError as e:
            raise ValueError(f"Couleur hex invalide: #{hex_color}") from e

        return f"rgba({r}, {g}, {b}, {alpha})"

    @classmethod
    def get_plotly_theme(cls) -> dict:
        """Retourne le thème Plotly complet.

        Returns:
            Dictionnaire de configuration Plotly avec fond, grilles,
            axes et palette de couleurs

        Examples:
            >>> theme = ColorTheme.get_plotly_theme()
            >>> fig.update_layout(**theme['layout'])
        """
        return {
            "layout": {
                "plot_bgcolor": cls.BACKGROUND_MAIN,
                "paper_bgcolor": cls.BACKGROUND_MAIN,
                "font": {"color": cls.TEXT_PRIMARY},
                "xaxis": {
                    "gridcolor": "#333333",
                    "linecolor": "#444444",
                },
                "yaxis": {
                    "gridcolor": "#333333",
                    "linecolor": "#444444",
                },
                "colorway": cls.CHART_COLORS,
            }
        }

    @classmethod
    def get_seasonal_colors(cls) -> dict[str, str]:
        """Retourne le mapping couleurs saisonnières.

        Returns:
            Dictionnaire {saison: couleur_hex}

        Examples:
            >>> colors = ColorTheme.get_seasonal_colors()
            >>> autumn_color = colors["Automne"]
            >>> # '#FF8C00'
        """
        return {
            "Printemps": "#90EE90",  # Vert clair
            "Été": "#FFD700",  # Jaune doré
            "Automne": cls.ORANGE_PRIMARY,  # Orange vif
            "Hiver": "#4682B4",  # Bleu acier
        }

    @classmethod
    def get_seasonal_color(cls, season: str) -> str:
        """Retourne la couleur pour une saison donnée.

        Args:
            season: Nom de la saison (Printemps, Été, Automne, Hiver)

        Returns:
            Couleur hex de la saison, ou ORANGE_PRIMARY si saison inconnue

        Examples:
            >>> ColorTheme.get_seasonal_color("Automne")
            '#FF8C00'

            >>> ColorTheme.get_seasonal_color("Inconnu")
            '#FF8C00'  # Fallback
        """
        seasonal_colors = cls.get_seasonal_colors()
        return seasonal_colors.get(season, cls.ORANGE_PRIMARY)
