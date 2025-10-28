"""
Tests unitaires pour les exceptions personnalisées.

Ce module teste la hiérarchie d'exceptions personnalisées de l'application
Mangetamain Analytics, conformément aux exigences académiques.
"""

import pytest
from src.mangetamain_analytics.exceptions import (
    MangetamainError,
    DataLoadError,
    AnalysisError,
    ConfigurationError,
    DatabaseError,
    ValidationError,
)


class TestMangetamainError:
    """Tests pour l'exception de base MangetamainError."""

    def test_mangetamain_error_is_exception(self):
        """Vérifie que MangetamainError hérite d'Exception."""
        assert issubclass(MangetamainError, Exception)

    def test_mangetamain_error_message(self):
        """Vérifie qu'on peut créer MangetamainError avec un message."""
        error = MangetamainError("Une erreur test")
        assert str(error) == "Une erreur test"

    def test_mangetamain_error_can_be_raised(self):
        """Vérifie qu'on peut lever MangetamainError."""
        with pytest.raises(MangetamainError) as exc_info:
            raise MangetamainError("Test error")
        assert "Test error" in str(exc_info.value)

    def test_mangetamain_error_catch_all_custom_exceptions(self):
        """Vérifie que MangetamainError capture toutes les exceptions custom."""
        # Toutes les exceptions custom doivent hériter de MangetamainError
        with pytest.raises(MangetamainError):
            raise DataLoadError(source="test", detail="test")


class TestDataLoadError:
    """Tests pour DataLoadError."""

    def test_data_load_error_inheritance(self):
        """Vérifie que DataLoadError hérite de MangetamainError."""
        assert issubclass(DataLoadError, MangetamainError)
        assert issubclass(DataLoadError, Exception)

    def test_data_load_error_attributes(self):
        """Vérifie que DataLoadError stocke source et detail."""
        error = DataLoadError(source="S3", detail="Bucket introuvable")
        assert error.source == "S3"
        assert error.detail == "Bucket introuvable"
        assert "S3" in str(error)
        assert "Bucket introuvable" in str(error)

    def test_data_load_error_message_format(self):
        """Vérifie le format du message d'erreur."""
        error = DataLoadError(source="DuckDB", detail="Fichier corrompu")
        expected = "Échec chargement depuis DuckDB: Fichier corrompu"
        assert str(error) == expected

    def test_data_load_error_can_be_caught(self):
        """Vérifie qu'on peut capturer DataLoadError spécifiquement."""
        with pytest.raises(DataLoadError) as exc_info:
            raise DataLoadError(source="S3", detail="Test")
        assert exc_info.value.source == "S3"
        assert exc_info.value.detail == "Test"

    def test_data_load_error_caught_by_mangetamain_error(self):
        """Vérifie que DataLoadError est capturée par MangetamainError."""
        with pytest.raises(MangetamainError):
            raise DataLoadError(source="S3", detail="Test")


class TestAnalysisError:
    """Tests pour AnalysisError."""

    def test_analysis_error_inheritance(self):
        """Vérifie que AnalysisError hérite de MangetamainError."""
        assert issubclass(AnalysisError, MangetamainError)

    def test_analysis_error_message(self):
        """Vérifie qu'on peut créer AnalysisError avec un message."""
        error = AnalysisError("Calcul de tendance impossible")
        assert "Calcul de tendance impossible" in str(error)

    def test_analysis_error_can_be_raised(self):
        """Vérifie qu'on peut lever AnalysisError."""
        with pytest.raises(AnalysisError):
            raise AnalysisError("Données insuffisantes")


class TestConfigurationError:
    """Tests pour ConfigurationError."""

    def test_configuration_error_inheritance(self):
        """Vérifie que ConfigurationError hérite de MangetamainError."""
        assert issubclass(ConfigurationError, MangetamainError)

    def test_configuration_error_message(self):
        """Vérifie qu'on peut créer ConfigurationError avec un message."""
        error = ConfigurationError("Variable S3_BUCKET_NAME manquante")
        assert "S3_BUCKET_NAME" in str(error)

    def test_configuration_error_can_be_raised(self):
        """Vérifie qu'on peut lever ConfigurationError."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Config invalide")


class TestDatabaseError:
    """Tests pour DatabaseError."""

    def test_database_error_inheritance(self):
        """Vérifie que DatabaseError hérite de MangetamainError."""
        assert issubclass(DatabaseError, MangetamainError)

    def test_database_error_message(self):
        """Vérifie qu'on peut créer DatabaseError avec un message."""
        error = DatabaseError("Table 'recipes' introuvable")
        assert "recipes" in str(error)

    def test_database_error_can_be_raised(self):
        """Vérifie qu'on peut lever DatabaseError."""
        with pytest.raises(DatabaseError):
            raise DatabaseError("Erreur SQL")


class TestValidationError:
    """Tests pour ValidationError."""

    def test_validation_error_inheritance(self):
        """Vérifie que ValidationError hérite de MangetamainError."""
        assert issubclass(ValidationError, MangetamainError)

    def test_validation_error_message(self):
        """Vérifie qu'on peut créer ValidationError avec un message."""
        error = ValidationError("Date invalide: 2025-13-45")
        assert "2025-13-45" in str(error)

    def test_validation_error_can_be_raised(self):
        """Vérifie qu'on peut lever ValidationError."""
        with pytest.raises(ValidationError):
            raise ValidationError("Valeur hors limites")


class TestExceptionHierarchy:
    """Tests pour vérifier la hiérarchie complète des exceptions."""

    def test_all_custom_exceptions_inherit_from_base(self):
        """Vérifie que toutes les exceptions custom héritent de MangetamainError."""
        custom_exceptions = [
            DataLoadError,
            AnalysisError,
            ConfigurationError,
            DatabaseError,
            ValidationError,
        ]

        for exc_class in custom_exceptions:
            # Créer une instance avec les arguments appropriés
            if exc_class == DataLoadError:
                instance = exc_class(source="test", detail="test")
            else:
                instance = exc_class("test")

            assert isinstance(instance, MangetamainError)
            assert isinstance(instance, Exception)

    def test_catch_multiple_exception_types(self):
        """Vérifie qu'on peut capturer plusieurs types d'exceptions."""
        # DataLoadError
        with pytest.raises((DataLoadError, DatabaseError)):
            raise DataLoadError(source="S3", detail="Test")

        # DatabaseError
        with pytest.raises((DataLoadError, DatabaseError)):
            raise DatabaseError("SQL error")

    def test_exception_specificity(self):
        """Vérifie que les exceptions spécifiques sont capturées avant la base."""
        caught_specific = False
        caught_base = False

        try:
            raise DataLoadError(source="S3", detail="Test")
        except DataLoadError:
            caught_specific = True
        except MangetamainError:
            caught_base = True

        assert caught_specific
        assert not caught_base

    def test_all_exceptions_are_unique(self):
        """Vérifie que chaque exception est une classe distincte."""
        exceptions = [
            MangetamainError,
            DataLoadError,
            AnalysisError,
            ConfigurationError,
            DatabaseError,
            ValidationError,
        ]

        # Vérifier qu'aucune classe n'est identique à une autre
        for i, exc1 in enumerate(exceptions):
            for j, exc2 in enumerate(exceptions):
                if i != j:
                    assert exc1 is not exc2
