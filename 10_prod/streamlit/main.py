"""Streamlit application for Mangetamain Analytics.

This module provides the main interface for analyzing Food.com dataset
using DuckDB as the backend database and Seaborn for visualizations.
"""

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import duckdb
from pathlib import Path
from loguru import logger
import sys
import os

def detect_environment():
    """Detect if running in PREPROD or PROD environment."""
    current_path = str(Path.cwd())
    
    # Check if we are in a Docker container
    if Path("/.dockerenv").exists():
        return "PROD (Docker)"
    
    # Check the current working directory path
    if "00_preprod" in current_path:
        return "PREPROD"
    elif "10_prod" in current_path:
        return "PROD"
    else:
        return "UNKNOWN"

def display_environment_badge():
    """Display environment badge in sidebar."""
    env = detect_environment()
    
    if "PREPROD" in env:
        st.sidebar.markdown(
            """
            <div style="background-color: #6c757d; padding: 6px; border-radius: 5px; text-align: center; margin-top: 15px;">
                <small style="color: white; margin: 0; font-weight: bold;">🔧 PREPROD</small>
                <p style="color: white; margin: 0; font-size: 9px;">Environnement de développement</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    elif "PROD (Docker)" in env:
        st.sidebar.markdown(
            """
            <div style="background-color: #6c757d; padding: 6px; border-radius: 5px; text-align: center; margin-top: 15px;">
                <small style="color: white; margin: 0; font-weight: bold;">🐳 PROD (Docker)</small>
                <p style="color: white; margin: 0; font-size: 9px;">Environnement production Docker</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    elif "PROD" in env:
        st.sidebar.markdown(
            """
            <div style="background-color: #6c757d; padding: 6px; border-radius: 5px; text-align: center; margin-top: 15px;">
                <small style="color: white; margin: 0; font-weight: bold;">🚀 PRODUCTION</small>
                <p style="color: white; margin: 0; font-size: 9px;">Environnement de production</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Remove default logger and configure Loguru only once
if not any("logs/mangetamain" in str(handler) for handler in logger._core.handlers.values()):
    logger.remove()
    
    logger.add("logs/mangetamain_app.log", 
              rotation="1 MB", 
              level="INFO",
              format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}")

    logger.add("logs/mangetamain_errors.log", 
              rotation="1 MB", 
              level="ERROR",
              format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}")

    logger.add(sys.stderr, level="DEBUG")  # Also log to console for debugging

# Configuration de la page
st.set_page_config(
    page_title="Mangetamain Analytics",
    page_icon="🍽️",
    layout="wide"
)

def get_db_connection():
    """Establish connection to the DuckDB database.
    
    Connects to the local DuckDB file containing Food.com dataset
    for recipe and user interaction analysis.
    
    Returns:
        duckdb.Connection: Active database connection, or None if file not found
        
    Raises:
        FileNotFoundError: If mangetamain.duckdb file doesn't exist
        
    Example:
        >>> conn = get_db_connection()
        >>> if conn:
        ...     tables = conn.execute("SHOW TABLES").fetchall()
    """
    db_path = "data/mangetamain.duckdb"
    
    if Path(db_path).exists():
        try:
            conn = duckdb.connect(db_path)
            
            # Log database info
            file_size = Path(db_path).stat().st_size / (1024 * 1024)
            tables = conn.execute("SHOW TABLES").fetchall()
            
            logger.info(f"✅ DuckDB connection established - File: {db_path}")
            logger.info(f"📊 Database size: {file_size:.1f} MB")
            logger.info(f"🗂️ Tables found: {len(tables)} - {[t[0] for t in tables]}")
            
            # Log table statistics
            for table_name, in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                logger.info(f"📈 Table {table_name}: {count:,} rows")
            
            return conn
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to DuckDB: {e}")
            return None
    else:
        logger.error(f"❌ DuckDB file not found: {db_path}")
        return None

def display_database_info(conn):
    """Display database information in the sidebar.
    
    Shows DuckDB file details, available tables with row counts,
    and CSV source files status with sizes.
    
    Args:
        conn (duckdb.Connection): Active database connection
        
    Returns:
        None
        
    Example:
        >>> conn = get_db_connection()
        >>> display_database_info(conn)
    """
    st.header("📊 Base de données")
    
    # Display DuckDB file path and size
    db_path = "data/mangetamain.duckdb"
    if Path(db_path).exists():
        file_size = Path(db_path).stat().st_size / (1024 * 1024)  # Size in MB
        st.success(f"✅ **Fichier DuckDB connecté**")
        st.code(f"📁 {db_path}")
        st.write(f"📏 Taille: {file_size:.1f} MB")
    else:
        st.error(f"❌ Fichier non trouvé: {db_path}")
    
    st.markdown("---")
    
    # Display available tables and their statistics
    st.subheader("🗂️ Tables disponibles")
    tables = conn.execute("SHOW TABLES").fetchall()
    for table_name, in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        st.write(f"**{table_name}**: {count:,} lignes")
    
    st.markdown("---")
    
    # Display CSV source files status
    st.subheader("📄 Fichiers CSV sources")
    csv_files = [
        "data/interactions_train.csv",
        "data/interactions_test.csv", 
        "data/interactions_validation.csv",
        "data/PP_users.csv"
    ]
    
    for csv_file in csv_files:
        if Path(csv_file).exists():
            file_size = Path(csv_file).stat().st_size / (1024 * 1024)  # MB
            st.write(f"✅ `{csv_file}` ({file_size:.1f} MB)")
        else:
            st.write(f"❌ `{csv_file}` (absent)")

def create_rating_distribution_chart(conn):
    """Create and display rating distribution visualization.
    
    Generates a bar chart showing the distribution of ratings (1-5 stars)
    from the interactions_train table using Seaborn.
    
    Args:
        conn (duckdb.Connection): Active database connection
        
    Returns:
        None
        
    Example:
        >>> conn = get_db_connection()
        >>> create_rating_distribution_chart(conn)
    """
    logger.info("📊 Creating rating distribution chart")
    
    st.subheader("Distribution des notes")
    ratings_df = conn.execute("""
        SELECT rating, COUNT(*) as count
        FROM interactions_train 
        WHERE rating IS NOT NULL
        GROUP BY rating
        ORDER BY rating
    """).fetchdf()
    
    if not ratings_df.empty:
        total_ratings = ratings_df['count'].sum()
        most_common_rating = ratings_df.loc[ratings_df['count'].idxmax(), 'rating']
        
        logger.info(f"📈 Rating distribution generated - Total: {total_ratings:,} ratings")
        logger.info(f"⭐ Most common rating: {most_common_rating} stars")
        
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=ratings_df, x='rating', y='count', hue='rating', palette='viridis', ax=ax, legend=False)
        ax.set_title('Distribution des Notes - Dataset Food.com', fontsize=14)
        ax.set_xlabel('Note (1-5 étoiles)')
        ax.set_ylabel('Nombre d\'évaluations')
        
        # Add values on top of bars
        for i, v in enumerate(ratings_df['count']):
            ax.text(i, v + 1000, f'{v:,}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        logger.info("✅ Rating distribution chart displayed successfully")
    else:
        logger.warning("⚠️ No rating data found for visualization")

def create_user_activity_charts(conn):
    """Create and display user activity visualizations.
    
    Generates two histograms showing the distribution of:
    1. Number of recipes per user
    2. Number of ratings per user
    
    Args:
        conn (duckdb.Connection): Active database connection
        
    Returns:
        None
        
    Example:
        >>> conn = get_db_connection()
        >>> create_user_activity_charts(conn)
    """
    logger.info("👥 Creating user activity charts")
    
    st.subheader("Activité des utilisateurs")
    users_df = conn.execute("""
        SELECT n_items, n_ratings
        FROM users 
        WHERE n_ratings > 0 AND n_items > 0
        LIMIT 1000
    """).fetchdf()
    
    if not users_df.empty:
        avg_recipes = users_df['n_items'].mean()
        avg_ratings = users_df['n_ratings'].mean()
        max_recipes = users_df['n_items'].max()
        max_ratings = users_df['n_ratings'].max()
        
        logger.info(f"📊 User activity analysis - Sample size: {len(users_df)} users")
        logger.info(f"🍳 Average recipes per user: {avg_recipes:.1f}")
        logger.info(f"⭐ Average ratings per user: {avg_ratings:.1f}")
        logger.info(f"🏆 Most active user: {max_recipes} recipes, {max_ratings} ratings")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Distribution of recipes per user
        sns.histplot(data=users_df, x='n_items', bins=30, kde=True, ax=ax1, color='skyblue')
        ax1.set_title('Nombre de recettes par utilisateur', fontsize=12)
        ax1.set_xlabel('Nombre de recettes')
        
        # Distribution of ratings per user
        sns.histplot(data=users_df, x='n_ratings', bins=30, kde=True, ax=ax2, color='lightcoral')
        ax2.set_title('Nombre d\'évaluations par utilisateur', fontsize=12)
        ax2.set_xlabel('Nombre d\'évaluations')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        logger.info("✅ User activity charts displayed successfully")
    else:
        logger.warning("⚠️ No user data found for activity visualization")

def display_raw_data_samples(conn):
    """Display raw data samples in expandable sections.
    
    Shows sample data from interactions_train and users tables
    for data exploration and verification purposes.
    
    Args:
        conn (duckdb.Connection): Active database connection
        
    Returns:
        None
        
    Example:
        >>> conn = get_db_connection()
        >>> display_raw_data_samples(conn)
    """
    with st.expander("🗄️ Voir les données brutes"):
        st.subheader("Échantillon interactions")
        interactions_sample = conn.execute("""
            SELECT user_id, recipe_id, rating, date
            FROM interactions_train 
            LIMIT 100
        """).fetchdf()
        st.dataframe(interactions_sample)
        
        st.subheader("Échantillon utilisateurs")
        users_sample = conn.execute("""
            SELECT u, n_items, n_ratings
            FROM users 
            LIMIT 100
        """).fetchdf()
        st.dataframe(users_sample)

def main():
    """Main Streamlit application for Mangetamain Analytics.
    
    Initializes the Streamlit interface, establishes database connection,
    and displays comprehensive analysis of Food.com dataset including:
    - Database information and statistics
    - Rating distribution visualization
    - User activity analysis
    - Raw data samples
    
    The application connects to a local DuckDB database containing
    Food.com recipe and user interaction data for analysis.
    
    Returns:
        None
        
    Raises:
        ConnectionError: If unable to connect to DuckDB database
        
    Example:
        Run with: streamlit run main.py
    """
    # Log each time the main function is called (happens on each Streamlit rerun)
    logger.info("🚀 Streamlit application starting - Mangetamain Analytics")
    logger.info("🏠 Main application function started")
    
    st.title("🍽️ Mangetamain Analytics")
    
    # Establish database connection
    conn = get_db_connection()
    if not conn:
        error_msg = "❌ Base DuckDB non trouvée dans data/mangetamain.duckdb"
        st.error(error_msg)
        logger.error("🚫 Application stopped - No database connection")
        return
    
    logger.info("🎯 Database connected successfully, proceeding with UI")
    
    # Display database information in sidebar
    with st.sidebar:
        display_database_info(conn)
        display_environment_badge()
    
    # Main content area - Food.com data analysis
    st.header("📈 Analyses des données Food.com")
    
    # Create visualizations
    create_rating_distribution_chart(conn)
    create_user_activity_charts(conn)
    
    # Display raw data samples
    display_raw_data_samples(conn)
    
    logger.info("✅ Application fully loaded and ready for user interaction")

if __name__ == "__main__":
    logger.info("🌟 Application entry point - Starting Mangetamain Analytics")
    main()
    logger.info("🏁 Application session completed")
