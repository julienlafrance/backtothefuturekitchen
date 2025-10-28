Documentation Mangetamain Analytics
====================================

Application web d'analyse de données culinaires basée sur le dataset Food.com (2.3M interactions, 1999-2018).

Environnements Déployés
-----------------------

* PREPROD : https://mangetamain.lafrance.io/
* PRODUCTION : https://backtothefuturekitchen.lafrance.io/

Dataset
-------

* 178,265 recettes
* 1.1M+ ratings utilisateurs
* 25,076 contributeurs
* Période 1999-2018

Métriques Projet
----------------

* Tests : 118 tests, 93% coverage
* Documentation : Sphinx auto-générée, docstrings Google style
* CI/CD : Pipeline automatisé GitHub Actions
* Type hinting : Complet sur toutes fonctions

Navigation
----------

.. toctree::
   :maxdepth: 2
   :caption: Le Projet

   projet
   quickstart
   installation

.. toctree::
   :maxdepth: 2
   :caption: Application Streamlit

   application
   usage

.. toctree::
   :maxdepth: 2
   :caption: Documentation Code

   modules/index
   modules/utils
   modules/visualization
   modules/data
   modules/exceptions
   modules/infrastructure

.. toctree::
   :maxdepth: 2
   :caption: Infrastructure

   s3
   architecture
   cicd
   tests

.. toctree::
   :maxdepth: 2
   :caption: Standards Qualité

   conformite

.. toctree::
   :maxdepth: 2
   :caption: Référence

   faq
   glossaire

Indices
=======

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
