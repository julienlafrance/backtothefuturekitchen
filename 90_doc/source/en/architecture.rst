Technical Architecture
=====================

Overview of the project's technical architecture.

**Terms and acronyms**: see :doc:`glossaire`

Deployment Infrastructure
--------------------------

IX-IA Host Server
^^^^^^^^^^^^^^^^^

* **Name**: IX-IA
* **OS**: Ubuntu 24.04.3 LTS
* **CPU**: 8 cores (Intel Core i7-11700K, 16 threads)
* **RAM**: 125 GB
* **Disks**: 915 GB (/), 1.7 TB (/home), 7.3 TB (/stock)
* **Network**: Dual IP (LAN 192.168.0.202 + DMZ 192.168.80.202)
* **Virtualization**: KVM/QEMU via virsh

Standalone VM dataia25-vm-v1 (virsh/KVM)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Technology**: Virtual machine created with virsh (KVM/QEMU)
* **Name**: dataia25-vm-v1
* **Hosting**: Physical server IX-IA (DMZ VLAN 80)
* **OS**: Ubuntu (Debian-based)
* **Resources**: 8 vCPUs (max 12), RAM 32 GB, Disk qcow2 with virtio
* **Network**: DMZ IP 192.168.80.210/24 (bridge br80 via TAP vnet0)
* **Shares**: 2x 9p filesystems (kaggle_data, temp)
* **Access**: SSH from OpenVPN (DMZ access only)

Docker Containerization on VM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All application environments run in **isolated Docker containers** on the dataia25-vm-v1 VM:

**PREPROD Container (mange_preprod)**:

* Name: mange_preprod
* Image: python:3.13.3-slim
* Port: 8500 (accessible via 192.168.80.210:8500)
* Network: mangetamain-preprod-network (172.18.0.0/16)
* Storage: S3 (s3fast.lafrance.io)
* Logs: 10_preprod/logs/
* Env variables: APP_ENV=preprod
* External URL: https://mangetamain.lafrance.io/ (via reverse proxy)

**PROD Container (mange_prod)**:

* Name: mange_prod
* Image: python:3.13.3-slim
* Port: 8501 (accessible via 192.168.80.210:8501)
* Network: mangetamain-prod-network (172.19.0.0/16)
* Storage: S3 (s3fast.lafrance.io)
* Logs: 20_prod/logs/
* Env variables: APP_ENV=prod
* External URL: https://backtothefuturekitchen.lafrance.io/ (via reverse proxy)

**Orchestration**: Docker Compose (30_docker/)

**Complete isolation**:

* Shared S3 storage (common data)
* Separate logs per environment
* Differentiated environment variables
* Isolated Docker networks (172.18 vs 172.19)
* No volume sharing between containers

GitHub Self-Hosted Runner
^^^^^^^^^^^^^^^^^^^^^^^^^^

The **GitHub self-hosted runner** installed on the dataia VM orchestrates deployments:

* Listens to GitHub events (push, workflow_dispatch)
* Executes CI/CD workflows (.github/workflows/)
* Direct access to containers for deployment
* Executes git reset + docker-compose restart
* **Advantage**: Automatic deployment without manual VPN

**See**: :doc:`cicd` for complete pipeline details.

S3 Infrastructure (Garage)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

S3-compatible storage is provided by **Garage** hosted on the IX-IA host server:

* **Container**: garage-fast (dxflrs/garage:v2.1.0)
* **Network mode**: host (accessible directly on host IP)
* **Ports**: 3910 (S3 API), 3913 (S3 Web)
* **Storage**: /s3fast (~646 MB currently used)

**Available endpoints**:

* **HTTP**: http://s3fast.lafrance.io (port 3910) - **Preferred in code**
* **HTTPS**: https://s3fast.lafrance.io (port 443, via reverse proxy)
* **Internal VM endpoint**: http://192.168.80.202:3910 (optimized direct access)

**HTTP choice**: The code uses HTTP for performance reasons (no TLS/SSL overhead) because communication remains within the secured DMZ network (192.168.80.0/24).

**Optimized VM access configuration**:

Access from the VM to S3 bypasses the reverse proxy for better performance:

* Entry in /etc/hosts on VM: ``192.168.80.202  s3fast.lafrance.io``
* Direct access via br80 bridge (same DMZ network)
* Significant performance gain (no double network hop)

Network and Security Architecture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Architecture objectives**:

* **Security**: DMZ isolation (VLAN 80) with dual-IP IX-IA host
* **Performance**: Direct VM → S3 route via br80 bridge (proxy bypass)

