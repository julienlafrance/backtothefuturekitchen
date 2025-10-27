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

* ``ORANGE_PRIMARY`` : Couleur primaire (#FF8C00)
* ``ORANGE_SECONDARY`` : Couleur secondaire (#E24E1B)
* ``BACKGROUND_MAIN`` : Fond principal (#1E1E1E)
* ``TEXT_PRIMARY`` : Texte principal (#F0F0F0)
* ``CHART_COLORS`` : Palette de 8 couleurs pour graphiques

utils.chart_theme
-----------------

Applique le thème unifié aux graphiques Plotly.

.. automodule:: mangetamain_analytics.utils.chart_theme
   :members:
   :undoc-members:
   :show-inheritance:

Fonctions Principales
^^^^^^^^^^^^^^^^^^^^^

* ``apply_chart_theme()`` : Applique le thème à un graphique Plotly
* ``get_default_layout()`` : Retourne la configuration de layout par défaut

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
