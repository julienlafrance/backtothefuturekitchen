# TODO: Refactoring Logging avec Détection Environnement

**Date**: 2025-10-28
**Problème**: LoggerConfig n'utilise pas la détection d'environnement pour différencier logs PREPROD/PROD

## Problème Actuel

### Code Existant
- ✅ `detect_environment()` existe dans `main.py` (lignes 54-72)
- ❌ `LoggerConfig` ne l'utilise PAS
- ❌ Logs identiques en PREPROD et PROD
- ❌ Tous les logs vont dans `logs/` (pas de séparation environnement)

### Comportement Actuel
```python
# utils_logger.py
log_config = LoggerConfig(log_dir="logs")  # Hardcodé !
log_config.setup_logger()
```

**Résultat**:
- PREPROD → `logs/app.log`, `logs/errors.log`
- PROD → `logs/app.log`, `logs/errors.log` (MÊME FICHIERS ! ❌)

---

## Objectif Conformité

Selon `conformite.rst` (lignes 107-128), il faut :

### Architecture Logging
- **2 fichiers par environnement** : `debug.log`, `errors.log`
- **Détection auto** : Variable `APP_ENV` ou path automatique
- **Rotation** : 10 MB (debug), 5 MB (errors) avec compression
- **Thread-safe** : `enqueue=True` pour Streamlit multithread
- **Backtrace** : Diagnostic complet des erreurs

### Différences PREPROD/PROD

| Aspect | PREPROD | PROD |
|--------|---------|------|
| **Logs debug** | ✅ Oui (`logs/preprod/debug.log`) | ❌ Non |
| **Logs erreurs** | ✅ Oui (`logs/preprod/errors.log`) | ✅ Oui (`logs/prod/errors.log`) |
| **Niveau console** | DEBUG | WARNING |
| **Rotation debug** | 10 MB | N/A |
| **Rotation errors** | 5 MB | 5 MB |
| **Retention** | 7 jours | 30 jours |

---

## Solution Proposée

### 1. Créer Classe EnvironmentDetector

**Fichier**: `src/mangetamain_analytics/utils/environment.py`

```python
"""Détection d'environnement centralisée."""

import os
from enum import Enum
from pathlib import Path
from typing import Optional


class Environment(Enum):
    """Environnements d'exécution possibles."""

    PREPROD = "PREPROD"
    PROD = "PROD"
    DOCKER = "DOCKER"
    UNKNOWN = "UNKNOWN"


class EnvironmentDetector:
    """Détecteur d'environnement avec cache."""

    _cached_env: Optional[Environment] = None

    @classmethod
    def detect(cls) -> Environment:
        """
        Détecte l'environnement d'exécution.

        Priorités:
        1. Variable APP_ENV (Docker ou manuel)
        2. Présence /.dockerenv (Docker)
        3. Path courant (10_preprod vs 20_prod)

        Returns:
            Environment détecté
        """
        if cls._cached_env:
            return cls._cached_env

        # Priority 1: Variable d'environnement
        app_env = os.getenv("APP_ENV", "").upper()
        if app_env in ("PREPROD", "PROD"):
            cls._cached_env = Environment[app_env]
            return cls._cached_env

        # Priority 2: Docker container
        if Path("/.dockerenv").exists():
            cls._cached_env = Environment.DOCKER
            return cls._cached_env

        # Priority 3: Current working directory
        current_path = str(Path.cwd())
        if "10_preprod" in current_path:
            cls._cached_env = Environment.PREPROD
        elif "20_prod" in current_path:
            cls._cached_env = Environment.PROD
        else:
            cls._cached_env = Environment.UNKNOWN

        return cls._cached_env

    @classmethod
    def is_production(cls) -> bool:
        """Retourne True si environnement de production."""
        env = cls.detect()
        return env in (Environment.PROD, Environment.DOCKER)

    @classmethod
    def is_preprod(cls) -> bool:
        """Retourne True si environnement de preprod."""
        return cls.detect() == Environment.PREPROD

    @classmethod
    def get_name(cls) -> str:
        """Retourne le nom de l'environnement."""
        return cls.detect().value
```

**Tests**:
```python
# tests/unit/test_environment.py

def test_detect_from_env_var(monkeypatch):
    monkeypatch.setenv("APP_ENV", "PROD")
    assert EnvironmentDetector.detect() == Environment.PROD

def test_detect_from_path(tmp_path, monkeypatch):
    preprod_path = tmp_path / "10_preprod"
    preprod_path.mkdir()
    monkeypatch.chdir(preprod_path)
    assert EnvironmentDetector.detect() == Environment.PREPROD

def test_is_production():
    # Avec APP_ENV=PROD
    assert EnvironmentDetector.is_production() == True
```

