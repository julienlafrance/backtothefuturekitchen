FAQ - Frequently Asked Questions
================================

22 common questions organized in 7 categories.

**Quick start**: see :doc:`quickstart` | **Definitions**: see :doc:`glossaire`

Installation and Configuration
-------------------------------

How to install Python 3.13?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Option 1 - Via uv (recommended):**

.. code-block:: bash

   uv python install 3.13

**Option 2 - From python.org:**

Download from https://www.python.org/downloads/ and install manually.

**Verification:**

.. code-block:: bash

   python3 --version
   # Expected: Python 3.13.7

Why uv and not pip?
^^^^^^^^^^^^^^^^^^^

**uv** is a modern Python package manager:

* **10-100x faster** than pip
* Automatic virtual environment management
* Lock file for reproducibility
* Integrated Python installation
* pyproject.toml compatible

**pip → uv migration**:

.. code-block:: bash

   # Old
   pip install -r requirements.txt

   # New
   uv sync

How to configure S3?
^^^^^^^^^^^^^^^^^^^^

1. Create the credentials file:

.. code-block:: bash

   mkdir -p 96_keys
   cat > 96_keys/credentials << EOF
   [s3fast]
   aws_access_key_id = YOUR_KEY
   aws_secret_access_key = YOUR_SECRET
   EOF
   chmod 600 96_keys/credentials

2. Test the connection:

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest test_s3_parquet_files.py -v

**See**: :doc:`s3` for complete configuration.

Data and Performance
--------------------

How much data is loaded?
^^^^^^^^^^^^^^^^^^^^^^^^^

* **Recipes**: 178,265 recipes (~250 MB Parquet)
* **Ratings**: 1.1M+ interactions (~180 MB Parquet)
* **Total**: ~450 MB compressed, ~2.5 GB in memory

**First load**: 5-10 seconds (from S3)
**Subsequent loads**: <0.1 second (Streamlit cache)

How to improve S3 performance?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**DNAT Bypass**: 10x performance gain (50 → 500-917 MB/s)

.. code-block:: bash

   sudo iptables -t nat -A OUTPUT -p tcp -d 192.168.80.202 --dport 80 \
        -j DNAT --to-destination 192.168.80.202:3910

**Check performance**:

.. code-block:: bash

   time aws s3 cp s3://mangetamain/recipes_clean.parquet /tmp/ --profile s3fast

**See**: :doc:`s3` section "DNAT Bypass Performance".

Why Polars and not Pandas?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Polars** offers:

* **5-10x faster** for aggregations
* **Reduced memory footprint** (columnar format)
* Lazy evaluation for complex transformations
* Expressive and type-safe syntax

**Conversion if needed**:

.. code-block:: python

   recipes_pd = recipes.to_pandas()  # Polars → Pandas

When does Streamlit cache expire?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**TTL**: 3600 seconds (1 hour)

**Force reload**:

1. Streamlit menu (⋮) → "Clear cache"
2. Reload the page
3. Or programmatically: ``st.cache_data.clear()``

Development
-----------

How to add a new analysis?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Create the module**: ``src/mangetamain_analytics/visualization/analyse_nouvelle.py``

.. code-block:: python

   from data.cached_loaders import get_recipes_clean
   import streamlit as st
   import plotly.graph_objects as go
   from utils import chart_theme

   def render_nouvelle_analysis():
       """Render new analysis."""
       st.header("New Analysis")

       # Load data
       recipes = get_recipes_clean()

       # Create visualization
       fig = go.Figure()
       fig.add_trace(go.Bar(x=..., y=...))

       # Apply theme
       chart_theme.apply_chart_theme(fig, title="My Chart")

       # Display
       st.plotly_chart(fig, use_container_width=True)

2. **Add to menu**: Modify ``src/mangetamain_analytics/main.py``

.. code-block:: python

   from visualization import analyse_nouvelle

   # In the sidebar
   analysis = st.sidebar.selectbox(
       "Choose analysis",
       ["Trends", "Seasonality", "Weekend", "Ratings", "New"]
   )

   if analysis == "New":
       analyse_nouvelle.render_nouvelle_analysis()

3. **Test locally**:

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py

4. **Add tests**: ``tests/unit/test_analyse_nouvelle.py``

How to customize colors?
^^^^^^^^^^^^^^^^^^^^^^^^^

**Modify**: ``src/mangetamain_analytics/utils/color_theme.py``

.. code-block:: python

   class ColorTheme:
       # Change primary color
       ORANGE_PRIMARY: str = "#FF8C00"  # Modify HEX here

       # Add new color
       MY_CUSTOM_COLOR: str = "#123456"

**Use**:

.. code-block:: python

   from utils.color_theme import ColorTheme

   fig.add_trace(go.Bar(
       x=data['x'],
       y=data['y'],
       marker_color=ColorTheme.MY_CUSTOM_COLOR
   ))

How to debug a Plotly chart?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**1. Display figure structure:**

.. code-block:: python

   print(fig)  # Display complete structure

**2. Check trace data:**

.. code-block:: python

   for trace in fig.data:
       print(f"Type: {trace.type}")
       print(f"X: {trace.x}")
       print(f"Y: {trace.y}")

**3. Streamlit logs:**

.. code-block:: python

   st.write("Debug:", data.head())  # Display data sample

**4. JSON export:**

.. code-block:: python

   import json
   fig_json = fig.to_json()
   st.download_button("Download JSON", fig_json, "figure.json")