**DMZ Configuration (VLAN 80)**:

* Interface: enp4s0.80 (802.1Q tagged VLAN)
* Bridge: br80 (192.168.80.202/24) on IX-IA host
* VM connected via TAP vnet0 on br80 bridge
* DMZ Network: 192.168.80.0/24
* DMZ Gateway: 192.168.80.1

**Complete network architecture diagram**:

::

                           Internet (Public IP)
                                  │
                                  │
               ┌──────────────────┴──────────────────┐
               │                                     │
               │      External Router/Firewall       │
               │                                     │
               └─────┬────────────────────────┬──────┘
                     │                        │
                     │ (OpenVPN)              │ (HTTPS/TLS)
                     │                        │
       ┌─────────────▼─────────────┐         │
       │  OpenVPN (192.168.0.254)  │         │
       │  Access: DMZ ONLY         │         │
       │  (192.168.80.0/24)        │         │
       └───────────────────────────┘         │
                                             │
                               ┌─────────────▼──────────────┐
                               │  Gateway (192.168.0.254)   │
                               └─────────────┬──────────────┘
                                             │
                           LAN Network (192.168.0.0/24)
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
    ║              Physical Server IX-IA (192.168.0.202)                      ║
    ║              Ubuntu 24.04.3 LTS - i7-11700K (8c/16t) - 125GB RAM        ║
    ║                                                                          ║
    ║  ┌─────────────────────────────────────────────────────────────────┐    ║
    ║  │ Network interface:                                              │    ║
    ║  │  • LAN IP: 192.168.0.202                                        │    ║
    ║  │  • DMZ IP: 192.168.80.202 (on bridge br80)                      │    ║
    ║  │  • VLAN 80 tagged on enp4s0.80                                  │    ║
    ║  └─────────────────────────────────────────────────────────────────┘    ║
    ║                                                                          ║
    ║  ┌──────────────────────────────┐  ┌──────────────────────────────┐    ║
    ║  │   Docker Garage S3           │  │   Bridge br80 (DMZ VLAN 80)  │    ║
    ║  │   garage-fast (mode: host)   │  │   192.168.80.202/24          │    ║
    ║  │                              │  │                              │    ║
    ║  │   • Port 3910 (S3 API)       │  │   ┌──────────────────────┐   │    ║
    ║  │   • Port 3913 (S3 Web)       │  │   │   TAP vnet0          │   │    ║
    ║  │   • /s3fast (~646MB)         │  │   │   (VM interface)     │   │    ║
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
    ║  │   (LOCAL S3 access via bridge br80 - ultra-fast)◄────────────┘ │    ║
    ║  │                                                                 │    ║
    ║  │   ┌───────────────────────────────────────────────┐             │    ║
    ║  │   │  Docker Containers (on VM)                    │             │    ║
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
    ║  │   │  (Outbound tunneling only)                    │─────────────┼────╋──► Internet
    ║  │   └───────────────────────────────────────────────┘             │    ║
    ║  │                                                                 │    ║
    ║  └─────────────────────────────────────────────────────────────────┘    ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝

    Note: The VM and S3 are on the SAME physical machine (IX-IA).
    VM → S3 access is ultra-fast (local communication via br80).

**Network flows**:

* **Flow 1 - VPN Access**: OpenVPN → DMZ only (security isolation)
* **Flow 2 - PREPROD Web**: Internet → Reverse Proxy → VM:8500 (mange_preprod)
* **Flow 3 - PROD Web**: Internet → Reverse Proxy → VM:8501 (mange_prod)
* **Flow 4 - External S3**: Internet → Reverse Proxy → Host ixia:3910 (Garage S3)
* **Flow 5 - Optimized internal S3**: VM → br80 → ixia:3910 (proxy bypass, performance)
* **Flow 6 - GitHub Runner**: VM → Internet (outbound GitHub tunneling only)

Monitoring and Surveillance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

External environment monitoring with **UptimeRobot**:

**Service**: UptimeRobot (free plan, 50 monitors)

**Monitored URLs**:

* PREPROD: https://mangetamain.lafrance.io/ (port 8500)
* PRODUCTION: https://backtothefuturekitchen.lafrance.io/ (port 8501)

**Configuration**:

* Check interval: every 5 minutes
* Timeout: 30 seconds
* Protocol: HTTPS (via reverse proxy)

**Detection**:

* Unreachable server (no network response)
* Streamlit backend down (reverse proxy 502/503 error)
* Timeouts exceeding 30 seconds
* HTTP errors (4xx/5xx status codes)

