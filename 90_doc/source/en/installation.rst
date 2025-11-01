Installation
============

**Quick guide**: see :doc:`quickstart` (installation in 2 minutes).

**Technical terms**: see :doc:`glossaire` for uv, S3, Docker, etc.

Prerequisites
-------------

* Python 3.13.7
* uv (package manager)
* S3 Access (Garage Storage) - see :doc:`s3`

Local Installation
------------------

1. Clone the Repository
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git ~/mangetamain
   cd ~/mangetamain/10_preprod

2. Create the Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv sync

This command automatically installs all dependencies defined in ``pyproject.toml``.

3. S3 Configuration
^^^^^^^^^^^^^^^^^^^

Copy S3 credentials to ``96_keys/credentials``:

.. code-block:: ini

   [s3fast]
   aws_access_key_id = YOUR_KEY
   aws_secret_access_key = YOUR_SECRET

Data is automatically loaded from S3 when the application starts.

4. Launch the Application
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py

The application is accessible at http://localhost:8501

Installation with Docker
------------------------

1. Clone the Repository
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git ~/mangetamain
   cd ~/mangetamain/30_docker

2. Launch with Docker Compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # PREPROD Environment (port 8500)
   docker-compose up -d

   # OR PRODUCTION Environment (port 8501)
   docker-compose -f docker-compose-prod.yml up -d

Access to Environments
^^^^^^^^^^^^^^^^^^^^^^

* **Local PREPROD**: http://localhost:8500
* **Local PRODUCTION**: http://localhost:8501
* **Network PREPROD**: http://192.168.80.210:8500
* **Public PREPROD**: https://mangetamain.lafrance.io/
* **Public PRODUCTION**: https://backtothefuturekitchen.lafrance.io/

Docker Volumes
^^^^^^^^^^^^^^

Docker volumes map local code to the container:

=================== =================== ====== ================================
Local               Container           Mode   Description
=================== =================== ====== ================================
``10_preprod/src/`` ``/app/src/``       RO     Source code (hot reload)
``10_preprod/data/`` ``/app/data/``     RW     DuckDB database
``pyproject.toml``  ``/app/pyproject.``  RO     uv configuration
=================== =================== ====== ================================

**Advantages**:

* Source code in read-only mode (prevents accidental modifications)
* Changes visible immediately (Streamlit hot reload)
* Persistent DuckDB data

Docker Management
^^^^^^^^^^^^^^^^^

**View logs:**

.. code-block:: bash

   docker-compose logs -f mangetamain_preprod

**Restart after adding a new dependency:**

.. code-block:: bash

   # 1. Add dependency locally
   cd ~/mangetamain/10_preprod
   uv add new-dependency

   # 2. Restart container
   cd ~/mangetamain/30_docker
   docker-compose restart

**Stop services:**

.. code-block:: bash

   docker-compose down

**Rebuild completely:**

.. code-block:: bash

   docker-compose up -d --force-recreate --build

Docker Debug
^^^^^^^^^^^^

**Enter the container:**

.. code-block:: bash

   docker-compose exec mangetamain_preprod bash
   # Then inside the container:
   uv run python -c "import streamlit; print(streamlit.__version__)"

**Check container health:**

.. code-block:: bash

   docker-compose ps
   # Should display: healthy

**Real-time logs:**

.. code-block:: bash

   docker-compose logs -f --tail=100

Docker Development Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Modify code**: Edit files in ``10_preprod/src/``
2. **View changes**: Streamlit reloads automatically
3. **Add dependency**: ``uv add package`` then ``docker-compose restart``
4. **Debug**: ``docker-compose logs -f`` or enter the container

Cleanup
^^^^^^^

**Stop and remove container:**

.. code-block:: bash

   docker-compose down

**Complete cleanup (images, volumes, networks):**

.. code-block:: bash

   docker system prune -a
   # Warning: Removes ALL unused Docker images

Tests
-----

Run Unit Tests
^^^^^^^^^^^^^^

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv run pytest tests/unit/ -v --cov=src

Expected result: 93% coverage (118 tests)

Check Code Quality
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # PEP8
   uv run flake8 src/ tests/ --config=../.flake8

   # Formatting
   uv run black --check src/ tests/

   # Docstrings
   uv run pydocstyle src/ --config=../.pydocstyle

Main Dependencies
-----------------

