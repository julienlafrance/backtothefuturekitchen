"""Page Streamlit pour visualisations innovantes.

Cette page présente des visualisations spectaculaires utilisant Altair et Plotly avancé
pour offrir des insights uniques et une expérience "WHAOH".
"""

import streamlit as st
import pandas as pd
import duckdb
from configparser import ConfigParser
from pathlib import Path

from mangetamain_analytics.data.cached_loaders import get_recipes_clean
from mangetamain_analytics.visualization.innovative_charts import (
    create_linked_brushing_dashboard,
    create_calendar_heatmap,
    create_sunburst_hierarchy,
    create_ridgeline_plot,
    create_stream_graph,
    create_parallel_coordinates,
    create_radar_chart_comparison,
)

st.set_page_config(
    page_title="Visualisations Innovantes",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=3600)
def load_recipes_with_ratings():
    """Charge recettes avec ratings agrégés par recette via DuckDB."""
    # Charger recettes
    recipes = get_recipes_clean()
    if hasattr(recipes, "to_pandas"):
        recipes = recipes.to_pandas()

    # Charger les credentials S3
    try:
        config = ConfigParser()
        cred_file = '/home/julien/code/mangetamain/000_dev/96_keys/credentials'
        config.read(cred_file)

        creds = {
            'aws_access_key_id': config['s3fast']['aws_access_key_id'],
            'aws_secret_access_key': config['s3fast']['aws_secret_access_key'],
            'endpoint_url': config['s3fast']['endpoint_url'],
            'region_name': config['s3fast']['region'],
            'bucket': config['s3fast']['bucket']
        }
    except Exception as e:
        st.error(f"Impossible de charger les credentials S3: {e}")
        # Retourner les recettes sans ratings
        df = recipes.copy()
        df["rating"] = 3.0
        df["n_ratings"] = 0
        df["n_users"] = 0
        return df

    # Connexion DuckDB pour lire les interactions depuis S3
    conn = duckdb.connect()
    conn.execute("INSTALL httpfs")
    conn.execute("LOAD httpfs")

    # Créer le secret S3
    conn.execute(f"""
        CREATE SECRET s3_secret (
            TYPE S3,
            KEY_ID '{creds['aws_access_key_id']}',
            SECRET '{creds['aws_secret_access_key']}',
            ENDPOINT '{creds['endpoint_url'].replace('http://', '')}',
            REGION '{creds['region_name']}',
            URL_STYLE 'path',
            USE_SSL false
        )
    """)

    # Charger et agréger les ratings depuis S3
    try:
        ratings_agg = conn.execute("""
            SELECT
                recipe_id as id,
                AVG(rating) as rating,
                COUNT(*) as n_ratings,
                COUNT(DISTINCT user_id) as n_users
            FROM 's3://mangetamain/final_interactions.parquet'
            GROUP BY recipe_id
        """).fetchdf()
    except Exception as e:
        st.warning(f"Impossible de charger les ratings: {e}")
        ratings_agg = pd.DataFrame(columns=['id', 'rating', 'n_ratings', 'n_users'])
    finally:
        conn.close()

    # Jointure
    df = recipes.merge(ratings_agg, on="id", how="left")

    # Remplir NaN pour recettes sans ratings
    df["rating"] = df["rating"].fillna(3.0)
    df["n_ratings"] = df["n_ratings"].fillna(0).astype(int)
    df["n_users"] = df["n_users"].fillna(0).astype(int)

    # Convertir la colonne tags en string pour éviter les problèmes de hashing
    if "tags" in df.columns:
        df["tags"] = df["tags"].astype(str)

    # Ajouter colonnes season si manquante
    if "season" not in df.columns and "submitted" in df.columns:
        df["month"] = pd.to_datetime(df["submitted"]).dt.month
        df["season"] = df["month"].map(
            {
                12: "Hiver",
                1: "Hiver",
                2: "Hiver",
                3: "Printemps",
                4: "Printemps",
                5: "Printemps",
                6: "Été",
                7: "Été",
                8: "Été",
                9: "Automne",
                10: "Automne",
                11: "Automne",
            }
        )

    # Ajouter complexity_category si manquante
    if "complexity_category" not in df.columns and "n_steps" in df.columns:
        df["complexity_category"] = pd.cut(
            df["n_steps"], bins=[0, 5, 10, 100], labels=["Facile", "Moyen", "Complexe"]
        )

    return df


