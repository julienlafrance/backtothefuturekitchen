Module utils
============

Utility functions for "Back to the Kitchen" visual identity: colors and Plotly theme.

**Practical usage**: see code examples below for integration into your charts.

utils.color_theme
------------------

ColorTheme OOP class for "Back to the Kitchen" visual identity.

.. automodule:: mangetamain_analytics.utils.color_theme
   :members:
   :undoc-members:
   :show-inheritance:

Main Constants
^^^^^^^^^^^^^^

**Base colors:**

* ``ORANGE_PRIMARY``: Bright orange #FF8C00 (primary color)
* ``ORANGE_SECONDARY``: Red/Orange #E24E1B (secondary accent)
* ``SECONDARY_ACCENT``: Golden yellow #FFD700
* ``BACKGROUND_MAIN``: Dark gray #1E1E1E (main area)
* ``BACKGROUND_SIDEBAR``: Pure black #000000 (sidebar)
* ``BACKGROUND_CARD``: Medium gray #333333 (cards and widgets)
* ``TEXT_PRIMARY``: Light gray #F0F0F0 (main text)
* ``TEXT_SECONDARY``: Medium gray #888888 (secondary text)
* ``TEXT_WHITE``: Pure white #ffffff

**Status colors:**

* ``SUCCESS``: Green #28A745 (success, PROD badge)
* ``WARNING``: Yellow #FFC107 (warnings, PREPROD badge)
* ``ERROR``: Red #DC3545 (errors)
* ``INFO``: Cyan #17A2B8 (information)

**Chart palettes:**

* ``CHART_COLORS``: List of 8 colors for Plotly charts
* ``STEELBLUE_PALETTE``: Palette of 3 shades of blue

**Seasonal palettes:**

* ``get_seasonal_colors()``: Mapping season → color (Autumn, Winter, Spring, Summer)
* ``get_seasonal_color(season)``: Individual color for a season

**Utility methods:**

* ``to_rgba(hex_color, alpha)``: Convert HEX to RGBA with validation
* ``get_plotly_theme()``: Return custom Plotly theme

Usage Examples
^^^^^^^^^^^^^^^

**Using primary colors:**

.. code-block:: python

   from utils.color_theme import ColorTheme
   import plotly.graph_objects as go

   # Chart with primary color
   fig = go.Figure()
   fig.add_trace(go.Bar(
       x=['A', 'B', 'C'],
       y=[10, 20, 30],
       marker_color=ColorTheme.ORANGE_PRIMARY
   ))

**Using chart palette:**

.. code-block:: python

   from utils.color_theme import ColorTheme

   # For multi-series charts
   fig = go.Figure()
   for i, serie in enumerate(data_series):
       color = ColorTheme.CHART_COLORS[i % len(ColorTheme.CHART_COLORS)]
       fig.add_trace(go.Scatter(
           x=serie['x'],
           y=serie['y'],
           name=serie['name'],
           line=dict(color=color)
       ))

**Using seasonal colors:**

.. code-block:: python

   from utils.color_theme import ColorTheme

   # Color by season (method 1)
   season_color = ColorTheme.get_seasonal_colors()['Autumn']  # #FF8C00

   # Color by season (method 2 - recommended)
   season_color = ColorTheme.get_seasonal_color('Autumn')  # #FF8C00

**Convert to RGBA:**

.. code-block:: python

   from utils.color_theme import ColorTheme

   # Add transparency
   transparent_orange = ColorTheme.to_rgba(ColorTheme.ORANGE_PRIMARY, alpha=0.5)
   # Returns: 'rgba(255, 140, 0, 0.5)'

utils.chart_theme
-----------------

Apply unified theme to Plotly charts.

.. automodule:: mangetamain_analytics.utils.chart_theme
   :members:
   :undoc-members:
   :show-inheritance:

Main Functions
^^^^^^^^^^^^^^^^^^^^^

* ``apply_chart_theme(fig, title)``: Apply theme to a Plotly chart
* ``apply_subplot_theme(fig, num_rows, num_cols)``: Theme for multiple subplots
* ``get_bar_color()``: Primary color for histogram bars
* ``get_line_colors()``: List of colors for multiple lines
* ``get_scatter_color()``: Color for scatter plots
* ``get_reference_line_color()``: Color for reference lines

Usage Examples
^^^^^^^^^^^^^^^

**Simple chart with theme:**

.. code-block:: python

   from utils import chart_theme
   import plotly.graph_objects as go

   fig = go.Figure()
   fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

   # Apply theme
   chart_theme.apply_chart_theme(fig, title="My Chart")

   # Display with Streamlit
   st.plotly_chart(fig, use_container_width=True)

**Chart with subplots:**

.. code-block:: python

   from utils import chart_theme
   from plotly.subplots import make_subplots

   # Create 2x2 layout
   fig = make_subplots(
       rows=2, cols=2,
       subplot_titles=("Chart 1", "Chart 2", "Chart 3", "Chart 4")
   )

   # Add traces
   fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]), row=1, col=1)
   fig.add_trace(go.Bar(x=[1, 2], y=[5, 6]), row=1, col=2)

   # Apply theme for subplots
   chart_theme.apply_subplot_theme(fig, num_rows=2, num_cols=2)

**Using predefined colors:**

.. code-block:: python

   from utils import chart_theme

   # Color for bars
   bar_color = chart_theme.get_bar_color()  # ORANGE_PRIMARY

   # Colors for multiple lines
   line_colors = chart_theme.get_line_colors()
   # Returns: [ORANGE_PRIMARY, STEELBLUE, ORANGE_SECONDARY, ...]

   # Color for scatter
   scatter_color = chart_theme.get_scatter_color()  # STEELBLUE

   # Color for reference line (mean, median)
   ref_color = chart_theme.get_reference_line_color()  # SECONDARY_ACCENT

**Complete chart with custom theme:**

.. code-block:: python

   from utils import chart_theme
   from utils.color_theme import ColorTheme
   import plotly.graph_objects as go

   fig = go.Figure()

   # Bars with custom color
   fig.add_trace(go.Bar(
       x=['Monday', 'Tuesday', 'Wednesday'],
       y=[120, 95, 140],
       marker_color=chart_theme.get_bar_color(),
       name='Volume'
   ))

   # Reference line (mean)
   fig.add_hline(
       y=118.3,
       line_dash="dash",
       line_color=chart_theme.get_reference_line_color(),
       annotation_text="Mean"
   )

   # Apply unified theme
   chart_theme.apply_chart_theme(
       fig,
       title="Volume by day of week"
   )

   # Additional customization
   fig.update_layout(
       showlegend=True,
       height=500
   )

   st.plotly_chart(fig, use_container_width=True)

Automatically Applied Theme
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The theme automatically configures:

* **Background**: Transparent background, subtle gray grid
* **Text**: ``TEXT_PRIMARY`` color (#F0F0F0)
* **Axes**: Gray color, dashed grid lines
* **Hover**: Labels formatted with thousands separators
* **Font**: Arial 14px for titles, 12px for axes
* **Margins**: Optimized for Streamlit (l=80, r=50, t=100, b=80)

**Note**: Use ``use_container_width=True`` with ``st.plotly_chart()`` for responsive design.
