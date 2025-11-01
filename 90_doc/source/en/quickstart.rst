Quick Start Guide
=======================

Installation and essential commands guide to get started in 2 minutes.

**Complete guide**: :doc:`installation` | **FAQ**: :doc:`faq` | **Glossary**: :doc:`glossaire`

2-Minute Installation
--------------------------

.. code-block:: bash

   # Clone and install
   git clone https://github.com/julienlafrance/backtothefuturekitchen.git ~/mangetamain
   cd ~/mangetamain/10_preprod
   uv sync

   # Launch application
   uv run streamlit run src/mangetamain_analytics/main.py

**Access**: http://localhost:8501

Essential Commands
-----------------------

Local Development
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Launch app
   uv run streamlit run src/mangetamain_analytics/main.py

   # Install new dependency
   uv add package-name

   # Tests
   uv run pytest tests/unit/ -v --cov=src

   # Check PEP8
   uv run flake8 src/ tests/

   # Format code
   uv run black src/ tests/

Docker
^^^^^^

.. code-block:: bash

   # Start PREPROD
   cd ~/mangetamain/30_docker
   docker-compose up -d

   # View logs
   docker-compose logs -f

   # Restart
   docker-compose restart

   # Stop
   docker-compose down

Git and Deployment
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Commit and push (triggers CI/CD)
   git add .
   git commit -m "My change"
   git push origin main

   # View CI status
   gh run list --limit 5
   gh run watch

Tests
^^^^^

.. code-block:: bash

   # Unit tests with coverage
   uv run pytest tests/unit/ -v --cov=src --cov-report=html

   # Specific test
   uv run pytest tests/unit/test_color_theme.py -v

   # Infrastructure tests
   cd ~/mangetamain/50_test
   pytest -v

Cheat Sheet
-----------

Project Structure
^^^^^^^^^^^^^^^^

::

    ~/mangetamain/
    ├── 00_eda/          # Exploration notebooks
    ├── 10_preprod/      # PREPROD source code
    │   ├── src/         # Application code
    │   ├── tests/       # Unit tests
    │   └── pyproject    # uv configuration
    ├── 20_prod/         # PRODUCTION artifact
    ├── 30_docker/       # Docker Compose
    ├── 40_utils/        # Data utilities (mangetamain_data_utils)
    ├── 50_test/         # Infrastructure tests
    ├── 70_scripts/      # Shell scripts (deploy, CI checks)
    ├── 90_doc/          # Sphinx documentation
    └── 96_keys/         # S3 credentials (gitignored)

Common Imports
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Data
   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Charts
   import plotly.graph_objects as go
   from utils.color_theme import ColorTheme
   from utils import chart_theme

   # Streamlit
   import streamlit as st

   # Data science
   import polars as pl
   import pandas as pd

Create a Chart
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from utils.color_theme import ColorTheme
   from utils import chart_theme
   import plotly.graph_objects as go

   # Create figure
   fig = go.Figure()
   fig.add_trace(go.Bar(
       x=['A', 'B', 'C'],
       y=[10, 20, 30],
       marker_color=ColorTheme.ORANGE_PRIMARY
   ))

   # Apply theme
   chart_theme.apply_chart_theme(fig, title="My Chart")

   # Display
   st.plotly_chart(fig, use_container_width=True)

Load Data
^^^^^^^^^^^^^^^

.. code-block:: python

   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Load recipes (178K recipes)
   recipes = get_recipes_clean()

   # Load ratings (1.1M+ ratings)
   ratings = get_ratings_longterm()

   # With options
   ratings, metadata = get_ratings_longterm(
       min_interactions=100,
       return_metadata=True
   )

Filter with Polars
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import polars as pl

   # Filter by year
   recipes_2018 = recipes.filter(pl.col('year') == 2018)

   # Quick recipes
   quick = recipes.filter(pl.col('minutes') < 30)

   # Winter recipes
   winter = recipes.filter(pl.col('season') == 'Winter')

   # Multiple conditions
   filtered = recipes.filter(
       (pl.col('year') >= 2010) &
       (pl.col('minutes') < 60) &
       (pl.col('calories') < 500)
   )

