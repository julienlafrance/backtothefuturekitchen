Utilisation
===========

Architecture de l'Application
------------------------------

L'application Mangetamain Analytics est organisée en modules :

* **utils/** : Fonctions utilitaires (couleurs, thème graphique)
* **visualization/** : Modules d'analyse et visualisation
* **data/** : Chargement et cache des données

Modules d'Analyse Disponibles
------------------------------

1. Analyse des Tendances
^^^^^^^^^^^^^^^^^^^^^^^^^

Module : ``visualization.analyse_trendlines_v2``

Analyse l'évolution des recettes de 1999 à 2018 :

* Volume d'interactions
* Durée de préparation moyenne et médiane
* Complexité des recettes
* Nombre d'ingrédients
* Profils nutritionnels
* Tags populaires

**Visualisations :**

* Graphiques temporels interactifs
* Tendances avec régression linéaire
* Subplots synchronisés (6 graphiques)

2. Analyse Saisonnière
^^^^^^^^^^^^^^^^^^^^^^^

Module : ``visualization.analyse_seasonality``

Identifie les patterns saisonniers :

* Recettes par saison
* Variations mensuelles des préférences nutritionnelles
* Pics saisonniers d'activité
* Distribution des catégories par saison

**Visualisations :**

* Histogrammes saisonniers
* Heatmaps mensuelles
* Graphiques de distribution

3. Analyse Weekend
^^^^^^^^^^^^^^^^^^

Module : ``visualization.analyse_weekend``

Étudie l'impact du rythme hebdomadaire :

* Comparaison jours ouvrés vs weekend
* Variations de complexité selon disponibilité
* Impact sur types de recettes

4. Analyse des Ratings
^^^^^^^^^^^^^^^^^^^^^^^

Module : ``visualization.analyse_ratings``

Étudie les notes utilisateurs :

* Distribution des notes (0-5 étoiles)
* Statistiques agrégées
* Corrélations avec caractéristiques recettes
* Analyse des outliers

**Visualisations :**

* Histogrammes interactifs
* Graphiques de distribution
* Métriques de satisfaction

Navigation dans l'Application
------------------------------

Sidebar
^^^^^^^

Le menu sidebar permet de :

* Sélectionner l'analyse à afficher
* Visualiser les badges environnement (PREPROD/PROD)
* Vérifier le statut S3

Widgets Interactifs
^^^^^^^^^^^^^^^^^^^

Chaque analyse propose des widgets :

* Sélecteurs temporels (plages de dates, mois, années)
* Filtres (catégories, tags, plages nutritionnelles)
* Sélecteurs de métriques

Personnalisation des Graphiques
--------------------------------

Utiliser le Module chart_theme
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from utils import chart_theme
   import plotly.graph_objects as go

   fig = go.Figure()
   # Ajouter traces
   chart_theme.apply_chart_theme(fig, title="Mon graphique")

Couleurs de la Charte
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from utils import colors

   primary = colors.ORANGE_PRIMARY      # #FF8C00
   secondary = colors.ORANGE_SECONDARY  # #E24E1B
   background = colors.BACKGROUND_MAIN  # #1E1E1E
   text = colors.TEXT_PRIMARY           # #F0F0F0

   # Palette complète pour graphiques
   chart_colors = colors.CHART_COLORS  # 8 couleurs

Cache des Données
-----------------

L'application utilise ``@st.cache_data`` pour optimiser les performances :

* TTL : 1 heure (3600 secondes)
* Chargement unique depuis S3
* Navigation instantanée entre pages

.. code-block:: python

   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Chargé une seule fois par heure
   recipes = get_recipes_clean()
   ratings = get_ratings_longterm()

Rafraîchir les Données
^^^^^^^^^^^^^^^^^^^^^^^

Pour forcer le rechargement des données :

1. Accéder au menu Streamlit (coin supérieur droit)
2. Sélectionner "Clear cache"
3. Recharger la page

URLs des Environnements
-----------------------

* **PREPROD** : https://mangetamain.lafrance.io/
* **PRODUCTION** : https://backtothefuturekitchen.lafrance.io/
