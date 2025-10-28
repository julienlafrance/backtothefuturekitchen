Architecture Technique
======================

Vue d'ensemble de l'architecture technique du projet.

**Termes et acronymes**: voir :doc:`glossaire`

Infrastructure Déploiement
---------------------------

VM Autonome (virsh/KVM)
^^^^^^^^^^^^^^^^^^^^^^^

* **Technologie** : Machine virtuelle créée avec virsh (KVM/QEMU)
* **Nom** : dataia
* **Hébergement** : Serveur physique (réseau VPN interne)
* **OS** : Linux (distribution basée Debian)
* **Ressources** : CPU 4 cores, RAM 32 GB, Disk 500 GB
* **Accès** : SSH uniquement depuis réseau VPN

Containerisation Docker
^^^^^^^^^^^^^^^^^^^^^^^

Tous les environnements applicatifs tournent dans des **containers Docker isolés** :

**Container PREPROD** :

* Nom : mangetamain_preprod
* Port : 8500
* Base données : 10_preprod/data/mangetamain.duckdb
* Logs : 10_preprod/logs/
* Variables env : APP_ENV=preprod

**Container PROD** :

* Nom : mangetamain_prod
* Port : 8501
* Base données : 20_prod/data/mangetamain.duckdb
* Logs : 20_prod/logs/
* Variables env : APP_ENV=prod

**Orchestration** : Docker Compose (30_docker/)

**Isolation complète** :

* Bases de données distinctes
* Logs séparés par environnement
* Variables d'environnement différenciées
* Pas de partage de volumes entre containers

Runner GitHub Self-Hosted
^^^^^^^^^^^^^^^^^^^^^^^^^^

Le **runner GitHub self-hosted** installé sur la VM dataia orchestre les déploiements :

* Écoute les événements GitHub (push, workflow_dispatch)
* Exécute les workflows CI/CD (.github/workflows/)
* Accès direct aux containers pour déploiement
* Exécute git reset + docker-compose restart
* **Avantage** : Déploiement automatique sans VPN manuel

**Voir** : :doc:`cicd` pour détails complets du pipeline.

Stack Technique
---------------

| Catégorie | Technologies |
|-----------|--------------|
| **Backend** | DuckDB 1.4.0 (base OLAP columnar) |
| **Frontend** | Streamlit 1.50.0 + Plotly 5.24.1 |
| **Data Science** | Pandas 2.2.3, NumPy 2.2.6, Polars 1.19.0 |
| **Logging** | Loguru 0.7.3 (rotation automatique) |
| **Package Manager** | uv 0.8.22 (ultrafast pip replacement) |
| **Tests** | pytest 8.5.0, pytest-cov 6.0.0 |
| **CI/CD** | GitHub Actions + self-hosted runner |
| **Déploiement** | Docker Compose, VM dataia (VPN) |
| **Monitoring** | Discord webhooks (notifications temps réel) |

Détails des Technologies Clés
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**DuckDB**

Base de données OLAP columnar performante :

* 10-100x plus rapide que SQLite pour analyses
* Zero-copy sur fichiers Parquet
* SQL standard complet
* Intégration native Pandas/Polars
* Fichier unique 581 MB (7 tables)

**Streamlit**

Framework web Python interactif :

* Widgets réactifs (sliders, selectbox, etc.)
* Cache intégré (@st.cache_data)
* Rechargement automatique du code
* Déploiement simple (Docker)

**Plotly**

Bibliothèque de visualisations interactives :

* Graphiques interactifs (zoom, pan, hover)
* Subplots synchronisés
* Thème personnalisable
* Export PNG/SVG

Outils de Développement
^^^^^^^^^^^^^^^^^^^^^^^^

* **uv 0.8.22** : Gestionnaire de paquets moderne
* **pytest 8.5.0** : Tests unitaires
* **pytest-cov 6.0.0** : Coverage des tests
* **flake8** : Vérification PEP8
* **black** : Formatage automatique du code
* **pydocstyle** : Validation des docstrings

Structure du Projet
--------------------

Organisation des Répertoires
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    ~/mangetamain/
    ├── 00_eda/                    # Notebooks Jupyter d'exploration
    ├── 10_preprod/                # Application PREPROD (source de vérité)
    │   ├── src/
    │   │   └── mangetamain_analytics/
    │   │       ├── main.py
    │   │       ├── utils/
    │   │       ├── visualization/
    │   │       ├── data/
    │   │       └── assets/
    │   ├── tests/
    │   └── pyproject.toml
    ├── 20_prod/                   # Application PRODUCTION (artefact)
    ├── 30_docker/                 # Docker Compose
    ├── 50_test/                   # Tests infrastructure
    ├── 90_doc/                    # Documentation (ce répertoire)
    └── .github/workflows/         # CI/CD

Modules Applicatifs
^^^^^^^^^^^^^^^^^^^

