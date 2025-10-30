"""Visualisations innovantes utilisant Altair et Plotly avancé.

Ce module contient des fonctions pour créer des visualisations spectaculaires
qui vont au-delà des graphiques standard pour offrir des insights uniques.
"""

import altair as alt
import pandas as pd
import plotly.graph_objects as go
from mangetamain_analytics.utils.color_theme import ColorTheme


def create_linked_brushing_dashboard(df: pd.DataFrame) -> alt.Chart:
    """
    Crée un dashboard Altair avec sélections inter-graphiques synchronisées.
    Copie exacte de l'exemple officiel Altair adapted to our data.

    Args:
        df: DataFrame avec colonnes 'minutes', 'rating', 'n_steps', 'season'

    Returns:
        Chart Altair composé avec linked brushing
    """
    # Exactly from official example
    brush = alt.selection_interval()

    # Base scatter plot
    points = alt.Chart(df).mark_point(size=60, opacity=0.8).encode(
        x=alt.X('minutes:Q', title='Durée (min)'),
        y=alt.Y('rating:Q', title='Note moyenne'),
        color=alt.when(brush).then("season").otherwise(alt.ColorValue("gray")),
        tooltip=['name', 'minutes', 'rating', 'season']
    ).add_params(brush).properties(
        width=500,
        height=400,
        title='Cliquez-glissez pour sélectionner'
    )

    # Histogram with filter
    bars = alt.Chart(df).mark_bar().encode(
        x=alt.X('rating:Q', bin=True),
        y='count()',
        color=alt.value('#FF8C00')
    ).transform_filter(brush).properties(
        width=500,
        height=150
    )

    return points & bars


def create_calendar_heatmap(df: pd.DataFrame, year: int = 2018) -> go.Figure:
    """
    Crée une heatmap calendrier style GitHub contributions.

    Args:
        df: DataFrame avec colonnes 'submitted', 'n_recipes' ou similaire
        year: Année à visualiser

    Returns:
        Figure Plotly heatmap calendrier
    """
    # Filtrer sur l'année
    df_year = df[df['submitted'].dt.year == year].copy()

    # Agréger par jour
    daily = df_year.groupby(df_year['submitted'].dt.date).size().reset_index()
    daily.columns = ['date', 'count']
    daily['date'] = pd.to_datetime(daily['date'])

    # Créer numéro de semaine unique pour l'année (évite duplicates)
    # Utiliser semaine de l'année basée sur le 1er janvier
    daily['week'] = ((daily['date'] - pd.Timestamp(f'{year}-01-01')).dt.days // 7) + 1
    daily['day_of_week'] = daily['date'].dt.dayofweek

    # Agréger les doublons avant pivot (en cas de semaines se chevauchant)
    daily_agg = daily.groupby(['day_of_week', 'week'])['count'].sum().reset_index()

    # Pivot pour heatmap
    heatmap_data = daily_agg.pivot(index='day_of_week', columns='week', values='count')
    heatmap_data = heatmap_data.fillna(0)

    fig = go.Figure(go.Heatmap(
        z=heatmap_data.values,
        x=list(range(1, 54)),
        y=['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        colorscale=[
            [0, '#EAEDF0'],
            [0.2, '#9BE9A8'],
            [0.4, '#40C463'],
            [0.6, '#30A14E'],
            [1, '#216E39']
        ],
        showscale=True,
        hovertemplate='Semaine %{x}<br>%{y}<br>%{z} recettes<extra></extra>',
        colorbar=dict(
            title=dict(text="Recettes", side="right"),
            tickmode="linear",
            tick0=0,
            dtick=10
        )
    ))

    fig.update_layout(
        title=f"📅 Activité quotidienne - {year}",
        xaxis=dict(
            title="Semaine de l'année",
            side="bottom",
            gridcolor='#333333'
        ),
        yaxis=dict(
            title="",
            gridcolor='#333333'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=ColorTheme.TEXT_PRIMARY),
        height=300,
        margin=dict(l=80, r=80, t=80, b=60)
    )

    return fig


def create_sunburst_hierarchy(df: pd.DataFrame) -> go.Figure:
    """
    Crée un sunburst interactif multi-niveaux.

    Hiérarchie: Saison → Difficulté → Top ingrédients
    Cliquer pour zoomer dans chaque niveau.

    Args:
        df: DataFrame avec 'season', 'complexity_category', 'top_ingredient'

    Returns:
        Figure Plotly sunburst
    """
    # Créer hiérarchie
    hierarchy = df.groupby(['season', 'complexity_category']).size().reset_index(name='count')

    # Construire listes pour sunburst
    labels = ['Toutes recettes']
    parents = ['']
    values = [len(df)]
    colors_list = ['#888888']

    # Niveau 1: Saisons
    for season in df['season'].unique():
        if pd.notna(season):
            count = len(df[df['season'] == season])
            labels.append(season)
            parents.append('Toutes recettes')
            values.append(count)
            colors_list.append(ColorTheme.get_seasonal_color(season))

    # Niveau 2: Complexité par saison
    for _, row in hierarchy.iterrows():
        if pd.notna(row['season']) and pd.notna(row['complexity_category']):
            label = f"{row['complexity_category']}"
            labels.append(label)
            parents.append(row['season'])
            values.append(row['count'])
            # Couleur basée sur complexité
            if 'Facile' in str(row['complexity_category']):
                colors_list.append('#9BE9A8')
            elif 'Moyen' in str(row['complexity_category']):
                colors_list.append('#FFC107')
            else:
                colors_list.append('#DC3545')

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(
            colors=colors_list,
            line=dict(width=2, color='#1E1E1E')
        ),
        hovertemplate='<b>%{label}</b><br>%{value} recettes<br>%{percentParent}<extra></extra>',
        textfont=dict(size=14, color='white')
    ))

    fig.update_layout(
        title="🌻 Hiérarchie Saisons → Complexité",
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=ColorTheme.TEXT_PRIMARY),
        height=600
    )

    return fig


