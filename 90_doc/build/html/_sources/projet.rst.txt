Le Projet
=========

Vue d'ensemble
--------------

Analyse de données culinaires avec workflow complet : exploration → développement → visualisation → déploiement.

Processus de Développement
---------------------------

**1. Exploration de Données (00_eda/)**

* Notebooks Jupyter d'analyse exploratoire
* 9 notebooks organisés par thématique (tendances, saisonnalité, weekend, ratings)
* Identification des patterns et insights

**2. Développement Application (10_preprod/)**

* Transformation analyses notebook → modules Python réutilisables
* Application Streamlit pour présentation interactive des résultats
* Architecture modulaire (utils, visualization, data, exceptions)

**3. Déploiement (20_prod/)**

* Pipeline CI/CD automatisé
* Environnements preprod/prod séparés
* Tests et validation continue

Correspondance EDA → Application
---------------------------------

Chaque analyse Streamlit s'appuie sur un ou plusieurs notebooks EDA :

* **Analyse tendances** ← 01_long_term/recipe_analysis_trendline.ipynb
* **Analyse saisonnalité** ← 02_seasonality/recipe_analysis_seasonality.ipynb
* **Analyse weekend** ← 03_week_end_effect/recipe_analysis_weekend.ipynb
* **Analyse ratings** ← 01_long_term/rating_analysis.ipynb

Les notebooks contiennent l'exploration complète (statistiques descriptives, visualisations, tests d'hypothèses). L'application Streamlit présente les résultats de manière interactive.

Stack Technique
---------------

* Python 3.13.3
* Streamlit 1.50.0 (interface web)
* DuckDB 1.4.0 (base OLAP)
* Polars 1.19.0 (traitement données)
* Plotly 5.24.1 (visualisations)

Environnements
--------------

* **PREPROD** : https://mangetamain.lafrance.io/ (port 8500)
* **PRODUCTION** : https://backtothefuturekitchen.lafrance.io/ (port 8501)

Standards Appliqués
-------------------

* Type hinting complet
* Tests unitaires pytest (93% coverage)
* Documentation docstrings Google style
* Validation PEP8 automatique
* Gestion exceptions personnalisées
* Pipeline CI/CD avec GitHub Actions
