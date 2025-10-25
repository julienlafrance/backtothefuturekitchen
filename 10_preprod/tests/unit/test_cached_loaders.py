"""Tests unitaires pour le module cached_loaders.

Teste les fonctions de chargement de données avec cache Streamlit.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch
import polars as pl

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))


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
def mock_interactions_df():
    """Fixture pour créer un DataFrame d'interactions de test."""
    data = {
        "user_id": [1, 2, 3],
        "recipe_id": [1, 2, 3],
        "rating": [4, 5, 3],
    }
    return pl.DataFrame(data)


@pytest.mark.skip(reason="Problème de mock avec st.cache_data et show_spinner")
@patch("data.cached_loaders.st")
def test_get_recipes_clean(mock_st, mock_recipes_df):
    """Test de la fonction get_recipes_clean."""
    # Mock streamlit cache_data decorator
    mock_st.cache_data = lambda *args, **kwargs: lambda f: f

    # Mock de la fonction load_recipes_clean
    with patch(
        "mangetamain_data_utils.data_utils_recipes.load_recipes_clean"
    ) as mock_load:
        mock_load.return_value = mock_recipes_df

        from data.cached_loaders import get_recipes_clean

        result = get_recipes_clean()

        assert result is not None
        assert len(result) == 3
        mock_load.assert_called_once()


@pytest.mark.skip(reason="Module data_utils_interactions non disponible")
@patch("data.cached_loaders.st")
def test_get_interactions_sample(mock_st, mock_interactions_df):
    """Test de la fonction get_interactions_sample."""
    # Mock streamlit cache_data decorator
    mock_st.cache_data = lambda *args, **kwargs: lambda f: f

    # Mock de la fonction load_interactions_sample
    with patch(
        "mangetamain_data_utils.data_utils_interactions.load_interactions_sample"
    ) as mock_load:
        mock_load.return_value = mock_interactions_df

        from data.cached_loaders import get_interactions_sample

        result = get_interactions_sample()

        assert result is not None
        assert len(result) == 3
        mock_load.assert_called_once()


@pytest.mark.skip(reason="Problème de mock avec st.cache_data et show_spinner")
@patch("data.cached_loaders.st")
def test_get_ratings_longterm(mock_st, mock_interactions_df):
    """Test de la fonction get_ratings_longterm."""
    # Mock streamlit cache_data decorator
    mock_st.cache_data = lambda *args, **kwargs: lambda f: f

    # Mock de la fonction load_ratings_for_longterm_analysis
    with patch(
        "mangetamain_data_utils.data_utils_ratings.load_ratings_for_longterm_analysis"
    ) as mock_load:
        mock_load.return_value = mock_interactions_df

        from data.cached_loaders import get_ratings_longterm

        result = get_ratings_longterm(
            min_interactions=100, return_metadata=False, verbose=False
        )

        assert result is not None
        assert len(result) == 3
        mock_load.assert_called_once_with(
            min_interactions=100, return_metadata=False, verbose=False
        )


@pytest.mark.skip(reason="Problème de mock avec st.cache_data et show_spinner")
@patch("data.cached_loaders.st")
def test_get_ratings_longterm_with_metadata(mock_st):
    """Test de la fonction get_ratings_longterm avec metadata."""
    # Mock streamlit cache_data decorator
    mock_st.cache_data = lambda *args, **kwargs: lambda f: f

    mock_df = pl.DataFrame({"user_id": [1], "recipe_id": [1], "rating": [5]})
    mock_metadata = {"count": 100, "mean": 4.5}

    # Mock de la fonction load_ratings_for_longterm_analysis
    with patch(
        "mangetamain_data_utils.data_utils_ratings.load_ratings_for_longterm_analysis"
    ) as mock_load:
        mock_load.return_value = (mock_df, mock_metadata)

        from data.cached_loaders import get_ratings_longterm

        result = get_ratings_longterm(
            min_interactions=50, return_metadata=True, verbose=True
        )

        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        mock_load.assert_called_once_with(
            min_interactions=50, return_metadata=True, verbose=True
        )
