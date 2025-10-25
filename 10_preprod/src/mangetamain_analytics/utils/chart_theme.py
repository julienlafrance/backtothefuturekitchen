"""Thème graphique pour les visualisations Plotly.

Ce module fournit des fonctions pour appliquer automatiquement
la charte graphique Back to the Kitchen aux graphiques Plotly.
"""

from . import colors


def apply_chart_theme(fig, title=None):
    """Applique le thème Back to the Kitchen à un graphique Plotly.

    Args:
        fig: Figure Plotly à thématiser
        title: Titre optionnel du graphique

    Returns:
        Figure Plotly avec le thème appliqué
    """
    fig.update_layout(
        # Arrière-plans transparents
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        # Police et couleurs de texte
        font=dict(color=colors.TEXT_PRIMARY, family="Inter, sans-serif", size=12),
        # Titre du graphique
        title=(
            dict(
                text=title,
                font=dict(color=colors.PRIMARY, size=16, family="Michroma, sans-serif"),
                x=0.5,
                xanchor="center",
            )
            if title
            else None
        ),
        # Grille et axes
        xaxis=dict(
            showgrid=True,
            gridcolor="#444444",
            gridwidth=1,
            tickfont=dict(color=colors.TEXT_PRIMARY, size=12),
            title=dict(font=dict(color=colors.TEXT_SECONDARY, size=13)),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#444444",
            gridwidth=1,
            tickfont=dict(color=colors.TEXT_PRIMARY, size=12),
            title=dict(font=dict(color=colors.TEXT_SECONDARY, size=13)),
        ),
        # Légende
        legend=dict(
            bgcolor="rgba(42, 42, 42, 0.8)",
            bordercolor="#666666",
            borderwidth=1,
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        # Hover label
        hoverlabel=dict(
            bgcolor=colors.BACKGROUND_CARD,
            font_size=12,
            font_family="Inter, sans-serif",
            font_color=colors.TEXT_WHITE,
            bordercolor=colors.PRIMARY,
        ),
        # Marges
        margin=dict(l=60, r=40, t=60, b=60),
        # Mode bar
        modebar=dict(
            bgcolor="rgba(0,0,0,0)",
            color=colors.TEXT_SECONDARY,
            activecolor=colors.PRIMARY,
        ),
    )

    return fig


def get_bar_color():
    """Retourne la couleur principale pour les barres.

    Returns:
        Couleur hex pour les barres d'histogramme
    """
    return colors.CHART_COLORS[0]


def get_line_colors():
    """Retourne la liste de couleurs pour les lignes multiples.

    Returns:
        Liste de couleurs hex
    """
    return colors.CHART_COLORS


def get_scatter_color():
    """Retourne la couleur pour les scatter plots.

    Returns:
        Couleur hex pour les points de scatter
    """
    return colors.CHART_COLORS[1]  # Bleu clair


def get_reference_line_color():
    """Retourne la couleur pour les lignes de référence (régression, etc).

    Returns:
        Couleur hex pour les lignes de référence
    """
    return colors.ERROR  # Rouge pour les lignes de référence


def apply_subplot_theme(fig, num_rows=1, num_cols=2):
    """Applique le thème à un graphique avec subplots.

    Args:
        fig: Figure Plotly avec subplots
        num_rows: Nombre de lignes de subplots
        num_cols: Nombre de colonnes de subplots

    Returns:
        Figure Plotly avec le thème appliqué
    """
    # Applique le thème global
    apply_chart_theme(fig)

    # Applique le thème à chaque subplot
    for row in range(1, num_rows + 1):
        for col in range(1, num_cols + 1):
            fig.update_xaxes(
                showgrid=True,
                gridcolor="#444444",
                gridwidth=1,
                tickfont=dict(color=colors.TEXT_PRIMARY, size=12),
                title_font=dict(color=colors.TEXT_SECONDARY, size=13),
                row=row,
                col=col,
            )
            fig.update_yaxes(
                showgrid=True,
                gridcolor="#444444",
                gridwidth=1,
                tickfont=dict(color=colors.TEXT_PRIMARY, size=12),
                title_font=dict(color=colors.TEXT_SECONDARY, size=13),
                row=row,
                col=col,
            )

    # Titres de subplots en orange
    fig.update_annotations(
        font=dict(color=colors.PRIMARY, size=13, family="Inter, sans-serif")
    )

    return fig
