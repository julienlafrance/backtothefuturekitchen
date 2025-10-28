"""Classes pour le chargement de données avec gestion d'erreurs.

Ce module contient les classes pour charger les données depuis S3/DuckDB
avec une gestion robuste des exceptions personnalisées.
"""

from typing import Any

try:
    from exceptions import DataLoadError
except ImportError:
    from mangetamain_analytics.exceptions import DataLoadError


class DataLoader:
    """Classe pour charger les données avec gestion d'erreurs robuste.

    Cette classe encapsule la logique de chargement de données depuis
    mangetamain_data_utils avec gestion appropriée des exceptions.

    Examples:
        >>> loader = DataLoader()
        >>> recipes = loader.load_recipes()
        >>> ratings = loader.load_ratings(min_interactions=100)
    """

    def load_recipes(self):
        """Charge les recettes depuis S3.

        Returns:
            DataFrame Polars avec les recettes

        Raises:
            DataLoadError: Si le module est introuvable ou si le chargement échoue
        """
        try:
            from mangetamain_data_utils.data_utils_recipes import load_recipes_clean
        except ImportError as e:
            raise DataLoadError(
                source="module mangetamain_data_utils",
                detail=f"Module introuvable: {e}"
            )

        try:
            return load_recipes_clean()
        except Exception as e:
            raise DataLoadError(
                source="S3 (recipes)",
                detail=f"Échec chargement recettes: {e}"
            )

    def load_ratings(
        self,
        min_interactions: int = 100,
        return_metadata: bool = False,
        verbose: bool = False
    ) -> Any:
        """Charge les ratings pour analyse long-terme depuis S3.

        Args:
            min_interactions: Nombre minimum d'interactions requises
            return_metadata: Si True, retourne (data, metadata)
            verbose: Mode verbeux

        Returns:
            DataFrame Polars avec les ratings (ou tuple si return_metadata=True)

        Raises:
            DataLoadError: Si le module est introuvable ou si le chargement échoue
        """
        try:
            from mangetamain_data_utils.data_utils_ratings import (
                load_ratings_for_longterm_analysis,
            )
        except ImportError as e:
            raise DataLoadError(
                source="module mangetamain_data_utils",
                detail=f"Module introuvable: {e}"
            )

        try:
            return load_ratings_for_longterm_analysis(
                min_interactions=min_interactions,
                return_metadata=return_metadata,
                verbose=verbose,
            )
        except Exception as e:
            raise DataLoadError(
                source="S3 (ratings)",
                detail=f"Échec chargement ratings: {e}"
            )
