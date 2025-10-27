Module utils
============

Le module ``utils`` contient les fonctions utilitaires pour la charte graphique.

utils.colors
------------

Définit la palette de couleurs du projet "Back to the Kitchen".

.. automodule:: mangetamain_analytics.utils.colors
   :members:
   :undoc-members:
   :show-inheritance:

Constantes Principales
^^^^^^^^^^^^^^^^^^^^^^

**Couleurs de base :**

* ``ORANGE_PRIMARY`` : Orange vif #FF8C00 (couleur principale)
* ``ORANGE_SECONDARY`` : Rouge/Orange #E24E1B (accent secondaire)
* ``SECONDARY_ACCENT`` : Jaune doré #FFD700
* ``BACKGROUND_MAIN`` : Gris foncé #1E1E1E (zone principale)
* ``BACKGROUND_SIDEBAR`` : Noir pur #000000 (sidebar)
* ``BACKGROUND_CARD`` : Gris moyen #333333 (cards et widgets)
* ``TEXT_PRIMARY`` : Gris clair #F0F0F0 (texte principal)
* ``TEXT_SECONDARY`` : Gris moyen #888888 (texte secondaire)
* ``TEXT_WHITE`` : Blanc pur #ffffff

**Couleurs d'état :**

* ``SUCCESS`` : Vert #28A745 (succès, badge PROD)
* ``WARNING`` : Jaune #FFC107 (warnings, badge PREPROD)
* ``ERROR`` : Rouge #DC3545 (erreurs)
* ``INFO`` : Cyan #17A2B8 (informations)

**Palettes graphiques :**

* ``CHART_COLORS`` : Liste de 8 couleurs pour graphiques Plotly
* ``STEELBLUE_PALETTE`` : Palette de 3 nuances de bleu

**Fonctions utilitaires :**

* ``get_rgba(hex_color, alpha)`` : Convertit HEX en RGBA
* ``get_plotly_theme()`` : Retourne le thème Plotly personnalisé

utils.chart_theme
-----------------

Applique le thème unifié aux graphiques Plotly.

.. automodule:: mangetamain_analytics.utils.chart_theme
   :members:
   :undoc-members:
   :show-inheritance:

Fonctions Principales
^^^^^^^^^^^^^^^^^^^^^

* ``apply_chart_theme(fig, title)`` : Applique le thème à un graphique Plotly
* ``apply_subplot_theme(fig, num_rows, num_cols)`` : Thème pour subplots multiples
* ``get_bar_color()`` : Couleur principale pour barres d'histogramme
* ``get_line_colors()`` : Liste de couleurs pour lignes multiples
* ``get_scatter_color()`` : Couleur pour scatter plots
* ``get_reference_line_color()`` : Couleur pour lignes de référence

Exemple d'Utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from utils import chart_theme
   import plotly.graph_objects as go

   fig = go.Figure()
   fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

   # Appliquer le thème
   chart_theme.apply_chart_theme(fig, title="Mon graphique")

   # Afficher avec Streamlit
   st.plotly_chart(fig, use_container_width=True)
