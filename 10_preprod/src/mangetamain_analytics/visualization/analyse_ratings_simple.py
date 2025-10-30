#!/usr/bin/env python3
# <MÉTADONNÉES>
# Nom: analyse_ratings_simple.py
# Description: Analyse simple de la distribution des notes des utilisateurs
# Auteur: Exemple
# Date: 2024-10-22
# Version: 1.0
# Catégorie: Analyse exploratoire
# </MÉTADONNÉES>

# <IMPORTS>
import sys
import duckdb

# Imports conditionnels pour Streamlit
try:
    import streamlit as st
    import plotly.express as px

    STREAMLIT_AVAILABLE = True
except ImportError:  # pragma: no cover
    STREAMLIT_AVAILABLE = False
    # Fallback pour matplotlib si pas de plotly
    try:  # pragma: no cover
        import matplotlib.pyplot as plt

        MATPLOTLIB_AVAILABLE = True
    except ImportError:  # pragma: no cover
        MATPLOTLIB_AVAILABLE = False
# </IMPORTS>


def setup_s3_connection():
    """Configure la connexion S3 pour DuckDB"""
    conn = duckdb.connect()
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    conn.execute("SET s3_region='garage-fast'")
    conn.execute("SET s3_endpoint='s3fast.lafrance.io'")
    conn.execute("SET s3_use_ssl=false")
    conn.execute("SET s3_url_style='path'")
    conn.execute("SET s3_access_key_id='GK4febbfbbce789dbbe85f1bad'")
    conn.execute(
        "SET s3_secret_access_key='50e63b5146a4298f2f79a7e0fe5d5b602b4ef26434c6c5c72d017b85d2d61321'"
    )
    return conn


def get_ratings_data():
    """Récupère les données depuis le Parquet S3"""
    # <REQUÊTE_SQL>
    conn = setup_s3_connection()

    ratings_data = conn.execute(
        """
        SELECT
            rating,
            COUNT(*) as count
        FROM 's3://mangetamain/interactions_sample.parquet'
        WHERE rating IS NOT NULL
        GROUP BY rating
        ORDER BY rating
    """
    ).fetchdf()
    # </REQUÊTE_SQL>

    return ratings_data


def process_data(ratings_data):
    """Traite les données pour l'analyse"""
    # <TRAITEMENT>
    if ratings_data.empty:
        return ratings_data, {}

    total = ratings_data["count"].sum()
    ratings_data["percentage"] = (ratings_data["count"] / total) * 100

    # Statistiques
    stats = {
        "total": total,
        "avg_rating": (ratings_data["rating"] * ratings_data["count"]).sum() / total,
        "mode_rating": ratings_data.loc[ratings_data["count"].idxmax(), "rating"],
        "pct_5_stars": (
            ratings_data[ratings_data["rating"] == 5]["percentage"].iloc[0]
            if 5 in ratings_data["rating"].values
            else 0
        ),
    }
    # </TRAITEMENT>

    return ratings_data, stats


