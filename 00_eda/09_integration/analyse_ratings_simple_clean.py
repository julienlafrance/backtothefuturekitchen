#!/usr/bin/env python3

# <MÉTADONNÉES>
# Nom: analyse_ratings_simple_clean.py
# Description: Analyse de la distribution des notes des utilisateurs
# Auteur: Exemple
# Date: 2024-10-22
# Version: 1.0
# Catégorie: Analyse exploratoire
# </MÉTADONNÉES>

# <IMPORTS>
import sys
import duckdb
import pandas as pd
from pathlib import Path
from configparser import ConfigParser

try:
    import streamlit as st
    import plotly.express as px
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    try:
        import matplotlib.pyplot as plt
        MATPLOTLIB_AVAILABLE = True
    except ImportError:
        MATPLOTLIB_AVAILABLE = False
# </IMPORTS>

# <REQUÊTE_SQL>
QUERY = """
    SELECT 
        rating,
        COUNT(*) as count
    FROM 's3://mangetamain/interactions_sample.parquet'
    WHERE rating IS NOT NULL
    GROUP BY rating
    ORDER BY rating
"""
# </REQUÊTE_SQL>

# <GRAPHIQUE_STREAMLIT>
def create_chart_streamlit(data):
    """Crée le graphique pour Streamlit"""
    fig = px.bar(data, x='rating', y='count', title='Distribution des Notes')
    st.plotly_chart(fig, use_container_width=True)
# </GRAPHIQUE_STREAMLIT>

# <GRAPHIQUE_MATPLOTLIB>
def create_chart_matplotlib(data):
    """Crée le graphique pour matplotlib"""
    plt.figure(figsize=(10, 5))
    plt.bar(data['rating'], data['count'], color='skyblue')
    plt.title('Distribution des Notes')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.show()
# </GRAPHIQUE_MATPLOTLIB>

# <INTERPRÉTATION>
OBSERVATIONS = [
    "Biais positif très fort : majorité de 5 étoiles",
    "Polarisation : notes basses très rares", 
    "Distribution asymétrique vers le haut"
]

IMPLICATIONS = [
    "Utilisateurs notent surtout les recettes aimées",
    "Système de notation volontaire = biais de sélection",
    "Normalisation nécessaire pour analyses prédictives"
]
# </INTERPRÉTATION>

# <MODULE_INFO>
MODULE_INFO = {
    "name": "Analyse Distribution des Notes",
    "description": "Distribution des ratings avec données Parquet sur S3",
    "category": "Analyse exploratoire",
    "author": "Exemple",
    "version": "1.0"
}
# </MODULE_INFO>

# ===================================================================
# FONCTIONS
# ===================================================================

def setup_s3():
    """Configure S3"""
    credentials_path = Path(__file__).parent / "../../96_keys/credentials"
    config = ConfigParser()
    config.read(credentials_path)
    s3 = config['s3fast']
    
    conn = duckdb.connect()
    conn.execute("INSTALL httpfs; LOAD httpfs;")
    conn.execute(f"SET s3_region='{s3['region']}'")
    conn.execute(f"SET s3_endpoint='{s3['endpoint_url'].replace('http://', '')}'")
    conn.execute("SET s3_use_ssl=false")
    conn.execute("SET s3_url_style='path'")
    conn.execute(f"SET s3_access_key_id='{s3['aws_access_key_id']}'")
    conn.execute(f"SET s3_secret_access_key='{s3['aws_secret_access_key']}'")
    
    return conn

def get_data():
    """Récupère les données"""
    conn = setup_s3()
    data = conn.execute(QUERY).fetchdf()
    
    # Calcul des pourcentages
    total = data['count'].sum()
    data['percentage'] = (data['count'] / total) * 100
    
    # Stats
    stats = {
        'total': total,
        'avg_rating': (data['rating'] * data['count']).sum() / total,
        'mode_rating': data.loc[data['count'].idxmax(), 'rating'],
        'pct_5_stars': data[data['rating']==5]['percentage'].iloc[0] if 5 in data['rating'].values else 0
    }
    
    return data, stats

# ===================================================================
# RENDU
# ===================================================================

def render_analysis(conn=None):
    """Interface Streamlit"""
    st.subheader("⭐ Distribution des Notes")
    
    try:
        data, stats = get_data()
        
        # Graphique principal
        create_chart_streamlit(data)
        
        # Métriques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", f"{stats['total']:,}")
        with col2:
            st.metric("Moyenne", f"{stats['avg_rating']:.2f} ⭐")
        with col3:
            st.metric("Mode", f"{stats['mode_rating']} ⭐")
        with col4:
            st.metric("% 5⭐", f"{stats['pct_5_stars']:.1f}%")
        
        # Interprétation
        st.markdown("**Observations :**")
        for obs in OBSERVATIONS:
            st.write(f"- {obs}")
            
        st.markdown("**Implications :**")
        for imp in IMPLICATIONS:
            st.write(f"- {imp}")
            
        # Données
        with st.expander("📊 Données"):
            st.dataframe(data)
            
    except Exception as e:
        st.error(f"Erreur : {e}")

def run_standalone():
    """Interface console"""
    print("🚀 Analyse des Ratings")
    print("="*50)
    
    try:
        data, stats = get_data()
        
        print("\nDONNÉES")
        print(data.to_string(index=False))
        
        print(f"\nTotal: {stats['total']:,}")
        print(f"Moyenne: {stats['avg_rating']:.2f} ⭐")
        print(f"Mode: {stats['mode_rating']} ⭐")
        print(f"% 5⭐: {stats['pct_5_stars']:.1f}%")
        
        print("\nObservations :")
        for obs in OBSERVATIONS:
            print(f"- {obs}")
            
        print("\nImplications :")
        for imp in IMPLICATIONS:
            print(f"- {imp}")
        
        if MATPLOTLIB_AVAILABLE:
            create_chart_matplotlib(data)
        
        input("\n🔸 Entrée pour quitter...")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        input("🔸 Entrée pour quitter...")

if __name__ == "__main__":
    run_standalone()