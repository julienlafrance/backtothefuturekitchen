Module data
===========

Data loading and caching from S3 Parquet with Streamlit @st.cache_data (TTL 3600s).

**Data**: 178K recipes + 1.1M ratings (~450 MB Parquet) → see :doc:`../glossaire` for details.

data.loaders
------------

DataLoader class for data loading with robust error handling.

.. automodule:: mangetamain_analytics.data.loaders
   :members:
   :undoc-members:
   :show-inheritance:

DataLoader Class
^^^^^^^^^^^^^^^^^

Encapsulates loading logic from mangetamain_data_utils with custom exceptions.

**Methods**:

* ``load_recipes()``: Load recipes from S3 Parquet
* ``load_ratings(min_interactions, return_metadata, verbose)``: Load ratings for long-term analysis

**Raised Exceptions**:

* ``DataLoadError``: If module not found or S3 loading fails

**Example**:

.. code-block:: python

   from mangetamain_analytics.data.loaders import DataLoader
   from mangetamain_analytics.exceptions import DataLoadError

   loader = DataLoader()

   try:
       recipes = loader.load_recipes()
       print(f"Loaded {len(recipes)} recipes")
   except DataLoadError as e:
       print(f"Error: {e.source} - {e.detail}")

Relationship with cached_loaders
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``cached_loaders`` uses DataLoader internally:

1. ``DataLoader``: Business logic + error handling (testable)
2. ``cached_loaders``: Wrapping with ``@st.cache_data`` (Streamlit cache)

This separation allows testing DataLoader without mocking Streamlit.

data.cached_loaders
-------------------

Data loading functions with Streamlit cache.

.. automodule:: mangetamain_analytics.data.cached_loaders
   :members:
   :undoc-members:
   :show-inheritance:

Main Functions
^^^^^^^^^^^^^^^^^^^^^

* ``get_recipes_clean()``: Load recipes from S3 Parquet
* ``get_ratings_longterm()``: Load ratings for long-term analysis

Data Schema
^^^^^^^^^^^^^^^^^^

**get_recipes_clean() returns**:

* ``id``: Unique recipe identifier (int)
* ``name``: Recipe name (str)
* ``minutes``: Preparation time in minutes (int)
* ``submitted``: Submission date (date)
* ``year``: Submission year (int)
* ``n_ingredients``: Number of ingredients (int)
* ``complexity_score``: Complexity score 0-10 (float)
* ``calories``, ``protein``, ``fat``, ``sodium``: Nutritional information (float)
* ``tags``: Recipe tags list (list[str])
* ``day_of_week``: Day of week (0=Monday, 6=Sunday)
* ``season``: Season (Autumn, Winter, Spring, Summer)

**Size**: 178,265 recipes, ~250 MB compressed Parquet

**get_ratings_longterm() returns**:

* ``user_id``: User identifier (int)
* ``recipe_id``: Recipe identifier (int)
* ``date``: Rating date (date)
* ``rating``: 0-5 star rating (int)
* ``review``: Optional comment text (str)

**Size**: 1.1M+ ratings, ~180 MB compressed Parquet

Advanced Options
^^^^^^^^^^^^^^^^

**get_ratings_longterm() accepts**:

* ``min_interactions`` (int, default 100): Filter recipes with minimum interactions
* ``return_metadata`` (bool, default False): Return tuple (data, metadata)
* ``verbose`` (bool, default False): Display detailed loading logs

Metadata contains:

* ``total_ratings``: Total number of ratings
* ``total_users``: Number of unique users
* ``total_recipes``: Number of rated recipes
* ``date_range``: Temporal range (min, max)
* ``load_time_ms``: Loading time in milliseconds

Cache Mechanism
^^^^^^^^^^^^^^^^^^

Functions use the ``@st.cache_data`` decorator with:

* **TTL**: 3600 seconds (1 hour)
* **Spinner**: Visible loading message
* **Lazy imports**: Local test compatibility

Usage Examples
^^^^^^^^^^^^^^^

**Basic loading:**