**Alerts**:

* Automatic email on detected outage
* Discord webhook for real-time notifications
* UptimeRobot dashboard with uptime history

**External monitoring advantages**:

* Reliable detection (external to monitored server)
* High frequency (5 min vs former GitHub checks 1h)
* No dependency on self-hosted runner
* Automatic uptime statistics and SLA

Technical Stack
---------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Category
     - Technologies
   * - **Backend**
     - DuckDB 1.4.0 (columnar OLAP database)
   * - **Frontend**
     - Streamlit 1.50.0 + Plotly 5.24.1
   * - **Data Science**
     - Pandas 2.2.3, NumPy 2.2.6, Polars 1.19.0
   * - **Logging**
     - Loguru 0.7.3 (automatic rotation)
   * - **Package Manager**
     - uv 0.8.22 (ultrafast pip replacement)
   * - **Tests**
     - pytest 8.5.0, pytest-cov 6.0.0
   * - **CI/CD**
     - GitHub Actions + self-hosted runner
   * - **Deployment**
     - Docker Compose, dataia VM (VPN)
   * - **Monitoring**
     - UptimeRobot (external monitoring every 5 min)

Key Technologies Details
^^^^^^^^^^^^^^^^^^^^^^^^^

**DuckDB**

High-performance columnar OLAP database:

* 10-100x faster than SQLite for analytics
* Zero-copy on Parquet files
* Complete standard SQL
* Native Pandas/Polars integration
* Single 581 MB file (7 tables)

**Streamlit**

Interactive Python web framework:

* Reactive widgets (sliders, selectbox, etc.)
* Built-in cache (@st.cache_data)
* Automatic code reload
* Simple deployment (Docker)

**Plotly**

Interactive visualization library:

* Interactive charts (zoom, pan, hover)
* Synchronized subplots
* Customizable theme
* PNG/SVG export

Development Tools
^^^^^^^^^^^^^^^^^

* **uv 0.8.22**: Modern package manager
* **pytest 8.5.0**: Unit testing
* **pytest-cov 6.0.0**: Test coverage
* **flake8**: PEP8 verification
* **black**: Automatic code formatting
* **pydocstyle**: Docstring validation

Project Structure
-----------------

Directory Organization
^^^^^^^^^^^^^^^^^^^^^^

::

    ~/mangetamain/
    ├── 00_eda/                    # Jupyter exploration notebooks
    ├── 10_preprod/                # PREPROD application (source of truth)
    │   ├── src/
    │   │   └── mangetamain_analytics/
    │   │       ├── main.py
    │   │       ├── utils/
    │   │       ├── visualization/
    │   │       ├── data/
    │   │       └── assets/
    │   ├── tests/
    │   └── pyproject.toml
    ├── 20_prod/                   # PRODUCTION application (artifact)
    ├── 30_docker/                 # Docker Compose
    ├── 40_utils/                  # Data utilities (mangetamain_data_utils)
    ├── 50_test/                   # Infrastructure tests S3/DuckDB
    ├── 70_scripts/                # Shell scripts (deploy, CI checks)
    ├── 90_doc/                    # Documentation (this directory)
    ├── 96_keys/                   # S3 credentials (ignored by git)
    └── .github/workflows/         # CI/CD

Application Modules
^^^^^^^^^^^^^^^^^^^

**utils Module**

* ``color_theme.py``: ColorTheme OOP class for "Back to the Kitchen" visual theme
* ``chart_theme.py``: Plotly theme application functions

**visualization Module**

* ``analyse_trendlines_v2.py``: Time trend analysis
* ``analyse_seasonality.py``: Seasonal pattern analysis
* ``analyse_weekend.py``: Day/weekend effect analysis
* ``analyse_ratings.py``: User rating analysis
* ``custom_charts.py``: Reusable charts

**data Module**

* ``cached_loaders.py``: Data loading with Streamlit cache
* ``loaders.py``: DataLoader class for data loading with error handling

**exceptions Module**

* ``exceptions.py``: Custom exception hierarchy (5 classes)

CI/CD Pipeline
--------------

Sequential Architecture
^^^^^^^^^^^^^^^^^^^^^^^

The CI/CD pipeline is organized in 3 phases:

1. **CI - Quality & Tests** (automatic on push)

   * PEP8 verification (flake8)
   * Docstring validation (pydocstyle)
   * Unit tests (pytest)
   * Coverage >= 90%

2. **CD Preprod** (automatic after successful CI)

   * Deployment to https://mangetamain.lafrance.io/
   * Docker container restart
   * Automatic health checks

