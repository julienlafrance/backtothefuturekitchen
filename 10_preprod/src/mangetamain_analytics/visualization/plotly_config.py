"""Configuration centralisée pour les graphiques Plotly.

Ce module définit les styles, couleurs et configurations réutilisables
pour tous les graphiques de l'application.
"""

# Palette de couleurs cohérente (inspirée de ton exemple matplotlib)
COLORS = {
    "observed": "#00416A",  # darkblue - pour données observées
    "regression": "#E94B3C",  # red - pour lignes de régression
    "confidence": "#2E8B57",  # green - pour intervalles de confiance
    "prediction": "#FF8C00",  # orange - pour intervalles de prédiction
    "primary": "#00416A",  # darkblue
    "secondary": "#4682B4",  # steelblue
    "tertiary": "#FF7F50",  # coral
    "success": "#2E8B57",  # green
    "warning": "#FF8C00",  # orange
    "danger": "#E94B3C",  # red
    "purple": "#8B008B",
}

# Configuration du layout pour fond blanc
WHITE_LAYOUT = {
    "plot_bgcolor": "white",
    "paper_bgcolor": "white",
    "font": {"family": "Arial, sans-serif", "size": 12, "color": "#333"},
    "hovermode": "x unified",
    "legend": {
        "bgcolor": "rgba(255, 255, 255, 0.9)",
        "bordercolor": "#ddd",
        "borderwidth": 1,
    },
}

# Configuration des axes avec grilles
AXIS_CONFIG = {
    "showgrid": True,
    "gridcolor": "#e0e0e0",
    "gridwidth": 1,
    "zeroline": True,
    "zerolinecolor": "#ccc",
    "zerolinewidth": 1,
}


def apply_theme(fig, title=None, height=600, add_grids=False):
    """Applique le thème blanc cohérent à un graphique Plotly.

    Args:
        fig: Figure Plotly à styliser
        title: Titre optionnel du graphique
        height: Hauteur du graphique en pixels
        add_grids: Si True, ajoute les grilles aux axes (défaut: False)
                   Pour les subplots, il vaut mieux configurer les grilles
                   directement dans le code de la fonction

    Returns:
        Figure Plotly avec thème appliqué

    Example:
        >>> fig = go.Figure()
        >>> fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6]))
        >>> fig = apply_theme(fig, title="Mon graphique", height=500)
    """
    # Appliquer uniquement le layout blanc, SANS toucher aux axes
    # Les axes doivent être configurés dans chaque fonction pour préserver
    # les configurations spécifiques des subplots
    fig.update_layout(**WHITE_LAYOUT)

    if title:
        fig.update_layout(title_text=title)

    if height:
        fig.update_layout(height=height)

    # Optionnel: ajouter les grilles seulement si demandé explicitement
    if add_grids:
        fig.update_xaxes(**AXIS_CONFIG)
        fig.update_yaxes(**AXIS_CONFIG)

    return fig


def get_scatter_config(name, color_key="observed", mode="markers", size=8, opacity=0.6):
    """Retourne la configuration pour un scatter plot.

    Args:
        name: Nom de la trace
        color_key: Clé de couleur dans COLORS
        mode: Mode Plotly ('markers', 'lines', 'lines+markers')
        size: Taille des markers
        opacity: Opacité

    Returns:
        Dict de configuration pour go.Scatter
    """
    return {
        "name": name,
        "mode": mode,
        "marker": {"color": COLORS[color_key], "size": size, "opacity": opacity},
        "line": {"color": COLORS[color_key], "width": 2},
    }


def get_regression_line_config(name="Régression", color_key="regression"):
    """Configuration pour ligne de régression.

    Args:
        name: Nom de la ligne
        color_key: Couleur dans COLORS

    Returns:
        Dict de configuration
    """
    return {
        "name": name,
        "mode": "lines",
        "line": {"color": COLORS[color_key], "width": 2, "dash": "solid"},
    }


def get_confidence_band_config(name="Intervalle de confiance", color_key="confidence"):
    """Configuration pour bande de confiance (fill_between).

    Args:
        name: Nom de la bande
        color_key: Couleur dans COLORS

    Returns:
        Dict de configuration
    """
    color = COLORS[color_key]
    # Convertir hex to rgba
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    return {
        "name": name,
        "mode": "lines",
        "line": {"color": color, "width": 2, "dash": "dash"},
        "fillcolor": f"rgba({r}, {g}, {b}, 0.2)",
        "fill": "tonexty",
    }


def get_prediction_band_config(name="Intervalle de prédiction", color_key="prediction"):
    """Configuration pour bande de prédiction.

    Args:
        name: Nom de la bande
        color_key: Couleur dans COLORS

    Returns:
        Dict de configuration
    """
    color = COLORS[color_key]
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)

    return {
        "name": name,
        "mode": "lines",
        "line": {"color": color, "width": 2, "dash": "dot"},
        "fillcolor": f"rgba({r}, {g}, {b}, 0.1)",
        "fill": "tonexty",
    }
