"""Palette de couleurs - Charte graphique Back to the Kitchen.

Ce module centralise toutes les couleurs utilisées dans l'application
Mangetamain Analytics, inspirées du style rétro années 80.
"""

# ============================================================================
# COULEURS PRINCIPALES
# ============================================================================

# Fond et surfaces
BACKGROUND_MAIN = "#1e1e1e"  # Gris foncé - zone principale
BACKGROUND_SIDEBAR = "#000000"  # Noir pur - sidebar
BACKGROUND_FOOTER = "#1a1a1a"  # Noir foncé - footer
BACKGROUND_CARD = "#2a2a2a"  # Gris moyen - cards et widgets

# Texte
TEXT_PRIMARY = "#e0e0e0"  # Gris clair - texte principal
TEXT_SECONDARY = "#888888"  # Gris moyen - texte secondaire
TEXT_WHITE = "#ffffff"  # Blanc pur - texte sur fond sombre

# Orange primaire (accent principal)
ORANGE_PRIMARY = "#ff8c42"  # Orange principal - titres, liens
ORANGE_SECONDARY = "#ff6b35"  # Orange secondaire - dégradés
ORANGE_LIGHT = "#ffa560"  # Orange clair - hover

# ============================================================================
# COULEURS D'ÉTAT
# ============================================================================

SUCCESS = "#5cb85c"  # Vert - succès, PROD badge
WARNING = "#f0ad4e"  # Jaune/Orange - warnings, PREPROD badge
ERROR = "#d9534f"  # Rouge - erreurs
INFO = "#5bc0de"  # Bleu clair - informations

# ============================================================================
# PALETTE GRAPHIQUES (Plotly/Matplotlib)
# ============================================================================

CHART_COLORS = [
    "#ff8c42",  # Orange principal
    "#5bc0de",  # Bleu clair
    "#5cb85c",  # Vert
    "#f0ad4e",  # Jaune/Orange
    "#d9534f",  # Rouge
    "#9b59b6",  # Violet
    "#1abc9c",  # Turquoise
    "#e74c3c",  # Rouge vif
    "#3498db",  # Bleu
    "#95a5a6",  # Gris
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

GRADIENT_ORANGE = f"linear-gradient(135deg, {ORANGE_PRIMARY} 0%, {ORANGE_SECONDARY} 100%)"
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
    "text": TEXT_WHITE,
    "icon": "🔍",
}

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