Visual Identity Colors
^^^^^^^^^^^^^^^

.. code-block:: python

   from utils.color_theme import ColorTheme

   # Main colors
   ORANGE_PRIMARY = "#FF8C00"      # Bright orange
   ORANGE_SECONDARY = "#E24E1B"    # Red/Orange
   BACKGROUND_MAIN = "#1E1E1E"     # Dark gray
   TEXT_PRIMARY = "#F0F0F0"        # Light gray

   # Palettes
   ColorTheme.CHART_COLORS             # 8 chart colors
   ColorTheme.get_seasonal_colors()    # season → color dict

URLs and Ports
^^^^^^^^^^^^^

================================= ===== ==============
Environment                       Port  URL
================================= ===== ==============
Local PREPROD                     8500  localhost:8500
Local PRODUCTION                  8501  localhost:8501
Public PREPROD                    443   mangetamain.lafrance.io
Public PRODUCTION                 443   backtothefuturekitchen.lafrance.io
================================= ===== ==============

Quick Troubleshooting
----------------------

"uv: command not found"
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env

"No S3 credentials"
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   mkdir -p 96_keys
   # Add credentials to 96_keys/credentials
   chmod 600 96_keys/credentials

"Coverage below 90%"
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Identify missing lines
   uv run pytest --cov=src --cov-report=term-missing

   # Add tests or mark as non-testable
   def ui_function():  # pragma: no cover
       st.plotly_chart(fig)

"Port already in use"
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Linux/macOS
   lsof -i :8501
   kill <PID>

   # Or use another port
   uv run streamlit run src/main.py --server.port 8502

"Docker container unhealthy"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # View logs
   docker-compose logs -f

   # Restart
   docker-compose down
   docker-compose up -d --build

Typical Workflow
------------------------

Local Development
^^^^^^^^^^^^^^^^^^^

1. **Create branch**:

.. code-block:: bash

   git checkout -b feature/my-feature

2. **Develop**: Modify code in ``10_preprod/src/``

3. **Test**:

.. code-block:: bash

   uv run pytest tests/unit/ -v --cov=src
   uv run flake8 src/

4. **Commit**:

.. code-block:: bash

   git add .
   git commit -m "Add my feature"

5. **Push and PR**:

.. code-block:: bash

   git push origin feature/my-feature
   gh pr create --title "My feature"

Deployment
^^^^^^^^^^^

**PREPROD** (automatic):

.. code-block:: bash

   git push origin main
   # CI/CD handles the rest

**PRODUCTION** (manual):

1. GitHub Actions → CD Production
2. "Run workflow"
3. Type "DEPLOY"
4. Confirm

Key Metrics
--------------

Project
^^^^^^

* **Source code**: ~15,000 lines Python
* **Tests**: 118 tests, 93% coverage
* **Documentation**: 4200+ lines RST
* **Data**: 178K recipes, 1.1M ratings

Performance
^^^^^^^^^^^

* **First load**: 5-10 seconds
* **Subsequent loads**: <0.1 second (cache)
* **S3 without DNAT**: 50-100 MB/s
* **S3 with DNAT**: 500-917 MB/s (10x gain)

CI/CD
^^^^^

* **CI build**: ~2-3 minutes
* **CD PREPROD**: ~30 seconds
* **CD PROD**: ~45 seconds (backup included)
* **Health checks**: 3 retries, 10s timeout

Resources
----------

* **Complete documentation**: :doc:`index`
* **Installation**: :doc:`installation`
* **FAQ**: :doc:`faq`
* **Code documentation**: :doc:`modules/index`
* **GitHub**: https://github.com/julienlafrance/backtothefuturekitchen
