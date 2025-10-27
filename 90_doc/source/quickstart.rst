Guide Démarrage Rapide
=======================

Guide d'installation et commandes essentielles pour démarrer en 2 minutes.

**Guide complet** : :doc:`installation` | **FAQ** : :doc:`faq` | **Glossaire** : :doc:`glossaire`

Installation en 2 Minutes
--------------------------

.. code-block:: bash

   # Cloner et installer
   git clone https://github.com/julienlafrance/backtothefuturekitchen.git
   cd backtothefuturekitchen/000_dev/10_preprod
   uv sync

   # Lancer l'application
   uv run streamlit run src/mangetamain_analytics/main.py

**Accès** : http://localhost:8501

Commandes Essentielles
-----------------------

Développement Local
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Lancer app
   uv run streamlit run src/mangetamain_analytics/main.py

   # Installer nouvelle dépendance
   uv add nom-package

   # Tests
   uv run pytest tests/unit/ -v --cov=src

   # Vérifier PEP8
   uv run flake8 src/ tests/

   # Formater code
   uv run black src/ tests/

Docker
^^^^^^

.. code-block:: bash

   # Démarrer PREPROD
   cd 30_docker
   docker-compose up -d

   # Voir logs
   docker-compose logs -f

   # Redémarrer
   docker-compose restart

   # Arrêter
   docker-compose down

Git et Déploiement
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Commit et push (déclenche CI/CD)
   git add .
   git commit -m "Ma modification"
   git push origin main

   # Voir statut CI
   gh run list --limit 5
   gh run watch

Tests
^^^^^

.. code-block:: bash

   # Tests unitaires avec coverage
   uv run pytest tests/unit/ -v --cov=src --cov-report=html

   # Test spécifique
   uv run pytest tests/unit/test_colors.py -v

   # Tests infrastructure
   cd 50_test
   pytest -v

Cheat Sheet
-----------

Structure Projet
^^^^^^^^^^^^^^^^

::

    000_dev/
    ├── 00_eda/          # Notebooks exploration
    ├── 10_preprod/      # Code source PREPROD
    │   ├── src/         # Code application
    │   ├── tests/       # Tests unitaires
    │   └── pyproject    # Configuration uv
    ├── 20_prod/         # Artefact PRODUCTION
    ├── 30_docker/       # Docker Compose
    ├── 50_test/         # Tests infrastructure
    ├── 90_doc/          # Documentation Sphinx
    └── 96_keys/         # Credentials S3 (gitignore)

Imports Courants
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Données
   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Graphiques
   import plotly.graph_objects as go
   from utils import chart_theme, colors

   # Streamlit
   import streamlit as st

   # Data science
   import polars as pl
   import pandas as pd

Créer un Graphique
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from utils import chart_theme, colors
   import plotly.graph_objects as go

   # Créer figure
   fig = go.Figure()
   fig.add_trace(go.Bar(
       x=['A', 'B', 'C'],
       y=[10, 20, 30],
       marker_color=colors.ORANGE_PRIMARY
   ))

   # Appliquer thème
   chart_theme.apply_chart_theme(fig, title="Mon Graphique")

   # Afficher
   st.plotly_chart(fig, use_container_width=True)

Charger Données
^^^^^^^^^^^^^^^

.. code-block:: python

   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Charger recettes (178K recettes)
   recipes = get_recipes_clean()

   # Charger ratings (1.1M+ ratings)
   ratings = get_ratings_longterm()

   # Avec options
   ratings, metadata = get_ratings_longterm(
       min_interactions=100,
       return_metadata=True
   )

Filtrer avec Polars
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import polars as pl

   # Filtrer par année
   recipes_2018 = recipes.filter(pl.col('year') == 2018)

   # Recettes rapides
   quick = recipes.filter(pl.col('minutes') < 30)

   # Recettes hiver
   winter = recipes.filter(pl.col('season') == 'Hiver')

   # Multiples conditions
   filtered = recipes.filter(
       (pl.col('year') >= 2010) &
       (pl.col('minutes') < 60) &
       (pl.col('calories') < 500)
   )