Tests and CI/CD
---------------

How to run tests?
^^^^^^^^^^^^^^^^^

**Unit tests (10_preprod):**

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv run pytest tests/unit/ -v --cov=src

**Infrastructure tests (50_test):**

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest -v

**Specific test:**

.. code-block:: bash

   uv run pytest tests/unit/test_color_theme.py::test_to_rgba_basic -v

How to increase coverage?
^^^^^^^^^^^^^^^^^^^^^^^^^^

**1. Identify missing lines:**

.. code-block:: bash

   uv run pytest --cov=src --cov-report=html
   xdg-open htmlcov/index.html

**2. Add tests for red lines**

**3. Mark untestable code:**

.. code-block:: python

   def display_ui():  # pragma: no cover
       """Untestable Streamlit UI function."""
       st.plotly_chart(fig)

**See**: :doc:`tests` for complete test patterns.

CI fails, how to debug?
^^^^^^^^^^^^^^^^^^^^^^^^

**1. Check locally first:**

.. code-block:: bash

   # PEP8
   uv run flake8 src/ tests/

   # Tests
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90

   # Formatting
   uv run black --check src/ tests/

**2. View CI logs on GitHub:**

.. code-block:: bash

   gh run list --limit 5
   gh run view <run-id>

**3. Re-run CI:**

From GitHub UI → Actions → Re-run failed jobs

**See**: :doc:`cicd` for complete CI/CD troubleshooting.

Docker
------

Docker container doesn't start
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Diagnostics:**

.. code-block:: bash

   # Check logs
   docker-compose logs mangetamain_preprod

   # Check health
   docker-compose ps

   # Check images
   docker images | grep mangetamain

**Common solutions:**

1. **Port occupied**:

.. code-block:: bash

   lsof -i :8500  # Identify process
   # Modify port in docker-compose.yml

2. **Missing volumes**:

.. code-block:: bash

   # Check paths exist
   ls -la ~/mangetamain/10_preprod/src
   ls -la ~/mangetamain/10_preprod/data

3. **Rebuild image**:

.. code-block:: bash

   docker-compose down
   docker-compose up -d --build

How to see changes in real-time?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Docker volume is mapped in read-only mode for source code:

1. **Modify**: Edit files in ``10_preprod/src/``
2. **Streamlit detects**: "Rerun" button appears automatically
3. **Click**: Rerun to see changes

**No container restart needed!**

Deployment
----------

How to deploy to PREPROD?
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Automatic**: Push to ``main`` triggers automatic deployment

.. code-block:: bash

   git add .
   git commit -m "My change"
   git push origin main

**CI/CD takes care of**:

1. Tests (PEP8, pytest, coverage ≥90%)
2. PREPROD deployment if tests OK
3. Discord notification

**Check deployment**:

* URL: https://mangetamain.lafrance.io/
* PREPROD badge visible in app

How to deploy to PRODUCTION?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Manual with confirmation**:

1. **Go to GitHub Actions** → CD Production
2. **Click**: "Run workflow"
3. **Type**: "DEPLOY" (exactly)
4. **Confirm**: Run workflow

**Automatic backup** performed before deployment

**Check**: https://backtothefuturekitchen.lafrance.io/

**See**: :doc:`cicd` for complete CD details.

How to rollback on error?
^^^^^^^^^^^^^^^^^^^^^^^^^^

**On the dataia VM:**

.. code-block:: bash

   ssh dataia
   cd ~/mangetamain/20_prod

   # View available backups
   ls backups/

   # Restore backup
   git reset --hard <commit-sha-stable>

   # Restart
   cd ../30_docker
   docker-compose -f docker-compose-prod.yml restart

**Discord notifications** contain the SHA of the commit to restore.

Common Errors
-------------

"ImportError: No module named 'streamlit'"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause**: Virtual environment not activated or missing dependencies

**Solution**:

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv sync  # Reinstall dependencies
   uv run streamlit --version  # Verify

"DuckDB database is locked"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause**: Multiple processes accessing DuckDB simultaneously

**Solution**:

.. code-block:: bash

   # Stop all Streamlit processes
   pkill -f streamlit

   # Or restart Docker container
   docker-compose restart

"S3 connection timeout"
^^^^^^^^^^^^^^^^^^^^^^^

**Possible causes**:

1. Invalid credentials → Check ``96_keys/credentials``
2. Unreachable endpoint → ``ping s3fast.lafrance.io``
3. Slow performance → Configure DNAT bypass

**DNAT Solution**: :doc:`s3` section "DNAT Bypass"

"Coverage below 90%"
^^^^^^^^^^^^^^^^^^^^

**CI blocks if coverage < 90%**

**Solution**:

1. Identify missing lines:

.. code-block:: bash

   uv run pytest --cov=src --cov-report=term-missing

2. Add tests for red lines
3. Or mark untestable code: ``# pragma: no cover``

**See**: :doc:`tests` for patterns.

Additional Resources
--------------------

* :doc:`installation` - Complete installation guide
* :doc:`usage` - Application usage
* :doc:`s3` - S3 Garage configuration
* :doc:`architecture` - Detailed technical stack
* :doc:`cicd` - CI/CD pipeline
* :doc:`tests` - Tests and coverage
* :doc:`api/index` - Complete API reference

**Support**: GitHub Issues → https://github.com/julienlafrance/backtothefuturekitchen/issues