---

### 2. Refactorer LoggerConfig

**Fichier**: `utils_logger.py` (MODIFIÉ)

```python
"""Configuration des logs avec Loguru pour Mangetamain Analytics."""

from typing import Dict, Any, Optional
from loguru import logger
import sys
from pathlib import Path
from utils.environment import EnvironmentDetector, Environment


class LoggerConfig:
    """Configuration centralisée des logs avec Loguru."""

    def __init__(self, base_log_dir: str = "logs") -> None:
        """
        Initialise la configuration des logs.

        Args:
            base_log_dir: Répertoire racine de stockage des logs
        """
        self.base_log_dir = Path(base_log_dir)
        self.env = EnvironmentDetector.detect()

        # Créer sous-répertoire par environnement
        if self.env == Environment.PREPROD:
            self.log_dir = self.base_log_dir / "preprod"
        elif self.env in (Environment.PROD, Environment.DOCKER):
            self.log_dir = self.base_log_dir / "prod"
        else:
            self.log_dir = self.base_log_dir / "unknown"

        self.log_dir.mkdir(parents=True, exist_ok=True)

    def setup_logger(self) -> None:
        """Configure les différents handlers de logs selon l'environnement."""
        # Supprimer le handler par défaut
        logger.remove()

        # ========================================
        # CONSOLE HANDLER (différent selon env)
        # ========================================

        if self.env == Environment.PREPROD:
            # PREPROD: Console verbeux avec couleurs
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                       "<level>{message}</level>",
                level="DEBUG",
                colorize=True,
                enqueue=True  # Thread-safe pour Streamlit
            )
        else:
            # PROD: Console minimal (warnings+errors seulement)
            logger.add(
                sys.stderr,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                level="WARNING",
                colorize=False,
                enqueue=True
            )

        # ========================================
        # DEBUG LOG (PREPROD SEULEMENT)
        # ========================================

        if self.env == Environment.PREPROD:
            logger.add(
                self.log_dir / "debug.log",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level="DEBUG",
                rotation="10 MB",
                retention="7 days",
                compression="zip",
                enqueue=True,
                backtrace=True,  # Backtrace complet
                diagnose=True
            )

        # ========================================
        # ERROR LOG (PREPROD + PROD)
        # ========================================

        retention_days = "7 days" if self.env == Environment.PREPROD else "30 days"

        logger.add(
            self.log_dir / "errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="5 MB",
            retention=retention_days,
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

        # ========================================
        # USER INTERACTIONS LOG (optionnel)
        # ========================================

        logger.add(
            self.log_dir / "user_interactions.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {extra[user_id]} | {extra[action]} | {message}",
            level="INFO",
            filter=lambda record: "user_interaction" in record["extra"],
            rotation="1 day",
            retention="90 days",
            enqueue=True
        )

        # Log environnement détecté
        logger.info(f"🔧 Logger configured for environment: {self.env.value}")
        logger.info(f"📁 Log directory: {self.log_dir.absolute()}")

    def get_user_logger(self, user_id: str = "anonymous"):
        """
        Retourne un logger configuré pour les interactions utilisateur.

        Args:
            user_id: Identifiant de l'utilisateur

        Returns:
            Logger configuré avec le contexte utilisateur
        """
        return logger.bind(user_id=user_id, user_interaction=True)


# Instance globale (détection auto environnement)
log_config = LoggerConfig()
log_config.setup_logger()

# Logger principal de l'application
app_logger = logger.bind(component="main")


def log_user_action(action: str, details: Dict[str, Any] = None, user_id: str = "anonymous") -> None:
    """
    Log une action utilisateur.

    Args:
        action: Type d'action effectuée
        details: Détails supplémentaires
        user_id: Identifiant de l'utilisateur
    """
    user_logger = log_config.get_user_logger(user_id)
    user_logger.bind(action=action).info(f"User action: {details or {}}")


def log_error(error: Exception, context: str = "") -> None:
    """
    Log une erreur avec contexte.

    Args:
        error: Exception capturée
        context: Contexte dans lequel l'erreur s'est produite
    """
    logger.error(f"Error in {context}: {error}", exc_info=True)


def log_performance(func_name: str, duration: float, **kwargs) -> None:
    """
    Log les performances d'une fonction.

    Args:
        func_name: Nom de la fonction
        duration: Durée d'exécution en secondes
        **kwargs: Paramètres supplémentaires
    """
    logger.info(f"Performance: {func_name} took {duration:.3f}s", extra=kwargs)
```

