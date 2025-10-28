"""Tests unitaires pour la classe DataLoader.

Teste le chargement de données avec gestion d'erreurs personnalisées.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch
import polars as pl

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from data.loaders import DataLoader

# Import depuis le même chemin que loaders.py pour cohérence
try:
    from exceptions import DataLoadError, MangetamainError
except ImportError:
    from src.mangetamain_analytics.exceptions import DataLoadError, MangetamainError


@pytest.fixture
def loader():
    """Fixture pour créer une instance de DataLoader."""
    return DataLoader()


@pytest.fixture
def mock_recipes_df():
    """Fixture pour créer un DataFrame de recettes de test."""
    data = {
        "id": [1, 2, 3],
        "name": ["Recipe 1", "Recipe 2", "Recipe 3"],
        "minutes": [30, 45, 60],
    }
    return pl.DataFrame(data)


@pytest.fixture
def mock_ratings_df():
    """Fixture pour créer un DataFrame de ratings de test."""
    data = {
        "user_id": [1, 2, 3],
        "recipe_id": [1, 2, 3],
        "rating": [4, 5, 3],
    }
    return pl.DataFrame(data)


class TestDataLoaderRecipes:
    """Tests pour le chargement des recettes."""

    @patch("mangetamain_data_utils.data_utils_recipes.load_recipes_clean")
    def test_load_recipes_success(self, mock_load, loader, mock_recipes_df):
        """Vérifie que load_recipes retourne les données correctement."""
        mock_load.return_value = mock_recipes_df

        result = loader.load_recipes()

        assert result is not None
        assert len(result) == 3
        mock_load.assert_called_once()

    @patch("mangetamain_data_utils.data_utils_recipes.load_recipes_clean")
    def test_load_recipes_raises_dataload_error_on_s3_failure(self, mock_load, loader):
        """Vérifie que DataLoadError est levée si S3 échoue."""
        mock_load.side_effect = Exception("S3 bucket not accessible")

        with pytest.raises(DataLoadError) as exc_info:
            loader.load_recipes()

        assert exc_info.value.source == "S3 (recipes)"
        assert "Échec chargement recettes" in exc_info.value.detail
        assert "S3 bucket not accessible" in str(exc_info.value)

    def test_load_recipes_raises_dataload_error_on_import_error(self, loader):
        """Vérifie que DataLoadError est levée si le module est introuvable."""
        with patch("builtins.__import__", side_effect=ImportError("Module not found")):
            with pytest.raises(DataLoadError) as exc_info:
                loader.load_recipes()

            assert exc_info.value.source == "module mangetamain_data_utils"
            assert "Module introuvable" in exc_info.value.detail


class TestDataLoaderRatings:
    """Tests pour le chargement des ratings."""

    @patch(
        "mangetamain_data_utils.data_utils_ratings.load_ratings_for_longterm_analysis"
    )
    def test_load_ratings_success(self, mock_load, loader, mock_ratings_df):
        """Vérifie que load_ratings retourne les données correctement."""
        mock_load.return_value = mock_ratings_df

        result = loader.load_ratings()

        assert result is not None
        assert len(result) == 3
        mock_load.assert_called_once_with(
            min_interactions=100, return_metadata=False, verbose=False
        )

    @patch(
        "mangetamain_data_utils.data_utils_ratings.load_ratings_for_longterm_analysis"
    )
    def test_load_ratings_with_parameters(self, mock_load, loader, mock_ratings_df):
        """Vérifie que load_ratings accepte les paramètres correctement."""
        mock_load.return_value = mock_ratings_df

        result = loader.load_ratings(min_interactions=50, verbose=True)

        assert result is not None
        mock_load.assert_called_once_with(
            min_interactions=50, return_metadata=False, verbose=True
        )

    @patch(
        "mangetamain_data_utils.data_utils_ratings.load_ratings_for_longterm_analysis"
    )
    def test_load_ratings_with_metadata(self, mock_load, loader):
        """Vérifie que load_ratings retourne metadata si demandé."""
        mock_data = pl.DataFrame({"user_id": [1], "rating": [5]})
        mock_metadata = {"count": 100, "mean": 4.5}
        mock_load.return_value = (mock_data, mock_metadata)

        result = loader.load_ratings(return_metadata=True)

        assert isinstance(result, tuple)
        assert len(result) == 2
        mock_load.assert_called_once_with(
            min_interactions=100, return_metadata=True, verbose=False
        )

    @patch(
        "mangetamain_data_utils.data_utils_ratings.load_ratings_for_longterm_analysis"
    )
    def test_load_ratings_raises_dataload_error_on_s3_failure(self, mock_load, loader):
        """Vérifie que DataLoadError est levée si S3 échoue."""
        mock_load.side_effect = Exception("Connection timeout")

        with pytest.raises(DataLoadError) as exc_info:
            loader.load_ratings()

        assert exc_info.value.source == "S3 (ratings)"
        assert "Échec chargement ratings" in exc_info.value.detail
        assert "Connection timeout" in str(exc_info.value)

    def test_load_ratings_raises_dataload_error_on_import_error(self, loader):
        """Vérifie que DataLoadError est levée si le module est introuvable."""
        with patch("builtins.__import__", side_effect=ImportError("Module not found")):
            with pytest.raises(DataLoadError) as exc_info:
                loader.load_ratings()

            assert exc_info.value.source == "module mangetamain_data_utils"
            assert "Module introuvable" in exc_info.value.detail


class TestDataLoaderExceptionIntegration:
    """Tests d'intégration pour la gestion des exceptions."""

    def test_dataload_error_is_catchable_as_mangetamain_error(self, loader):
        """Vérifie que DataLoadError peut être capturée comme MangetamainError."""
        with patch(
            "mangetamain_data_utils.data_utils_recipes.load_recipes_clean"
        ) as mock_load:
            mock_load.side_effect = Exception("Test error")

            with pytest.raises(MangetamainError):
                loader.load_recipes()

    def test_dataload_error_attributes_are_preserved(self, loader):
        """Vérifie que les attributs source et detail sont préservés."""
        with patch(
            "mangetamain_data_utils.data_utils_recipes.load_recipes_clean"
        ) as mock_load:
            mock_load.side_effect = Exception("Test error")

            with pytest.raises(DataLoadError) as exc_info:
                loader.load_recipes()

            # Vérifier attributs
            assert hasattr(exc_info.value, "source")
            assert hasattr(exc_info.value, "detail")
            assert exc_info.value.source == "S3 (recipes)"
            assert "Test error" in exc_info.value.detail
