Modules Infrastructure
======================

Documentation des composants infrastructure : logging (Loguru), base de données (DuckDB), utilitaires EDA.

**Voir aussi** : :doc:`../architecture` (stack technique), :doc:`../tests` (tests infrastructure)

Configuration et Logging
-------------------------

utils_logger
^^^^^^^^^^^^

Module de configuration des logs avec Loguru.

**Emplacement**: ``10_preprod/utils_logger.py``

Classe LoggerConfig
"""""""""""""""""""

Classe de configuration centralisée des logs avec rotation automatique.

**Handlers configurés**:

* **Console** (stdout): Format colorisé pour développement, niveau INFO
* **app.log**: Logs DEBUG avec rotation 10MB, rétention 7 jours
* **errors.log**: Erreurs uniquement, rotation 5MB, rétention 30 jours
* **user_interactions.log**: Analytics utilisateur, rotation quotidienne, rétention 90 jours

**Méthodes principales**:

.. code-block:: python

    # Initialisation
    log_config = LoggerConfig(log_dir="logs")
    log_config.setup_logger()

    # Logger utilisateur avec contexte
    user_logger = log_config.get_user_logger(user_id="user123")

    # Fonctions utilitaires
    log_user_action(action="page_view", details={"page": "accueil"}, user_id="user123")
    log_error(error=exception, context="chargement_donnees")
    log_performance(func_name="load_data", duration=2.5, rows=10000)

**Configuration**:

* Rotation automatique des logs (taille et temps)
* Compression automatique des anciens logs (zip)
* Filtres personnalisés pour séparer les types de logs
* Contexte utilisateur avec binding

Gestion Base de Données
------------------------

models_database
^^^^^^^^^^^^^^^

Module de gestion de la base de données DuckDB avec cache Streamlit.

**Emplacement**: ``10_preprod/models_database.py``

Classe DatabaseManager
"""""""""""""""""""""""

Gestionnaire de base de données DuckDB avec patterns context manager et cache.

**Initialisation**:

.. code-block:: python

    # Instance singleton cachée
    db_manager = get_database_manager()

    # Ou création directe
    db_manager = DatabaseManager(db_path="data/mangetamain.duckdb")

**Méthodes principales**:

* ``get_connection()``: Context manager pour connexion sécurisée
* ``execute_query(query, **params)``: Exécution SQL avec cache Streamlit
* ``load_csv_to_db(csv_path, table_name)``: Import CSV optimisé
* ``get_table_info(table_name)``: Métadonnées table (schéma, nb lignes)
* ``list_tables()``: Liste des tables disponibles
* ``initialize_from_csvs(data_dir)``: Init complète depuis CSVs

**Index automatiques**:

* Tables interactions: index sur user_id, recipe_id, date
* Tables users: index sur u (user id)
* Création conditionnelle selon type de table

**Exemple d'usage**:

.. code-block:: python

    # Chargement CSV
    db_manager.load_csv_to_db("data/interactions.csv", "interactions_train")

    # Requête SQL avec cache
    df = db_manager.execute_query("""
        SELECT recipe_id, COUNT(*) as count
        FROM interactions_train
        GROUP BY recipe_id
        ORDER BY count DESC
        LIMIT 100
    """)

    # Context manager pour connexion directe
    with db_manager.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM users").fetchone()

Classe QueryTemplates
"""""""""""""""""""""

Templates de requêtes SQL prédéfinies pour analyses fréquentes.

**Méthodes statiques**:

* ``get_user_stats()``: Statistiques agrégées utilisateurs
* ``get_recipe_popularity()``: Top 100 recettes populaires
* ``get_rating_distribution()``: Distribution des notes (%)
* ``get_user_activity_over_time()``: Activité mensuelle

**Exemple**:

.. code-block:: python

    # Utilisation template
    query = QueryTemplates.get_recipe_popularity()
    df = db_manager.execute_query(query)

**Caractéristiques avancées**:

* Cache Streamlit intégré (@st.cache_data, @st.cache_resource)
* Gestion automatique fermeture connexions
* Logging complet avec Loguru
* Gestion d'erreurs avec try/except et logging

**Architecture**:

* DatabaseManager: Pattern Singleton avec cache Streamlit
* Context Manager: Gestion sécurisée connexions
* QueryTemplates: Séparation requêtes / logique métier
* Index automatiques: Optimisation performances selon schéma

Utilitaires Exploration Données
--------------------------------

00_eda/_data_utils
^^^^^^^^^^^^^^^^^^

Modules utilitaires pour exploration et nettoyage des données (notebooks EDA).

**Fichiers**:

* ``data_utils_common.py`` (196 lignes): Connexion S3, quality checks
* ``data_utils_recipes.py`` (755 lignes): Chargement/nettoyage recettes
* ``data_utils_ratings.py`` (289 lignes): Chargement/nettoyage ratings

**Fonctions principales (data_utils_common.py)**:

.. code-block:: python

    # Connexion S3 via DuckDB
    conn = get_s3_duckdb_connection()
    df = conn.execute("SELECT * FROM 's3://mangetamain/PP_recipes.csv'").pl()

    # Analyse qualité données
    report = analyze_data_quality(df, name="recipes")

**Fonctionnalités**:

* Configuration automatique credentials S3 (96_keys/credentials)
* Analyse qualité: valeurs manquantes, types, duplicatas
* Chargement optimisé avec DuckDB httpfs
* Support Polars et Pandas

Tests Infrastructure
--------------------

50_test
^^^^^^^

Scripts de tests d'infrastructure S3, DuckDB, SQL.

**Fichiers**:

* ``main.py``: Tests principaux infrastructure
* ``S3_duckdb_test.py``: Tests spécifiques S3+DuckDB

**Usage**: Tests exécutés pour valider infrastructure avant déploiement.

Voir Also
---------

* :doc:`data` - Module data.cached_loaders
* :doc:`utils` - Modules utils.colors et utils.chart_theme
* :doc:`../conformite` - Conformité académique et tests
