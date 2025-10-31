Architecture Technique
======================

Vue d'ensemble de l'architecture technique du projet.

**Termes et acronymes**: voir :doc:`glossaire`

Infrastructure Déploiement
---------------------------

Serveur Hôte IX-IA
^^^^^^^^^^^^^^^^^^

* **Nom** : IX-IA
* **OS** : Ubuntu 24.04.3 LTS
* **CPU** : 8 cores (Intel Core i7-11700K, 16 threads)
* **RAM** : 125 GB
* **Disques** : 915 GB (/), 1.7 TB (/home), 7.3 TB (/stock)
* **Réseau** : Double IP (LAN 192.168.0.202 + DMZ 192.168.80.202)
* **Virtualisation** : KVM/QEMU via virsh

VM Autonome dataia25-vm-v1 (virsh/KVM)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Technologie** : Machine virtuelle créée avec virsh (KVM/QEMU)
* **Nom** : dataia25-vm-v1
* **Hébergement** : Serveur physique IX-IA (DMZ VLAN 80)
* **OS** : Ubuntu (Debian-based)
* **Ressources** : 8 vCPUs (max 12), RAM 32 GB, Disk qcow2 avec virtio
* **Réseau** : IP DMZ 192.168.80.210/24 (bridge br80 via TAP vnet0)
* **Partages** : 2x 9p filesystems (kaggle_data, temp)
* **Accès** : SSH depuis OpenVPN (accès DMZ uniquement)

Containerisation Docker sur VM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tous les environnements applicatifs tournent dans des **containers Docker isolés** sur la VM dataia25-vm-v1 :

**Container PREPROD (mange_preprod)** :

* Nom : mange_preprod
* Image : python:3.13.3-slim
* Port : 8500 (accessible via 192.168.80.210:8500)
* Réseau : mangetamain-preprod-network (172.18.0.0/16)
* Stockage : S3 (s3fast.lafrance.io)
* Logs : 10_preprod/logs/
* Variables env : APP_ENV=preprod
* URL externe : https://mangetamain.lafrance.io/ (via reverse proxy)

**Container PROD (mange_prod)** :

* Nom : mange_prod
* Image : python:3.13.3-slim
* Port : 8501 (accessible via 192.168.80.210:8501)
* Réseau : mangetamain-prod-network (172.19.0.0/16)
* Stockage : S3 (s3fast.lafrance.io)
* Logs : 20_prod/logs/
* Variables env : APP_ENV=prod
* URL externe : https://backtothefuturekitchen.lafrance.io/ (via reverse proxy)

**Orchestration** : Docker Compose (30_docker/)

**Isolation complète** :

* Stockage S3 partagé (données communes)
* Logs séparés par environnement
* Variables d'environnement différenciées
* Réseaux Docker isolés (172.18 vs 172.19)
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

Infrastructure S3 (Garage)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le stockage S3-compatible est assuré par **Garage** hébergé sur le serveur hôte IX-IA :

* **Container** : garage-fast (dxflrs/garage:v2.1.0)
* **Mode réseau** : host (accessible directement sur IP hôte)
* **Ports** : 3910 (API S3), 3913 (Web S3)
* **Stockage** : /s3fast (~646 MB utilisés actuellement)
* **Endpoint public** : http://s3fast.lafrance.io (via reverse proxy)
* **Endpoint interne VM** : http://192.168.80.202:3910 (accès direct optimisé)

**Configuration accès VM optimisé** :

L'accès depuis la VM vers le S3 bypass le reverse proxy pour de meilleures performances :

* Entrée /etc/hosts sur VM : ``192.168.80.202  s3fast.lafrance.io``
* Accès direct via bridge br80 (même réseau DMZ)
* Gain de performance significatif (pas de double passage réseau)

Architecture Réseau et Sécurité
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Objectifs de l'architecture** :

* **Sécurité** : Isolation DMZ (VLAN 80) avec hôte IX-IA à double IP
* **Performance** : Route directe VM → S3 via bridge br80 (bypass proxy)

**Configuration DMZ (VLAN 80)** :

* Interface : enp4s0.80 (VLAN tagué 802.1Q)
* Bridge : br80 (192.168.80.202/24) sur hôte IX-IA
* VM connectée via TAP vnet0 sur bridge br80
* Réseau DMZ : 192.168.80.0/24
* Gateway DMZ : 192.168.80.1

**Schéma d'architecture réseau complet** :