**Module utils**

* ``colors.py`` : Palette de couleurs de la charte graphique
* ``chart_theme.py`` : Thème Plotly unifié

**Module visualization**

* ``analyse_trendlines_v2.py`` : Analyse des tendances temporelles
* ``analyse_seasonality.py`` : Analyse des patterns saisonniers
* ``analyse_weekend.py`` : Analyse de l'effet jour/weekend
* ``analyse_ratings.py`` : Analyse des notes utilisateurs
* ``custom_charts.py`` : Graphiques réutilisables

**Module data**

* ``cached_loaders.py`` : Chargement des données avec cache Streamlit
* ``loaders.py`` : Classe DataLoader pour chargement données avec gestion d'erreurs

**Module exceptions**

* ``exceptions.py`` : Hiérarchie d'exceptions personnalisées (5 classes)

CI/CD Pipeline
--------------

Architecture Séquentielle
^^^^^^^^^^^^^^^^^^^^^^^^^^

Le pipeline CI/CD est organisé en 3 phases :

1. **CI - Quality & Tests** (automatique sur push)

   * Vérification PEP8 (flake8)
   * Validation docstrings (pydocstyle)
   * Tests unitaires (pytest)
   * Coverage >= 90%

2. **CD Preprod** (automatique après CI réussi)

   * Déploiement sur https://mangetamain.lafrance.io/
   * Redémarrage container Docker
   * Health checks automatiques

3. **CD Production** (manuel avec confirmation)

   * Backup automatique
   * Déploiement sur https://backtothefuturekitchen.lafrance.io/
   * Health checks avec retry

Workflows GitHub Actions
^^^^^^^^^^^^^^^^^^^^^^^^^

* ``.github/workflows/ci.yml`` : Pipeline CI complet
* ``.github/workflows/cd-preprod.yml`` : Déploiement PREPROD
* ``.github/workflows/cd-prod.yml`` : Déploiement PRODUCTION

Runner Self-Hosted
^^^^^^^^^^^^^^^^^^

* Localisation : VM dataia (réseau VPN)
* Avantage : Déploiement sans connexion VPN manuelle
* Notifications : Discord webhooks en temps réel

Environnements
--------------

PREPROD
^^^^^^^

* **URL** : https://mangetamain.lafrance.io/
* **Port** : 8500
* **Usage** : Développement et tests
* **Déploiement** : Automatique sur push vers main

PRODUCTION
^^^^^^^^^^

* **URL** : https://backtothefuturekitchen.lafrance.io/
* **Port** : 8501
* **Usage** : Application stable
* **Déploiement** : Manuel avec confirmation

Différences
^^^^^^^^^^^

* Bases de données distinctes
* Logs séparés
* Variables d'environnement différenciées
* Badges visuels auto-détectés

Base de Données
---------------

DuckDB
^^^^^^

Fichier : ``mangetamain.duckdb`` (581 MB)

**Tables principales :**

* ``recipes`` : 178,265 recettes
* ``interactions`` : 1.1M+ interactions utilisateurs
* ``users`` : 25,076 utilisateurs
* Tables dérivées pour analyses

**Avantages DuckDB :**

* OLAP columnar (10-100x plus rapide que SQLite)
* Zero-copy sur fichiers Parquet
* SQL standard complet
* Intégration native Pandas/Polars

Stockage S3
^^^^^^^^^^^

* **Endpoint** : s3fast.lafrance.io
* **Bucket** : mangetamain
* **Credentials** : Fichier 96_keys/credentials
* **Performance** : 500-917 MB/s

Chargement des Données
^^^^^^^^^^^^^^^^^^^^^^^

Les données sont chargées automatiquement depuis S3 au démarrage via le module ``data.cached_loaders`` avec cache Streamlit (TTL 1h).

Tests et Qualité
----------------

Métriques
^^^^^^^^^

* **Coverage** : 93% (objectif 90%)
* **Tests unitaires** : 118 tests
* **PEP8 compliance** : 100%
* **Docstrings** : Google style

Types de Tests
^^^^^^^^^^^^^^

* **Tests unitaires** : 10_preprod/tests/unit/ (83 tests)
* **Tests infrastructure** : 50_test/ (35 tests S3/DuckDB/SQL)

Configuration
^^^^^^^^^^^^^

* ``.flake8`` : Configuration PEP8
* ``.pydocstyle`` : Configuration docstrings
* ``pyproject.toml`` : Configuration pytest et coverage

Logging
-------

Architecture Loguru
^^^^^^^^^^^^^^^^^^^

Le système de logging utilise **Loguru 0.7.3** avec séparation automatique des environnements.

**Fonctionnalités clés :**

* Détection automatique environnement (prod/preprod/local)
* 2 fichiers séparés : debug.log et errors.log
* Rotation automatique (10 MB debug, 5 MB errors)
* Compression automatique (.zip)
* Thread-safe pour Streamlit (``enqueue=True``)
* Backtrace complet pour erreurs

