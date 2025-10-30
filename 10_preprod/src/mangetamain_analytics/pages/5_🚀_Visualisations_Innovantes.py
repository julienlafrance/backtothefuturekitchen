"""Page Streamlit pour visualisations innovantes.

Cette page présente des visualisations spectaculaires utilisant Altair et Plotly avancé
pour offrir des insights uniques et une expérience "WHAOH".
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from mangetamain_analytics.data.cached_loaders import get_recipes_clean
from mangetamain_analytics.visualization.innovative_charts import (
    create_linked_brushing_dashboard,
    create_calendar_heatmap,
    create_sunburst_hierarchy,
    create_ridgeline_plot,
    create_stream_graph,
    create_parallel_coordinates,
    create_radar_chart_comparison
)
from mangetamain_analytics.utils.color_theme import ColorTheme

st.set_page_config(
    page_title="Visualisations Innovantes",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=3600)
def load_and_prepare_data():
    """Charge et prépare les données pour visualisations innovantes."""
    df = get_recipes_clean()

    # Convertir Polars vers pandas pour compatibilité avec Altair/Plotly
    if hasattr(df, 'to_pandas'):
        df = df.to_pandas()

    # Ajouter colonnes calculées si manquantes
    if 'season' not in df.columns and 'submitted' in df.columns:
        df['month'] = pd.to_datetime(df['submitted']).dt.month
        df['season'] = df['month'].map({
            12: 'Hiver', 1: 'Hiver', 2: 'Hiver',
            3: 'Printemps', 4: 'Printemps', 5: 'Printemps',
            6: 'Été', 7: 'Été', 8: 'Été',
            9: 'Automne', 10: 'Automne', 11: 'Automne'
        })

    if 'complexity_category' not in df.columns:
        if 'n_steps' in df.columns:
            df['complexity_category'] = pd.cut(
                df['n_steps'],
                bins=[0, 5, 10, 100],
                labels=['Facile', 'Moyen', 'Complexe']
            )

    # Calculer note moyenne si nécessaire
    if 'rating' not in df.columns and 'avg_rating' in df.columns:
        df['rating'] = df['avg_rating']

    return df


@st.cache_data(ttl=3600)
def prepare_temporal_data(df):
    """Prépare données temporelles pour stream graph."""
    if 'submitted' not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df['date'] = pd.to_datetime(df['submitted'])
    df['year_month'] = df['date'].dt.to_period('M').dt.to_timestamp()

    # Catégoriser recettes
    if 'tags' in df.columns:
        # Extraire catégorie dominante des tags
        def categorize_recipe(tags):
            if tags is None or (isinstance(tags, float) and pd.isna(tags)):
                return 'Autre'
            tags_str = str(tags).lower()
            if 'dessert' in tags_str:
                return 'Desserts'
            elif 'main' in tags_str or 'dish' in tags_str:
                return 'Plats principaux'
            elif 'appetizer' in tags_str:
                return 'Entrées'
            elif 'salad' in tags_str:
                return 'Salades'
            elif 'soup' in tags_str:
                return 'Soupes'
            else:
                return 'Autre'

        df['category'] = df['tags'].apply(categorize_recipe)
    else:
        df['category'] = 'Recettes'

    # Agréger par mois et catégorie
    temporal = df.groupby(['year_month', 'category']).size().reset_index(name='count')
    temporal.columns = ['date', 'category', 'count']

    return temporal


@st.cache_data(ttl=3600)
def prepare_seasonal_profiles(df):
    """Prépare profils saisonniers pour radar chart."""
    if 'season' not in df.columns:
        return pd.DataFrame()

    profiles = []
    for season in ['Printemps', 'Été', 'Automne', 'Hiver']:
        season_data = df[df['season'] == season]

        if len(season_data) == 0:
            continue

        # Calculer métriques
        volume = len(season_data)
        avg_duration = season_data['minutes'].mean() if 'minutes' in season_data else 30
        avg_complexity = season_data['n_steps'].mean() if 'n_steps' in season_data else 7
        avg_ingredients = season_data['n_ingredients'].mean() if 'n_ingredients' in season_data else 9
        avg_rating = season_data['rating'].mean() if 'rating' in season_data else 4.0
        popularity = season_data['n_interactions'].sum() if 'n_interactions' in season_data else volume

        # Normaliser sur [0, 100]
        profiles.append({
            'season': season,
            'volume_norm': min(100, (volume / df['season'].value_counts().max()) * 100),
            'duration_norm': min(100, (avg_duration / 120) * 100),
            'complexity_norm': min(100, (avg_complexity / 20) * 100),
            'ingredients_norm': min(100, (avg_ingredients / 20) * 100),
            'rating_norm': (avg_rating / 5) * 100,
            'popularity_norm': min(100, (popularity / df.groupby('season')['n_interactions'].sum().max()) * 100) if 'n_interactions' in df else 50
        })

    return pd.DataFrame(profiles)


def main():
    """Interface principale de la page."""
    st.title("🚀 Visualisations Innovantes")

    st.markdown("""
    Explorez les données avec des visualisations spectaculaires utilisant **Altair** et **Plotly avancé**.
    Ces graphiques offrent des interactions et insights impossibles avec des visualisations standard.
    """)

    # Chargement données
    with st.spinner("Chargement des données..."):
        df = load_and_prepare_data()

    # Filtres globaux dans sidebar
    with st.sidebar:
        st.header("⚙️ Filtres")

        # Filtre années
        if 'submitted' in df.columns:
            years = sorted(pd.to_datetime(df['submitted']).dt.year.unique())
            year_range = st.slider(
                "Plage d'années",
                min_value=int(min(years)),
                max_value=int(max(years)),
                value=(int(min(years)), int(max(years)))
            )

            df = df[
                (pd.to_datetime(df['submitted']).dt.year >= year_range[0]) &
                (pd.to_datetime(df['submitted']).dt.year <= year_range[1])
            ]

        # Échantillonage pour performance
        sample_size = st.number_input(
            "Taille échantillon (pour performance)",
            min_value=1000,
            max_value=len(df),
            value=min(10000, len(df)),
            step=1000,
            help="Réduire pour améliorer performance sur graphiques lourds"
        )

        df_sample = df.sample(n=min(sample_size, len(df)), random_state=42)

        st.metric("📊 Recettes affichées", f"{len(df_sample):,}")

    # Tabs pour organiser visualisations
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔗 Interactif Altair",
        "📊 Plotly Avancé",
        "🌊 Flux Temporels",
        "🎯 Multi-Dimensions"
    ])

    with tab1:
        st.header("🔗 Visualisations Interactives Altair")

        st.subheader("📍 Linked Brushing Dashboard")
        st.markdown("""
        **Cliquez-glissez** sur le graphique du haut pour filtrer automatiquement l'histogramme.
        Découvrez les corrélations entre durée, note et nombre d'étapes !
        """)

        if all(col in df_sample.columns for col in ['minutes', 'rating', 'n_steps', 'season']):
            # Nettoyer données
            df_viz = df_sample[['minutes', 'rating', 'n_steps', 'season', 'name']].copy()
            df_viz = df_viz.dropna()
            df_viz = df_viz[
                (df_viz['minutes'] > 0) &
                (df_viz['minutes'] < 300) &
                (df_viz['rating'] >= 1) &
                (df_viz['rating'] <= 5)
            ]

            chart = create_linked_brushing_dashboard(df_viz)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Colonnes nécessaires manquantes pour linked brushing")

        st.divider()

        st.subheader("🏔️ Ridgeline Plot - Distribution des Notes")
        st.markdown("Style **Joy Division** montrant l'évolution de la distribution des notes année par année.")

        if 'rating' in df_sample.columns and 'submitted' in df.columns:
            df_ridge = df_sample[['rating', 'submitted']].copy()
            df_ridge['year'] = pd.to_datetime(df_ridge['submitted']).dt.year
            df_ridge = df_ridge.dropna()

            # Limiter aux années avec assez de données
            year_counts = df_ridge['year'].value_counts()
            valid_years = year_counts[year_counts > 100].index
            df_ridge = df_ridge[df_ridge['year'].isin(valid_years)]

            if len(df_ridge) > 0:
                chart = create_ridgeline_plot(df_ridge)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Pas assez de données pour le ridgeline plot")
        else:
            st.warning("Colonnes rating et submitted nécessaires")

    with tab2:
        st.header("📊 Plotly Avancé")

        st.subheader("📅 Calendar Heatmap - Activité Quotidienne")
        st.markdown("Visualisation style **GitHub contributions** de l'activité par jour.")

        if 'submitted' in df.columns:
            year_to_viz = st.selectbox(
                "Sélectionner année",
                options=sorted(pd.to_datetime(df['submitted']).dt.year.unique(), reverse=True)
            )

            df_cal = df[pd.to_datetime(df['submitted']).dt.year == year_to_viz]

            if len(df_cal) > 0:
                fig = create_calendar_heatmap(df_cal, year=year_to_viz)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Pas de données pour {year_to_viz}")
        else:
            st.warning("Colonne submitted nécessaire")

        st.divider()

        st.subheader("🌻 Sunburst - Hiérarchie Saisons → Complexité")
        st.markdown("**Cliquez** sur une section pour zoomer dans la hiérarchie.")

        if all(col in df_sample.columns for col in ['season', 'complexity_category']):
            df_sun = df_sample[['season', 'complexity_category']].copy()
            df_sun = df_sun.dropna()

            if len(df_sun) > 0:
                fig = create_sunburst_hierarchy(df_sun)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas assez de données pour sunburst")
        else:
            st.warning("Colonnes season et complexity_category nécessaires")

    with tab3:
        st.header("🌊 Flux Temporels")

        st.subheader("🌊 Stream Graph - Évolution des Catégories")
        st.markdown("Flux temporel montrant comment les catégories de recettes évoluent.")

        temporal_data = prepare_temporal_data(df)

        if len(temporal_data) > 0:
            fig = create_stream_graph(temporal_data)
            st.plotly_chart(fig, use_container_width=True)

            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📆 Période couverte",
                         f"{temporal_data['date'].min().strftime('%Y')} - {temporal_data['date'].max().strftime('%Y')}")
            with col2:
                st.metric("🏷️ Catégories", len(temporal_data['category'].unique()))
            with col3:
                st.metric("📊 Points temporels", len(temporal_data['date'].unique()))
        else:
            st.warning("Impossible de créer le stream graph avec les données disponibles")

    with tab4:
        st.header("🎯 Exploration Multi-Dimensions")

        st.subheader("🎯 Parallel Coordinates - Filtrage Multi-Critères")
        st.markdown("""
        **Glissez** les barres verticales pour filtrer interactivement sur plusieurs dimensions.
        Trouvez les recettes qui matchent exactement vos critères !
        """)

        if all(col in df_sample.columns for col in ['minutes', 'n_steps', 'rating']):
            df_par = df_sample[['minutes', 'n_steps', 'n_ingredients', 'rating', 'season']].copy()
            df_par = df_par.dropna()

            if len(df_par) > 5000:
                st.info(f"📊 Échantillon de 5000 recettes pour performance (total: {len(df_par):,})")
                df_par = df_par.sample(n=5000, random_state=42)

            if len(df_par) > 0:
                fig = create_parallel_coordinates(df_par)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas assez de données pour parallel coordinates")
        else:
            st.warning("Colonnes numériques nécessaires manquantes")

        st.divider()

        st.subheader("📊 Radar Chart - Profils Saisonniers")
        st.markdown("Comparaison visuelle des profils de recettes par saison.")

        profiles = prepare_seasonal_profiles(df)

        if len(profiles) > 0:
            fig = create_radar_chart_comparison(profiles)
            st.plotly_chart(fig, use_container_width=True)

            # Explication
            with st.expander("ℹ️ Interprétation du radar chart"):
                st.markdown("""
                - **Volume**: Nombre relatif de recettes
                - **Durée moy.**: Temps de préparation moyen
                - **Complexité**: Nombre moyen d'étapes
                - **Ingrédients**: Nombre moyen d'ingrédients
                - **Note**: Note moyenne normalisée
                - **Popularité**: Volume d'interactions

                Plus la zone est grande, plus la saison est marquée sur cette dimension.
                """)
        else:
            st.warning("Impossible de créer les profils saisonniers")

    # Footer
    st.divider()
    st.caption("""
    🚀 Visualisations créées avec **Altair** (grammaire Vega-Lite) et **Plotly**
    pour une expérience interactive maximale.
    """)


if __name__ == "__main__":
    main()