::

                           Internet (IP publique)
                                  │
                                  │
               ┌──────────────────┴──────────────────┐
               │                                     │
               │      Routeur/Firewall Externe       │
               │                                     │
               └─────┬────────────────────────┬──────┘
                     │                        │
                     │ (OpenVPN)              │ (HTTPS/TLS)
                     │                        │
       ┌─────────────▼─────────────┐         │
       │  OpenVPN (192.168.0.254)  │         │
       │  Accès: DMZ UNIQUEMENT    │         │
       │  (192.168.80.0/24)        │         │
       └───────────────────────────┘         │
                                             │
                               ┌─────────────▼──────────────┐
                               │  Gateway (192.168.0.254)   │
                               └─────────────┬──────────────┘
                                             │
                           Réseau LAN (192.168.0.0/24)
                                             │
                               ┌─────────────▼─────────────────────┐
                               │ Reverse Proxy (192.168.0.201)     │
                               │  - HTTPS/TLS termination          │
                               │  - mangetamain.lafrance.io        │
                               │  - backtothefuturekitchen.lafrance.io │
                               │  - s3fast.lafrance.io             │
                               └─────┬──────────────────┬──────────┘
                                     │                  │
                                     │                  │
    ╔════════════════════════════════▼══════════════════▼══════════════════════╗
    ║                                                                          ║
    ║              Serveur Physique IX-IA (192.168.0.202)                     ║
    ║              Ubuntu 24.04.3 LTS - i7-11700K (8c/16t) - 125GB RAM        ║
    ║                                                                          ║
    ║  ┌─────────────────────────────────────────────────────────────────┐    ║
    ║  │ Interface réseau:                                               │    ║
    ║  │  • IP LAN: 192.168.0.202                                        │    ║
    ║  │  • IP DMZ: 192.168.80.202 (sur bridge br80)                     │    ║
    ║  │  • VLAN 80 tagué sur enp4s0.80                                  │    ║
    ║  └─────────────────────────────────────────────────────────────────┘    ║
    ║                                                                          ║
    ║  ┌──────────────────────────────┐  ┌──────────────────────────────┐    ║
    ║  │   Docker Garage S3           │  │   Bridge br80 (DMZ VLAN 80)  │    ║
    ║  │   garage-fast (mode: host)   │  │   192.168.80.202/24          │    ║
    ║  │                              │  │                              │    ║
    ║  │   • Port 3910 (API S3)       │  │   ┌──────────────────────┐   │    ║
    ║  │   • Port 3913 (Web S3)       │  │   │   TAP vnet0          │   │    ║
    ║  │   • /s3fast (~646MB)         │  │   │   (interface VM)     │   │    ║
    ║  │                              │  │   └──────────┬───────────┘   │    ║
    ║  │   Accessible via:            │  │              │               │    ║
    ║  │   • LAN: 192.168.0.202:3910  │◄─┼──────────────┼──────────┐    │    ║
    ║  │   • DMZ: 192.168.80.202:3910 │◄─┼──────────────┘          │    │    ║
    ║  └──────────────────────────────┘  └───────────────────────────┘  │    ║
    ║                                          │                         │    ║
    ║  ┌───────────────────────────────────────▼──────────────────────┐ │    ║
    ║  │                                                               │ │    ║
    ║  │        VM dataia25-vm-v1 (KVM/QEMU - virsh)                  │ │    ║
    ║  │        8 vCPUs, 32GB RAM, qcow2 virtio                       │ │    ║
    ║  │        192.168.80.210/24                                     │ │    ║
    ║  │                                                               │ │    ║
    ║  │   /etc/hosts: 192.168.80.202 = s3fast.lafrance.io            │ │    ║
    ║  │   (Accès S3 LOCAL via bridge br80 - ultra-rapide)◄───────────┘ │    ║
    ║  │                                                                 │    ║
    ║  │   ┌───────────────────────────────────────────────┐             │    ║
    ║  │   │  Docker Containers (sur VM)                   │             │    ║
    ║  │   │                                               │             │    ║
    ║  │   │  • mange_preprod (172.18.0.x:8500)            │◄────────────┼────╋─┐
    ║  │   │    → mangetamain.lafrance.io                  │             │    ║ │
    ║  │   │                                               │             │    ║ │ Via
    ║  │   │  • mange_prod (172.19.0.x:8501)               │◄────────────┼────╋─┘ reverse
    ║  │   │    → backtothefuturekitchen.lafrance.io       │             │    ║   proxy
    ║  │   │                                               │             │    ║   HTTPS
    ║  │   └───────────────────────────────────────────────┘             │    ║
    ║  │                                                                 │    ║
    ║  │   ┌───────────────────────────────────────────────┐             │    ║
    ║  │   │  GitHub Actions Runner                        │             │    ║
    ║  │   │  (Tunneling sortant uniquement)               │─────────────┼────╋──► Internet
    ║  │   └───────────────────────────────────────────────┘             │    ║
    ║  │                                                                 │    ║
    ║  └─────────────────────────────────────────────────────────────────┘    ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝

    Note: La VM et le S3 sont sur la MÊME machine physique (IX-IA).
    Les accès VM → S3 sont ultra-rapides (communication locale via br80).

