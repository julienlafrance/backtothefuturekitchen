"""Module de gestion de la base de données DuckDB pour Mangetamain Analytics."""

import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from loguru import logger
import streamlit as st


class DatabaseManager:
    """Gestionnaire de base de données DuckDB avec cache Streamlit."""
    
    def __init__(self, db_path: str = "data/mangetamain.duckdb") -> None:
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            db_path: Chemin vers le fichier de base de données DuckDB
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initializing database at {self.db_path}")
        
    @contextmanager
    def get_connection(self):
        """
        Context manager pour obtenir une connexion à la base de données.
        
        Yields:
            Connexion DuckDB
        """
        conn = None
        try:
            conn = duckdb.connect(str(self.db_path))
            logger.debug("Database connection established")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Database connection closed")
    
    @st.cache_data
    def load_csv_to_db(_self, csv_path: str, table_name: str, **kwargs) -> bool:
        """
        Charge un fichier CSV dans la base de données.
        
        Args:
            csv_path: Chemin vers le fichier CSV
            table_name: Nom de la table à créer
            **kwargs: Arguments supplémentaires pour pandas.read_csv
            
        Returns:
            True si le chargement a réussi
        """
        try:
            with _self.get_connection() as conn:
                logger.info(f"Loading {csv_path} into table {table_name}")
                
                # Lire le CSV avec pandas
                df = pd.read_csv(csv_path, **kwargs)
                logger.info(f"Loaded {len(df)} rows from {csv_path}")
                
                # Insérer dans DuckDB
                conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
                
                # Créer des index pour optimiser les performances
                _self._create_indexes(conn, table_name, df.columns.tolist())
                
                logger.info(f"Successfully loaded {table_name} with {len(df)} rows")
                return True
                
        except Exception as e:
            logger.error(f"Error loading {csv_path} to {table_name}: {e}")
            return False
    
    def _create_indexes(self, conn: duckdb.DuckDBPyConnection, table_name: str, columns: List[str]) -> None:
        """
        Crée des index appropriés selon le nom de la table.
        
        Args:
            conn: Connexion DuckDB
            table_name: Nom de la table
            columns: Liste des colonnes
        """
        try:
            # Index spécifiques selon le type de table
            if 'interactions' in table_name.lower():
                if 'user_id' in columns:
                    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_user_id ON {table_name}(user_id)")
                if 'recipe_id' in columns:
                    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_recipe_id ON {table_name}(recipe_id)")
                if 'date' in columns:
                    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name}(date)")
                    
            elif 'users' in table_name.lower():
                if 'u' in columns:
                    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_u ON {table_name}(u)")
                    
            logger.debug(f"Created indexes for table {table_name}")
            
        except Exception as e:
            logger.warning(f"Error creating indexes for {table_name}: {e}")
    
    @st.cache_data
    def execute_query(_self, query: str, **params) -> pd.DataFrame:
        """
        Exécute une requête SQL et retourne un DataFrame pandas.
        
        Args:
            query: Requête SQL à exécuter
            **params: Paramètres de la requête
            
        Returns:
            DataFrame avec les résultats
        """
        try:
            with _self.get_connection() as conn:
                logger.debug(f"Executing query: {query[:100]}...")
                
                # Préparer la requête avec les paramètres
                if params:
                    for key, value in params.items():
                        query = query.replace(f":{key}", str(value))
                
                result = conn.execute(query).df()
                logger.debug(f"Query returned {len(result)} rows")
                return result
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Obtient des informations sur une table.
        
        Args:
            table_name: Nom de la table
            
        Returns:
            Dictionnaire avec les informations de la table
        """
        try:
            with self.get_connection() as conn:
                # Informations de base
                info_query = f"DESCRIBE {table_name}"
                schema = conn.execute(info_query).df()
                
                # Nombre de lignes
                count_query = f"SELECT COUNT(*) as count FROM {table_name}"
                count = conn.execute(count_query).fetchone()[0]
                
                return {
                    "table_name": table_name,
                    "row_count": count,
                    "schema": schema.to_dict('records')
                }
                
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {}
    
    def list_tables(self) -> List[str]:
        """
        Liste toutes les tables de la base de données.
        
        Returns:
            Liste des noms de tables
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute("SHOW TABLES").df()
                return result['name'].tolist() if 'name' in result.columns else []
                
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []
    
    def initialize_from_csvs(self, data_dir: str) -> bool:
        """
        Initialise la base de données à partir des fichiers CSV.
        
        Args:
            data_dir: Répertoire contenant les fichiers CSV
            
        Returns:
            True si l'initialisation a réussi
        """
        data_path = Path(data_dir)
        
        if not data_path.exists():
            logger.error(f"Data directory {data_dir} does not exist")
            return False
        
        # Mapping des fichiers CSV vers les noms de tables
        csv_files = {
            "interactions_train.csv": "interactions_train",
            "interactions_test.csv": "interactions_test", 
            "interactions_validation.csv": "interactions_validation",
            "PP_users.csv": "users"
        }
        
        success = True
        for csv_file, table_name in csv_files.items():
            csv_path = data_path / csv_file
            if csv_path.exists():
                if not self.load_csv_to_db(str(csv_path), table_name):
                    success = False
            else:
                logger.warning(f"CSV file not found: {csv_path}")
        
        if success:
            logger.info("Database initialization completed successfully")
        else:
            logger.error("Database initialization completed with errors")
            
        return success


# Instance globale avec cache Streamlit
@st.cache_resource
def get_database_manager() -> DatabaseManager:
    """Retourne une instance cachée du gestionnaire de base de données."""
    return DatabaseManager()


# Requêtes prédéfinies pour l'analyse
class QueryTemplates:
    """Templates de requêtes SQL fréquemment utilisées."""
    
    @staticmethod
    def get_user_stats() -> str:
        """Statistiques des utilisateurs."""
        return """
        SELECT 
            COUNT(*) as total_users,
            AVG(n_ratings) as avg_ratings_per_user,
            AVG(n_items) as avg_items_per_user,
            MAX(n_ratings) as max_ratings_per_user
        FROM users
        """
    
    @staticmethod
    def get_recipe_popularity() -> str:
        """Popularité des recettes."""
        return """
        SELECT 
            recipe_id,
            COUNT(*) as interaction_count,
            AVG(rating) as avg_rating,
            MIN(date) as first_interaction,
            MAX(date) as last_interaction
        FROM interactions_train
        WHERE rating IS NOT NULL
        GROUP BY recipe_id
        ORDER BY interaction_count DESC
        LIMIT 100
        """
    
    @staticmethod
    def get_rating_distribution() -> str:
        """Distribution des notes."""
        return """
        SELECT 
            rating,
            COUNT(*) as count,
            COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
        FROM interactions_train
        WHERE rating IS NOT NULL
        GROUP BY rating
        ORDER BY rating
        """
    
    @staticmethod
    def get_user_activity_over_time() -> str:
        """Activité des utilisateurs dans le temps."""
        return """
        SELECT 
            DATE_TRUNC('month', CAST(date AS DATE)) as month,
            COUNT(DISTINCT user_id) as active_users,
            COUNT(*) as total_interactions
        FROM interactions_train
        GROUP BY DATE_TRUNC('month', CAST(date AS DATE))
        ORDER BY month
        """
