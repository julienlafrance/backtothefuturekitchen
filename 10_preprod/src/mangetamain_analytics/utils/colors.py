"""Palette de couleurs - Charte graphique Back to the Kitchen.

Ce module centralise toutes les couleurs utilisées dans l'application
Mangetamain Analytics, inspirées du style rétro années 80.
"""

# ============================================================================
# COULEURS PRINCIPALES
# ============================================================================

# Fond et surfaces
BACKGROUND = "#1E1E1E"  # Fond sombre principal
SECONDARY_BACKGROUND = "#333333"  # Fond des widgets/cartes
BACKGROUND_MAIN = "#1E1E1E"  # Gris foncé - zone principale (alias)
BACKGROUND_SIDEBAR = "#000000"  # Noir pur - sidebar
BACKGROUND_FOOTER = "#1a1a1a"  # Noir foncé - footer
BACKGROUND_CARD = "#333333"  # Gris moyen - cards et widgets

# Texte
TEXT = "#F0F0F0"  # Texte clair principal
TEXT_PRIMARY = "#F0F0F0"  # Gris clair - texte principal (alias)
TEXT_SECONDARY = "#888888"  # Gris moyen - texte secondaire
TEXT_WHITE = "#ffffff"  # Blanc pur - texte sur fond sombre

# Orange primaire (accent principal) - COULEURS DU LOGO
PRIMARY = "#FF8C00"  # Orange vif - couleur principale
SECONDARY_ACCENT = "#FFD700"  # Jaune doré - accent secondaire
ORANGE_PRIMARY = "#FF8C00"  # Orange vif (alias de PRIMARY)
ORANGE_SECONDARY = "#E24E1B"  # Rouge/Orange profond du logo
ORANGE_LIGHT = "#FFA07A"  # Saumon - teinte douce du dégradé

# ============================================================================
# COULEURS D'ÉTAT
# ============================================================================

SUCCESS = "#28A745"  # Vert - succès, PROD badge
WARNING = "#FFC107"  # Jaune - warnings, PREPROD badge
ERROR = "#DC3545"  # Rouge - erreurs
INFO = "#17A2B8"  # Cyan - informations

# ============================================================================
# PALETTE GRAPHIQUES (Plotly/Matplotlib)
# ============================================================================

CHART_COLORS = [
    "#FF8C00",  # Base Orange (du milieu du dégradé du logo)
    "#FFD700",  # Base Jaune (du point lumineux du dégradé du logo)
    "#E24E1B",  # Rouge/Orange Profond (de la base du dégradé du logo)
    "#1E90FF",  # Bleu Vif (du contour et des effets de vitesse)
    "#00CED1",  # Cyan (accent technologique du logo)
    "#FFA07A",  # Saumon (teinte plus douce du dégradé orange)
    "#B0E0E6",  # Bleu Clair (teinte plus claire du contour bleu)
    "#DAA520",  # Jaune Doré (pour une variation riche du jaune)
]

# Palette steelblue (comme dans les wireframes)
STEELBLUE_PALETTE = [
    "#4682b4",  # SteelBlue principal
    "#5a9bd5",  # SteelBlue clair
    "#3a6ba5",  # SteelBlue foncé
]

# ============================================================================
# DÉGRADÉS
# ============================================================================

GRADIENT_ORANGE = f"linear-gradient(135deg, {PRIMARY} 0%, {ORANGE_SECONDARY} 100%)"
GRADIENT_DARK = f"linear-gradient(180deg, {BACKGROUND_SIDEBAR} 0%, {BACKGROUND_MAIN} 100%)"

# ============================================================================
# BADGES ENVIRONNEMENT
# ============================================================================

ENV_PROD = {
    "bg": SUCCESS,
    "text": TEXT_WHITE,
    "icon": "🟢",
}

ENV_PREPROD = {
    "bg": WARNING,
    "text": "#333333",  # Texte sombre sur fond jaune pour meilleure lisibilité
    "icon": "🔍",
}

# Constantes séparées pour utilisation directe
ENV_PROD_BG = SUCCESS
ENV_PROD_TEXT = TEXT_WHITE
ENV_PREPROD_BG = WARNING
ENV_PREPROD_TEXT = "#333333"

# ============================================================================
# COMPOSANTS UI
# ============================================================================

# Boutons
BUTTON_PRIMARY_BG = ORANGE_PRIMARY
BUTTON_PRIMARY_TEXT = TEXT_WHITE
BUTTON_PRIMARY_HOVER = ORANGE_LIGHT

BUTTON_SECONDARY_BG = "transparent"
BUTTON_SECONDARY_BORDER = ORANGE_PRIMARY
BUTTON_SECONDARY_TEXT = ORANGE_PRIMARY

# Cards et conteneurs
CARD_BORDER = "#333333"
CARD_SHADOW = "0 4px 6px rgba(0, 0, 0, 0.3)"
CARD_SHADOW_ORANGE = "0 4px 6px rgba(255, 140, 66, 0.3)"

# Inputs et contrôles
INPUT_BORDER = "#444444"
INPUT_FOCUS_BORDER = ORANGE_PRIMARY
INPUT_BG = BACKGROUND_CARD

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convertit une couleur HEX en RGBA.

    Args:
        hex_color: Couleur au format hex (#RRGGBB)
        alpha: Transparence (0.0 à 1.0)

    Returns:
        Couleur au format rgba(r, g, b, a)
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


def get_plotly_theme() -> dict:
    """Retourne le thème Plotly personnalisé.

    Returns:
        Dictionnaire de configuration Plotly
    """
    return {
        "layout": {
            "plot_bgcolor": BACKGROUND_MAIN,
            "paper_bgcolor": BACKGROUND_MAIN,
            "font": {"color": TEXT_PRIMARY},
            "xaxis": {
                "gridcolor": "#333333",
                "linecolor": "#444444",
            },
            "yaxis": {
                "gridcolor": "#333333",
                "linecolor": "#444444",
            },
            "colorway": CHART_COLORS,
        }
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Couleurs principales
    "PRIMARY",
    "SECONDARY_ACCENT",
    "BACKGROUND",
    "SECONDARY_BACKGROUND",
    "TEXT",
    "BACKGROUND_MAIN",
    "BACKGROUND_SIDEBAR",
    "BACKGROUND_FOOTER",
    "BACKGROUND_CARD",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    "TEXT_WHITE",
    "ORANGE_PRIMARY",
    "ORANGE_SECONDARY",
    "ORANGE_LIGHT",
    # États
    "SUCCESS",
    "WARNING",
    "ERROR",
    "INFO",
    # Palettes
    "CHART_COLORS",
    "STEELBLUE_PALETTE",
    # Dégradés
    "GRADIENT_ORANGE",
    "GRADIENT_DARK",
    # Badges
    "ENV_PROD",
    "ENV_PREPROD",
    "ENV_PROD_BG",
    "ENV_PROD_TEXT",
    "ENV_PREPROD_BG",
    "ENV_PREPROD_TEXT",
    # Composants
    "BUTTON_PRIMARY_BG",
    "BUTTON_PRIMARY_TEXT",
    "CARD_BORDER",
    "CARD_SHADOW",
    "CARD_SHADOW_ORANGE",
    # Helpers
    "get_rgba",
    "get_plotly_theme",
]
