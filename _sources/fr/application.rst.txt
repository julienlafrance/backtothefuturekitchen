Application Streamlit
=====================

Architecture
------------

Application web interactive développée avec Streamlit pour présenter les analyses issues des notebooks EDA.

Structure
---------

* Page principale avec navigation sidebar
* 4 modules d'analyse indépendants
* Widgets interactifs (sliders, selectbox, filtres)
* Cache données (TTL 1h) pour performance

Les 4 Analyses
--------------

1. Analyse des Tendances Long-Terme
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source** : 01_long_term/recipe_analysis_trendline.ipynb

Présente l'évolution 1999-2018 de :

* Volume d'interactions
* Durée de préparation
* Complexité des recettes
* Profils nutritionnels

**Visualisations** : 6 graphiques temporels synchronisés avec régression linéaire.

2. Analyse de Saisonnalité
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source** : 02_seasonality/recipe_analysis_seasonality.ipynb

Identifie les patterns saisonniers :

* Distribution recettes par saison
* Variations mensuelles nutritionnelles
* Pics d'activité saisonniers

**Visualisations** : Histogrammes, heatmaps mensuelles, palette couleurs thématique.

3. Analyse Effet Weekend
^^^^^^^^^^^^^^^^^^^^^^^^^

**Source** : 03_week_end_effect/recipe_analysis_weekend.ipynb

Compare publications jour ouvré vs weekend :

* Volume par jour de semaine
* Impact sur complexité/durée
* Tests statistiques (Chi-2)

**Visualisations** : 3 panels comparatifs avec p-values affichées.

4. Analyse des Ratings
^^^^^^^^^^^^^^^^^^^^^^^

**Source** : 01_long_term/rating_analysis.ipynb

Étudie la distribution des notes utilisateurs :

* Distribution 0-5 étoiles
* Statistiques agrégées
* Détection biais positif

**Visualisations** : Histogrammes interactifs, boxplots, métriques satisfaction.

Chargement des Données
-----------------------

Les données sont chargées depuis S3 au démarrage via :

* DataLoader (gestion erreurs)
* cached_loaders (cache Streamlit TTL 1h)
* 178K recettes + 1.1M ratings (~450 MB Parquet)

Navigation
----------

* **Sidebar** : Sélection analyse + badges environnement
* **Filtres** : Années, catégories, plages nutritionnelles
* **Graphiques** : Interactifs Plotly (zoom, pan, hover)

Performance
-----------

* Premier chargement : 5-10 secondes (S3)
* Chargements suivants : <0.1 seconde (cache)
* Optimisation DNAT : 500+ MB/s
