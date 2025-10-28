Module visualization
====================

Modules d'analyse et génération de graphiques interactifs Plotly.

**Guide utilisateur** : voir :doc:`../usage` pour description détaillée des 4 analyses.

visualization.analyse_trendlines_v2
-----------------------------------

Analyse des tendances temporelles (1999-2018).

.. automodule:: mangetamain_analytics.visualization.analyse_trendlines_v2
   :members:
   :undoc-members:
   :show-inheritance:

Métriques Analysées
^^^^^^^^^^^^^^^^^^^

* Volume d'interactions
* Durée de préparation (moyenne, médiane)
* Complexité des recettes
* Nombre d'ingrédients
* Profils nutritionnels
* Tags populaires

Insights Clés
^^^^^^^^^^^^^

* **Boom 2008-2018** : +350% volume interactions
* **Simplification** : Recettes plus rapides (-15% temps préparation)
* **Santé** : Réduction calories, hausse tags végétariens/healthy
* **Complexité** : Score +12% sur 20 ans
* **Ingrédients** : Stable ~9 ingrédients par recette

Visualisations Générées
^^^^^^^^^^^^^^^^^^^^^^^^

* 6 graphiques temporels synchronisés (subplots)
* Tendances avec régression linéaire (R² affichés)
* Annotations des insights majeurs
* Zoom interactif Plotly avec rangeselector

Exemple d'Utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_trendlines_v2
   from data.cached_loaders import get_recipes_clean

   # Charger données
   recipes = get_recipes_clean()

   # Afficher analyse complète
   analyse_trendlines_v2.render_trendlines_analysis()

   # L'analyse génère automatiquement:
   # - Widgets sélection temporelle (slider années)
   # - 6 graphiques tendances
   # - Métriques statistiques (R², p-values)

visualization.analyse_seasonality
---------------------------------

Analyse des patterns saisonniers.

.. automodule:: mangetamain_analytics.visualization.analyse_seasonality
   :members:
   :undoc-members:
   :show-inheritance:

Métriques Analysées
^^^^^^^^^^^^^^^^^^^

* Distribution par saison
* Variations mensuelles
* Pics saisonniers d'activité
* Catégories de recettes par saison

Insights Clés
^^^^^^^^^^^^^

* **Hiver** : Pics calories (+12%), recettes réconfort
* **Été** : Recettes légères, salades, BBQ
* **Décembre** : Pic absolu (+45% vs moyenne annuelle)
* **Automne** : +18% recettes vs été
* **Patterns stables** : Reproduction annuelle prévisible

Visualisations Générées
^^^^^^^^^^^^^^^^^^^^^^^^

* Histogrammes saisonniers avec palette thématique (orange/bleu/vert/rouge)
* Heatmaps mensuelles (12 mois × métriques nutritionnelles)
* Distribution nutritionnelle par saison
* Codage couleur automatique par saison

Exemple d'Utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_seasonality
   from data.cached_loaders import get_recipes_clean

   # Charger données
   recipes = get_recipes_clean()

   # Afficher analyse saisonnière
   analyse_seasonality.render_seasonality_analysis()

   # L'analyse génère:
   # - Sélecteur saison (Automne, Hiver, Printemps, Été)
   # - Graphiques distribution saisonnière
   # - Heatmap mensuelle interactive
   # - Statistiques par saison

visualization.analyse_weekend
-----------------------------

Analyse de l'effet jour de la semaine vs weekend.

.. automodule:: mangetamain_analytics.visualization.analyse_weekend
   :members:
   :undoc-members:
   :show-inheritance:

Métriques Analysées
^^^^^^^^^^^^^^^^^^^

* Comparaison jours ouvrés vs weekend
* Variations de complexité
* Impact sur types de recettes

Insights Clés
^^^^^^^^^^^^^

* **Lundi = champion** : +45% publications vs moyenne hebdomadaire
* **Samedi = creux** : -49% publications (le plus bas)
* **Durée/complexité** : Aucune différence significative semaine vs weekend
* **Conclusion** : Moment publication ≠ type recette
* **Effet psychologique** : Planification début semaine

Visualisations Générées
^^^^^^^^^^^^^^^^^^^^^^^^

* 3 panels comparatifs (volume, distribution, écarts à la moyenne)
* Tests statistiques Chi-2 avec p-values affichées
* Barres bicolores semaine (bleu) vs weekend (orange)
* Écarts à la moyenne en pourcentage

Exemple d'Utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_weekend
   from data.cached_loaders import get_recipes_clean

   # Charger données
   recipes = get_recipes_clean()

   # Afficher analyse weekend
   analyse_weekend.render_weekend_analysis()

   # L'analyse génère:
   # - Comparaison jour par jour (7 jours)
   # - Tests statistiques Chi-2
   # - Distribution complexité/durée
   # - Insights sur effet jour semaine

visualization.analyse_ratings
-----------------------------

Analyse des notes utilisateurs.

.. automodule:: mangetamain_analytics.visualization.analyse_ratings
   :members:
   :undoc-members:
   :show-inheritance:

Métriques Analysées
^^^^^^^^^^^^^^^^^^^

* Distribution des notes (0-5 étoiles)
* Statistiques agrégées
* Corrélations avec caractéristiques
* Analyse des outliers

Insights Clés
^^^^^^^^^^^^^

* **Biais positif massif** : 78% notes = 5 étoiles
* **Moyenne** : 4.63/5 (distribution asymétrique)
* **Notes basses rares** : <2% notes ≤ 2 étoiles
* **Corrélations faibles** : Complexité/temps ≠ note
* **Effet auto-sélection** : Utilisateurs satisfaits notent

Visualisations Générées
^^^^^^^^^^^^^^^^^^^^^^^^

* Histogrammes interactifs avec hover détails
* Distribution avec courbe de densité
* Métriques satisfaction (moyenne, médiane, mode)
* Boxplots par tranche de rating

Exemple d'Utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_ratings
   from data.cached_loaders import get_ratings_longterm

   # Charger ratings
   ratings = get_ratings_longterm()

   # Afficher analyse ratings
   analyse_ratings.render_ratings_analysis()

   # L'analyse génère:
   # - Distribution complète 0-5 étoiles
   # - Statistiques descriptives
   # - Corrélations avec attributs recettes
   # - Identification outliers

visualization.analyse_ratings_simple
------------------------------------

Version simplifiée de l'analyse des ratings.

.. automodule:: mangetamain_analytics.visualization.analyse_ratings_simple
   :members:
   :undoc-members:
   :show-inheritance:

visualization.analyse_trendlines
--------------------------------

Version initiale de l'analyse des tendances.

.. automodule:: mangetamain_analytics.visualization.analyse_trendlines
   :members:
   :undoc-members:
   :show-inheritance:

visualization.custom_charts
---------------------------

Fonctions utilitaires pour créer des graphiques réutilisables.

.. automodule:: mangetamain_analytics.visualization.custom_charts
   :members:
   :undoc-members:
   :show-inheritance:

visualization.plotly_config
---------------------------

Configuration Plotly pour l'application.

.. automodule:: mangetamain_analytics.visualization.plotly_config
   :members:
   :undoc-members:
   :show-inheritance:
