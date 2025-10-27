Installation
============

Prérequis
---------

* Python 3.13.3
* uv (gestionnaire de paquets)
* Accès S3 (Garage Storage)

Installation Locale
-------------------

1. Cloner le Repository
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git
   cd backtothefuturekitchen/000_dev/10_preprod

2. Créer l'Environnement Virtuel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv sync

Cette commande installe automatiquement toutes les dépendances définies dans ``pyproject.toml``.

3. Configuration S3
^^^^^^^^^^^^^^^^^^^

Copier les credentials S3 dans ``96_keys/credentials`` :

.. code-block:: ini

   [s3fast]
   aws_access_key_id = YOUR_KEY
   aws_secret_access_key = YOUR_SECRET

Les données sont chargées automatiquement depuis S3 au démarrage de l'application.

4. Lancer l'Application
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py

L'application est accessible sur http://localhost:8501

Installation avec Docker
------------------------

1. Cloner le Repository
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git
   cd backtothefuturekitchen/000_dev/30_docker

2. Lancer avec Docker Compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Environnement PREPROD (port 8500)
   docker-compose up -d

   # OU Environnement PRODUCTION (port 8501)
   docker-compose -f docker-compose-prod.yml up -d

Tests
-----

Lancer les Tests Unitaires
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd 10_preprod
   uv run pytest tests/unit/ -v --cov=src

Résultat attendu : 93% coverage (118 tests)

Vérifier la Qualité du Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # PEP8
   uv run flake8 src/ tests/ --config=../.flake8

   # Formatage
   uv run black --check src/ tests/

   # Docstrings
   uv run pydocstyle src/ --config=../.pydocstyle

Dépendances Principales
-----------------------

* streamlit >= 1.50.0
* plotly >= 5.24.1
* pandas >= 2.2.3
* numpy >= 2.2.6
* duckdb >= 1.4.0
* polars >= 1.19.0
* loguru >= 0.7.3
* pytest >= 8.5.0 (dev)
* pytest-cov >= 6.0.0 (dev)

La liste complète est disponible dans ``10_preprod/pyproject.toml``.