def create_ridgeline_plot(df: pd.DataFrame) -> alt.Chart:
    """
    Crée un ridgeline plot (Joy Division style) pour distributions temporelles.

    Args:
        df: DataFrame avec 'year', 'rating' ou 'minutes'

    Returns:
        Chart Altair ridgeline
    """
    # S'assurer qu'on a les années
    df = df.copy()

    # Créer le ridgeline
    chart = alt.Chart(df).transform_density(
        'rating',
        as_=['rating', 'density'],
        extent=[1, 5],
        groupby=['year']
    ).mark_area(
        interpolate='monotone',
        fillOpacity=0.7,
        stroke=ColorTheme.TEXT_PRIMARY,
        strokeWidth=1.5
    ).encode(
        x=alt.X('rating:Q', title='Note'),
        y=alt.Y(
            'density:Q',
            scale=alt.Scale(range=[50, 0]),
            axis=None
        ),
        color=alt.Color(
            'year:O',
            scale=alt.Scale(scheme='viridis'),
            legend=alt.Legend(title="Année")
        ),
        row=alt.Row(
            'year:O',
            header=alt.Header(
                labelAngle=0,
                labelAlign='left',
                labelFontSize=12
            ),
            spacing=0
        ),
        tooltip=[
            alt.Tooltip('year:O', title='Année'),
            alt.Tooltip('rating:Q', title='Note', format='.1f'),
            alt.Tooltip('density:Q', title='Densité', format='.3f')
        ]
    ).properties(
        height=60,
        width=600,
        title='📊 Évolution distribution des notes par année'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    )

    return chart


def create_stream_graph(df: pd.DataFrame) -> go.Figure:
    """
    Crée un stream graph animé pour flux temporels par catégorie.

    Args:
        df: DataFrame avec 'date', 'category', 'count'

    Returns:
        Figure Plotly stream graph
    """
    # Préparer données
    pivot = df.pivot_table(
        index='date',
        columns='category',
        values='count',
        fill_value=0
    )

    fig = go.Figure()

    categories = pivot.columns
    colors = ColorTheme.CHART_COLORS[:len(categories)]

    for i, category in enumerate(categories):
        fig.add_trace(go.Scatter(
            x=pivot.index,
            y=pivot[category],
            mode='lines',
            name=category,
            stackgroup='one',
            fillcolor=colors[i],
            line=dict(width=0.5, color=colors[i]),
            hovertemplate=f'<b>{category}</b><br>%{{y}} recettes<br>%{{x}}<extra></extra>'
        ))

    fig.update_layout(
        title="🌊 Évolution des catégories de recettes",
        xaxis=dict(
            title="Date",
            gridcolor='#333333',
            type='date'
        ),
        yaxis=dict(
            title="Nombre de recettes",
            gridcolor='#333333'
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=ColorTheme.TEXT_PRIMARY),
        height=500
    )

    return fig