**Flux réseau** :

* **Flux 1 - Accès VPN** : OpenVPN → DMZ uniquement (isolation sécurité)
* **Flux 2 - Web PREPROD** : Internet → Reverse Proxy → VM:8500 (mange_preprod)
* **Flux 3 - Web PROD** : Internet → Reverse Proxy → VM:8501 (mange_prod)
* **Flux 4 - S3 externe** : Internet → Reverse Proxy → Hôte ixia:3910 (Garage S3)
* **Flux 5 - S3 interne optimisé** : VM → br80 → ixia:3910 (bypass proxy, performances)
* **Flux 6 - GitHub Runner** : VM → Internet (tunneling GitHub sortant uniquement)

Monitoring et Surveillance
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Surveillance externe des environnements avec **UptimeRobot** :

**Service** : UptimeRobot (plan gratuit, 50 monitors)

**URLs surveillées** :

* PREPROD : https://mangetamain.lafrance.io/ (port 8500)
* PRODUCTION : https://backtothefuturekitchen.lafrance.io/ (port 8501)

**Configuration** :

* Intervalle de vérification : toutes les 5 minutes
* Timeout : 30 secondes
* Protocole : HTTPS (via reverse proxy)

**Détection** :

* Serveur inaccessible (pas de réponse réseau)
* Backend Streamlit down (erreur 502/503 du reverse proxy)
* Timeouts dépassant 30 secondes
* Erreurs HTTP (codes 4xx/5xx)

**Alertes** :

* Email automatique en cas de panne détectée
* Webhook Discord pour notifications temps réel
* Dashboard UptimeRobot avec historique uptime

**Avantages monitoring externe** :

* Détection fiable (externe au serveur surveillé)
* Fréquence élevée (5 min vs anciennes checks GitHub 1h)
* Pas de dépendance au runner self-hosted
* Statistiques d'uptime et SLA automatiques

Stack Technique
---------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Catégorie
     - Technologies
   * - **Backend**
     - DuckDB 1.4.0 (base OLAP columnar)
   * - **Frontend**
     - Streamlit 1.50.0 + Plotly 5.24.1
   * - **Data Science**
     - Pandas 2.2.3, NumPy 2.2.6, Polars 1.19.0
   * - **Logging**
     - Loguru 0.7.3 (rotation automatique)
   * - **Package Manager**
     - uv 0.8.22 (ultrafast pip replacement)
   * - **Tests**
     - pytest 8.5.0, pytest-cov 6.0.0
   * - **CI/CD**
     - GitHub Actions + self-hosted runner
   * - **Déploiement**
     - Docker Compose, VM dataia (VPN)
   * - **Monitoring**
     - UptimeRobot (surveillance externe toutes les 5 min)

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
    ├── 40_utils/                  # Utilitaires data (mangetamain_data_utils)
    ├── 50_test/                   # Tests infrastructure S3/DuckDB
    ├── 70_scripts/                # Scripts shell (deploy, CI checks)
    ├── 90_doc/                    # Documentation (ce répertoire)
    ├── 96_keys/                   # Credentials S3 (ignoré par git)
    └── .github/workflows/         # CI/CD

Modules Applicatifs
^^^^^^^^^^^^^^^^^^^

**Module utils**

* ``color_theme.py`` : Classe ColorTheme POO pour la charte graphique "Back to the Kitchen"
* ``chart_theme.py`` : Fonctions d'application du thème Plotly

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
* 3 fichiers séparés : debug.log, errors.log, user_interactions.log
* Rotation automatique (10 MB debug, 5 MB errors, 1 jour user_interactions)
* Compression automatique (.zip)
* Thread-safe pour Streamlit (``enqueue=True``)
* Backtrace complet pour erreurs
* Module EnvironmentDetector avec cache

Configuration
^^^^^^^^^^^^^

**Module**: ``utils_logger.py``

.. code-block:: python

   from utils_logger import LoggerConfig, log_user_action, log_error, log_performance

   # Configuration automatique au démarrage
   log_config = LoggerConfig()  # Détecte env automatiquement
   log_config.setup_logger()