* streamlit >= 1.50.0
* plotly >= 5.24.1
* pandas >= 2.2.3
* numpy >= 2.2.6
* duckdb >= 1.4.0
* polars >= 1.19.0
* loguru >= 0.7.3
* pytest >= 8.5.0 (dev)
* pytest-cov >= 6.0.0 (dev)

The complete list is available in ``10_preprod/pyproject.toml``.

Installation Verification
--------------------------

Verify uv
^^^^^^^^^

.. code-block:: bash

   uv --version
   # Expected: uv 0.8.22 or higher

If ``uv`` is not installed:

.. code-block:: bash

   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

Verify Python
^^^^^^^^^^^^^

.. code-block:: bash

   python3 --version
   # Expected: Python 3.13.7

The project requires Python 3.13+ for compatibility with all dependencies.

Verify Environment
^^^^^^^^^^^^^^^^^^

After ``uv sync``, verify that the environment is activated:

.. code-block:: bash

   uv run python --version
   # Expected: Python 3.13.7

   uv run python -c "import streamlit; print(streamlit.__version__)"
   # Expected: 1.50.0 or higher

Verify S3
^^^^^^^^^

Test S3 connection:

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest test_s3_parquet_files.py -v

If the test fails, verify:

1. The file ``96_keys/credentials`` exists and contains the correct keys
2. The S3 endpoint is accessible: ``ping s3fast.lafrance.io``
3. DNAT iptables rules are configured (if applicable)

**See**: :doc:`s3` for detailed S3 Garage configuration.

Troubleshooting
---------------

Error: "uv: command not found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Install uv with the official script:

.. code-block:: bash

   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env  # Reload PATH

Error: "Python 3.13 not found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: uv can install Python automatically:

.. code-block:: bash

   uv python install 3.13

Or install manually from https://www.python.org/downloads/

Error: "No credentials found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom**: Message "S3 credentials not found" in the app

**Solution**:

1. Create the directory: ``mkdir -p 96_keys``
2. Create the file ``96_keys/credentials`` with INI format:

.. code-block:: ini

   [s3fast]
   aws_access_key_id = YOUR_KEY
   aws_secret_access_key = YOUR_SECRET

3. Check permissions: ``chmod 600 96_keys/credentials``

Error: "Connection timeout" S3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Possible causes**:

1. **Network**: Check connectivity: ``curl -I http://s3fast.lafrance.io``
2. **Firewall**: Check that port 80 is open
3. **DNAT**: Configure bypass for maximum performance

**DNAT Solution** (optional, 10x performance gain):

.. code-block:: bash

   sudo iptables -t nat -A OUTPUT -p tcp -d 192.168.80.202 --dport 80 \
        -j DNAT --to-destination 192.168.80.202:3910

**See**: :doc:`s3` section "DNAT Performance Optimization".

Error: pytest tests fail
^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**:

1. Verify that the environment is up to date:

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv sync
   uv run pytest --version  # Expected: pytest 8.5.0+

2. Run tests with verbosity:

.. code-block:: bash

   uv run pytest tests/unit/ -vv

3. If a specific module fails, test it in isolation:

.. code-block:: bash

   uv run pytest tests/unit/test_color_theme.py -v

Port 8501 already in use
^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom**: "Address already in use" at startup

**Solution**:

1. Identify the process using the port:

.. code-block:: bash

   # Linux/macOS
   lsof -i :8501

   # Windows
   netstat -ano | findstr :8501

2. Stop the process or use another port:

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py --server.port 8502

Application loads slowly
^^^^^^^^^^^^^^^^^^^^^^^^

**First launch**: 5-10 seconds (normal S3 loading)

**Subsequent launches slow**: Check Streamlit cache

**Solution**:

1. In the app, click menu (⋮) > "Clear cache"
2. Or delete cache manually:

.. code-block:: bash

   rm -rf ~/.streamlit/cache

S3 Performance < 100 MB/s
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Configure DNAT bypass to reach 500-917 MB/s

**See**: :doc:`s3` section "DNAT Bypass Performance".

Additional Resources
--------------------

* **S3 Documentation**: :doc:`s3` - Garage Storage configuration
* **Tests**: :doc:`tests` - Complete testing and coverage guide
* **CI/CD**: :doc:`cicd` - Automated pipeline
* **Architecture**: :doc:`architecture` - Detailed technical stack
* **Code documentation**: :doc:`modules/index` - Complete module reference
