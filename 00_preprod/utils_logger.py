"""Configuration des logs avec Loguru pour Mangetamain Analytics."""

from typing import Dict, Any
from loguru import logger
import sys
from pathlib import Path


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
        
    def setup_logger(self) -> None:
        """Configure les différents handlers de logs."""
        # Supprimer le handler par défaut
        logger.remove()
        
        # Handler console pour le développement
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # Handler pour les logs d'information et debug
        logger.add(
            self.log_dir / "app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
        
        # Handler pour les erreurs uniquement
        logger.add(
            self.log_dir / "errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="5 MB",
            retention="30 days",
            compression="zip"
        )
        
        # Handler pour les interactions utilisateur (analytics)
        logger.add(
            self.log_dir / "user_interactions.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {extra[user_id]} | {extra[action]} | {message}",
            level="INFO",
            filter=lambda record: "user_interaction" in record["extra"],
            rotation="1 day",
            retention="90 days"
        )
        
    def get_user_logger(self, user_id: str = "anonymous") -> logger:
        """
        Retourne un logger configuré pour les interactions utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Logger configuré avec le contexte utilisateur
        """
        return logger.bind(user_id=user_id, user_interaction=True)


# Instance globale
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
