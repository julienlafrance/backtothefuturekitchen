Usage
===========

Usage guide for the Mangetamain Analytics application.

**Code documentation**: see :doc:`modules/index` for detailed reference.

**Code examples**: see :doc:`modules/utils` (colors, theme) and :doc:`modules/data` (data loading).

Application Architecture
------------------------------

The Mangetamain Analytics application is organized into modules:

* **utils/**: Utility functions (colors, chart theme)
* **visualization/**: Analysis and visualization modules
* **data/**: Data loading and caching

Available Analysis Modules
------------------------------

1. Trends Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^

Module: ``visualization.analyse_trendlines_v2``

Analyzes recipe evolution from 1999 to 2018:

* Interaction volume (exponential growth)
* Preparation time (15% reduction over 20 years)
* Recipe complexity (+12% score)
* Number of ingredients (stable ~9 ingredients)
* Nutritional profiles (-8% calories)
* Popular tags (shift towards healthy/vegan)

**Key insights**:

* **2008-2018 Boom**: +350% interaction volume
* **Simplification**: Faster recipes (-15% time)
* **Health**: Reduced calories, increased vegetarian tags

**Visualizations**:

* Interactive temporal charts with zoom
* Trends with linear regression (R² displayed)
* Synchronized subplots (6 charts)
* Major insights annotations

2. Seasonal Analysis
^^^^^^^^^^^^^^^^^^^^^^^

Module: ``visualization.analyse_seasonality``

Identifies seasonal patterns:

* Recipes by season (+18% autumn vs summer)
* Monthly nutritional variations
* Seasonal activity peaks
* Category distribution by season

**Key insights**:

* **Winter**: Calorie peaks (+12%), comfort recipes
* **Summer**: Light recipes, salads, BBQ
* **December**: Absolute peak (+45% vs average)
* **Stable patterns**: Annual reproduction

**Visualizations**:

* Seasonal histograms with thematic palette
* Monthly heatmaps (12 months × metrics)
* Nutritional distribution charts
* Season color coding (orange/blue/green/red)

3. Weekend Analysis
^^^^^^^^^^^^^^^^^^

Module: ``visualization.analyse_weekend``

Studies weekly rhythm impact:

* Weekday vs weekend comparison
* Complexity variations by availability
* Impact on recipe types

**Key insights**:

* **Monday = champion**: +45% publications vs average
* **Saturday = low point**: -49% publications
* **Duration/complexity**: No significant difference
* **Conclusion**: Publication timing ≠ recipe type
* **Psychological effect**: Week start planning

**Visualizations**:

* 3 comparative panels (volume, distribution, deviations)
* Chi-2 statistical tests (displayed p-values)
* Two-color bars weekday/weekend
* Deviations from mean in %

4. Ratings Analysis
^^^^^^^^^^^^^^^^^^^^^^^

Module: ``visualization.analyse_ratings``

Studies user ratings:

* Rating distribution (0-5 stars)
* Aggregated statistics (mean 4.63/5)
* Correlations with recipe characteristics
* Outlier analysis

**Key insights**:

* **Massive positive bias**: 78% ratings = 5 stars
* **Mean: 4.63/5** (asymmetric distribution)
* **Rare low ratings**: <2% ratings ≤ 2 stars
* **Weak correlations**: Complexity/time ≠ rating
* **Self-selection effect**: Satisfied users rate

**Visualizations**:

* Interactive histograms (hover details)
* Distribution with density curve
* Satisfaction metrics (mean, median, mode)
* Boxplots by rating range

Application Navigation
------------------------------

Sidebar
^^^^^^^

The sidebar menu allows you to:

* Select the analysis to display
* View environment badges (PREPROD/PROD)
* Check S3 status

Interactive Widgets
^^^^^^^^^^^^^^^^^^^

Each analysis provides widgets:

* Temporal selectors (date ranges, months, years)
* Filters (categories, tags, nutritional ranges)
* Metrics selectors

Customization and API
-----------------------

**Chart theme and colors**: see :doc:`modules/utils` for complete examples (``chart_theme``, ``colors``).

**Data loading and caching**: see :doc:`modules/data` for details on Streamlit cache (TTL 3600s) and functions ``get_recipes_clean()``, ``get_ratings_longterm()``.

**Environment URLs**: see :doc:`glossaire` for PREPROD/PRODUCTION.
