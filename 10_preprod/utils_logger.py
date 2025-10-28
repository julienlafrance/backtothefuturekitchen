"""Configuration des logs avec Loguru pour Mangetamain Analytics."""

from typing import Dict, Any
from loguru import logger
import sys
from pathlib import Path

# Import du module de détection d'environnement
try:
    from mangetamain_analytics.utils.environment import EnvironmentDetector, Environment
except ImportError:
    # Fallback si le module n'est pas encore dans le path
    import os
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from mangetamain_analytics.utils.environment import EnvironmentDetector, Environment


class LoggerConfig:
    """Configuration centralisée des logs avec Loguru."""

    def __init__(self, log_dir: str = "logs") -> None:
        """
        Initialise la configuration des logs.

        Args:
            log_dir: Répertoire de stockage des logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Détecter l'environnement
        self.env = EnvironmentDetector.detect()
        self.env_name = self.env.value  # 'preprod', 'prod', ou 'local'

    def setup_logger(self) -> None:
        """Configure les différents handlers de logs selon l'environnement."""
        # Supprimer le handler par défaut
        logger.remove()

        # ========================================
        # CONSOLE HANDLER (différent selon env)
        # ========================================

        if self.env == Environment.PREPROD or self.env == Environment.LOCAL:
            # PREPROD/LOCAL: Console verbeux avec couleurs
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>",
                level="DEBUG",
                colorize=True,
                enqueue=True,  # Thread-safe pour Streamlit
            )
        else:
            # PROD: Console minimal (warnings+errors seulement)
            logger.add(
                sys.stderr,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                level="WARNING",
                colorize=False,
                enqueue=True,
            )

        # ========================================
        # DEBUG LOG (PREPROD + PROD)
        # ========================================

        logger.add(
            self.log_dir / f"{self.env_name}_debug.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            enqueue=True,
        )

        # ========================================
        # ERROR LOG (PREPROD + PROD)
        # ========================================

        # Rétention différenciée selon environnement
        retention_days = "7 days" if self.env == Environment.PREPROD else "30 days"

        logger.add(
            self.log_dir / f"{self.env_name}_errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="5 MB",
            retention=retention_days,
            compression="zip",
            enqueue=True,
            backtrace=True,  # Backtrace complet pour debugging
            diagnose=True,  # Diagnostic détaillé des erreurs
        )

        # ========================================
        # USER INTERACTIONS LOG (analytics)
        # ========================================

        # Rétention différenciée : 90j preprod, 30j prod
        interactions_retention = (
            "90 days" if self.env == Environment.PREPROD else "30 days"
        )

        logger.add(
            self.log_dir / f"{self.env_name}_user_interactions.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {extra[user_id]} | {extra[action]} | {message}",
            level="INFO",
            filter=lambda record: "user_interaction" in record["extra"],
            rotation="1 day",  # 1 fichier par jour
            retention=interactions_retention,
            compression="zip",
            enqueue=True,
        )

        # Log environnement détecté
        logger.info(f"Logging initialized for environment: {self.env_name.upper()}")
        logger.info(f"Log directory: {self.log_dir.absolute()}")

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


def log_user_action(
    action: str, details: Dict[str, Any] = None, user_id: str = "anonymous"
) -> None:
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
