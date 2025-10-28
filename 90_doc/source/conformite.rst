Standards Qualité
=================

Ce projet respecte les standards de qualité pour un projet Python moderne.

**Voir aussi** : :doc:`tests` (coverage 93%), :doc:`cicd` (pipeline automatisé), :doc:`architecture` (stack technique)

Gestion de Projet
-----------------

Structure Cohérente
^^^^^^^^^^^^^^^^^^^

* Packages organisés : ``utils/``, ``visualization/``, ``data/``
* Modules séparés par fonctionnalité
* Séparation logique code/tests/documentation

Environnement Python
^^^^^^^^^^^^^^^^^^^^

* Gestionnaire moderne : ``uv`` (remplaçant pip)
* Configuration : ``pyproject.toml``
* Environnement virtuel isolé
* Dépendances versionnées

Git et GitHub
^^^^^^^^^^^^^

* Commits réguliers et descriptifs
* Branches de développement
* Pull Requests avec review
* Historique traçable

Documentation
^^^^^^^^^^^^^

* README.md complet (installation, utilisation)
* Documentation Sphinx auto-générée
* Guides techniques (CI/CD, tests, S3)
* Docstrings sur toutes les fonctions

Streamlit
^^^^^^^^^

* Interface utilisateur intuitive
* Widgets interactifs (sliders, selectbox)
* Storytelling des analyses
* Graphiques Plotly dynamiques

Programmation
-------------

Programmation Orientée Objet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Classes implémentées dans le projet :

**Classe DataLoader** (``data.loaders``)

Gestion du chargement de données avec exceptions :

.. code-block:: python

   class DataLoader:
       def load_recipes(self) -> pl.DataFrame:
           """Charge recettes depuis S3 avec gestion erreurs."""

       def load_ratings(
           self,
           min_interactions: int = 100,
           return_metadata: bool = False,
           verbose: bool = False
       ) -> pl.DataFrame | tuple:
           """Charge ratings avec options configurables."""

**Hiérarchie Exceptions** (``exceptions.py``)

6 classes d'exceptions personnalisées :

.. code-block:: python

   class MangetamainError(Exception):
       """Exception de base."""

   class DataLoadError(MangetamainError):
       """Erreur chargement S3/DuckDB."""
       def __init__(self, source: str, detail: str): ...

   class AnalysisError(MangetamainError):
       """Erreur analyse statistique."""

   class ConfigurationError(MangetamainError):
       """Erreur configuration."""

   class DatabaseError(MangetamainError):
       """Erreur opérations DuckDB."""

   class ValidationError(MangetamainError):
       """Erreur validation données."""

**Autres Classes**

* Configuration environnement (logging, détection preprod/prod)
* Utilitaires graphiques (application thème, gestion couleurs)

Type Hinting
^^^^^^^^^^^^

Annotations de types complètes :

.. code-block:: python

   def apply_chart_theme(fig: go.Figure, title: str = None) -> go.Figure:
       """Applique le thème à un graphique."""
       pass

   def get_ratings_longterm(
       min_interactions: int = 100,
       return_metadata: bool = False,
       verbose: bool = False
   ) -> pd.DataFrame:
       """Charge les ratings depuis S3."""
       pass

Respect PEP8
^^^^^^^^^^^^

* Validation automatique avec ``flake8``
* Formatage avec ``black``
* Ligne maximale : 88 caractères
* Pipeline CI vérifie à chaque push

Gestion des Exceptions
^^^^^^^^^^^^^^^^^^^^^^^

Try/except personnalisés avec messages clairs :

.. code-block:: python

   try:
       data = load_from_s3(bucket, key)
   except boto3.exceptions.NoCredentialsError:
       st.error("Credentials S3 introuvables. Vérifier 96_keys/credentials")
   except Exception as e:
       st.error(f"Erreur chargement données : {e}")
       return None

Logging
^^^^^^^

Système Loguru 0.7.3 complet avec séparation PREPROD/PROD :

* **Architecture** : 2 fichiers (debug.log, errors.log) par environnement
* **Détection auto** : Variable ``APP_ENV`` ou path automatique
* **Rotation** : 10 MB (debug), 5 MB (errors) avec compression
* **Thread-safe** : ``enqueue=True`` pour Streamlit multithread
* **Backtrace** : Diagnostic complet des erreurs

.. code-block:: python

   from loguru import logger

   def load_data():
       try:
           logger.info("Starting data load")
           data = load_from_s3()
           logger.success(f"Loaded {len(data)} records")
       except Exception as e:
           logger.error(f"Load failed: {e}")
           raise

**Voir** : :doc:`architecture` section Logging pour configuration complète.

Sécurité
^^^^^^^^

* Credentials S3 dans fichier gitignore (``96_keys/``)
* Secrets GitHub chiffrés
* Pas de tokens en clair dans le code
* Validation des inputs utilisateurs

Tests et Qualité
----------------

Tests Unitaires
^^^^^^^^^^^^^^^

