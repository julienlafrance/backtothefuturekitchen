Documentation Mangetamain Analytics
====================================

**Mangetamain Analytics** est une application web interactive d'analyse de données culinaires Food.com développée dans le cadre d'un projet académique.

Architecture : Python 3.13.3 + Streamlit + DuckDB + S3 Storage.

Liens
-----

* Application PREPROD: https://mangetamain.lafrance.io/
* Application PRODUCTION: https://backtothefuturekitchen.lafrance.io/
* Repository GitHub: https://github.com/julienlafrance/backtothefuturekitchen

Fonctionnalités Principales
----------------------------

* **Analyse des tendances** : Évolution des recettes 1999-2018
* **Analyse saisonnière** : Patterns saisonniers des recettes
* **Analyse weekend** : Impact du rythme hebdomadaire
* **Analyse des ratings** : Distribution des notes utilisateurs
* **Visualisations interactives** : Graphiques Plotly dynamiques

Dataset Food.com
-----------------

* 2.3M+ interactions (1999-2018)
* 25K+ utilisateurs contributeurs
* 230K+ recettes avec tags, nutrition, ingrédients
* 1.1M+ ratings utilisateurs

Démarrage Rapide
----------------

**Installation locale**:

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git
   cd backtothefuturekitchen/000_dev/10_preprod
   uv sync
   uv run streamlit run src/mangetamain_analytics/main.py

**Voir**: :doc:`installation` pour guide complet

**Documentation S3**: :doc:`s3` pour configuration stockage

**Tests**: 93% coverage, 118 tests → :doc:`tests`

**CI/CD**: Pipeline automatisé → :doc:`cicd`

Sommaire
--------

.. toctree::
   :maxdepth: 2
   :caption: Guide Utilisateur

   installation
   usage
   faq
   s3
   architecture
   cicd
   tests
   conformite

.. toctree::
   :maxdepth: 3
   :caption: Référence API

   api/index
   api/utils
   api/visualization
   api/data
   api/infrastructure

Indices et Tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
