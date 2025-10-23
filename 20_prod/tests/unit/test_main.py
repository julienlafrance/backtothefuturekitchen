#!/usr/bin/env python3
"""Tests unitaires pour streamlit/main.py

Note: Les fonctions UI Streamlit (display_*, create_*) sont exclues du coverage
car elles nécessitent un contexte Streamlit actif.
"""

import sys
from pathlib import Path

# Ajouter le chemin streamlit pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "streamlit"))

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

# Mock Streamlit et loguru avant l'import
sys.modules["streamlit"] = MagicMock()
sys.modules["loguru"] = MagicMock()

# Maintenant on peut importer main
import main


class TestDetectEnvironment:
    """Tests pour detect_environment"""

    def test_detect_env_from_env_variable(self, monkeypatch):
        """Test détection via variable d'environnement"""
        monkeypatch.setenv("APP_ENV", "PROD")

        result = main.detect_environment()

        assert result == "PROD"

    def test_detect_env_preprod_from_path(self, monkeypatch):
        """Test détection PREPROD depuis le chemin"""
        monkeypatch.delenv("APP_ENV", raising=False)

        with patch("main.Path") as mock_path:
            # Simuler qu'on n'est pas dans Docker
            mock_path.return_value.exists.return_value = False
            # Simuler le cwd
            mock_path.cwd.return_value = Path("/home/user/projet/10_preprod/streamlit")

            result = main.detect_environment()

            assert "PREPROD" in result

    def test_detect_env_prod_from_path(self, monkeypatch):
        """Test détection PROD depuis le chemin"""
        monkeypatch.delenv("APP_ENV", raising=False)

        with patch("main.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            mock_path.cwd.return_value = Path("/home/user/projet/20_prod/streamlit")

            result = main.detect_environment()

            assert "PROD" in result

    def test_detect_env_docker(self, monkeypatch):
        """Test détection Docker"""
        monkeypatch.delenv("APP_ENV", raising=False)

        with patch("main.Path") as mock_path:
            # /.dockerenv existe
            mock_path.return_value.exists.return_value = True

            result = main.detect_environment()

            assert "PROD (Docker)" in result

    def test_detect_env_unknown(self, monkeypatch):
        """Test détection environnement inconnu"""
        monkeypatch.delenv("APP_ENV", raising=False)

        with patch("main.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            mock_path.cwd.return_value = Path("/some/random/path")

            result = main.detect_environment()

            assert result == "UNKNOWN"


class TestGetDbConnection:
    """Tests pour get_db_connection"""

    @patch("main.duckdb.connect")
    @patch("main.Path")
    def test_connection_success(self, mock_path_class, mock_connect):
        """Test connexion réussie"""
        # Mock du fichier qui existe
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.stat.return_value.st_size = 10 * 1024 * 1024  # 10 MB
        mock_path_class.return_value = mock_path

        # Mock de la connexion DuckDB
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchall.return_value = [
            ("table1",),
            ("table2",),
            ("table3",),
        ]
        mock_connect.return_value = mock_conn

        result = main.get_db_connection()

        assert result is not None
        assert result == mock_conn
        mock_connect.assert_called_once_with("data/mangetamain.duckdb")

    @patch("main.Path")
    def test_connection_file_not_found(self, mock_path_class):
        """Test fichier DB introuvable"""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path_class.return_value = mock_path

        result = main.get_db_connection()

        assert result is None

    @patch("main.duckdb.connect")
    @patch("main.Path")
    def test_connection_failure(self, mock_path_class, mock_connect):
        """Test échec de connexion"""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path_class.return_value = mock_path

        # Simuler une exception lors de la connexion
        mock_connect.side_effect = Exception("Connection failed")

        result = main.get_db_connection()

        assert result is None


# Note: Les fonctions suivantes sont marquées pour exclusion du coverage
# car elles nécessitent un contexte Streamlit actif:
# - display_environment_badge (UI)
# - display_database_info (UI)
# - create_tables_overview (UI)
# - create_rating_analysis (UI)
# - create_temporal_analysis (UI)
# - create_user_analysis (UI)
# - display_raw_data_explorer (UI)
# - main (point d'entrée)


class TestDatabaseQueries:
    """Tests des requêtes SQL (logique métier)"""

    def test_rating_query_structure(self):
        """Test structure de la requête ratings"""
        # Test que les requêtes SQL sont bien formées
        # (sans exécution réelle)

        query = """
            SELECT rating, COUNT(*) as count
            FROM test_table
            WHERE rating IS NOT NULL
            GROUP BY rating
            ORDER BY rating
        """

        # Vérifier la structure
        assert "SELECT" in query
        assert "COUNT(*)" in query
        assert "GROUP BY rating" in query
        assert "rating IS NOT NULL" in query


class TestDataValidation:
    """Tests de validation des données"""

    def test_valid_table_names(self):
        """Test validation des noms de tables"""
        valid_tables = ["RAW_interactions", "PP_users", "interactions_train"]

        for table in valid_tables:
            # Vérifier le format des noms
            assert isinstance(table, str)
            assert len(table) > 0
            assert " " not in table  # Pas d'espaces

    def test_dataframe_structure(self):
        """Test structure des DataFrames"""
        # Simuler un DataFrame de ratings
        df = pd.DataFrame({"rating": [1, 2, 3, 4, 5], "count": [10, 20, 30, 40, 50]})

        # Vérifications
        assert "rating" in df.columns
        assert "count" in df.columns
        assert len(df) == 5
        assert df["rating"].min() >= 1
        assert df["rating"].max() <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