@st.cache_data(ttl=3600)
def load_and_prepare_data():
    """Charge et prépare les données pour visualisations innovantes."""
    df = get_recipes_clean()

    # Convertir Polars vers pandas pour compatibilité avec Altair/Plotly
    if hasattr(df, "to_pandas"):
        df = df.to_pandas()

    # Ajouter colonnes calculées si manquantes
    if "season" not in df.columns and "submitted" in df.columns:
        df["month"] = pd.to_datetime(df["submitted"]).dt.month
        df["season"] = df["month"].map(
            {
                12: "Hiver",
                1: "Hiver",
                2: "Hiver",
                3: "Printemps",
                4: "Printemps",
                5: "Printemps",
                6: "Été",
                7: "Été",
                8: "Été",
                9: "Automne",
                10: "Automne",
                11: "Automne",
            }
        )

    if "complexity_category" not in df.columns:
        if "n_steps" in df.columns:
            df["complexity_category"] = pd.cut(
                df["n_steps"],
                bins=[0, 5, 10, 100],
                labels=["Facile", "Moyen", "Complexe"],
            )

    # Calculer note moyenne si nécessaire
    if "rating" not in df.columns and "avg_rating" in df.columns:
        df["rating"] = df["avg_rating"]

    return df


@st.cache_data(ttl=3600)
def prepare_temporal_data(df):
    """Prépare données temporelles pour stream graph."""
    if "submitted" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["date"] = pd.to_datetime(df["submitted"])
    df["year_month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    # Catégoriser recettes
    if "tags" in df.columns:
        # Extraire catégorie dominante des tags
        def categorize_recipe(tags):
            if tags is None or (isinstance(tags, float) and pd.isna(tags)):
                return "Autre"
            tags_str = str(tags).lower()
            if "dessert" in tags_str:
                return "Desserts"
            elif "main" in tags_str or "dish" in tags_str:
                return "Plats principaux"
            elif "appetizer" in tags_str:
                return "Entrées"
            elif "salad" in tags_str:
                return "Salades"
            elif "soup" in tags_str:
                return "Soupes"
            else:
                return "Autre"

        df["category"] = df["tags"].apply(categorize_recipe)
    else:
        df["category"] = "Recettes"

    # Agréger par mois et catégorie
    temporal = df.groupby(["year_month", "category"]).size().reset_index(name="count")
    temporal.columns = ["date", "category", "count"]

    return temporal


@st.cache_data(ttl=3600)
def prepare_seasonal_profiles(df):
    """Prépare profils saisonniers pour radar chart."""
    if "season" not in df.columns:
        return pd.DataFrame()

    # Filtrer les saisons valides
    df_with_season = df[df["season"].notna()].copy()
    if len(df_with_season) == 0:
        return pd.DataFrame()

    # Calculer max volumes pour normalisation
    season_counts = df_with_season["season"].value_counts()
    max_volume = season_counts.max() if len(season_counts) > 0 else 1

    # Calculer max popularity
    max_popularity = 1
    if "n_ratings" in df_with_season.columns:
        popularity_by_season = df_with_season.groupby("season")["n_ratings"].sum()
        max_popularity = popularity_by_season.max() if len(popularity_by_season) > 0 else 1

    profiles = []
    # Mapping saisons anglais -> français pour affichage
    season_mapping = {
        'Spring': 'Printemps',
        'Summer': 'Été',
        'Autumn': 'Automne',
        'Winter': 'Hiver'
    }

    for season_en, season_fr in season_mapping.items():
        season_data = df_with_season[df_with_season["season"] == season_en]

        if len(season_data) == 0:
            continue

        # Calculer métriques en filtrant les valeurs extrêmes (outliers)
        volume = len(season_data)

        # Durée: filtrer valeurs < 5 min ou > 180 min (3h)
        if "minutes" in season_data.columns and season_data["minutes"].notna().any():
            duration_filtered = season_data["minutes"][(season_data["minutes"] >= 5) & (season_data["minutes"] <= 180)]
            avg_duration = float(duration_filtered.mean()) if len(duration_filtered) > 0 else 30.0
        else:
            avg_duration = 30.0

        # Complexité: filtrer valeurs > 25 étapes
        if "n_steps" in season_data.columns and season_data["n_steps"].notna().any():
            steps_filtered = season_data["n_steps"][season_data["n_steps"] <= 25]
            avg_complexity = float(steps_filtered.mean()) if len(steps_filtered) > 0 else 7.0
        else:
            avg_complexity = 7.0

        # Ingrédients: filtrer valeurs < 2 ou > 25
        if "n_ingredients" in season_data.columns and season_data["n_ingredients"].notna().any():
            ingredients_filtered = season_data["n_ingredients"][(season_data["n_ingredients"] >= 2) & (season_data["n_ingredients"] <= 25)]
            avg_ingredients = float(ingredients_filtered.mean()) if len(ingredients_filtered) > 0 else 9.0
        else:
            avg_ingredients = 9.0

        avg_rating = float(season_data["rating"].mean()) if "rating" in season_data.columns and season_data["rating"].notna().any() else 4.0

        popularity = volume
        if "n_ratings" in season_data.columns:
            popularity = float(season_data["n_ratings"].sum())

        # Normaliser sur [0, 100] - ajuster échelles pour mieux couvrir le radar
        # Utiliser des valeurs max plus réalistes basées sur les moyennes attendues
        profiles.append(
            {
                "season": season_fr,
                "volume_norm": min(100, (volume / max_volume) * 100) if max_volume > 0 else 50,
                "duration_norm": min(100, (avg_duration / 60) * 100),  # Max 60 min au lieu de 120
                "complexity_norm": min(100, (avg_complexity / 12) * 100),  # Max 12 étapes au lieu de 20
                "ingredients_norm": min(100, (avg_ingredients / 12) * 100),  # Max 12 ingrédients au lieu de 20
                "rating_norm": (avg_rating / 5) * 100,
                "popularity_norm": min(100, (popularity / max_popularity) * 100) if max_popularity > 0 else 50,
            }
        )

    return pd.DataFrame(profiles)


def main():
    """Interface principale de la page."""
    st.title("🚀 Visualisations Innovantes")

    st.markdown(
        """
    Explorez les données avec des visualisations spectaculaires utilisant **Altair** et **Plotly avancé**.
    Ces graphiques offrent des interactions et insights impossibles avec des visualisations standard.
    """
    )

    # Chargement données
    with st.spinner("Chargement des données..."):
        df = load_recipes_with_ratings()

    # Filtres globaux dans sidebar
    with st.sidebar:
        st.header("⚙️ Filtres")

        # Filtre années
        if "submitted" in df.columns:
            years = sorted(pd.to_datetime(df["submitted"]).dt.year.unique())
            year_range = st.slider(
                "Plage d'années",
                min_value=int(min(years)),
                max_value=int(max(years)),
                value=(int(min(years)), int(max(years))),
            )

            df = df[
                (pd.to_datetime(df["submitted"]).dt.year >= year_range[0])
                & (pd.to_datetime(df["submitted"]).dt.year <= year_range[1])
            ]

        # Échantillonage pour performance
        sample_size = st.number_input(
            "Taille échantillon (pour performance)",
            min_value=1000,
            max_value=len(df),
            value=min(10000, len(df)),
            step=1000,
            help="Réduire pour améliorer performance sur graphiques lourds",
        )

        df_sample = df.sample(n=min(sample_size, len(df)), random_state=42)

        st.metric("📊 Recettes affichées", f"{len(df_sample):,}")

    # Tabs pour organiser visualisations
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🔗 Interactif Altair",
            "📊 Plotly Avancé",
            "🌊 Flux Temporels",
            "🎯 Multi-Dimensions",
        ]
    )

    with tab1:
        st.header("🔗 Visualisations Interactives Altair")

        st.subheader("📍 Linked Brushing Dashboard")
        st.markdown(
            """
        **Cliquez-glissez** sur le graphique du haut pour filtrer automatiquement l'histogramme.
        Découvrez les corrélations entre durée, note et nombre d'étapes !
        """
        )

        if all(
            col in df_sample.columns
            for col in ["minutes", "rating", "n_steps", "season"]
        ):
            # Nettoyer données
            df_viz = df_sample[
                ["minutes", "rating", "n_steps", "season", "name"]
            ].copy()
            df_viz = df_viz.dropna()
            df_viz = df_viz[
                (df_viz["minutes"] > 0)
                & (df_viz["minutes"] < 300)
                & (df_viz["rating"] >= 1)
                & (df_viz["rating"] <= 5)
            ]

            chart = create_linked_brushing_dashboard(df_viz)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Colonnes nécessaires manquantes pour linked brushing")

        st.divider()

        st.subheader("🏔️ Ridgeline Plot - Distribution des Notes")
        st.markdown(
            "Style **Joy Division** montrant l'évolution de la distribution des notes année par année."
        )

        if "rating" in df_sample.columns and "submitted" in df.columns:
            df_ridge = df_sample[["rating", "submitted"]].copy()
            df_ridge["year"] = pd.to_datetime(df_ridge["submitted"]).dt.year
            df_ridge = df_ridge.dropna()

            # Limiter aux années avec assez de données
            year_counts = df_ridge["year"].value_counts()
            valid_years = year_counts[year_counts > 100].index
            df_ridge = df_ridge[df_ridge["year"].isin(valid_years)]

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
        st.markdown(
            "Visualisation style **GitHub contributions** de l'activité par jour."
        )

        if "submitted" in df.columns:
            year_to_viz = st.selectbox(
                "Sélectionner année",
                options=sorted(
                    pd.to_datetime(df["submitted"]).dt.year.unique(), reverse=True
                ),
            )

            df_cal = df[pd.to_datetime(df["submitted"]).dt.year == year_to_viz]

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

        if all(col in df_sample.columns for col in ["season", "complexity_category"]):
            df_sun = df_sample[["season", "complexity_category"]].copy()
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
        st.markdown(
            "Flux temporel montrant comment les catégories de recettes évoluent."
        )

        temporal_data = prepare_temporal_data(df)

        if len(temporal_data) > 0:
            fig = create_stream_graph(temporal_data)
            st.plotly_chart(fig, use_container_width=True)

            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "📆 Période couverte",
                    f"{temporal_data['date'].min().strftime('%Y')} - "
                    f"{temporal_data['date'].max().strftime('%Y')}",
                )
            with col2:
                st.metric("🏷️ Catégories", len(temporal_data["category"].unique()))
            with col3:
                st.metric("📊 Points temporels", len(temporal_data["date"].unique()))
        else:
            st.warning(
                "Impossible de créer le stream graph avec les données disponibles"
            )

    with tab4:
        st.header("🎯 Exploration Multi-Dimensions")

        st.subheader("🎯 Parallel Coordinates - Filtrage Multi-Critères")
        st.markdown(
            """
        **Glissez** les barres verticales pour filtrer interactivement sur plusieurs dimensions.
        Trouvez les recettes qui matchent exactement vos critères !
        """
        )

        if all(col in df_sample.columns for col in ["minutes", "n_steps", "rating"]):
            df_par = df_sample[
                ["minutes", "n_steps", "n_ingredients", "rating", "season"]
            ].copy()
            df_par = df_par.dropna()

            if len(df_par) > 5000:
                st.info(
                    f"📊 Échantillon de 5000 recettes pour performance (total: {len(df_par):,})"
                )
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
                st.markdown(
                    """
                - **Volume**: Nombre relatif de recettes
                - **Durée moy.**: Temps de préparation moyen
                - **Complexité**: Nombre moyen d'étapes
                - **Ingrédients**: Nombre moyen d'ingrédients
                - **Note**: Note moyenne normalisée
                - **Popularité**: Volume d'interactions

                Plus la zone est grande, plus la saison est marquée sur cette dimension.
                """
                )
        else:
            st.warning("Impossible de créer les profils saisonniers")

    # Footer
    st.divider()
    st.caption(
        """
    🚀 Visualisations créées avec **Altair** (grammaire Vega-Lite) et **Plotly**
    pour une expérience interactive maximale.
    """
    )


if __name__ == "__main__":
    main()