.. code-block:: python

   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Loaded once per hour from S3
   recipes = get_recipes_clean()  # DataFrame 178K recipes
   ratings = get_ratings_longterm()  # DataFrame 1.1M+ ratings

   print(f"Loaded {len(recipes)} recipes, {len(ratings)} ratings")

**With advanced options:**

.. code-block:: python

   # Filter popular recipes + metadata
   ratings, metadata = get_ratings_longterm(
       min_interactions=100,  # Minimum 100 ratings
       return_metadata=True,
       verbose=True
   )

   print(f"Total users: {metadata['total_users']:,}")
   print(f"Date range: {metadata['date_range']}")
   print(f"Load time: {metadata['load_time_ms']} ms")

**Analyzing data:**

.. code-block:: python

   import polars as pl

   # Filter recipes by year
   recipes_2018 = recipes.filter(pl.col('year') == 2018)

   # Quick recipes (< 30 min)
   quick_recipes = recipes.filter(pl.col('minutes') < 30)

   # Recipes by season
   winter_recipes = recipes.filter(pl.col('season') == 'Winter')

   # Top rated recipes
   top_ratings = ratings.filter(pl.col('rating') == 5)

**Joining recipes and ratings:**

.. code-block:: python

   # Join for combined analysis
   recipes_with_ratings = recipes.join(
       ratings,
       left_on='id',
       right_on='recipe_id',
       how='inner'
   )

   # Calculate average rating per recipe
   avg_ratings = recipes_with_ratings.group_by('id').agg([
       pl.col('rating').mean().alias('avg_rating'),
       pl.col('rating').count().alias('num_ratings')
   ])

**Cache management:**

.. code-block:: python

   import streamlit as st

   # Force programmatic reload
   st.cache_data.clear()

   # Reload fresh data
   recipes = get_recipes_clean()

   # Display cache info
   st.info(f"Cache TTL: 1 hour. Last update: {datetime.now()}")

Performance
^^^^^^^^^^^

* First load: 5-10 seconds (from S3 Parquet)
* Subsequent loads: <0.1 second (Streamlit memory cache)
* Gain: 50-100x on repeated navigations

To force reload:

1. Streamlit menu → "Clear cache"
2. Reload page

Memory Optimization
^^^^^^^^^^^^^^^^^^^^

Data is loaded in **Polars** (columnar format) for:

* Reduced memory footprint vs Pandas
* 5-10x faster filter/aggregation performance
* Lazy evaluation for complex transformations

Pandas conversion if needed:

.. code-block:: python

   recipes_pd = recipes.to_pandas()  # Polars → Pandas

Troubleshooting
^^^^^^^^^^^^^^^

**Error: "No S3 credentials"**

Solution: Verify ``96_keys/credentials`` file exists with valid INI format.

**See**: :doc:`/s3` for complete S3 configuration.

**Error: "Cache data too large"**

If the app consumes too much memory:

1. Reduce cache TTL in code: ``@st.cache_data(ttl=1800)`` (30 min)
2. Filter data before caching
3. Increase server RAM (current: 32 GB dataia)

**Slow loading (> 30 seconds)**

Possible causes:

1. Slow S3 connection → Check DNAT bypass (:doc:`/s3`)
2. First load normal (cache creation)
3. Expired cache → Reloaded every hour

**Missing columns in DataFrame**

Some columns are calculated:

* ``season``: Derived from ``submitted`` (month → season)
* ``day_of_week``: Derived from ``submitted`` (0-6)
* ``complexity_score``: Calculated from ``n_steps``, ``n_ingredients``

If missing: verify S3 Parquet version is up to date.

Data Source
^^^^^^^^^^^^^^^^^^

* **Original dataset**: Food.com (Kaggle)
* **Period**: 1999-2018 (20 years)
* **Preprocessing**: Cleaning, enrichment, feature engineering
* **Format**: Snappy-compressed Parquet
* **Storage**: S3 Garage (s3fast.lafrance.io)
* **Total**: ~450 MB compressed, ~2.5 GB uncompressed

**See**: EDA project documentation (``00_eda/``) for preprocessing details.