Configuration
^^^^^^^^^^^^^

.. code-block:: python

   from loguru import logger
   import sys
   from pathlib import Path

   def setup_logging():
       """Configure Loguru avec fichiers spécifiques à l'environnement."""

       env = get_environment()  # 'prod', 'preprod', ou 'local'
       log_dir = Path("logs")
       log_dir.mkdir(exist_ok=True)

       logger.remove()  # Supprimer handler par défaut

       # 1. Handler DEBUG + INFO
       logger.add(
           f"logs/{env}_debug.log",
           level="DEBUG",
           rotation="10 MB",
           retention="7 days",
           compression="zip",
           filter=lambda record: record["level"].name in ["DEBUG", "INFO", "SUCCESS"],
           enqueue=True,
       )

       # 2. Handler ERROR + CRITICAL
       logger.add(
           f"logs/{env}_errors.log",
           level="ERROR",
           rotation="5 MB",
           retention="30 days",
           compression="zip",
           backtrace=True,
           diagnose=True,
           enqueue=True,
       )

       # 3. Handler console (local uniquement)
       if env == "local":
           logger.add(sys.stderr, level="INFO", colorize=True)

       logger.info(f"Logging initialized for environment: {env}")

Détection Environnement
^^^^^^^^^^^^^^^^^^^^^^^^

La détection se fait automatiquement par :

1. **Variable d'environnement** ``APP_ENV`` (prioritaire)
2. **Path automatique** : détection via ``10_preprod/`` ou ``20_prod/`` dans le path
3. **Fallback** : ``local`` si aucun des deux

.. code-block:: python

   def get_environment() -> str:
       """Detect current environment."""
       env = os.getenv("APP_ENV", None)
       if env:
           return env.lower()

       current_path = str(Path.cwd())
       if "20_prod" in current_path:
           return "prod"
       elif "10_preprod" in current_path:
           return "preprod"
       return "local"

Structure des Logs
^^^^^^^^^^^^^^^^^^

::

    10_preprod/logs/
    ├── preprod_debug.log       # DEBUG, INFO, SUCCESS
    ├── preprod_errors.log      # ERROR, CRITICAL
    └── .gitkeep

    20_prod/logs/
    ├── prod_debug.log          # DEBUG, INFO, SUCCESS
    ├── prod_errors.log         # ERROR, CRITICAL
    └── .gitkeep

**Rotation :**

* Debug logs : 10 MB max, rétention 7 jours
* Error logs : 5 MB max, rétention 30 jours
* Compression automatique en .zip

Utilisation
^^^^^^^^^^^

.. code-block:: python

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

   def process_input(value):
       """Process user input."""
       logger.debug(f"User input received: {value}")

       if not validate(value):
           logger.warning(f"Invalid input: {value}")
           return None

       result = compute(value)
       logger.info(f"Computation result: {result}")
       return result

Configuration Docker
^^^^^^^^^^^^^^^^^^^^

Les fichiers Docker Compose définissent explicitement l'environnement :

**docker-compose-preprod.yml :**

.. code-block:: yaml

   services:
     mangetamain_preprod:
       environment:
         - APP_ENV=preprod
       volumes:
         - ../10_preprod/logs:/app/logs

**docker-compose-prod.yml :**

.. code-block:: yaml

   services:
     mangetamain_prod:
       environment:
         - APP_ENV=prod
       volumes:
         - ../20_prod/logs:/app/logs

Avantages
^^^^^^^^^

* ✅ **Séparation Prod/Preprod** : Logs distincts automatiquement
* ✅ **Thread-safe** : Compatible Streamlit multithread
* ✅ **Rotation automatique** : Pas de logs géants
* ✅ **Compression** : Économie d'espace disque
* ✅ **Détection auto** : Fonctionne sans configuration manuelle
* ✅ **Backtrace complet** : Debugging simplifié pour erreurs

Performance
-----------

Optimisations
^^^^^^^^^^^^^

* **Cache Streamlit** : ``@st.cache_data`` (TTL 1h)
* **DuckDB columnar** : Requêtes analytiques optimisées
* **Polars** : Traitement de données haute performance
* **S3 DNAT bypass** : 500-917 MB/s

Temps de Chargement
^^^^^^^^^^^^^^^^^^^

* Premier chargement : 5-10 secondes (depuis S3)
* Chargements suivants : <0.1 seconde (cache mémoire)
* Gain : 50-100x sur navigations répétées

Sécurité
--------

Bonnes Pratiques
^^^^^^^^^^^^^^^^

* Credentials S3 non commités (96_keys/ dans .gitignore)
* Secrets GitHub chiffrés
* Runner isolé sur VPN
* Validation des inputs utilisateurs
* Gestion des exceptions personnalisée
