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

Sommaire
--------

.. toctree::
   :maxdepth: 2
   :caption: Guide Utilisateur

   installation
   usage
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

Indices et Tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