---

### 3. Migrer detect_environment() vers EnvironmentDetector

**Fichier**: `main.py` (MODIFIÉ)

```python
# AVANT
def detect_environment():
    """Detect if running in PREPROD or PROD environment."""
    app_env = os.getenv("APP_ENV")
    # ...

# APRÈS
from utils.environment import EnvironmentDetector

def display_environment_badge():
    """Display environment badge in sidebar."""
    env = EnvironmentDetector.get_name()  # Utilise la classe centralisée

    if "PREPROD" in env:
        badge_config = colors.ENV_PREPROD
        # ...
```

---

## Structure Logs Résultante

```
logs/
├── preprod/
│   ├── debug.log       # DEBUG+ (10 MB rotation, 7 jours)
│   ├── errors.log      # ERROR+ (5 MB rotation, 7 jours)
│   └── user_interactions.log
└── prod/
    ├── errors.log      # ERROR+ (5 MB rotation, 30 jours)
    └── user_interactions.log
```

---

## Tests à Ajouter

### Test EnvironmentDetector
```python
# tests/unit/test_environment.py

def test_cache_mechanism():
    """Vérifie que l'environnement est caché."""
    env1 = EnvironmentDetector.detect()
    env2 = EnvironmentDetector.detect()
    assert env1 is env2  # Même objet en mémoire

def test_is_production_docker():
    """Vérifie détection Docker comme PROD."""
    # Mock /.dockerenv exists
    assert EnvironmentDetector.is_production() == True
```

### Test LoggerConfig
```python
# tests/unit/test_logger_config.py

def test_log_dir_preprod(monkeypatch):
    """Vérifie répertoire logs PREPROD."""
    monkeypatch.setenv("APP_ENV", "PREPROD")
    config = LoggerConfig(base_log_dir="logs")
    assert config.log_dir == Path("logs/preprod")

def test_log_dir_prod(monkeypatch):
    """Vérifie répertoire logs PROD."""
    monkeypatch.setenv("APP_ENV", "PROD")
    config = LoggerConfig(base_log_dir="logs")
    assert config.log_dir == Path("logs/prod")

def test_logger_setup_creates_files(tmp_path, monkeypatch):
    """Vérifie création fichiers logs."""
    monkeypatch.setenv("APP_ENV", "PREPROD")
    config = LoggerConfig(base_log_dir=str(tmp_path))
    config.setup_logger()

    logger.debug("Test debug")
    logger.error("Test error")

    assert (tmp_path / "preprod" / "debug.log").exists()
    assert (tmp_path / "preprod" / "errors.log").exists()
```

---

## Checklist Implémentation

- [ ] Créer `utils/environment.py` avec `EnvironmentDetector`
- [ ] Écrire tests `test_environment.py`
- [ ] Modifier `utils_logger.py` pour utiliser `EnvironmentDetector`
- [ ] Écrire tests `test_logger_config.py`
- [ ] Migrer `main.py` pour utiliser `EnvironmentDetector.get_name()`
- [ ] Supprimer ancienne fonction `detect_environment()` de `main.py`
- [ ] Créer `.gitkeep` dans `logs/preprod/` et `logs/prod/`
- [ ] Mettre à jour documentation (`conformite.rst`) si nécessaire
- [ ] Tester en local PREPROD
- [ ] Tester en Docker PROD
- [ ] Commit et push

---

## Temps Estimé

- Création `EnvironmentDetector` + tests : **1h**
- Refactoring `LoggerConfig` + tests : **1.5h**
- Migration `main.py` : **0.5h**
- Tests intégration + validation : **1h**

**Total : 4h**

---

## Bénéfices

✅ **Séparation logs PREPROD/PROD** (plus de confusion)
✅ **Configuration auto** (détection environnement)
✅ **Thread-safe** (`enqueue=True`)
✅ **Backtrace activé** (diagnostic erreurs)
✅ **Tests unitaires complets**
✅ **Centralisation logique** (1 classe EnvironmentDetector)
✅ **Conformité académique** (répond aux exigences)

---

**Auteur**: Analyse réalisée le 2025-10-28
**Priorité**: HAUTE (conformité académique)
**Statut**: À implémenter
