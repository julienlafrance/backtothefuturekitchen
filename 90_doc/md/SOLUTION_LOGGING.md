# Solution Logging Streamlit (Prod vs Preprod)

## Problème
- Distinguer les logs PROD et PREPROD
- 2 fichiers séparés : debug.log et errors.log
- Fonctionne en local, preprod, et prod

## Solution : Variable d'environnement + Loguru

### 1. Détecter l'environnement

```python
# 10_preprod/src/mangetamain_analytics/main.py

import os
from pathlib import Path
from loguru import logger
import sys

def get_environment() -> str:
    """Detect current environment.

    Returns:
        Environment name: 'prod', 'preprod', or 'local'
    """
    # Option 1: Variable d'environnement explicite
    env = os.getenv("APP_ENV", None)
    if env:
        return env.lower()

    # Option 2: Détection automatique par path
    current_path = str(Path.cwd())
    if "20_prod" in current_path:
        return "prod"
    elif "10_preprod" in current_path:
        return "preprod"
    else:
        return "local"

def setup_logging():
    """Configure Loguru logging with environment-specific files."""

    env = get_environment()

    # Créer dossier logs si nécessaire
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Remove default handler
    logger.remove()

    # 1. Handler DEBUG + INFO (fichier debug)
    logger.add(
        f"logs/{env}_debug.log",  # preprod_debug.log ou prod_debug.log
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        filter=lambda record: record["level"].name in ["DEBUG", "INFO", "SUCCESS"],
        enqueue=True,  # Thread-safe pour Streamlit
    )

    # 2. Handler ERROR + CRITICAL (fichier errors)
    logger.add(
        f"logs/{env}_errors.log",  # preprod_errors.log ou prod_errors.log
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    # 3. Handler console (optionnel, pour debug local)
    if env == "local":
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True,
        )

    logger.info(f"Logging initialized for environment: {env}")
    return env

# Au début de main.py, appeler une seule fois
if 'logging_setup' not in st.session_state:
    env = setup_logging()
    st.session_state.logging_setup = True
    st.session_state.environment = env
```

### 2. Utilisation dans le code

```python
# Dans n'importe quelle fonction

from loguru import logger

def load_data():
    """Load data from S3."""
    try:
        logger.info("Starting data load from S3")
        data = some_loading_function()
        logger.success(f"Loaded {len(data)} records")
        return data
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise

def process_user_input(user_value):
    """Process user input."""
    logger.debug(f"User input received: {user_value}")

    if not validate(user_value):
        logger.warning(f"Invalid user input: {user_value}")
        return None

    result = compute(user_value)
    logger.info(f"Computation result: {result}")
    return result
```

### 3. Configuration Docker (Prod et Preprod)

**30_docker/docker-compose-preprod.yml**
```yaml
services:
  mangetamain_preprod:
    environment:
      - APP_ENV=preprod  # ← Définir explicitement
    volumes:
      - ../10_preprod/logs:/app/logs  # Persister les logs
```

**30_docker/docker-compose-prod.yml**
```yaml
services:
  mangetamain_prod:
    environment:
      - APP_ENV=prod  # ← Définir explicitement
    volumes:
      - ../20_prod/logs:/app/logs  # Persister les logs
```

### 4. Structure finale des logs

```
10_preprod/logs/
├── preprod_debug.log       # DEBUG, INFO, SUCCESS
├── preprod_errors.log      # ERROR, CRITICAL
└── .gitkeep

20_prod/logs/
├── prod_debug.log          # DEBUG, INFO, SUCCESS
├── prod_errors.log         # ERROR, CRITICAL
└── .gitkeep
```

### 5. .gitignore

```gitignore
# Logs (ne pas commit les vrais logs)
**/logs/*.log
**/logs/*.log.*
**/logs/*.gz

# Garder la structure
!**/logs/.gitkeep
```

### 6. Exemple de logs générés

**preprod_debug.log**
```
2025-10-27 14:23:15 | INFO     | main:load_data:234 - Starting data load from S3
2025-10-27 14:23:18 | SUCCESS  | main:load_data:238 - Loaded 178265 records
2025-10-27 14:23:20 | INFO     | analyse_ratings:render_ratings_analysis:45 - Rendering ratings analysis
2025-10-27 14:23:21 | DEBUG    | custom_charts:create_bar_chart:12 - Creating bar chart with 100 bars
```

**preprod_errors.log**
```
2025-10-27 14:25:30 | ERROR    | data_utils:connect_s3:89 - Failed to connect to S3: ConnectionTimeout
Traceback (most recent call last):
  File "data_utils.py", line 87, in connect_s3
    client = boto3.client('s3', endpoint_url=url)
  ...
```

### 7. Avantages de cette solution

✅ **Séparation Prod/Preprod** - Logs distincts automatiquement
✅ **2 fichiers** - debug.log et errors.log comme demandé
✅ **Thread-safe** - `enqueue=True` pour Streamlit multithread
✅ **Rotation automatique** - Pas de logs géants
✅ **Compression** - Économise l'espace disque
✅ **Détection auto** - Marche sans config si structure respectée
✅ **Facile à tester** - Logger disponible partout via `from loguru import logger`

### 8. Test rapide

```python
# Ajouter en haut de main.py après setup_logging()

logger.info("🚀 Application started")
logger.debug(f"Environment: {st.session_state.environment}")
logger.success("Configuration loaded successfully")

# Forcer une erreur pour tester errors.log
try:
    1 / 0
except ZeroDivisionError as e:
    logger.error(f"Test error logging: {e}")
```

Vérifier que 2 fichiers sont créés dans `logs/` :
- `preprod_debug.log` ou `prod_debug.log`
- `preprod_errors.log` ou `prod_errors.log`

---

## Estimation temps : 1h
- 30min : Implémenter setup_logging()
- 15min : Ajouter logger.info/error dans le code
- 15min : Tester + vérifier fichiers générés
