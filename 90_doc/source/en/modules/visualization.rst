Module visualization
====================

Analysis and interactive Plotly chart generation modules.

**User guide**: see :doc:`../usage` for detailed description of the 4 analyses.

visualization.analyse_trendlines_v2
-----------------------------------

Temporal trend analysis (1999-2018).

.. automodule:: mangetamain_analytics.visualization.analyse_trendlines_v2
   :members:
   :undoc-members:
   :show-inheritance:

Analyzed Metrics
^^^^^^^^^^^^^^^^^^^

* Interaction volume
* Preparation time (mean, median)
* Recipe complexity
* Number of ingredients
* Nutritional profiles
* Popular tags

Key Insights
^^^^^^^^^^^^^

* **2008-2018 Boom**: +350% interaction volume
* **Simplification**: Faster recipes (-15% preparation time)
* **Health**: Reduced calories, increased vegetarian/healthy tags
* **Complexity**: +12% score over 20 years
* **Ingredients**: Stable ~9 ingredients per recipe

Generated Visualizations
^^^^^^^^^^^^^^^^^^^^^^^^

* 6 synchronized temporal charts (subplots)
* Trends with linear regression (R² displayed)
* Major insights annotations
* Interactive Plotly zoom with rangeselector

Usage Example
^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_trendlines_v2
   from data.cached_loaders import get_recipes_clean

   # Load data
   recipes = get_recipes_clean()

   # Display complete analysis
   analyse_trendlines_v2.render_trendlines_analysis()

   # The analysis automatically generates:
   # - Temporal selection widgets (year slider)
   # - 6 trend charts
   # - Statistical metrics (R², p-values)

visualization.analyse_seasonality
---------------------------------

Seasonal pattern analysis.

.. automodule:: mangetamain_analytics.visualization.analyse_seasonality
   :members:
   :undoc-members:
   :show-inheritance:

Analyzed Metrics
^^^^^^^^^^^^^^^^^^^

* Distribution by season
* Monthly variations
* Seasonal activity peaks
* Recipe categories by season

Key Insights
^^^^^^^^^^^^^

* **Winter**: Calorie peaks (+12%), comfort recipes
* **Summer**: Light recipes, salads, BBQ
* **December**: Absolute peak (+45% vs annual average)
* **Autumn**: +18% recipes vs summer
* **Stable patterns**: Predictable annual reproduction

Generated Visualizations
^^^^^^^^^^^^^^^^^^^^^^^^

* Seasonal histograms with thematic palette (orange/blue/green/red)
* Monthly heatmaps (12 months × nutritional metrics)
* Nutritional distribution by season
* Automatic color coding by season

Usage Example
^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_seasonality
   from data.cached_loaders import get_recipes_clean

   # Load data
   recipes = get_recipes_clean()

   # Display seasonal analysis
   analyse_seasonality.render_seasonality_analysis()

   # The analysis generates:
   # - Season selector (Autumn, Winter, Spring, Summer)
   # - Seasonal distribution charts
   # - Interactive monthly heatmap
   # - Statistics by season

visualization.analyse_weekend
-----------------------------

Day of week vs weekend effect analysis.

.. automodule:: mangetamain_analytics.visualization.analyse_weekend
   :members:
   :undoc-members:
   :show-inheritance:

Analyzed Metrics
^^^^^^^^^^^^^^^^^^^

* Weekday vs weekend comparison
* Complexity variations
* Impact on recipe types

Key Insights
^^^^^^^^^^^^^

* **Monday = champion**: +45% publications vs weekly average
* **Saturday = low point**: -49% publications (lowest)
* **Duration/complexity**: No significant difference weekday vs weekend
* **Conclusion**: Publication timing ≠ recipe type
* **Psychological effect**: Planning at week start

Generated Visualizations
^^^^^^^^^^^^^^^^^^^^^^^^

* 3 comparative panels (volume, distribution, deviations from mean)
* Chi-2 statistical tests with displayed p-values
* Two-color bars weekday (blue) vs weekend (orange)
* Deviations from mean in percentage

Usage Example
^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_weekend
   from data.cached_loaders import get_recipes_clean

   # Load data
   recipes = get_recipes_clean()

   # Display weekend analysis
   analyse_weekend.render_weekend_analysis()

   # The analysis generates:
   # - Day by day comparison (7 days)
   # - Chi-2 statistical tests
   # - Complexity/duration distribution
   # - Insights on day of week effect

visualization.analyse_ratings
-----------------------------

User ratings analysis.

.. automodule:: mangetamain_analytics.visualization.analyse_ratings
   :members:
   :undoc-members:
   :show-inheritance:

Analyzed Metrics
^^^^^^^^^^^^^^^^^^^

* Rating distribution (0-5 stars)
* Aggregated statistics
* Correlations with characteristics
* Outlier analysis

Key Insights
^^^^^^^^^^^^^

* **Massive positive bias**: 78% ratings = 5 stars
* **Average**: 4.63/5 (asymmetric distribution)
* **Rare low ratings**: <2% ratings ≤ 2 stars
* **Weak correlations**: Complexity/time ≠ rating
* **Self-selection effect**: Satisfied users rate

Generated Visualizations
^^^^^^^^^^^^^^^^^^^^^^^^

* Interactive histograms with hover details
* Distribution with density curve
* Satisfaction metrics (mean, median, mode)
* Boxplots by rating range

Usage Example
^^^^^^^^^^^^^

.. code-block:: python

   from visualization import analyse_ratings
   from data.cached_loaders import get_ratings_longterm

   # Load ratings
   ratings = get_ratings_longterm()

   # Display ratings analysis
   analyse_ratings.render_ratings_analysis()

   # The analysis generates:
   # - Complete 0-5 stars distribution
   # - Descriptive statistics
   # - Correlations with recipe attributes
   # - Outlier identification

visualization.analyse_ratings_simple
------------------------------------

Simplified version of ratings analysis.

.. automodule:: mangetamain_analytics.visualization.analyse_ratings_simple
   :members:
   :undoc-members:
   :show-inheritance:

visualization.analyse_trendlines
--------------------------------

Initial version of trend analysis.

.. automodule:: mangetamain_analytics.visualization.analyse_trendlines
   :members:
   :undoc-members:
   :show-inheritance:

visualization.custom_charts
---------------------------

Utility functions for creating reusable charts.

.. automodule:: mangetamain_analytics.visualization.custom_charts
   :members:
   :undoc-members:
   :show-inheritance:

visualization.plotly_config
---------------------------

Plotly configuration for the application.

.. automodule:: mangetamain_analytics.visualization.plotly_config
   :members:
   :undoc-members:
   :show-inheritance:
