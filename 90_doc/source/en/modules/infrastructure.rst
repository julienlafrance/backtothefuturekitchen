Infrastructure Modules
======================

Infrastructure component documentation: logging (Loguru), database (DuckDB), EDA utilities.

**See also**: :doc:`../architecture` (technical stack), :doc:`../tests` (infrastructure tests)

Configuration and Logging
-------------------------

utils_logger
^^^^^^^^^^^^

Log configuration module with Loguru.

**Location**: ``10_preprod/utils_logger.py``

LoggerConfig Class
"""""""""""""""""""

Centralized log configuration class with automatic rotation.

**Configured handlers**:

* **Console** (stdout): Colorized format for development, INFO level
* **app.log**: DEBUG logs with 10MB rotation, 7-day retention
* **errors.log**: Errors only, 5MB rotation, 30-day retention
* **user_interactions.log**: User analytics, daily rotation, 90-day retention

**Main methods**:

.. code-block:: python

    # Initialization
    log_config = LoggerConfig(log_dir="logs")
    log_config.setup_logger()

    # User logger with context
    user_logger = log_config.get_user_logger(user_id="user123")

    # Utility functions
    log_user_action(action="page_view", details={"page": "home"}, user_id="user123")
    log_error(error=exception, context="data_loading")
    log_performance(func_name="load_data", duration=2.5, rows=10000)

**Configuration**:

* Automatic log rotation (size and time)
* Automatic compression of old logs (zip)
* Custom filters to separate log types
* User context with binding

Database Management
------------------------

models_database
^^^^^^^^^^^^^^^

DuckDB database management module with Streamlit cache.

**Location**: ``10_preprod/models_database.py``

DatabaseManager Class
"""""""""""""""""""""""

DuckDB database manager with context manager and cache patterns.

**Initialization**:

.. code-block:: python

    # Cached singleton instance
    db_manager = get_database_manager()

    # Or direct creation
    db_manager = DatabaseManager(db_path="data/mangetamain.duckdb")

**Main methods**:

* ``get_connection()``: Context manager for secure connection
* ``execute_query(query, **params)``: SQL execution with Streamlit cache
* ``load_csv_to_db(csv_path, table_name)``: Optimized CSV import
* ``get_table_info(table_name)``: Table metadata (schema, row count)
* ``list_tables()``: List of available tables
* ``initialize_from_csvs(data_dir)``: Complete initialization from CSVs

**Automatic indexes**:

* Interactions tables: indexes on user_id, recipe_id, date
* Users tables: index on u (user id)
* Conditional creation based on table type

**Usage example**:

.. code-block:: python

    # CSV loading
    db_manager.load_csv_to_db("data/interactions.csv", "interactions_train")

    # SQL query with cache
    df = db_manager.execute_query("""
        SELECT recipe_id, COUNT(*) as count
        FROM interactions_train
        GROUP BY recipe_id
        ORDER BY count DESC
        LIMIT 100
    """)

    # Context manager for direct connection
    with db_manager.get_connection() as conn:
        result = conn.execute("SELECT COUNT(*) FROM users").fetchone()

QueryTemplates Class
"""""""""""""""""""""

Predefined SQL query templates for frequent analyses.

**Static methods**:

* ``get_user_stats()``: Aggregated user statistics
* ``get_recipe_popularity()``: Top 100 popular recipes
* ``get_rating_distribution()``: Rating distribution (%)
* ``get_user_activity_over_time()``: Monthly activity

**Example**:

.. code-block:: python

    # Using template
    query = QueryTemplates.get_recipe_popularity()
    df = db_manager.execute_query(query)

**Advanced features**:

* Integrated Streamlit cache (@st.cache_data, @st.cache_resource)
* Automatic connection closing management
* Complete logging with Loguru
* Error handling with try/except and logging

**Architecture**:

* DatabaseManager: Singleton pattern with Streamlit cache
* Context Manager: Secure connection management
* QueryTemplates: Query / business logic separation
* Automatic indexes: Performance optimization based on schema

Data Exploration Utilities
--------------------------------

00_eda/_data_utils
^^^^^^^^^^^^^^^^^^

Utility modules for data exploration and cleaning (EDA notebooks).

**Files**:

* ``data_utils_common.py`` (196 lines): S3 connection, quality checks
* ``data_utils_recipes.py`` (755 lines): Recipe loading/cleaning
* ``data_utils_ratings.py`` (289 lines): Rating loading/cleaning

**Main functions (data_utils_common.py)**:

.. code-block:: python

    # S3 connection via DuckDB
    conn = get_s3_duckdb_connection()
    df = conn.execute("SELECT * FROM 's3://mangetamain/PP_recipes.csv'").pl()

    # Data quality analysis
    report = analyze_data_quality(df, name="recipes")

**Features**:

* Automatic S3 credentials configuration (96_keys/credentials)
* Quality analysis: missing values, types, duplicates
* Optimized loading with DuckDB httpfs
* Polars and Pandas support

Infrastructure Tests
--------------------

50_test
^^^^^^^

S3, DuckDB, SQL infrastructure test scripts.

**Files**:

* ``main.py``: Main infrastructure tests
* ``S3_duckdb_test.py``: Specific S3+DuckDB tests

**Usage**: Tests executed to validate infrastructure before deployment.

See Also
---------

* :doc:`data` - Module data.cached_loaders
* :doc:`utils` - Modules utils.colors and utils.chart_theme
* :doc:`../conformite` - Academic compliance and tests
