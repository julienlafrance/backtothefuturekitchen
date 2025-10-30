"""Module pour les graphiques personnalisés."""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Optional


def create_correlation_heatmap(conn, table_name: str) -> None:
    """Crée une heatmap de corrélation."""
    try:
        # Récupérer les colonnes numériques
        numeric_data = conn.execute(
            f"""
            SELECT * FROM {table_name}
            WHERE rating IS NOT NULL
            LIMIT 1000
        """
        ).fetchdf()

        # Sélectionner uniquement les colonnes numériques
        numeric_cols = numeric_data.select_dtypes(include=["float64", "int64"]).columns

        if len(numeric_cols) > 1:
            corr_matrix = numeric_data[numeric_cols].corr()

            # Plotly heatmap
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Matrice de corrélation",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Pas assez de colonnes numériques pour la corrélation")

    except Exception as e:
        st.error(f"Erreur: {e}")


def create_distribution_plot(conn, table_name: str, column_name: str) -> None:
    """Crée un graphique de distribution."""
    try:
        data_df = conn.execute(
            f"""
            SELECT {column_name}
            FROM {table_name}
            WHERE {column_name} IS NOT NULL
            LIMIT 5000
        """
        ).fetchdf()

        # Histogramme avec Plotly
        fig = px.histogram(
            data_df, x=column_name, title=f"Distribution de {column_name}", nbins=30
        )
        st.plotly_chart(fig, use_container_width=True)

        # Statistiques descriptives
        st.write("**Statistiques:**")
        st.write(data_df[column_name].describe())

    except Exception as e:
        st.error(f"Erreur: {e}")


def create_time_series_plot(
    conn, table_name: str, date_col: str, value_col: str
) -> None:
    """Crée un graphique temporel."""
    try:
        data_df = conn.execute(
            f"""
            SELECT {date_col}, {value_col}
            FROM {table_name}
            WHERE {date_col} IS NOT NULL AND {value_col} IS NOT NULL
            ORDER BY {date_col}
            LIMIT 1000
        """
        ).fetchdf()

        # Convertir en datetime
        data_df[date_col] = pd.to_datetime(data_df[date_col])

        # Line chart avec Plotly
        fig = px.line(
            data_df,
            x=date_col,
            y=value_col,
            title=f"Évolution de {value_col} dans le temps",
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur: {e}")


def create_custom_scatter_plot(
    conn, table_name: str, x_col: str, y_col: str, color_col: Optional[str] = None
) -> None:
    """Crée un graphique en nuage de points personnalisé."""
    try:
        color_clause = f", {color_col}" if color_col else ""
        data_df = conn.execute(
            f"""
            SELECT {x_col}, {y_col}{color_clause}
            FROM {table_name}
            WHERE {x_col} IS NOT NULL AND {y_col} IS NOT NULL
            LIMIT 2000
        """
        ).fetchdf()

        # Scatter plot avec Plotly
        fig = px.scatter(
            data_df,
            x=x_col,
            y=y_col,
            color=color_col if color_col else None,
            title=f"{y_col} vs {x_col}",
            opacity=0.7,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Calculer la corrélation
        correlation = data_df[x_col].corr(data_df[y_col])
        st.metric("Corrélation", f"{correlation:.3f}")

    except Exception as e:
        st.error(f"Erreur: {e}")
