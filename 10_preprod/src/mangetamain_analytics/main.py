"""Streamlit application for Mangetamain Analytics - Updated Version.

This module provides the main interface for analyzing Food.com dataset.
Data is loaded from S3 Parquet files via mangetamain_data_utils package.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from loguru import logger
import sys
import plotly.express as px
from utils.environment import EnvironmentDetector
from i18n import init_language, render_language_selector
from utils.i18n_helper import t
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
from visualization.analyse_seasonality import render_seasonality_analysis
from visualization.analyse_weekend import render_weekend_analysis
from visualization.analyse_ratings import render_ratings_analysis
from utils.color_theme import ColorTheme
from exceptions import DataLoadError, DatabaseError, AnalysisError, ConfigurationError

# Configuration des chemins relatifs (fonctionne en PREPROD et PROD)
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / "assets"


# Fonction helper pour créer des options de menu avec icônes Lucide
def create_nav_option_with_icon(icon_name, text) -> str:
    """Crée une option de navigation avec icône Lucide inline."""
    # SVG Lucide inline pour meilleur contrôle
    lucide_icons = {
        "calendar-days": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/></svg>',
        "sun": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>',
        "sparkles": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
        "bar-chart-2": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/></svg>',
        "refresh-cw": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>',
    }

    icon_svg = lucide_icons.get(icon_name, "")
    return f'<div style="display: flex; align-items: center; gap: 10px;">{icon_svg}<span>{text}</span></div>'


def display_environment_badge() -> None:
    """Display environment badge in sidebar."""
    env = EnvironmentDetector.get_name()

    if "PREPROD" in env:
        badge_config = ColorTheme.ENV_PREPROD
        label = "PREPROD"
    elif "PROD" in env:
        badge_config = ColorTheme.ENV_PROD
        label = "PROD"
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
    "logs/mangetamain" in str(handler) for handler in logger._core.handlers.values()  # type: ignore[attr-defined]
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
st.set_page_config(
    page_title="Mangetamain Analytics",
    page_icon=str(ASSETS_DIR / "favicon.png"),
    layout="wide",
)

# Initialize language system
init_language()


########################################################################################################
# OBSOLETE FUNCTIONS REMOVED - All data now loaded from S3 Parquet via mangetamain_data_utils
########################################################################################################
# - get_db_connection() → data/mangetamain.duckdb no longer used
# - display_database_info(conn) → Removed
# - create_tables_overview(conn) → Removed
# - create_rating_analysis(conn) → Removed
# - create_temporal_analysis(conn) → Removed
# - create_user_analysis(conn) → Removed
# - display_raw_data_explorer(conn) → Removed
# - create_custom_visualizations(conn) → Removed
#
# All analyses now use:
#   - load_recipes_clean() from mangetamain_data_utils.data_utils_recipes
#   - load_ratings_for_longterm_analysis() from mangetamain_data_utils.data_utils_ratings
#   - Data source: S3 Parquet files (s3://mangetamain/*.parquet)
########################################################################################################


def _OBSOLETE_create_tables_overview(conn) -> None:
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


def create_rating_analysis(conn) -> None:
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

        except DatabaseError:
            # Table n'existe pas ou erreur SQL, continuer avec la suivante
            continue
        except Exception as e:
            # Autres erreurs (pandas, plotly, etc.)
            logger.warning(f"Erreur lors de l'analyse de {table}: {e}")
            continue
    else:
        st.warning("⚠️ Aucune table avec des notes trouvée")


def create_temporal_analysis(conn) -> None:
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
        except DatabaseError:
            # Table n'existe pas ou erreur SQL, continuer
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

        except DatabaseError as e:
            st.error(f"❌ Erreur base de données lors de l'analyse temporelle: {e}")
            logger.error(f"DatabaseError in temporal analysis: {e}")
        except AnalysisError as e:
            st.error(f"❌ Erreur d'analyse temporelle: {e}")
            logger.error(f"AnalysisError in temporal analysis: {e}")
        except Exception as e:
            st.error(f"❌ Erreur inattendue lors de l'analyse temporelle: {e}")
            logger.error(f"Unexpected error in temporal analysis: {e}")
    else:
        st.warning("⚠️ Aucune table avec des dates trouvée")


def create_user_analysis(conn) -> None:
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

    except DatabaseError as e:
        st.error(f"❌ Erreur base de données lors de l'analyse utilisateurs: {e}")
        logger.error(f"DatabaseError in user analysis: {e}")
    except AnalysisError as e:
        st.error(f"❌ Erreur d'analyse utilisateurs: {e}")
        logger.error(f"AnalysisError in user analysis: {e}")
    except Exception as e:
        st.error(f"❌ Erreur inattendue lors de l'analyse utilisateurs: {e}")
        logger.error(f"Unexpected error in user analysis: {e}")


def display_raw_data_explorer(conn) -> None:
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


def create_custom_visualizations(conn) -> None:
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


def main() -> None:
    """Main Streamlit application - Enhanced version."""
    logger.info("🚀 Enhanced Streamlit application starting")

    # Load custom CSS from external file
    css_path = ASSETS_DIR / "custom.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        logger.warning(f"CSS file not found: {css_path}")

    # Initialize session state for current page if not exists (store key, not label)
    if "current_page" not in st.session_state:
        st.session_state.current_page = "trends"

    # Sidebar with navigation
    with st.sidebar:
        # Logo at the top
        logo_path = ASSETS_DIR / "back_to_the_kitchen_logo.png"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            # Fallback: display text logo if image not found
            st.markdown("### 🍳 Back to the Kitchen")

        st.markdown("---")

        # Language selector directly under the logo
        render_language_selector()

        # Titre de section ANALYSES avec classe CSS
        st.markdown(
            f'<h3 class="sidebar-category-title">{t("analyses_section")}</h3>',
            unsafe_allow_html=True,
        )

        # Texte introductif
        st.markdown(
            f'<p class="sidebar-subtitle">{t("choose_analysis")}</p>',
            unsafe_allow_html=True,
        )

        # Menu items with Lucide icons
        menu_options = [
            ("bar-chart-2", "trends"),
            ("calendar-days", "seasonality"),
            ("sun", "weekend"),
            ("star", "ratings"),
        ]

        # Options pour st.radio (texte traduit)
        menu_labels = [t(opt[1], category="pages") for opt in menu_options]

        # Radio avec icônes en préfixe (les icônes seront ajoutées via CSS)
        # Get current page index from key
        page_keys = [opt[1] for opt in menu_options]
        current_index = (
            page_keys.index(st.session_state.current_page)
            if st.session_state.current_page in page_keys
            else 0
        )

        selected_label = st.radio(
            "Navigation",
            menu_labels,
            index=current_index,
            label_visibility="collapsed",
            key="main_nav",
            horizontal=False,
        )

        # Convert selected label back to key
        selected_key = page_keys[menu_labels.index(selected_label)]

        # Mettre à jour session state
        if selected_key != st.session_state.current_page:
            st.session_state.current_page = selected_key

        # Séparateur avant bouton Rafraîchir
        st.markdown(
            "<hr style='border: 0.5px solid rgba(240, 240, 240, 0.1); margin: 20px 0;'>",
            unsafe_allow_html=True,
        )

        # Bouton Rafraîchir - Vide le cache et recharge les données
        if st.button(
            f"🔄 {t('refresh_button')}", key="btn_refresh", use_container_width=True
        ):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.toast(f"✅ {t('refresh_toast')}", icon="🔄")
            st.rerun()

        # Spacer pour pousser les badges en bas (via CSS flexbox)
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)

        # BADGE STATUT S3 - Style pill avec icône
        s3_ready = False
        try:
            # Test S3 simplifié
            import boto3
            from configparser import ConfigParser

            config = ConfigParser()
            possible_paths = [
                Path("/app/96_keys/credentials"),
                Path("../../96_keys/credentials"),
                Path("/home/dataia25/mangetamain/96_keys/credentials"),
            ]

            credentials_path = next((p for p in possible_paths if p.exists()), None)

            if credentials_path:
                config.read(str(credentials_path))
                s3 = boto3.client(
                    "s3",
                    endpoint_url="http://s3fast.lafrance.io",
                    aws_access_key_id=config["s3fast"]["aws_access_key_id"],
                    aws_secret_access_key=config["s3fast"]["aws_secret_access_key"],
                    region_name="garage-fast",
                )
                response = s3.list_objects_v2(Bucket="mangetamain", MaxKeys=1)
                s3_ready = "Contents" in response
        except (ConfigurationError, DataLoadError) as e:
            logger.warning(f"S3 not accessible: {e}")
            s3_ready = False
        except Exception as e:
            logger.warning(f"Unexpected error checking S3: {e}")
            s3_ready = False

        # Indicateur S3 Ready avec classe CSS
        s3_status = t("s3_ready") if s3_ready else t("s3_error")
        st.markdown(
            f"""
            <div class="s3-ready-indicator">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>{s3_status}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # BADGE ENVIRONNEMENT - Style pill avec classe CSS
        env = EnvironmentDetector.get_name()
        if "PREPROD" in env:
            badge_class = "env-badge preprod-badge"
            label = "PREPROD"
        elif "PROD" in env:
            badge_class = "env-badge prod-badge"
            label = "PROD"
        else:
            badge_class = "env-badge preprod-badge"
            label = "UNKNOWN"

        st.markdown(
            f"""
            <div class="{badge_class}">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="2"/>
                </svg>
                <span>{label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Main content - Display selected analysis
    if st.session_state.current_page == "trends":
        st.markdown(
            f'<h1 style="margin-top: 0; padding-top: 0;">📈 {t("main_title", category="trends")}</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(t("main_description", category="trends"))

        # Métriques clés en cartouches stylés
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div style="background-color: {ColorTheme.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {ColorTheme.CARD_BORDER};">
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">📅 {t("metric_period", category="trends")}</div>
                    <div style="color: {ColorTheme.TEXT_WHITE}; font-size: 1.75rem; font-weight: 700;">1999-2018</div>
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">{t("metric_period_value", category="trends")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div style="background-color: {ColorTheme.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {ColorTheme.CARD_BORDER};">
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">🍽️ {t("metric_recipes", category="trends")}</div>
                    <div style="color: {ColorTheme.TEXT_WHITE}; font-size: 1.75rem; font-weight: 700;">178,265</div>
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">{t("metric_recipes_value", category="trends")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div style="background-color: {ColorTheme.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {ColorTheme.CARD_BORDER};">
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">📊 {t("metric_analyses", category="trends")}</div>
                    <div style="color: {ColorTheme.TEXT_WHITE}; font-size: 1.75rem; font-weight: 700;">6</div>
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">{t("metric_analyses_value", category="trends")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"""
                <div style="background-color: {ColorTheme.BACKGROUND_CARD}; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid {ColorTheme.CARD_BORDER};">
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 8px;">📈 {t("metric_method", category="trends")}</div>
                    <div style="color: {ColorTheme.ORANGE_PRIMARY}; font-size: 1.25rem; font-weight: 700;">WLS</div>
                    <div style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.75rem; margin-top: 4px;">{t("metric_method_value", category="trends")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Display all 6 analyses without dropdown
        st.subheader(f"📊 {t('volume_title', category='trends')}")
        analyse_trendline_volume()
        st.markdown("---")

        st.subheader(f"⏱️ {t('duration_title', category='trends')}")
        analyse_trendline_duree()
        st.markdown("---")

        st.subheader(f"🔧 {t('complexity_title', category='trends')}")
        analyse_trendline_complexite()
        st.markdown("---")

        st.subheader(f"🥗 {t('nutrition_title', category='trends')}")
        analyse_trendline_nutrition()
        st.markdown("---")

        st.subheader(f"🥘 {t('ingredients_title', category='trends')}")
        st.info(f"💡 {t('ingredients_info', category='trends')}")
        analyse_trendline_ingredients(top_n=10)
        st.markdown("---")

        st.subheader(f"🏷️ {t('tags_title', category='trends')}")
        st.info(f"💡 {t('tags_info', category='trends')}")
        analyse_trendline_tags(top_n=10)

    elif st.session_state.current_page == "seasonality":
        # Appel du module d'analyse saisonnière avec charte graphique
        render_seasonality_analysis()

    elif st.session_state.current_page == "weekend":
        # Appel du module d'analyse weekend avec charte graphique
        render_weekend_analysis()

    elif st.session_state.current_page == "ratings":
        # Appel du module d'analyse ratings avec charte graphique
        render_ratings_analysis()

    else:
        # Fallback
        st.markdown(
            f'<h1 style="margin-top: 0; padding-top: 0;">{t(st.session_state.current_page, category="pages")}</h1>',
            unsafe_allow_html=True,
        )
        st.info(f"🚧 {t('coming_soon')}")

    # Footer - Cartouche gris visible (pas fixe)
    from datetime import datetime

    today = "2025-10-31"

    st.markdown("<br><br>", unsafe_allow_html=True)  # Espace avant footer

    # Footer en 3 colonnes
    footer_col1, footer_col2, footer_col3 = st.columns(3)

    with footer_col1:
        st.markdown(
            f"""
            <div style="background-color: {ColorTheme.BACKGROUND_CARD}; padding: 12px 20px; border-radius: 8px; border: 1px solid {ColorTheme.CARD_BORDER}; text-align: center;">
                <span style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.875rem;">🕒 {t("last_update")}: </span>
                <span style="color: {ColorTheme.TEXT_PRIMARY}; font-weight: 600;">{today}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with footer_col2:
        st.markdown(
            f"""
            <div style="background-color: {ColorTheme.BACKGROUND_CARD}; padding: 12px 20px; border-radius: 8px; border: 1px solid {ColorTheme.CARD_BORDER}; text-align: center;">
                <span style="color: {ColorTheme.TEXT_SECONDARY}; font-size: 0.875rem;">📦 {t("version")}: </span>
                <span style="color: {ColorTheme.TEXT_PRIMARY}; font-weight: 600;">2.0.0</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with footer_col3:
        st.markdown(
            f"""
            <div style="background-color: {ColorTheme.BACKGROUND_CARD}; padding: 12px 20px; border-radius: 8px; border: 1px solid {ColorTheme.CARD_BORDER}; text-align: center;">
                <a href="https://github.com/julienlafrance/backtothefuturekitchen" target="_blank" style="color: {ColorTheme.ORANGE_PRIMARY}; text-decoration: none; font-weight: 600;">
                    📚 {t("documentation")}
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    logger.info("✅ Application fully loaded")


if __name__ == "__main__":
    logger.info("🌟 Starting Enhanced Mangetamain Analytics")
    main()