* **Framework** : pytest 8.5.0
* **Nombre** : 118 tests
* **Résultat** : 118 tests passent
* **Organisation** : ``tests/unit/`` + ``50_test/``

Coverage
^^^^^^^^

* **Objectif** : >= 90%
* **Atteint** : 93%
* **Outil** : pytest-cov
* **Rapport** : HTML avec lignes manquantes

Métriques par Module
^^^^^^^^^^^^^^^^^^^^

=========================== ========= ======
Module                      Coverage  Tests
=========================== ========= ======
utils/colors.py             100%      10
utils/chart_theme.py        100%      10
visualization/trendlines.py 100%      8
visualization/ratings.py    90-100%   5-14
data/cached_loaders.py      78%       3
=========================== ========= ======

Commentaires
^^^^^^^^^^^^

* Documentation inline des sections complexes
* Explication des algorithmes
* Références aux sources de données
* Notes sur les optimisations

Docstrings
^^^^^^^^^^

* **Format** : Google Style
* **Couverture** : Toutes fonctions/classes/modules
* **Validation** : pydocstyle dans CI
* **Exemple** :

.. code-block:: python

   def calculate_seasonal_patterns(df: pd.DataFrame) -> pd.DataFrame:
       """Calcule les patterns saisonniers des recettes.

       Analyse la distribution mensuelle des recettes et identifie
       les pics d'activité saisonniers.

       Args:
           df: DataFrame avec colonnes 'date' et 'recipe_id'

       Returns:
           DataFrame avec patterns saisonniers agrégés par mois

       Raises:
           ValueError: Si colonnes requises manquantes
       """
       pass

Documentation Sphinx
^^^^^^^^^^^^^^^^^^^^

* Génération automatique depuis docstrings
* Theme Read the Docs professionnel
* API documentation complète
* Guides utilisateur (installation, usage, architecture)

CI/CD
-----

Pipeline CI
^^^^^^^^^^^

Vérifications automatiques à chaque push :

1. **PEP8** : flake8 avec config ``.flake8``
2. **Docstrings** : pydocstyle (convention Google)
3. **Tests** : pytest avec coverage >= 90%
4. **Quality** : black, mypy (optionnel)

Exécution Automatique
^^^^^^^^^^^^^^^^^^^^^

* Sur **push** vers branche de développement
* Sur **Pull Request** vers main
* Sur **merge** vers main
* **Bloque le merge** si tests échouent

CD PREPROD
^^^^^^^^^^

Déploiement automatique sur https://mangetamain.lafrance.io/

* Déclenché après succès du CI
* Runner self-hosted (VM dataia)
* Health checks automatiques
* Notifications Discord

CD PRODUCTION
^^^^^^^^^^^^^

Déploiement manuel sur https://backtothefuturekitchen.lafrance.io/

* Confirmation obligatoire (taper "DEPLOY")
* Backup automatique avant déploiement
* Rollback documenté si échec
* Notifications Discord avec détails

Alerting
^^^^^^^^

Notifications Discord temps réel :

* Démarrage déploiement
* Succès/échec avec détails
* Instructions rollback si échec
* Historique complet des déploiements

Points Bonus
------------

Base de Données
^^^^^^^^^^^^^^^

DuckDB - Base OLAP columnar :

* 10-100x plus rapide que SQLite
* Zero-copy sur Parquet
* 581 MB, 7 tables
* 178K recettes, 1.1M+ interactions

Runner Self-Hosted
^^^^^^^^^^^^^^^^^^

Innovation : Déploiement sans VPN

* Runner GitHub sur VM dataia
* Déploiement en 30 secondes
* Gain : 10 minutes manuelles → 30 secondes auto

Architecture PREPROD/PROD
^^^^^^^^^^^^^^^^^^^^^^^^^

Isolation complète :

* Bases de données distinctes
* Logs séparés (debug PREPROD, errors PROD)
* Variables d'environnement différenciées
* Ports distincts (8500 vs 8501)

Résumé Standards
----------------

============================== ========= ===================
Standard                       Statut    Détails
============================== ========= ===================
Structure projet               ✅        Packages, modules
Environnement Python           ✅        uv + pyproject.toml
Git + GitHub                   ✅        Commits réguliers
README.md                      ✅        Complet
Streamlit                      ✅        UX interactive
POO                            ✅        DataLoader + hiérarchie exceptions
Type Hinting                   ✅        Complet
PEP8                           ✅        100% compliance
Exceptions personnalisées      ✅        Hiérarchie 6 classes
Logger                         ✅        Loguru complet
Sécurité                       ✅        Secrets protégés
Tests unitaires                ✅        118 tests
Coverage >= 90%                ✅        93% atteint
Commentaires                   ✅        Sections complexes
Docstrings                     ✅        Google Style
Documentation Sphinx           ✅        Auto-générée
Pipeline CI                    ✅        PEP8 + tests + cov
Exécution auto                 ✅        Push + PR + merge
CD (bonus)                     ✅        PREPROD + PROD
============================== ========= ===================
