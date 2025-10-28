"""
Exceptions personnalisées pour Mangetamain Analytics.

Ce module définit une hiérarchie d'exceptions personnalisées pour améliorer
la gestion des erreurs dans l'application. Toutes les exceptions héritent
de MangetamainError pour permettre une capture globale si nécessaire.

Conformément aux exigences académiques du projet, ces exceptions permettent
de distinguer les différents types d'erreurs et d'améliorer le debugging.
"""

from typing import Optional


class MangetamainError(Exception):
    """
    Exception de base pour toutes les erreurs de l'application Mangetamain.

    Toutes les exceptions personnalisées de l'application héritent de cette
    classe de base, permettant une capture globale avec `except MangetamainError`.

    Examples:
        >>> try:
        ...     raise MangetamainError("Une erreur s'est produite")
        ... except MangetamainError as e:
        ...     print(f"Erreur capturée: {e}")
    """

    pass


class DataLoadError(MangetamainError):
    """
    Erreur lors du chargement de données depuis S3, DuckDB ou fichiers locaux.

    Cette exception est levée lorsqu'une erreur se produit pendant le chargement
    de données, que ce soit depuis AWS S3, une base DuckDB, ou des fichiers locaux.

    Attributes:
        source: Source de données concernée (ex: "S3", "DuckDB", "local")
        detail: Détails supplémentaires sur l'erreur
        message: Message d'erreur complet

    Examples:
        >>> raise DataLoadError(
        ...     source="S3",
        ...     detail="Bucket introuvable: food-com-data"
        ... )
    """

    def __init__(self, source: str, detail: str) -> None:
        """
        Initialise l'exception DataLoadError.

        Args:
            source: Source de données (S3, DuckDB, local, etc.)
            detail: Description détaillée de l'erreur
        """
        self.source = source
        self.detail = detail
        self.message = f"Échec chargement depuis {source}: {detail}"
        super().__init__(self.message)

    def __str__(self) -> str:
        """Retourne une représentation lisible de l'erreur."""
        return self.message


class AnalysisError(MangetamainError):
    """
    Erreur lors de l'exécution d'une analyse statistique ou de calculs.

    Cette exception est levée lorsqu'une erreur se produit pendant l'analyse
    des données (calculs statistiques, tendances, saisonnalité, ratings, etc.).

    Examples:
        >>> raise AnalysisError("Impossible de calculer la tendance: données insuffisantes")
    """

    pass


class ConfigurationError(MangetamainError):
    """
    Erreur de configuration de l'application.

    Cette exception est levée lorsqu'une configuration invalide est détectée
    (paramètres manquants, valeurs incorrectes, fichiers de config absents, etc.).

    Examples:
        >>> raise ConfigurationError("Variable S3_BUCKET_NAME non définie")
    """

    pass


class DatabaseError(MangetamainError):
    """
    Erreur lors des opérations avec la base de données DuckDB.

    Cette exception est levée lors d'erreurs SQL, de connexion, ou de transactions
    avec la base de données DuckDB.

    Examples:
        >>> raise DatabaseError("Erreur SQL: table 'recipes' introuvable")
    """

    pass


class ValidationError(MangetamainError):
    """
    Erreur de validation des données.

    Cette exception est levée lorsque des données ne respectent pas les contraintes
    attendues (format incorrect, valeurs hors limites, types incompatibles, etc.).

    Examples:
        >>> raise ValidationError("Date invalide: '2025-13-45' n'est pas une date valide")
    """

    pass
