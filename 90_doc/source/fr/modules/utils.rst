Module utils
============

Fonctions utilitaires pour la charte graphique "Back to the Kitchen" : couleurs et thème Plotly.

**Usage pratique** : voir exemples code ci-dessous pour intégration dans vos graphiques.

utils.color_theme
------------------

Classe POO ColorTheme pour la charte graphique "Back to the Kitchen".

.. automodule:: mangetamain_analytics.utils.color_theme
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

**Palettes saisonnières :**

* ``get_seasonal_colors()`` : Mapping saison → couleur (Automne, Hiver, Printemps, Été)
* ``get_seasonal_color(season)`` : Couleur individuelle pour une saison

**Méthodes utilitaires :**

* ``to_rgba(hex_color, alpha)`` : Convertit HEX en RGBA avec validation
* ``get_plotly_theme()`` : Retourne le thème Plotly personnalisé

Exemples d'Utilisation
^^^^^^^^^^^^^^^^^^^^^^^

**Utiliser les couleurs principales :**

.. code-block:: python

   from utils.color_theme import ColorTheme
   import plotly.graph_objects as go

   # Graphique avec couleur primaire
   fig = go.Figure()
   fig.add_trace(go.Bar(
       x=['A', 'B', 'C'],
       y=[10, 20, 30],
       marker_color=ColorTheme.ORANGE_PRIMARY
   ))

**Utiliser la palette graphique :**

.. code-block:: python

   from utils.color_theme import ColorTheme

   # Pour graphiques multi-séries
   fig = go.Figure()
   for i, serie in enumerate(data_series):
       color = ColorTheme.CHART_COLORS[i % len(ColorTheme.CHART_COLORS)]
       fig.add_trace(go.Scatter(
           x=serie['x'],
           y=serie['y'],
           name=serie['name'],
           line=dict(color=color)
       ))

**Utiliser les couleurs saisonnières :**

.. code-block:: python

   from utils.color_theme import ColorTheme

   # Couleur par saison (méthode 1)
   season_color = ColorTheme.get_seasonal_colors()['Automne']  # #FF8C00

   # Couleur par saison (méthode 2 - recommandée)
   season_color = ColorTheme.get_seasonal_color('Automne')  # #FF8C00

**Convertir en RGBA :**

.. code-block:: python

   from utils.color_theme import ColorTheme

   # Ajouter transparence
   transparent_orange = ColorTheme.to_rgba(ColorTheme.ORANGE_PRIMARY, alpha=0.5)
   # Retourne: 'rgba(255, 140, 0, 0.5)'

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

Exemples d'Utilisation
^^^^^^^^^^^^^^^^^^^^^^^

**Graphique simple avec thème :**

.. code-block:: python

   from utils import chart_theme
   import plotly.graph_objects as go

   fig = go.Figure()
   fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

   # Appliquer le thème
   chart_theme.apply_chart_theme(fig, title="Mon graphique")

   # Afficher avec Streamlit
   st.plotly_chart(fig, use_container_width=True)

**Graphique avec subplots :**

.. code-block:: python

   from utils import chart_theme
   from plotly.subplots import make_subplots

   # Créer layout 2x2
   fig = make_subplots(
       rows=2, cols=2,
       subplot_titles=("Graphique 1", "Graphique 2", "Graphique 3", "Graphique 4")
   )

   # Ajouter traces
   fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
   fig.add_trace(go.Bar(x=[1, 2], y=[5, 6]), row=1, col=2)

   # Appliquer thème pour subplots
   chart_theme.apply_subplot_theme(fig, num_rows=2, num_cols=2)

**Utiliser les couleurs prédéfinies :**

.. code-block:: python

   from utils import chart_theme

   # Couleur pour barres
   bar_color = chart_theme.get_bar_color()  # ORANGE_PRIMARY

   # Couleurs pour lignes multiples
   line_colors = chart_theme.get_line_colors()
   # Retourne: [ORANGE_PRIMARY, STEELBLUE, ORANGE_SECONDARY, ...]

   # Couleur pour scatter
   scatter_color = chart_theme.get_scatter_color()  # STEELBLUE

   # Couleur ligne référence (moyenne, médiane)
   ref_color = chart_theme.get_reference_line_color()  # SECONDARY_ACCENT

**Graphique complet avec thème personnalisé :**

.. code-block:: python

   from utils import chart_theme
   from utils.color_theme import ColorTheme
   import plotly.graph_objects as go

   fig = go.Figure()

   # Barres avec couleur personnalisée
   fig.add_trace(go.Bar(
       x=['Lundi', 'Mardi', 'Mercredi'],
       y=[120, 95, 140],
       marker_color=chart_theme.get_bar_color(),
       name='Volume'
   ))

   # Ligne de référence (moyenne)
   fig.add_hline(
       y=118.3,
       line_dash="dash",
       line_color=chart_theme.get_reference_line_color(),
       annotation_text="Moyenne"
   )

   # Appliquer thème unifié
   chart_theme.apply_chart_theme(
       fig,
       title="Volume par jour de semaine"
   )

   # Personnalisation supplémentaire
   fig.update_layout(
       showlegend=True,
       height=500
   )

   st.plotly_chart(fig, use_container_width=True)

Thème Appliqué Automatiquement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le thème configure automatiquement :

* **Background** : Fond transparent, grille subtile grise
* **Texte** : Couleur ``TEXT_PRIMARY`` (#F0F0F0)
* **Axes** : Couleur grise, lignes de grille pointillées
* **Hover** : Labels formatés avec séparateurs de milliers
* **Police** : Arial 14px pour titres, 12px pour axes
* **Marges** : Optimisées pour Streamlit (l=80, r=50, t=100, b=80)

**Note** : Utiliser ``use_container_width=True`` avec ``st.plotly_chart()`` pour responsive design.