def create_plots_streamlit(ratings_data, stats) -> None:  # pragma: no cover
    """Crée les graphiques pour Streamlit"""
    # <GRAPHIQUE_PRINCIPAL>
    fig = px.bar(
        ratings_data,
        x="rating",
        y="count",
        title="Distribution des Notes (0-5 étoiles)",
        labels={"count": "Nombre d'évaluations", "rating": "Note"},
        color="rating",
        color_continuous_scale="viridis",
    )

    fig.update_layout(
        xaxis_title="Note", yaxis_title="Nombre d'évaluations", showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
    # </GRAPHIQUE_PRINCIPAL>

    # <GRAPHIQUES_SECONDAIRES>
    fig_pie = px.pie(
        ratings_data,
        values="count",
        names="rating",
        title="Répartition des Notes (Pourcentages)",
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    # </GRAPHIQUES_SECONDAIRES>


def create_plots_matplotlib(ratings_data, stats) -> None:  # pragma: no cover
    """Crée les graphiques avec matplotlib (mode standalone)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Graphique en barres
    ax1.bar(
        ratings_data["rating"], ratings_data["count"], color="skyblue", edgecolor="navy"
    )
    ax1.set_xlabel("Note")
    ax1.set_ylabel("Nombre d'évaluations")
    ax1.set_title("Distribution des Notes")
    ax1.set_xticks(ratings_data["rating"])

    # Graphique en camembert
    ax2.pie(ratings_data["count"], labels=ratings_data["rating"], autopct="%1.1f%%")
    ax2.set_title("Répartition des Notes (%)")

    plt.tight_layout()
    plt.savefig("/tmp/ratings_analysis.png", dpi=300, bbox_inches="tight")
    print("📊 Graphique sauvé : /tmp/ratings_analysis.png")
    plt.show()


def print_stats(stats) -> None:
    """Affiche les statistiques en mode console"""
    print("\n" + "=" * 50)
    print("📊 STATISTIQUES")
    print("=" * 50)
    print(f"Total évaluations    : {stats['total']:,}")
    print(f"Note moyenne         : {stats['avg_rating']:.2f} ⭐")
    print(f"Note la plus fréquente : {stats['mode_rating']} ⭐")
    print(f"% de 5 étoiles       : {stats['pct_5_stars']:.1f}%")


def print_interpretation() -> None:
    """Affiche l'interprétation"""
    # <INTERPRÉTATION>
    print("\n" + "=" * 50)
    print("🔍 ANALYSE")
    print("=" * 50)
    print("Observations principales :")
    print("- Biais positif très fort : majorité de 5 étoiles")
    print("- Polarisation : notes basses très rares")
    print("- Distribution asymétrique vers le haut")
    print("\nImplications :")
    print("- Utilisateurs notent surtout les recettes aimées")
    print("- Système de notation volontaire = biais de sélection")
    print("- Normalisation nécessaire pour analyses prédictives")
    # </INTERPRÉTATION>


def render_analysis(conn=None) -> None:  # pragma: no cover
    """
    Fonction principale pour Streamlit

    Args:
        conn: Connexion DuckDB (ignorée, on utilise S3 directement)
    """

    # <TITRE>
    st.subheader("⭐ Distribution des Notes - Analyse Simple")
    # </TITRE>

    # <DESCRIPTION>
    st.markdown(
        """
    Cette analyse examine la répartition des notes données par les utilisateurs aux recettes.

    **Contexte :** Dataset Food.com avec 50k interactions échantillonnées depuis S3
    **Objectif :** Identifier les patterns de notation et les biais utilisateurs
    """
    )
    # </DESCRIPTION>

    try:
        ratings_data = get_ratings_data()
        ratings_data, stats = process_data(ratings_data)

        if not ratings_data.empty:
            create_plots_streamlit(ratings_data, stats)

            # <STATISTIQUES>
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total évaluations", f"{stats['total']:,}")
            with col2:
                st.metric("Note moyenne", f"{stats['avg_rating']:.2f} ⭐")
            with col3:
                st.metric("Note la plus fréquente", f"{stats['mode_rating']} ⭐")
            with col4:
                st.metric("% de 5 étoiles", f"{stats['pct_5_stars']:.1f}%")
            # </STATISTIQUES>

            # <DONNÉES_BRUTES>
            with st.expander("Détails des données"):
                st.write("**Table de distribution :**")
                display_df = ratings_data.copy()
                display_df["percentage"] = display_df["percentage"].round(2)
                st.dataframe(display_df)
            # </DONNÉES_BRUTES>

    except Exception as e:
        st.error(f"Erreur dans l'analyse : {e}")


def main() -> None:  # pragma: no cover
    """Fonction principale pour exécution standalone"""
    print("🚀 Analyse des Ratings - Mode Standalone")
    print("=" * 50)

    try:
        print("📡 Connexion à S3 et récupération des données...")
        ratings_data = get_ratings_data()
        print(f"✅ {len(ratings_data)} niveaux de notes récupérés")

        ratings_data, stats = process_data(ratings_data)

        # Affichage des données
        print("\n📊 DONNÉES")
        print(ratings_data.to_string(index=False))

        # Statistiques
        print_stats(stats)

        # Interprétation
        print_interpretation()

        # Graphiques si matplotlib disponible
        if MATPLOTLIB_AVAILABLE:
            print("\n📈 Génération des graphiques...")
            create_plots_matplotlib(ratings_data, stats)
        else:
            print("\n⚠️  Matplotlib non disponible - pas de graphiques")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)


# <MODULE_INFO>
MODULE_INFO = {
    "name": "Analyse Distribution des Notes",
    "description": "Distribution des ratings avec données Parquet sur S3",
    "category": "Analyse exploratoire",
    "author": "Exemple",
    "version": "1.0",
    "tags": ["ratings", "distribution", "s3", "parquet"],
    "data_sources": ["interactions_sample.parquet"],
    "created_date": "2024-10-22",
    "last_modified": "2024-10-22",
}
# </MODULE_INFO>

if __name__ == "__main__":
    main()