3. **CD Production** (manual with confirmation)

   * Automatic backup
   * Deployment to https://backtothefuturekitchen.lafrance.io/
   * Health checks with retry

GitHub Actions Workflows
^^^^^^^^^^^^^^^^^^^^^^^^^

* ``.github/workflows/ci.yml``: Complete CI pipeline
* ``.github/workflows/cd-preprod.yml``: PREPROD deployment
* ``.github/workflows/cd-prod.yml``: PRODUCTION deployment

Self-Hosted Runner
^^^^^^^^^^^^^^^^^^

* Location: dataia VM (VPN network)
* Advantage: Deployment without manual VPN connection
* Notifications: Real-time Discord webhooks

Environments
------------

PREPROD
^^^^^^^

* **URL**: https://mangetamain.lafrance.io/
* **Port**: 8500
* **Usage**: Development and testing
* **Deployment**: Automatic on push to main

PRODUCTION
^^^^^^^^^^

* **URL**: https://backtothefuturekitchen.lafrance.io/
* **Port**: 8501
* **Usage**: Stable application
* **Deployment**: Manual with confirmation

Differences
^^^^^^^^^^^

* Distinct databases
* Separate logs
* Differentiated environment variables
* Auto-detected visual badges

Database
--------

DuckDB
^^^^^^

File: ``mangetamain.duckdb`` (581 MB)

**Main tables:**

* ``recipes``: 178,265 recipes
* ``interactions``: 1.1M+ user interactions
* ``users``: 25,076 users
* Derived tables for analysis

**DuckDB advantages:**

* Columnar OLAP (10-100x faster than SQLite)
* Zero-copy on Parquet files
* Complete standard SQL
* Native Pandas/Polars integration

S3 Storage
^^^^^^^^^^

* **Endpoint**: s3fast.lafrance.io
* **Bucket**: mangetamain
* **Credentials**: File 96_keys/credentials
* **Performance**: 500-917 MB/s

Data Loading
^^^^^^^^^^^^

Data is automatically loaded from S3 at startup via the ``data.cached_loaders`` module with Streamlit cache (TTL 1h).

Tests and Quality
-----------------

Metrics
^^^^^^^

* **Coverage**: 93% (target 90%)
* **Unit tests**: 118 tests
* **PEP8 compliance**: 100%
* **Docstrings**: Google style

Test Types
^^^^^^^^^^

* **Unit tests**: 10_preprod/tests/unit/ (83 tests)
* **Infrastructure tests**: 50_test/ (35 tests S3/DuckDB/SQL)

Configuration
^^^^^^^^^^^^^

* ``.flake8``: PEP8 configuration
* ``.pydocstyle``: Docstring configuration
* ``pyproject.toml``: pytest and coverage configuration

Logging
-------

Loguru Architecture
^^^^^^^^^^^^^^^^^^^

The logging system uses **Loguru 0.7.3** with automatic environment separation.

**Key features:**

* Automatic environment detection (prod/preprod/local)
* 3 separate files: debug.log, errors.log, user_interactions.log
* Automatic rotation (10 MB debug, 5 MB errors, 1 day user_interactions)
* Automatic compression (.zip)
* Thread-safe for Streamlit (``enqueue=True``)
* Complete backtrace for errors
* EnvironmentDetector module with cache

Configuration
^^^^^^^^^^^^^

**Module**: ``utils_logger.py``

.. code-block:: python

   from utils_logger import LoggerConfig, log_user_action, log_error, log_performance

   # Automatic configuration at startup
   log_config = LoggerConfig()  # Detects env automatically
   log_config.setup_logger()

**Configured handlers**:

1. **Console**: PREPROD/LOCAL (colorized DEBUG), PROD (non-colorized WARNING)
2. **Debug**: {env}_debug.log - All levels ≥ DEBUG (10 MB, 7d, zip)
3. **Errors**: {env}_errors.log - ERROR and CRITICAL (5 MB, 7d preprod / 30d prod, zip, backtrace)
4. **User Interactions**: {env}_user_interactions.log - User actions (1 day, 90d preprod / 30d prod, zip)

**Utility functions**:

.. code-block:: python

   # Errors with context
   log_error(exception, context="data_loading")

   # User actions
   log_user_action("filter_change", {"value": "2024"}, user_id="anonymous")

   # Performance metrics
   log_performance("load_ratings", 1.234, records=1000)

Environment Detection
^^^^^^^^^^^^^^^^^^^^^

**Module**: ``src/mangetamain_analytics/utils/environment.py``