def create_parallel_coordinates(df: pd.DataFrame) -> go.Figure:
    """
    Crée un parallel coordinates plot pour exploration multi-critères.

    Args:
        df: DataFrame avec dimensions numériques

    Returns:
        Figure Plotly parallel coordinates
    """
    # Sélectionner colonnes pertinentes
    dimensions = []

    if 'minutes' in df.columns:
        dimensions.append(dict(
            label='Durée (min)',
            values=df['minutes'].clip(upper=120),  # Limiter outliers
            range=[0, 120]
        ))

    if 'n_steps' in df.columns:
        dimensions.append(dict(
            label='Étapes',
            values=df['n_steps'].clip(upper=20),
            range=[1, 20]
        ))

    if 'n_ingredients' in df.columns:
        dimensions.append(dict(
            label='Ingrédients',
            values=df['n_ingredients'].clip(upper=20),
            range=[3, 20]
        ))

    if 'rating' in df.columns:
        dimensions.append(dict(
            label='Note',
            values=df['rating'],
            range=[1, 5]
        ))

    # Encoder saison si présente
    if 'season' in df.columns:
        season_map = {
            'Printemps': 0, 'Été': 1, 'Automne': 2, 'Hiver': 3
        }
        df['season_encoded'] = df['season'].map(season_map).fillna(-1)
        dimensions.append(dict(
            label='Saison',
            values=df['season_encoded'],
            tickvals=[0, 1, 2, 3],
            ticktext=['Printemps', 'Été', 'Automne', 'Hiver'],
            range=[-0.5, 3.5]
        ))

    fig = go.Figure(go.Parcoords(
        line=dict(
            color=df['rating'] if 'rating' in df.columns else df.index,
            colorscale='Viridis',
            showscale=True,
            cmin=1,
            cmax=5,
            colorbar=dict(title="Note")
        ),
        dimensions=dimensions
    ))

    fig.update_layout(
        title="🎯 Exploration Multi-Critères (glisser pour filtrer)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=ColorTheme.TEXT_PRIMARY, size=12),
        height=600,
        margin=dict(l=150, r=150, t=80, b=60)
    )

    return fig


def create_radar_chart_comparison(df: pd.DataFrame) -> go.Figure:
    """
    Crée un radar chart comparant profils saisonniers.

    Args:
        df: DataFrame agrégé par saison avec métriques normalisées

    Returns:
        Figure Plotly radar chart
    """
    fig = go.Figure()

    categories = ['Volume', 'Durée moy.', 'Complexité',
                  'Ingrédients', 'Note', 'Popularité']

    seasons = ['Printemps', 'Été', 'Automne', 'Hiver']

    for season in seasons:
        if season in df['season'].values:
            season_data = df[df['season'] == season].iloc[0]

            # Normaliser les valeurs sur [0, 100]
            values = [
                season_data.get('volume_norm', 50),
                season_data.get('duration_norm', 50),
                season_data.get('complexity_norm', 50),
                season_data.get('ingredients_norm', 50),
                season_data.get('rating_norm', 50),
                season_data.get('popularity_norm', 50)
            ]

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=season,
                line_color=ColorTheme.get_seasonal_color(season),
                opacity=0.6,
                hovertemplate=f'<b>{season}</b><br>%{{theta}}: %{{r:.1f}}<extra></extra>'
            ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='#444444'
            ),
            angularaxis=dict(
                gridcolor='#444444'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        title="📊 Profils Saisonniers Comparés",
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=ColorTheme.TEXT_PRIMARY),
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )

    return fig
