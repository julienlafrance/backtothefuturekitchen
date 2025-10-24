"""Streamlit application for Mangetamain Analytics - Updated Version.

This module provides the main interface for analyzing Food.com dataset
using DuckDB as the backend database with all imported tables.
"""

import streamlit as st
import pandas as pd
import duckdb
from pathlib import Path
from loguru import logger
import sys
import os
import plotly.express as px
from visualization.custom_charts import (
    create_correlation_heatmap,
    create_distribution_plot,
    create_time_series_plot,
    create_custom_scatter_plot,
)
from visualization.analyse_trendlines_v2 import (
    analyse_trendline_volume,
    analyse_trendline_duree,
    analyse_trendline_complexite,
    analyse_trendline_nutrition,
    analyse_trendline_ingredients,
    analyse_trendline_tags,
)
from utils import colors


def detect_environment():
    """Detect if running in PREPROD or PROD environment."""
    # Priority 1: Check environment variable (Docker or manual set)
    app_env = os.getenv("APP_ENV")
    if app_env:
        return app_env.upper()

    # Priority 2: Check if we are in a Docker container
    if Path("/.dockerenv").exists():
        return "PROD (Docker)"

    # Priority 3: Check the current working directory path
    current_path = str(Path.cwd())
    if "10_preprod" in current_path:
        return "PREPROD"
    elif "20_prod" in current_path:
        return "PROD"
    else:
        return "UNKNOWN"


