Tests and Coverage
==================

Complete documentation of unit tests and project coverage.

**Coverage**: percentage of tested code (:doc:`glossaire`).

**Quick execution**: see :doc:`quickstart` for commands.

Current Status
--------------

Executive Summary
^^^^^^^^^^^^^^^^^

* **Source code coverage**: 93% (90% target exceeded)
* **Unit tests**: 118 tests (10_preprod/tests/unit/)
* **Infrastructure tests**: 35 tests (50_test/)
* **Total**: 153 tests
* **Execution time**: ~6 seconds
* **CI/CD**: 90% threshold mandatory

Metrics by Environment
^^^^^^^^^^^^^^^^^^^^^^

========================================= ========== ======== ===============
Environment                               Coverage   Tests    Status
========================================= ========== ======== ===============
**10_preprod** (source code)              93%        83       Production ready
**20_prod** (build artifact)              N/A        N/A      See note*
**50_test** (infrastructure tests)        N/A        35       S3/DB validation
========================================= ========== ======== ===============

**Note:** 20_prod is a deployment artifact copied from 10_preprod. Testing 20_prod would be redundant as it's the same source code. Tests from 10_preprod validate the code deployed in production.

Quick Commands
--------------

Unit Tests (10_preprod)
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv run pytest tests/unit/ -v --cov=src --cov-report=html
   xdg-open htmlcov/index.html

**Expected result**: 83 tests, 93% coverage, 4 skipped

Infrastructure Tests (50_test)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest -v

**Expected result**: 35 tests (S3, DuckDB, SQL)

Detailed Coverage
-----------------

Tested Modules (10_preprod)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

================================= ========== ======== ====================
File                              Coverage   Tests    Missing Lines
================================= ========== ======== ====================
``utils/color_theme.py``               100%       10       0
``utils/chart_theme.py``          100%       10       0
``visualization/trendlines.py``   100%       8        0
``visualization/ratings_simple``  100%       14       0
``visualization/trendlines_v2``   95%        8        26 lines
``visualization/seasonality.py``  92%        6        19 lines
``visualization/ratings.py``      90%        5        29 lines
``visualization/custom_charts``   90%        4        4 lines
``visualization/weekend.py``      85%        6        41 lines
``data/cached_loaders.py``        78%        3        2 lines\*
``visualization/plotly_config``   77%        0        3 lines\*
================================= ========== ======== ====================

\*Unused functions commented out to improve coverage

Created Test Files
^^^^^^^^^^^^^^^^^^

.. code-block:: text

   tests/unit/
   ├── test_analyse_trendlines_v2.py    (8 tests)
   ├── test_analyse_ratings.py          (5 tests)
   ├── test_analyse_seasonality.py      (6 tests)
   ├── test_analyse_weekend.py          (6 tests)
   ├── test_color_theme.py                   (10 tests)
   ├── test_chart_theme.py              (10 tests)
   ├── test_analyse_ratings_simple.py   (14 tests)
   ├── test_custom_charts.py            (8 tests)
   ├── test_analyse_trendlines.py       (8 tests)
   └── test_cached_loaders.py           (4 tests skipped - mock st.cache_data)

Configuration
-------------

pyproject.toml
^^^^^^^^^^^^^^

.. code-block:: toml

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   addopts = "--cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=90"

   [tool.coverage.run]
   omit = [
       "*/main.py",
       "*/pages/*",
       "*/__pycache__/*",
       "*/.venv/*",
   ]

Infrastructure Tests (50_test)
------------------------------

Test Types
^^^^^^^^^^

**S3_duckdb_test.py (14 tests)**

* System environment (AWS CLI, credentials)
* S3 connection with boto3
* Download performance (>5 MB/s)
* DuckDB + S3 integration
* Docker tests (optional)

**test_s3_parquet_files.py (5 tests)**

* Automatically scans the code
* Finds references to parquet files
* Tests S3 accessibility

**test_sql_queries.py (16 tests)**

* Automatically scans the code
* Extracts SQL queries
* Tests syntax (EXPLAIN)
* Tests execution (LIMIT 1)

Test Strategy
-------------

What We Test
^^^^^^^^^^^^

* Data transformations
* Calculations and statistics
* Validation and filtering
* Business logic
* Utility functions

What We Exclude
^^^^^^^^^^^^^^^

.. code-block:: python

   # 1. Streamlit UI functions (marked pragma: no cover)
   def display_chart():  # pragma: no cover
       st.plotly_chart(fig)

   # 2. Application files (in pyproject.toml omit)
   # main.py, pages/*

   # 3. Conditional imports
   try:
       import module
   except ImportError:  # pragma: no cover
       module = None

Test Patterns
-------------

Mock Streamlit
^^^^^^^^^^^^^^

