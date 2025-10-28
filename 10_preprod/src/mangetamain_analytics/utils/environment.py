"""Détection d'environnement centralisée."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional


class Environment(Enum):
    """Environnements d'exécution possibles."""

    PREPROD = "preprod"
    PROD = "prod"
    LOCAL = "local"


class EnvironmentDetector:
    """Détecteur d'environnement avec cache."""

    _cached_env: Optional[Environment] = None

    @classmethod
    def detect(cls) -> Environment:
        """
        Détecte l'environnement d'exécution.

        Priorités:
        1. Variable APP_ENV (Docker - 99% des cas)
        2. Path courant (10_preprod vs 20_prod - dev local)
        3. Fallback : LOCAL

        Returns:
            Environment détecté

        Examples:
            >>> EnvironmentDetector.detect()
            <Environment.PREPROD: 'preprod'>
        """
        if cls._cached_env:
            return cls._cached_env

        # Priority 1: Variable d'environnement (Docker)
        app_env = os.getenv("APP_ENV", "").lower()
        if app_env == "preprod":
            cls._cached_env = Environment.PREPROD
            return cls._cached_env
        if app_env == "prod":
            cls._cached_env = Environment.PROD
            return cls._cached_env

        # Priority 2: Current working directory (dev local)
        current_path = str(Path.cwd())
        if "10_preprod" in current_path:
            cls._cached_env = Environment.PREPROD
        elif "20_prod" in current_path:
            cls._cached_env = Environment.PROD
        else:
            cls._cached_env = Environment.LOCAL

        return cls._cached_env

    @classmethod
    def get_name(cls) -> str:
        """
        Retourne le nom de l'environnement.

        Returns:
            Nom de l'environnement (string)

        Examples:
            >>> EnvironmentDetector.get_name()
            'PREPROD'
        """
        return cls.detect().value.upper()

    @classmethod
    def reset_cache(cls) -> None:
        """
        Réinitialise le cache (utile pour les tests).

        Examples:
            >>> EnvironmentDetector.reset_cache()
        """
        cls._cached_env = None
