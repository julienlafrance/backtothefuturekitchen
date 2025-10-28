"""Tests pour le module utils.environment."""

from mangetamain_analytics.utils.environment import Environment, EnvironmentDetector


class TestEnvironment:
    """Tests pour l'enum Environment."""

    def test_environment_values(self):
        """Vérifie les valeurs de l'enum Environment."""
        assert Environment.PREPROD.value == "preprod"
        assert Environment.PROD.value == "prod"
        assert Environment.LOCAL.value == "local"


class TestEnvironmentDetector:
    """Tests pour la classe EnvironmentDetector."""

    def setup_method(self):
        """Réinitialise le cache avant chaque test."""
        EnvironmentDetector.reset_cache()

    def test_detect_from_env_var_preprod(self, monkeypatch):
        """Vérifie détection depuis APP_ENV=preprod."""
        monkeypatch.setenv("APP_ENV", "preprod")
        env = EnvironmentDetector.detect()
        assert env == Environment.PREPROD

    def test_detect_from_env_var_prod(self, monkeypatch):
        """Vérifie détection depuis APP_ENV=prod."""
        monkeypatch.setenv("APP_ENV", "prod")
        env = EnvironmentDetector.detect()
        assert env == Environment.PROD

    def test_detect_from_env_var_uppercase(self, monkeypatch):
        """Vérifie détection avec APP_ENV en majuscules."""
        monkeypatch.setenv("APP_ENV", "PREPROD")
        env = EnvironmentDetector.detect()
        assert env == Environment.PREPROD

    def test_detect_from_path_preprod(self, tmp_path, monkeypatch):
        """Vérifie détection depuis path contenant 10_preprod."""
        monkeypatch.delenv("APP_ENV", raising=False)
        preprod_path = tmp_path / "10_preprod" / "src"
        preprod_path.mkdir(parents=True)
        monkeypatch.chdir(preprod_path)

        EnvironmentDetector.reset_cache()
        env = EnvironmentDetector.detect()
        assert env == Environment.PREPROD

    def test_detect_from_path_prod(self, tmp_path, monkeypatch):
        """Vérifie détection depuis path contenant 20_prod."""
        monkeypatch.delenv("APP_ENV", raising=False)
        prod_path = tmp_path / "20_prod" / "src"
        prod_path.mkdir(parents=True)
        monkeypatch.chdir(prod_path)

        EnvironmentDetector.reset_cache()
        env = EnvironmentDetector.detect()
        assert env == Environment.PROD

    def test_detect_fallback_local(self, tmp_path, monkeypatch):
        """Vérifie fallback vers LOCAL si aucune détection."""
        monkeypatch.delenv("APP_ENV", raising=False)
        local_path = tmp_path / "somewhere"
        local_path.mkdir()
        monkeypatch.chdir(local_path)

        EnvironmentDetector.reset_cache()
        env = EnvironmentDetector.detect()
        assert env == Environment.LOCAL

    def test_priority_env_var_over_path(self, tmp_path, monkeypatch):
        """Vérifie que APP_ENV a priorité sur le path."""
        monkeypatch.setenv("APP_ENV", "prod")
        preprod_path = tmp_path / "10_preprod"
        preprod_path.mkdir()
        monkeypatch.chdir(preprod_path)

        EnvironmentDetector.reset_cache()
        env = EnvironmentDetector.detect()
        # APP_ENV=prod devrait avoir priorité sur path=10_preprod
        assert env == Environment.PROD

    def test_cache_mechanism(self, monkeypatch):
        """Vérifie que le cache fonctionne."""
        monkeypatch.setenv("APP_ENV", "preprod")
        env1 = EnvironmentDetector.detect()

        # Changer APP_ENV après première détection
        monkeypatch.setenv("APP_ENV", "prod")
        env2 = EnvironmentDetector.detect()

        # Doit retourner la valeur cachée (preprod)
        assert env1 == env2 == Environment.PREPROD

    def test_reset_cache(self, monkeypatch):
        """Vérifie que reset_cache() fonctionne."""
        monkeypatch.setenv("APP_ENV", "preprod")
        env1 = EnvironmentDetector.detect()
        assert env1 == Environment.PREPROD

        # Réinitialiser le cache et changer environnement
        EnvironmentDetector.reset_cache()
        monkeypatch.setenv("APP_ENV", "prod")
        env2 = EnvironmentDetector.detect()

        # Doit détecter la nouvelle valeur
        assert env2 == Environment.PROD

    def test_get_name_preprod(self, monkeypatch):
        """Vérifie get_name() retourne string en majuscules."""
        monkeypatch.setenv("APP_ENV", "preprod")
        EnvironmentDetector.reset_cache()
        name = EnvironmentDetector.get_name()
        assert name == "PREPROD"
        assert isinstance(name, str)

    def test_get_name_prod(self, monkeypatch):
        """Vérifie get_name() pour PROD."""
        monkeypatch.setenv("APP_ENV", "prod")
        EnvironmentDetector.reset_cache()
        name = EnvironmentDetector.get_name()
        assert name == "PROD"

    def test_get_name_local(self, tmp_path, monkeypatch):
        """Vérifie get_name() pour LOCAL."""
        monkeypatch.delenv("APP_ENV", raising=False)
        local_path = tmp_path / "anywhere"
        local_path.mkdir()
        monkeypatch.chdir(local_path)

        EnvironmentDetector.reset_cache()
        name = EnvironmentDetector.get_name()
        assert name == "LOCAL"