Couleurs Charte
^^^^^^^^^^^^^^^

.. code-block:: python

   from utils import colors

   # Couleurs principales
   ORANGE_PRIMARY = "#FF8C00"      # Orange vif
   ORANGE_SECONDARY = "#E24E1B"    # Rouge/Orange
   BACKGROUND_MAIN = "#1E1E1E"     # Gris foncé
   TEXT_PRIMARY = "#F0F0F0"        # Gris clair

   # Palettes
   colors.CHART_COLORS             # 8 couleurs graphiques
   colors.SEASONAL_COLORS          # Dict saison → couleur

URLs et Ports
^^^^^^^^^^^^^

================================= ===== ==============
Environnement                     Port  URL
================================= ===== ==============
Local PREPROD                     8500  localhost:8500
Local PRODUCTION                  8501  localhost:8501
Public PREPROD                    443   mangetamain.lafrance.io
Public PRODUCTION                 443   backtothefuturekitchen.lafrance.io
================================= ===== ==============

Troubleshooting Rapide
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
   # Ajouter credentials dans 96_keys/credentials
   chmod 600 96_keys/credentials

"Coverage below 90%"
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Identifier lignes manquantes
   uv run pytest --cov=src --cov-report=term-missing

   # Ajouter tests ou marquer non testable
   def ui_function():  # pragma: no cover
       st.plotly_chart(fig)

"Port already in use"
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Linux/macOS
   lsof -i :8501
   kill <PID>

   # Ou utiliser autre port
   uv run streamlit run src/main.py --server.port 8502

"Docker container unhealthy"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Voir logs
   docker-compose logs -f

   # Redémarrer
   docker-compose down
   docker-compose up -d --build

Flux de Travail Typique
------------------------

Développement Local
^^^^^^^^^^^^^^^^^^^

1. **Créer branche** :

.. code-block:: bash

   git checkout -b feature/ma-fonctionnalite

2. **Développer** : Modifier code dans ``10_preprod/src/``

3. **Tester** :

.. code-block:: bash

   uv run pytest tests/unit/ -v --cov=src
   uv run flake8 src/

4. **Commit** :

.. code-block:: bash

   git add .
   git commit -m "Ajouter ma fonctionnalité"

5. **Push et PR** :

.. code-block:: bash

   git push origin feature/ma-fonctionnalite
   gh pr create --title "Ma fonctionnalité"

Déploiement
^^^^^^^^^^^

**PREPROD** (automatique) :

.. code-block:: bash

   git push origin main
   # CI/CD s'occupe du reste

**PRODUCTION** (manuel) :

1. GitHub Actions → CD Production
2. "Run workflow"
3. Taper "DEPLOY"
4. Confirmer

Métriques Clés
--------------

Projet
^^^^^^

* **Code source** : ~15,000 lignes Python
* **Tests** : 118 tests, 93% coverage
* **Documentation** : 4200+ lignes RST
* **Données** : 178K recettes, 1.1M ratings

Performance
^^^^^^^^^^^

* **Premier chargement** : 5-10 secondes
* **Chargements suivants** : <0.1 seconde (cache)
* **S3 sans DNAT** : 50-100 MB/s
* **S3 avec DNAT** : 500-917 MB/s (10x gain)

CI/CD
^^^^^

* **CI build** : ~2-3 minutes
* **CD PREPROD** : ~30 secondes
* **CD PROD** : ~45 secondes (backup inclus)
* **Health checks** : 3 tentatives, 10s timeout

Ressources
----------

* **Documentation complète** : :doc:`index`
* **Installation** : :doc:`installation`
* **FAQ** : :doc:`faq`
* **API** : :doc:`api/index`
* **GitHub** : https://github.com/julienlafrance/backtothefuturekitchen
