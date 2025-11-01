Quality Standards
================

This project adheres to quality standards for a modern Python project.

**See also**: :doc:`tests` (93% coverage), :doc:`cicd` (automated pipeline), :doc:`architecture` (technical stack)

Project Management
------------------

Consistent Structure
^^^^^^^^^^^^^^^^^^^^

* Organized packages: ``utils/``, ``visualization/``, ``data/``
* Modules separated by functionality
* Logical separation of code/tests/documentation

Python Environment
^^^^^^^^^^^^^^^^^^

* Modern manager: ``uv`` (pip replacement)
* Configuration: ``pyproject.toml``
* Isolated virtual environment
* Versioned dependencies

Git and GitHub
^^^^^^^^^^^^^^

* Regular and descriptive commits
* Development branches
* Pull Requests with review
* Traceable history

Documentation
^^^^^^^^^^^^^

* Complete README.md (installation, usage)
* Auto-generated Sphinx documentation
* Technical guides (CI/CD, tests, S3)
* Docstrings on all functions

Streamlit
^^^^^^^^^

* Intuitive user interface
* Interactive widgets (sliders, selectbox)
* Analysis storytelling
* Dynamic Plotly charts

Programming
-----------

Object-Oriented Programming
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Classes implemented in the project:

**DataLoader Class** (``data.loaders``)

Data loading management with exceptions:

.. code-block:: python

   class DataLoader:
       def load_recipes(self) -> pl.DataFrame:
           """Load recipes from S3 with error handling."""

       def load_ratings(
           self,
           min_interactions: int = 100,
           return_metadata: bool = False,
           verbose: bool = False
       ) -> pl.DataFrame | tuple:
           """Load ratings with configurable options."""

**Exception Hierarchy** (``exceptions.py``)

6 custom exception classes:

.. code-block:: python

   class MangetamainError(Exception):
       """Base exception."""

   class DataLoadError(MangetamainError):
       """S3/DuckDB loading error."""
       def __init__(self, source: str, detail: str): ...

   class AnalysisError(MangetamainError):
       """Statistical analysis error."""

   class ConfigurationError(MangetamainError):
       """Configuration error."""

   class DatabaseError(MangetamainError):
       """DuckDB operations error."""

   class ValidationError(MangetamainError):
       """Data validation error."""

**Other Classes**

* Environment configuration (logging, preprod/prod detection)
* Graphics utilities (theme application, color management)

Type Hinting
^^^^^^^^^^^^

Complete type annotations:

.. code-block:: python

   def apply_chart_theme(fig: go.Figure, title: str = None) -> go.Figure:
       """Apply theme to a chart."""
       pass

   def get_ratings_longterm(
       min_interactions: int = 100,
       return_metadata: bool = False,
       verbose: bool = False
   ) -> pd.DataFrame:
       """Load ratings from S3."""
       pass

PEP8 Compliance
^^^^^^^^^^^^^^^

* Automatic validation with ``flake8``
* Formatting with ``black``
* Maximum line: 88 characters
* CI pipeline checks on every push

Exception Handling
^^^^^^^^^^^^^^^^^^

Custom try/except with clear messages:

.. code-block:: python

   try:
       data = load_from_s3(bucket, key)
   except boto3.exceptions.NoCredentialsError:
       st.error("S3 credentials not found. Check 96_keys/credentials")
   except Exception as e:
       st.error(f"Data loading error: {e}")
       return None

Logging
^^^^^^^

Complete Loguru 0.7.3 system with PREPROD/PROD separation:

* **Architecture**: 2 files (debug.log, errors.log) per environment
* **Auto-detection**: ``APP_ENV`` variable or automatic path
* **Rotation**: 10 MB (debug), 5 MB (errors) with compression
* **Thread-safe**: ``enqueue=True`` for Streamlit multithreading
* **Backtrace**: Complete error diagnostics

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

**See**: :doc:`architecture` Logging section for complete configuration.

Logged Events
^^^^^^^^^^^^^

The Streamlit application logs **21 events** to log files.

**main.py (13 events)**

Application startup:

* ``logger.info`` (519): "🚀 Enhanced Streamlit application starting"
* ``logger.info`` (833): "✅ Application fully loaded"
* ``logger.info`` (837): "🌟 Starting Enhanced Mangetamain Analytics"

Resources and checks:

* ``logger.warning`` (527): "CSS file not found: {css_path}"
* ``logger.warning`` (633): "S3 not accessible: {e}"
* ``logger.warning`` (636): "Unexpected error checking S3: {e}"

Analysis errors:

* ``logger.warning`` (246): "Erreur lors de l'analyse de {table}: {e}"
* ``logger.error`` (315): "DatabaseError in temporal analysis: {e}"
* ``logger.error`` (318): "AnalysisError in temporal analysis: {e}"
* ``logger.error`` (321): "Unexpected error in temporal analysis: {e}"
* ``logger.error`` (381): "DatabaseError in user analysis: {e}"
* ``logger.error`` (384): "AnalysisError in user analysis: {e}"
* ``logger.error`` (387): "Unexpected error in user analysis: {e}"

**Data loading (data/loaders.py - 8 events)**

Loading Parquet files from S3 generates detailed logs with error handling via ``DataLoadError``:

Loading recipes:

* ``logger.error`` (40): "Module mangetamain_data_utils introuvable: {e}"
* ``logger.info`` (47): "Chargement recettes depuis S3 (Parquet)"
* ``logger.info`` (49): "Recettes chargées: {len(recipes)} lignes"
* ``logger.error`` (52): "Échec chargement recettes depuis S3: {e}"

Loading ratings:

* ``logger.error`` (81): "Module mangetamain_data_utils introuvable: {e}"
* ``logger.info`` (88): "Chargement ratings depuis S3 (Parquet) - min_interactions={min_interactions}"
* ``logger.info`` (98/100): "Ratings chargés: {len(data)} lignes (avec metadata)" or "Ratings chargés: {len(result)} lignes"
* ``logger.error`` (103): "Échec chargement ratings depuis S3: {e}"

**Distribution by level:**

* INFO: 7 events (3 startup + 4 data loading)
* WARNING: 4 events (CSS, S3, analyses)
* ERROR: 10 events (6 analyses + 4 data loading)

Security
^^^^^^^^

* S3 credentials in gitignore file (``96_keys/``)
* Encrypted GitHub secrets
* No tokens in clear text in code
* User input validation

Tests and Quality
-----------------

Unit Tests
^^^^^^^^^^

* **Framework**: pytest 8.5.0
* **Number**: 118 tests
* **Result**: 118 tests passing
* **Organization**: ``tests/unit/`` + ``50_test/``

Coverage
^^^^^^^^

* **Target**: >= 90%
* **Achieved**: 93%
* **Tool**: pytest-cov
* **Report**: HTML with missing lines

Metrics per Module
^^^^^^^^^^^^^^^^^^

=========================== ========= ======
Module                      Coverage  Tests
=========================== ========= ======
utils/color_theme.py        97%       35
utils/chart_theme.py        100%      10
visualization/trendlines.py 100%      8
visualization/ratings.py    90-100%   5-14
data/cached_loaders.py      78%       3
=========================== ========= ======

Comments
^^^^^^^^

* Inline documentation for complex sections
* Algorithm explanations
* Data source references
* Optimization notes

Docstrings
^^^^^^^^^^

* **Format**: Google Style
* **Coverage**: All functions/classes/modules
* **Validation**: pydocstyle in CI
* **Example**:

.. code-block:: python

   def calculate_seasonal_patterns(df: pd.DataFrame) -> pd.DataFrame:
       """Calculate seasonal patterns of recipes.

       Analyzes the monthly distribution of recipes and identifies
       seasonal activity peaks.

       Args:
           df: DataFrame with 'date' and 'recipe_id' columns

       Returns:
           DataFrame with seasonal patterns aggregated by month

       Raises:
           ValueError: If required columns are missing
       """
       pass

Sphinx Documentation
^^^^^^^^^^^^^^^^^^^^

* Automatic generation from docstrings
* Professional Read the Docs theme
* Complete API documentation
* User guides (installation, usage, architecture)

CI/CD
-----

CI Pipeline
^^^^^^^^^^^

Automatic checks on every push:

1. **PEP8**: flake8 with ``.flake8`` config
2. **Docstrings**: pydocstyle (Google convention)
3. **Tests**: pytest with coverage >= 90%
4. **Quality**: black, mypy (optional)

Automatic Execution
^^^^^^^^^^^^^^^^^^^

* On **push** to development branch
* On **Pull Request** to main
* On **merge** to main
* **Blocks merge** if tests fail

PREPROD CD
^^^^^^^^^^

Automatic deployment to https://mangetamain.lafrance.io/

* **Triggered in parallel with CI** (no waiting)
* **Ultra-fast deployment**: ~40 seconds
* **Automatic rollback** if CI fails
* Self-hosted runner (dataia VM)
* Automatic health checks
* Discord notifications

PRODUCTION CD
^^^^^^^^^^^^^

Manual deployment to https://backtothefuturekitchen.lafrance.io/

* Mandatory confirmation (type "DEPLOY")
* Automatic backup before deployment
* Documented rollback if failure
* Discord notifications with details

Alerting
^^^^^^^^

Real-time Discord notifications:

* Deployment start
* Success/failure with details
* Rollback instructions if failure
* Complete deployment history

Advanced Technical Choices
---------------------------

OLAP Database
^^^^^^^^^^^^^

**DuckDB** - High-performance columnar database:

* **Performance**: 10-100x faster than SQLite on aggregations
* **Zero-copy**: Direct Parquet reading without import
* **Volume**: 581 MB, 7 tables
* **Data**: 178K recipes, 1.1M+ interactions

Self-Hosted Runner
^^^^^^^^^^^^^^^^^^

**Autonomous infrastructure**: VPN-independent deployment

* GitHub runner hosted on dataia VM
* **Ultra-fast deployment**: 30-40 seconds
* **Productivity gain**: 10 min manual → 30s automated
* **Availability**: 24/7 without intervention

Multi-Environment Architecture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Complete PREPROD/PROD isolation**:

* **Databases**: Distinct per environment
* **Logs**: Debug level (PREPROD), errors only (PROD)
* **Variables**: Environment-specific configuration
* **Ports**: 8500 (PREPROD) vs 8501 (PROD)

Standards Summary
-----------------

============================== ========= ===================
Standard                       Status    Details
============================== ========= ===================
Project structure              ✅        Packages, modules
Python environment             ✅        uv + pyproject.toml
Git + GitHub                   ✅        Regular commits
README.md                      ✅        Complete
Streamlit                      ✅        Interactive UX
OOP                            ✅        DataLoader + exception hierarchy
Type Hinting                   ✅        Complete
PEP8                           ✅        100% compliance
Custom exceptions              ✅        6-class hierarchy
Logger                         ✅        Complete Loguru
Security                       ✅        Protected secrets
Unit tests                     ✅        118 tests
Coverage >= 90%                ✅        93% achieved
Comments                       ✅        Complex sections
Docstrings                     ✅        Google Style
Sphinx documentation           ✅        Auto-generated
CI pipeline                    ✅        PEP8 + tests + cov
Auto execution                 ✅        Push + PR + merge
CD (bonus)                     ✅        PREPROD + PROD
============================== ========= ===================