**Handlers configurés**:

1. **Console**: PREPROD/LOCAL (DEBUG colorisé), PROD (WARNING non colorisé)
2. **Debug**: {env}_debug.log - Tous niveaux ≥ DEBUG (10 MB, 7j, zip)
3. **Errors**: {env}_errors.log - ERROR et CRITICAL (5 MB, 7j preprod / 30j prod, zip, backtrace)
4. **User Interactions**: {env}_user_interactions.log - Actions utilisateur (1 jour, 90j preprod / 30j prod, zip)

**Fonctions utilitaires**:

.. code-block:: python

   # Erreurs avec contexte
   log_error(exception, context="data_loading")

   # Actions utilisateur
   log_user_action("filter_change", {"value": "2024"}, user_id="anonymous")

   # Métriques performance
   log_performance("load_ratings", 1.234, records=1000)

Détection Environnement
^^^^^^^^^^^^^^^^^^^^^^^^

**Module**: ``src/mangetamain_analytics/utils/environment.py``

La détection se fait automatiquement via la classe ``EnvironmentDetector`` :

1. **Variable d'environnement** ``APP_ENV`` (case-insensitive, prioritaire)
2. **Path automatique** : détection via ``10_preprod/`` ou ``20_prod/`` dans le path
3. **Fallback** : ``LOCAL`` si aucun des deux

**Caractéristiques** :

* Cache du résultat (performance)
* Méthode ``reset_cache()`` pour tests unitaires
* Méthode ``get_name()`` retournant string uppercase

.. code-block:: python

   from mangetamain_analytics.utils.environment import Environment, EnvironmentDetector

   # Détection automatique avec cache
   env = EnvironmentDetector.detect()  # Returns Environment.PREPROD|PROD|LOCAL

   # Nom environnement (string uppercase)
   env_name = EnvironmentDetector.get_name()  # Returns "PREPROD"|"PROD"|"LOCAL"

   # Reset cache (tests uniquement)
   EnvironmentDetector.reset_cache()

Structure des Logs
^^^^^^^^^^^^^^^^^^

::

    10_preprod/logs/
    ├── preprod_debug.log              # Tous niveaux ≥ DEBUG
    ├── preprod_errors.log             # ERROR, CRITICAL (7j)
    ├── preprod_user_interactions.log  # Actions utilisateur (90j)
    └── .gitkeep

    20_prod/logs/
    ├── prod_debug.log                 # Tous niveaux ≥ DEBUG
    ├── prod_errors.log                # ERROR, CRITICAL (30j)
    ├── prod_user_interactions.log     # Actions utilisateur (30j)
    └── .gitkeep

**Rotation :**

* Debug logs : 10 MB max, rétention 7 jours
* Error logs : 5 MB max, rétention 7j (preprod) / 30j (prod)
* User interactions : 1 jour, rétention 90j (preprod) / 30j (prod)
* Compression automatique en .zip

Utilisation
^^^^^^^^^^^

**Logging basique**:

.. code-block:: python

   from loguru import logger

   logger.info("Application started")
   logger.warning("S3 not accessible")
   logger.error("Failed to load data", exc_info=True)

**Avec fonctions utilitaires**:

.. code-block:: python

   from utils_logger import log_error, log_user_action, log_performance

   # Erreurs avec contexte
   try:
       data = load_from_s3()
   except Exception as e:
       log_error(e, context="data_loading")

   # Actions utilisateur (pour analytics)
   log_user_action(
       action="filter_applied",
       details={"filter": "year", "value": "2024"},
       user_id="anonymous"
   )

   # Métriques de performance
   import time
   start = time.time()
   result = expensive_computation()
   duration = time.time() - start
   log_performance("expensive_computation", duration, records=len(result))

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

* ✅ **Séparation Prod/Preprod/Local** : Logs distincts automatiquement par environnement
* ✅ **Thread-safe** : Compatible Streamlit multithread (``enqueue=True``)
* ✅ **Rotation automatique** : Pas de logs géants (taille et temps)
* ✅ **Compression** : Économie d'espace disque (.zip)
* ✅ **Détection auto** : ``EnvironmentDetector`` avec cache
* ✅ **Backtrace complet** : Debugging simplifié pour erreurs (``backtrace=True``, ``diagnose=True``)
* ✅ **Tracking utilisateur** : Fichier dédié ``user_interactions.log``
* ✅ **Fonctions utilitaires** : ``log_error()``, ``log_user_action()``, ``log_performance()``
* ✅ **Rétention différenciée** : 7j preprod, 30j prod pour errors

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
