The Project
=========

Overview
--------------

Culinary data analysis with complete workflow: exploration → development → visualization → deployment.

Development Process
---------------------------

**1. Data Exploration (00_eda/)**

* Jupyter notebooks for exploratory analysis
* 9 notebooks organized by theme (trends, seasonality, weekend, ratings)
* Pattern and insight identification

**2. Application Development (10_preprod/)**

* Transform notebook analyses → reusable Python modules
* Streamlit application for interactive result presentation
* Modular architecture (utils, visualization, data, exceptions)

**3. Deployment (20_prod/)**

* Automated CI/CD pipeline
* Separate preprod/prod environments
* Continuous testing and validation

EDA → Application Mapping
---------------------------------

Each Streamlit analysis is based on one or more EDA notebooks:

* **Trend analysis** ← 01_long_term/recipe_analysis_trendline.ipynb
* **Seasonality analysis** ← 02_seasonality/recipe_analysis_seasonality.ipynb
* **Weekend analysis** ← 03_week_end_effect/recipe_analysis_weekend.ipynb
* **Ratings analysis** ← 01_long_term/rating_analysis.ipynb

The notebooks contain complete exploration (descriptive statistics, visualizations, hypothesis testing). The Streamlit application presents results interactively.

Technical Stack
---------------

* Python 3.13.7
* Streamlit 1.50.0 (web interface)
* DuckDB 1.4.0 (OLAP database)
* Polars 1.19.0 (data processing)
* Plotly 5.24.1 (visualizations)

Environments
--------------

* **PREPROD**: https://mangetamain.lafrance.io/ (port 8500)
* **PRODUCTION**: https://backtothefuturekitchen.lafrance.io/ (port 8501)

Applied Standards
-------------------

* Complete type hinting
* Pytest unit tests (93% coverage)
* Google-style docstring documentation
* Automatic PEP8 validation
* Custom exception handling
* CI/CD pipeline with GitHub Actions
