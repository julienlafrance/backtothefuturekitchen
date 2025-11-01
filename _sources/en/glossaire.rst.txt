Glossary
=========

Technical Terms
-----------------

CI/CD
   Continuous Integration / Continuous Deployment. DevOps practice for automating code testing and deployment.

Coverage
   Measure of code percentage tested by unit tests. Project objective: ≥90%.

DuckDB
   High-performance columnar OLAP (Online Analytical Processing) database. SQLite alternative for analytics.

DNAT
   Destination Network Address Translation. iptables technique to redirect network traffic directly to port 3910, bypassing reverse proxy for 10x performance gain.

Flake8
   Python tool verifying PEP8 compliance (standard Python code style).

Parquet
   Compressed columnar file format optimized for analytics. 5-10x more performant than CSV.

Polars
   High-performance Python DataFrame library, Pandas alternative. Rust engine, Arrow format.

Pytest
   Most popular Python unit testing framework.

S3 Garage
   Self-hosted Amazon S3 protocol implementation. Used for project dataset storage.

Streamlit
   Python framework for creating interactive data science web apps without JavaScript.

TTL
   Time To Live. Cache duration before expiration (project: 3600s = 1h).

uv
   Modern ultra-fast Python package manager. pip replacement, 10-100x faster.

Project Terms
-------------

PREPROD
   Pre-production environment for testing before PROD deployment. URL: https://mangetamain.lafrance.io/, port 8500.

PRODUCTION
   Stable production environment. URL: https://backtothefuturekitchen.lafrance.io/, port 8501.

Recipes Clean
   Cleaned dataset of 178,265 Food.com recipes (1999-2018). File: recipes_clean.parquet (250 MB).

Ratings Longterm
   Dataset of 1.1M+ user interactions. File: ratings_longterm.parquet (180 MB).

Back to the Kitchen
   Project name and visual identity (orange/black palette).

Runner Self-Hosted
   GitHub Actions machine running CI/CD directly on dataia VM (avoids VPN).

Analytics Terms
----------------

Trends Analysis
   Module ``analyse_trendlines_v2`` studying recipe evolution 1999-2018 (volume, duration, complexity).

Seasonal Analysis
   Module ``analyse_seasonality`` identifying seasonal patterns (winter/summer, December peaks).

Weekend Analysis
   Module ``analyse_weekend`` comparing weekday vs weekend publications (Monday +45%, Saturday -49%).

Ratings Analysis
   Module ``analyse_ratings`` studying user rating distribution (78% positive bias = 5★).

Complexity Score
   0-10 score calculated from number of steps + ingredients + preparation time.

Visual Identity
   Unified color palette: ``ORANGE_PRIMARY`` (#FF8C00), ``BACKGROUND_MAIN`` (#1E1E1E).

Infrastructure Terms
---------------------

Dataia
   VM hosting PREPROD/PROD services, Garage S3, GitHub Actions runner. IP: 192.168.80.202.

Docker Compose
   Docker container orchestration tool. Files: docker-compose.yml (PREPROD), docker-compose-prod.yml (PROD).

Health Check
   HTTP endpoint verifying application health. URL: ``/_stcore/health``. Retry 3 times, timeout 10s.

Loguru
   Modern Python logging library. Config: 2 files (debug.log, errors.log), automatic rotation.

Discord Webhook
   Real-time CI/CD notifications in #deployments channel.

Acronyms
---------

API
   Application Programming Interface. Documented Python module reference.

ASCII
   American Standard Code for Information Interchange. Text diagrams used in documentation.

CSV
   Comma-Separated Values. Tabular file format (replaced by Parquet for performance).

EDA
   Exploratory Data Analysis. Jupyter notebooks for data exploration (``00_eda/``).

FAQ
   Frequently Asked Questions. Common questions page.

JSON
   JavaScript Object Notation. Data exchange format.

OLAP
   Online Analytical Processing. Database type optimized for analytics (DuckDB).

PEP8
   Python Enhancement Proposal 8. Standard Python code style guide.

PR
   Pull Request. GitHub code merge request.

REST
   Representational State Transfer. API architecture (not used in project, web app).

RST
   reStructuredText. Sphinx documentation markup format.

SQL
   Structured Query Language. Database query language.

SSH
   Secure Shell. Protocol for secure dataia VM connection.

TTL
   Time To Live. Cache duration.

UI
   User Interface. Streamlit user interface.

URL
   Uniform Resource Locator. Web address.

VPN
   Virtual Private Network. Virtual private network (dataia accessible via VPN).

Common Commands
-------------------

``uv sync``
   Installs all project dependencies from pyproject.toml.

``uv run streamlit run``
   Launches Streamlit application in development mode.

``pytest``
   Runs unit tests.

``flake8``
   Verifies PEP8 compliance.

``black``
   Automatically formats Python code (opinionated style).

``docker-compose up -d``
   Starts Docker containers in background.

``git push origin main``
   Pushes commits to main branch, triggers CI/CD.

``gh run watch``
   Monitors GitHub Actions workflow execution in real time.

``ssh dataia``
   SSH connection to dataia VM.

``aws s3 cp --profile s3fast``
   Copies files from/to S3 Garage.

Key Values
------------

Quality Objectives
^^^^^^^^^^^^^^^^^

* **Coverage**: ≥90% (achieved: 93%)
* **Tests**: 118 tests (83 unit + 35 infrastructure)
* **PEP8**: 100% compliance
* **Docstrings**: Google Style, 100% functions

Performance Metrics
^^^^^^^^^^^^^^^^^^^^^

* **S3 without DNAT**: 50-100 MB/s
* **S3 with DNAT**: 500-917 MB/s (10x)
* **Streamlit cache**: <0.1s (after first load 5-10s)
* **CI build**: ~2-3 minutes
* **CD PREPROD**: ~40 seconds
* **CD PROD**: ~1 minute

Project Data
^^^^^^^^^^^^^^

* **Recipes**: 178,265 recipes
* **Ratings**: 1,132,367 interactions
* **Users**: 25,076 contributors
* **Period**: 1999-2018 (20 years)
* **Tags**: ~500 unique tags
* **Storage**: ~450 MB compressed Parquet

Configurations
^^^^^^^^^^^^^^

* **Python**: 3.13.7
* **Streamlit**: 1.50.0
* **Plotly**: 5.24.1
* **DuckDB**: 1.4.0
* **Polars**: 1.19.0
* **Cache TTL**: 3600s (1h)

See Also
----------

* :doc:`quickstart` - Quick start guide
* :doc:`faq` - Frequently asked questions
* :doc:`architecture` - Detailed technical architecture
* :doc:`api/index` - Complete API reference
