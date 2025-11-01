Streamlit Application
=====================

Architecture
------------

Interactive web application developed with Streamlit to present analyses from EDA notebooks.

Structure
---------

* Main page with sidebar navigation
* 4 independent analysis modules
* Interactive widgets (sliders, selectbox, filters)
* Data caching (TTL 1h) for performance

The 4 Analyses
--------------

1. Long-Term Trends Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source**: 01_long_term/recipe_analysis_trendline.ipynb

Presents evolution from 1999-2018 of:

* Interaction volume
* Preparation time
* Recipe complexity
* Nutritional profiles

**Visualizations**: 6 synchronized temporal charts with linear regression.

2. Seasonality Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source**: 02_seasonality/recipe_analysis_seasonality.ipynb

Identifies seasonal patterns:

* Recipe distribution by season
* Monthly nutritional variations
* Seasonal activity peaks

**Visualizations**: Histograms, monthly heatmaps, thematic color palette.

3. Weekend Effect Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^

**Source**: 03_week_end_effect/recipe_analysis_weekend.ipynb

Compares weekday vs weekend publications:

* Volume by day of week
* Impact on complexity/duration
* Statistical tests (Chi-2)

**Visualizations**: 3 comparative panels with displayed p-values.

4. Ratings Analysis
^^^^^^^^^^^^^^^^^^^^^^^

**Source**: 01_long_term/rating_analysis.ipynb

Studies user rating distribution:

* 0-5 star distribution
* Aggregated statistics
* Positive bias detection

**Visualizations**: Interactive histograms, boxplots, satisfaction metrics.

Data Loading
-----------------------

Data is loaded from S3 at startup via:

* DataLoader (error handling)
* cached_loaders (Streamlit cache TTL 1h)
* 178K recipes + 1.1M ratings (~450 MB Parquet)

Navigation
----------

* **Sidebar**: Analysis selection + environment badges
* **Filters**: Years, categories, nutritional ranges
* **Charts**: Interactive Plotly (zoom, pan, hover)

Performance
-----------

* First load: 5-10 seconds (S3)
* Subsequent loads: <0.1 second (cache)
* DNAT optimization: 500+ MB/s