def display_environment_badge():
    """Display environment badge in sidebar."""
    env = detect_environment()

    if "PREPROD" in env:
        badge_config = colors.ENV_PREPROD
        label = "PREPROD"
    elif "PROD" in env:
        badge_config = colors.ENV_PROD
        label = "PRODUCTION"
    else:
        return

    st.sidebar.markdown(
        f"""
        <div style="background-color: {badge_config['bg']}; padding: 8px; border-radius: 8px; text-align: center; margin-top: 15px;">
            <small style="color: {badge_config['text']}; margin: 0; font-weight: bold; font-size: 11px;">{badge_config['icon']} {label}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Configure Loguru logger (only once)
if not any(
    "logs/mangetamain" in str(handler) for handler in logger._core.handlers.values()
):
    logger.remove()

    logger.add(
        "logs/mangetamain_app.log",
        rotation="1 MB",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    )

    logger.add(
        "logs/mangetamain_errors.log",
        rotation="1 MB",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    )

    logger.add(sys.stderr, level="DEBUG")

# Page configuration
st.set_page_config(page_title="Mangetamain Analytics", page_icon="🍽️", layout="wide")


def get_db_connection():
    """Establish connection to the DuckDB database."""
    db_path = "data/mangetamain.duckdb"

    if Path(db_path).exists():
        try:
            conn = duckdb.connect(db_path)

            file_size = Path(db_path).stat().st_size / (1024 * 1024)
            tables = conn.execute("SHOW TABLES").fetchall()

            logger.info(f"✅ DuckDB connection established - File: {db_path}")
            logger.info(f"📊 Database size: {file_size:.1f} MB")
            logger.info(f"🗂️ Tables found: {len(tables)} - {[t[0] for t in tables]}")

            return conn

        except Exception as e:
            logger.error(f"❌ Failed to connect to DuckDB: {e}")
            return None
    else:
        logger.error(f"❌ DuckDB file not found: {db_path}")
        return None


def display_database_info(conn):
    """Display comprehensive database information in sidebar."""
    # This function is now empty - database info removed from sidebar
    pass


def create_tables_overview(conn):
    """Create interactive overview of all tables."""
    st.subheader("📊 Vue d'ensemble des tables")

    # Get table statistics
    tables = conn.execute("SHOW TABLES").fetchall()
    table_stats = []

    for (table_name,) in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        columns = conn.execute(f"DESCRIBE {table_name}").fetchall()

        # Categorize tables
        if table_name.startswith("RAW_"):
            category = "Données brutes"
        elif table_name.startswith("PP_"):
            category = "Données préprocessées"
        elif "interactions_" in table_name:
            category = "Datasets ML"
        else:
            category = "Autres"

        table_stats.append(
            {
                "Table": table_name,
                "Lignes": count,
                "Colonnes": len(columns),
                "Catégorie": category,
            }
        )

    df_stats = pd.DataFrame(table_stats)

    # Interactive bar chart with Plotly
    fig = px.bar(
        df_stats,
        x="Table",
        y="Lignes",
        color="Catégorie",
        title="Nombre de lignes par table",
        hover_data=["Colonnes"],
    )

    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Display as table
    st.dataframe(df_stats, use_container_width=True)


def create_rating_analysis(conn):
    """Enhanced rating distribution analysis."""
    st.subheader("⭐ Analyse des notes")

    # Try different interaction tables
    rating_tables = [
        "RAW_interactions",
        "interactions_train",
        "interactions_test",
        "interactions_validation",
    ]

    for table in rating_tables:
        try:
            # Check if table exists and has rating column
            schema = conn.execute(f"DESCRIBE {table}").fetchall()
            column_names = [col[0] for col in schema]

            if "rating" in column_names:
                st.write(f"📊 Analyse des notes - Table: **{table}**")

                ratings_df = conn.execute(
                    f"""
                    SELECT rating, COUNT(*) as count
                    FROM {table}
                    WHERE rating IS NOT NULL
                    GROUP BY rating
                    ORDER BY rating
                """
                ).fetchdf()

                if not ratings_df.empty:
                    # Create interactive pie chart
                    fig = px.pie(
                        ratings_df,
                        values="count",
                        names="rating",
                        title=f"Distribution des notes - {table}",
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Statistics
                    total_ratings = ratings_df["count"].sum()
                    avg_rating = (
                        ratings_df["rating"] * ratings_df["count"]
                    ).sum() / total_ratings

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total évaluations", f"{total_ratings:,}")
                    with col2:
                        st.metric("Note moyenne", f"{avg_rating:.2f} ⭐")
                    with col3:
                        most_common = ratings_df.loc[
                            ratings_df["count"].idxmax(), "rating"
                        ]
                        st.metric("Note la plus fréquente", f"{most_common} ⭐")

                    break

        except Exception:
            continue
    else:
        st.warning("⚠️ Aucune table avec des notes trouvée")


def create_temporal_analysis(conn):
    """Analyze temporal patterns in interactions."""
    st.subheader("📅 Analyse temporelle")

    # Look for date columns in interaction tables
    tables_with_dates = []

    for table in [
        "RAW_interactions",
        "interactions_train",
        "interactions_test",
        "interactions_validation",
    ]:
        try:
            schema = conn.execute(f"DESCRIBE {table}").fetchall()
            column_names = [col[0] for col in schema]

            if "date" in column_names:
                tables_with_dates.append(table)
        except Exception:
            continue

    if tables_with_dates:
        selected_table = st.selectbox("Choisir une table:", tables_with_dates)

        try:
            # Get temporal data
            temporal_df = conn.execute(
                f"""
                SELECT date, COUNT(*) as interactions_count
                FROM {selected_table}
                WHERE date IS NOT NULL
                GROUP BY date
                ORDER BY date
                LIMIT 1000
            """
            ).fetchdf()

            if not temporal_df.empty:
                # Convert to datetime
                temporal_df["date"] = pd.to_datetime(temporal_df["date"])

                # Create time series plot
                fig = px.line(
                    temporal_df,
                    x="date",
                    y="interactions_count",
                    title=f"Évolution des interactions dans le temps - {selected_table}",
                )

                st.plotly_chart(fig, use_container_width=True)

                # Time range info
                date_range = temporal_df["date"].max() - temporal_df["date"].min()
                st.info(
                    f"📊 Période analysée: du {temporal_df['date'].min().strftime('%Y-%m-%d')} "
                    f"au {temporal_df['date'].max().strftime('%Y-%m-%d')} "
                    f"({date_range.days} jours)"
                )

        except Exception as e:
            st.error(f"❌ Erreur lors de l'analyse temporelle: {e}")
    else:
        st.warning("⚠️ Aucune table avec des dates trouvée")


def create_user_analysis(conn):
    """Enhanced user activity analysis."""
    st.subheader("👥 Analyse des utilisateurs")

    try:
        # Get user data from PP_users table
        users_df = conn.execute(
            """
            SELECT n_items, n_ratings
            FROM PP_users
            WHERE n_ratings > 0 AND n_items > 0
            ORDER BY n_ratings DESC
            LIMIT 10000
        """
        ).fetchdf()

        if not users_df.empty:
            # Create scatter plot
            fig = px.scatter(
                users_df,
                x="n_items",
                y="n_ratings",
                title="Relation entre nombre de recettes et nombre d'évaluations",
                labels={
                    "n_items": "Nombre de recettes",
                    "n_ratings": "Nombre d'évaluations",
                },
                opacity=0.6,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Utilisateurs actifs", f"{len(users_df):,}")
            with col2:
                st.metric(
                    "Recettes moy./utilisateur", f"{users_df['n_items'].mean():.1f}"
                )
            with col3:
                st.metric(
                    "Évaluations moy./utilisateur",
                    f"{users_df['n_ratings'].mean():.1f}",
                )
            with col4:
                correlation = users_df["n_items"].corr(users_df["n_ratings"])
                st.metric("Corrélation", f"{correlation:.3f}")

        else:
            st.warning("⚠️ Aucune donnée utilisateur trouvée")

    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse des utilisateurs: {e}")


def display_raw_data_explorer(conn):
    """Interactive data explorer."""
    with st.expander("🔍 Explorateur de données"):
        # Table selector
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]

        selected_table = st.selectbox("Sélectionner une table:", table_names)

        if selected_table:
            # Get table info
            count = conn.execute(f"SELECT COUNT(*) FROM {selected_table}").fetchone()[0]
            schema = conn.execute(f"DESCRIBE {selected_table}").fetchall()

            st.write(f"**{selected_table}**: {count:,} lignes, {len(schema)} colonnes")

            # Column info
            st.write("**Colonnes:**")
            for col_name, col_type, _, _, _, _ in schema:
                st.write(f"- `{col_name}` ({col_type})")

            # Sample size selector
            sample_size = st.slider("Nombre de lignes à afficher:", 10, 1000, 100)

            # Display sample data
            sample_df = conn.execute(
                f"SELECT * FROM {selected_table} LIMIT {sample_size}"
            ).fetchdf()
            st.dataframe(sample_df, use_container_width=True)


def create_custom_visualizations(conn):
    """Interface pour créer des graphiques personnalisés."""
    st.subheader("📈 Graphiques personnalisés")

    # Get available tables
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]

    selected_table = st.selectbox(
        "Choisir une table:", table_names, key="custom_viz_table"
    )

    if selected_table:
        # Get columns for the selected table
        schema = conn.execute(f"DESCRIBE {selected_table}").fetchall()
        columns = [col[0] for col in schema]
        numeric_columns = []
        date_columns = []

        # Identify column types
        for col_name, col_type, _, _, _, _ in schema:
            if any(
                t in col_type.lower() for t in ["int", "float", "double", "numeric"]
            ):
                numeric_columns.append(col_name)
            if any(t in col_type.lower() for t in ["date", "time"]):
                date_columns.append(col_name)

        # Chart type selector
        chart_type = st.selectbox(
            "Type de graphique:",
            [
                "Corrélation (heatmap)",
                "Distribution",
                "Nuage de points",
                "Série temporelle",
            ],
        )

        if chart_type == "Corrélation (heatmap)":
            if len(numeric_columns) > 1:
                create_correlation_heatmap(conn, selected_table)
            else:
                st.warning(
                    "Cette table n'a pas assez de colonnes numériques pour une matrice de corrélation"
                )

        elif chart_type == "Distribution":
            if numeric_columns:
                selected_column = st.selectbox("Colonne à analyser:", numeric_columns)
                create_distribution_plot(conn, selected_table, selected_column)
            else:
                st.warning("Cette table n'a pas de colonnes numériques")

        elif chart_type == "Nuage de points":
            if len(numeric_columns) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_column = st.selectbox("Axe X:", numeric_columns, key="scatter_x")
                with col2:
                    y_column = st.selectbox("Axe Y:", numeric_columns, key="scatter_y")

                color_column = st.selectbox(
                    "Colonne de couleur (optionnel):",
                    ["Aucune"] + columns,
                    key="scatter_color",
                )
                color_col = color_column if color_column != "Aucune" else None

                create_custom_scatter_plot(
                    conn, selected_table, x_column, y_column, color_col
                )
            else:
                st.warning(
                    "Cette table n'a pas assez de colonnes numériques pour un nuage de points"
                )

        elif chart_type == "Série temporelle":
            if date_columns and numeric_columns:
                col1, col2 = st.columns(2)
                with col1:
                    date_column = st.selectbox(
                        "Colonne de date:", date_columns, key="ts_date"
                    )
                with col2:
                    value_column = st.selectbox(
                        "Colonne de valeur:", numeric_columns, key="ts_value"
                    )

                create_time_series_plot(conn, selected_table, date_column, value_column)
            else:
                st.warning(
                    "Cette table n'a pas de colonnes de date ou de valeurs numériques pour une série temporelle"
                )


def main():
    """Main Streamlit application - Enhanced version."""
    logger.info("🚀 Enhanced Streamlit application starting")

    # Database connection
    conn = get_db_connection()
    if not conn:
        st.error("❌ Impossible de se connecter à la base DuckDB")
        st.info("💡 Assurez-vous que le fichier `data/mangetamain.duckdb` existe")
        return

    # Load custom CSS from external file
    css_path = Path("src/mangetamain_analytics/assets/custom.css")
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        logger.warning(f"CSS file not found: {css_path}")

    # Sidebar with navigation
    with st.sidebar:
        # Logo at the top
        logo_path = Path("src/mangetamain_analytics/assets/back_to_the_kitchen_logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            # Fallback: display text logo if image not found
            st.markdown("### 🍳 Back to the Kitchen")

        st.markdown("---")

        # Navigation menu with Analyses title
        st.markdown("### Analyses")

        # Menu items with icons
        menu_options = {
            "📈 Tendances 1999-2018": "📈",
            "📊 Saisonnalité": "🌡️",
            "📊 Effet weekend": "📅",
            "📊 Recommandations": "⭐"
        }

        selected_page = st.radio(
            "Choisir une analyse:",
            list(menu_options.keys()),
            index=0,
            label_visibility="collapsed"
        )

        # Bouton Rafraîchir orange avec Streamlit
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()

        # Spacer to push badges to bottom
        for _ in range(5):
            st.markdown("")

        # Database status and environment badge at bottom (within sidebar)
        st.markdown("---")
        db_path = "data/mangetamain.duckdb"
        if Path(db_path).exists():
            st.success("✅ **Fichier DuckDB connecté**")
        else:
            st.error("❌ **Fichier DuckDB non trouvé**")

        # Environment badge
        display_environment_badge()

    # Main content - Display selected analysis
    if selected_page == "📈 Tendances 1999-2018":
        st.header("📈 Analyses des tendances temporelles (1999-2018)")
        st.markdown(
            """
            Cette section présente les **analyses de tendances à long terme** des recettes Food.com
            sur la période 1999-2018, en utilisant des **régressions WLS (Weighted Least Squares)**
            pour identifier les évolutions significatives.
            """
        )

        # Métriques clés en cartouches stylés
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div style="background-color: {colors.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {colors.CARD_BORDER};">
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">📅 Période</div>
                    <div style="color: {colors.TEXT_WHITE}; font-size: 1.75rem; font-weight: 700;">1999-2018</div>
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">20 années</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div style="background-color: {colors.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {colors.CARD_BORDER};">
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">🍽️ Recettes</div>
                    <div style="color: {colors.TEXT_WHITE}; font-size: 1.75rem; font-weight: 700;">178,265</div>
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">Total analysées</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div style="background-color: {colors.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {colors.CARD_BORDER};">
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">📊 Analyses</div>
                    <div style="color: {colors.TEXT_WHITE}; font-size: 1.75rem; font-weight: 700;">6</div>
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">Dimensions étudiées</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:
            st.markdown(
                f"""
                <div style="background-color: {colors.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {colors.CARD_BORDER};">
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">📈 Méthode</div>
                    <div style="color: {colors.ORANGE_PRIMARY}; font-size: 1.25rem; font-weight: 700;">WLS</div>
                    <div style="color: {colors.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">Weighted Least Squares</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # Display all 6 analyses without dropdown
        st.subheader("📊 Volume de recettes")
        analyse_trendline_volume()
        st.markdown("---")

        st.subheader("⏱️ Durée de préparation")
        analyse_trendline_duree()
        st.markdown("---")

        st.subheader("🔧 Complexité des recettes")
        analyse_trendline_complexite()
        st.markdown("---")

        st.subheader("🥗 Valeurs nutritionnelles")
        analyse_trendline_nutrition()
        st.markdown("---")

        st.subheader("🥘 Ingrédients")
        st.info("💡 Analyse des 10 ingrédients les plus populaires")
        analyse_trendline_ingredients(top_n=10)
        st.markdown("---")

        st.subheader("🏷️ Tags/Catégories")
        st.info("💡 Analyse des 10 tags les plus fréquents")
        analyse_trendline_tags(top_n=10)

    elif selected_page == "📊 Saisonnalité":
        st.header("🌡️ Analyse de Saisonnalité")
        st.info("🚧 Cette analyse sera disponible prochainement.")
        st.markdown(
            """
            Analyse des patterns saisonniers dans les données Food.com :
            - Tendances par mois/saison
            - Ingrédients saisonniers
            - Popularité des recettes selon les saisons
            """
        )

    elif selected_page == "📊 Effet weekend":
        st.header("📅 Analyse de l'Effet Weekend")
        st.info("🚧 Cette analyse sera disponible prochainement.")
        st.markdown(
            """
            Analyse des comportements différenciés weekend vs semaine :
            - Volume d'activité par jour de semaine
            - Types de recettes préférées
            - Durée de préparation
            """
        )

    elif selected_page == "📊 Recommandations":
        st.header("⭐ Système de Recommandations")
        st.info("🚧 Cette analyse sera disponible prochainement.")
        st.markdown(
            """
            Système de recommandations basé sur le ML :
            - Recommandations personnalisées
            - Clustering d'utilisateurs
            - Prédiction de popularité
            """
        )

    else:
        # Fallback
        st.header(selected_page)
        st.info("🚧 Cette analyse sera disponible prochainement.")

    # Footer - Cartouche gris visible (pas fixe)
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    st.markdown("<br><br>", unsafe_allow_html=True)  # Espace avant footer

    # Footer en 3 colonnes
    footer_col1, footer_col2, footer_col3 = st.columns(3)

    with footer_col1:
        st.markdown(
            f"""
            <div style="background-color: {colors.BACKGROUND_CARD}; padding: 12px 20px; border-radius: 8px; border: 1px solid {colors.CARD_BORDER}; text-align: center;">
                <span style="color: {colors.TEXT_SECONDARY}; font-size: 0.875rem;">🕒 Dernière màj: </span>
                <span style="color: {colors.TEXT_PRIMARY}; font-weight: 600;">{today}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with footer_col2:
        st.markdown(
            f"""
            <div style="background-color: {colors.BACKGROUND_CARD}; padding: 12px 20px; border-radius: 8px; border: 1px solid {colors.CARD_BORDER}; text-align: center;">
                <span style="color: {colors.TEXT_SECONDARY}; font-size: 0.875rem;">📦 Version: </span>
                <span style="color: {colors.TEXT_PRIMARY}; font-weight: 600;">1.0.0</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with footer_col3:
        st.markdown(
            f"""
            <div style="background-color: {colors.BACKGROUND_CARD}; padding: 12px 20px; border-radius: 8px; border: 1px solid {colors.CARD_BORDER}; text-align: center;">
                <a href="https://github.com/julienlafrance/backtothefuturekitchen" target="_blank" style="color: {colors.ORANGE_PRIMARY}; text-decoration: none; font-weight: 600;">
                    📚 Documentation
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    logger.info("✅ Application fully loaded")


if __name__ == "__main__":
    logger.info("🌟 Starting Enhanced Mangetamain Analytics")
    main()