Detection is done automatically via the ``EnvironmentDetector`` class:

1. **Environment variable** ``APP_ENV`` (case-insensitive, priority)
2. **Automatic path**: detection via ``10_preprod/`` or ``20_prod/`` in path
3. **Fallback**: ``LOCAL`` if neither

**Characteristics**:

* Result caching (performance)
* ``reset_cache()`` method for unit tests
* ``get_name()`` method returning uppercase string

.. code-block:: python

   from mangetamain_analytics.utils.environment import Environment, EnvironmentDetector

   # Automatic detection with cache
   env = EnvironmentDetector.detect()  # Returns Environment.PREPROD|PROD|LOCAL

   # Environment name (uppercase string)
   env_name = EnvironmentDetector.get_name()  # Returns "PREPROD"|"PROD"|"LOCAL"

   # Reset cache (tests only)
   EnvironmentDetector.reset_cache()

Log Structure
^^^^^^^^^^^^^

::

    10_preprod/logs/
    ├── preprod_debug.log              # All levels ≥ DEBUG
    ├── preprod_errors.log             # ERROR, CRITICAL (7d)
    ├── preprod_user_interactions.log  # User actions (90d)
    └── .gitkeep

    20_prod/logs/
    ├── prod_debug.log                 # All levels ≥ DEBUG
    ├── prod_errors.log                # ERROR, CRITICAL (30d)
    ├── prod_user_interactions.log     # User actions (30d)
    └── .gitkeep

**Rotation:**

* Debug logs: 10 MB max, 7 days retention
* Error logs: 5 MB max, 7d (preprod) / 30d (prod) retention
* User interactions: 1 day, 90d (preprod) / 30d (prod) retention
* Automatic compression to .zip

Usage
^^^^^

**Basic logging**:

.. code-block:: python

   from loguru import logger

   logger.info("Application started")
   logger.warning("S3 not accessible")
   logger.error("Failed to load data", exc_info=True)

**With utility functions**:

.. code-block:: python

   from utils_logger import log_error, log_user_action, log_performance

   # Errors with context
   try:
       data = load_from_s3()
   except Exception as e:
       log_error(e, context="data_loading")

   # User actions (for analytics)
   log_user_action(
       action="filter_applied",
       details={"filter": "year", "value": "2024"},
       user_id="anonymous"
   )

   # Performance metrics
   import time
   start = time.time()
   result = expensive_computation()
   duration = time.time() - start
   log_performance("expensive_computation", duration, records=len(result))

Docker Configuration
^^^^^^^^^^^^^^^^^^^^

Docker Compose files explicitly define the environment:

**docker-compose-preprod.yml:**

.. code-block:: yaml

   services:
     mangetamain_preprod:
       environment:
         - APP_ENV=preprod
       volumes:
         - ../10_preprod/logs:/app/logs

**docker-compose-prod.yml:**

.. code-block:: yaml

   services:
     mangetamain_prod:
       environment:
         - APP_ENV=prod
       volumes:
         - ../20_prod/logs:/app/logs

Advantages
^^^^^^^^^^

* ✅ **Prod/Preprod/Local separation**: Distinct logs automatically per environment
* ✅ **Thread-safe**: Compatible with Streamlit multithread (``enqueue=True``)
* ✅ **Automatic rotation**: No huge logs (size and time)
* ✅ **Compression**: Disk space savings (.zip)
* ✅ **Auto detection**: ``EnvironmentDetector`` with cache
* ✅ **Complete backtrace**: Simplified debugging for errors (``backtrace=True``, ``diagnose=True``)
* ✅ **User tracking**: Dedicated ``user_interactions.log`` file
* ✅ **Utility functions**: ``log_error()``, ``log_user_action()``, ``log_performance()``
* ✅ **Differentiated retention**: 7d preprod, 30d prod for errors

Performance
-----------

Optimizations
^^^^^^^^^^^^^

* **Streamlit cache**: ``@st.cache_data`` (TTL 1h)
* **Columnar DuckDB**: Optimized analytical queries
* **Polars**: High-performance data processing
* **S3 DNAT bypass**: 500-917 MB/s

Loading Times
^^^^^^^^^^^^^

* First load: 5-10 seconds (from S3)
* Subsequent loads: <0.1 second (memory cache)
* Gain: 50-100x on repeated navigations

Security
--------

Best Practices
^^^^^^^^^^^^^^

* S3 credentials not committed (96_keys/ in .gitignore)
* Encrypted GitHub secrets
* Runner isolated on VPN
* User input validation
* Custom exception handling