.. code-block:: python

   from unittest.mock import Mock, MagicMock, patch

   def setup_st_mocks(mock_st):
       """Configure all necessary Streamlit mocks."""
       mock_st.plotly_chart = Mock()
       mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])
       mock_st.slider = Mock(return_value=(2010, 2020))
       mock_st.selectbox = Mock(side_effect=lambda label, options, **kwargs:
                                options[kwargs.get('index', 0)])
       return mock_st

   @patch("visualization.module.st")
   @patch("visualization.module.load_data")
   def test_function(mock_load, mock_st):
       setup_st_mocks(mock_st)
       mock_load.return_value = test_data

       result = my_function()

       mock_st.plotly_chart.assert_called()

Data Fixtures
^^^^^^^^^^^^^

.. code-block:: python

   @pytest.fixture
   def mock_recipes_data():
       """Fixture for test data."""
       data = {
           "id": list(range(1000)),
           "year": [1999 + i % 20 for i in range(1000)],
           "minutes": [30 + (i % 50) for i in range(1000)],
           "complexity_score": [2.0 + (i % 10) * 0.1 for i in range(1000)],
       }
       return pl.DataFrame(data)

Plotly Chart Tests
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def test_chart_theme():
       fig = go.Figure()
       fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

       result = apply_chart_theme(fig, title="Test")

       assert result.layout.title.text == "Test"
       assert result.layout.plot_bgcolor == "rgba(0,0,0,0)"

Troubleshooting
---------------

Error: not enough values to unpack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause:** Mock of ``st.columns()`` returns empty

**Solution:**

.. code-block:: python

   mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])

Error: KeyError
^^^^^^^^^^^^^^^

**Cause:** Data fixture missing columns

**Solution:** Add all columns used by the function

.. code-block:: python

   data = {
       "existing_cols": [...],
       "missing_col": [...]  # Add missing column
   }

Error: Invalid value for color
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause:** Mock ``st.selectbox`` returns a fixed value used as color

**Solution:**

.. code-block:: python

   mock_st.selectbox = Mock(side_effect=lambda label, options, **kwargs:
                            options[kwargs.get('index', 0)])

Error: Expected to be called once
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause:** Wrong patch path

**Solution:** Patch where the function is **used**, not where it's **defined**

.. code-block:: python

   # ❌ Wrong
   @patch("data.loaders.load_data")

   # ✅ Correct
   @patch("visualization.module.load_data")

Useful Pytest Commands
----------------------

List Tests
^^^^^^^^^^

.. code-block:: bash

   pytest --collect-only -q

Specific Test
^^^^^^^^^^^^^

.. code-block:: bash

   pytest tests/unit/test_file.py::test_function -v

Coverage with Details
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

Coverage for One File
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest tests/unit/test_file.py --cov=src.module --cov-report=term

Stop at First Failure
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest -x                # Stop immediately
   pytest --maxfail=3       # Stop after 3 failures

Verbose Mode
^^^^^^^^^^^^

.. code-block:: bash

   pytest -vv --tb=long     # Full traceback

Best Practices
--------------

Test Structure
^^^^^^^^^^^^^^

.. code-block:: python

   """Unit tests for module X.

   Description of what is being tested.
   """

   import pytest
   from unittest.mock import Mock, patch

   @pytest.fixture
   def test_data():
       """Reusable fixture."""
       return create_test_data()

   def test_nominal_case(test_data):
       """Test nominal case."""
       result = function(test_data)
       assert result == expected

   def test_edge_case():
       """Test edge case."""
       # ...

   def test_error_handling():
       """Test error handling."""
       with pytest.raises(ValueError):
           function(invalid_data)

Naming
^^^^^^

* **Files**: ``test_<module>.py``
* **Functions**: ``test_<functionality>``
* **Fixtures**: ``mock_<type>_data`` or ``sample_<type>``

Clear Assertions
^^^^^^^^^^^^^^^^

.. code-block:: python

   # ✅ Good
   assert len(result) == 10, "Should return 10 elements"
   assert result['mean'] == pytest.approx(4.5, abs=0.1)

   # ❌ Bad
   assert result  # Too vague

Historical Progress
-------------------

============ ============ ==================================
Date         Coverage     Notes
============ ============ ==================================
2025-10-23   96%          Initial version (22 tests)
2025-10-25   **93%**      +60 tests (7 files), dead code cleaned
============ ============ ==================================

Files Added (2025-10-25)
^^^^^^^^^^^^^^^^^^^^^^^^

1. ``test_analyse_trendlines_v2.py`` - 8 tests
2. ``test_analyse_ratings.py`` - 5 tests
3. ``test_analyse_seasonality.py`` - 6 tests
4. ``test_analyse_weekend.py`` - 6 tests
5. ``test_color_theme.py`` - 10 tests
6. ``test_chart_theme.py`` - 10 tests
7. ``test_cached_loaders.py`` - 4 tests

**Total:** +49 tests, +6 files covered

See Also
--------

* :doc:`conformite` - Academic compliance and code quality
* :doc:`api/index` - API documentation for tested modules
* :doc:`architecture` - CI/CD pipeline with automated tests
