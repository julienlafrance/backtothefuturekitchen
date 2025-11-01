Mangetamain Analytics Documentation
====================================

Web application for culinary data analysis based on the Food.com dataset (2.3M interactions, 1999-2018).

Deployed Environments
-----------------------

* PREPROD: https://mangetamain.lafrance.io/
* PRODUCTION: https://backtothefuturekitchen.lafrance.io/

Dataset
-------

* 178,265 recipes
* 1.1M+ user ratings
* 25,076 contributors
* Period 1999-2018

Project Metrics
----------------

* Tests: 118 tests, 93% coverage
* Documentation: Auto-generated Sphinx, Google-style docstrings
* CI/CD: Automated GitHub Actions pipeline
* Type hinting: Complete on all functions

Navigation
----------

.. toctree::
   :maxdepth: 2
   :caption: The Project

   projet
   quickstart
   installation

.. toctree::
   :maxdepth: 2
   :caption: Streamlit Application

   application
   usage

.. toctree::
   :maxdepth: 2
   :caption: Code Documentation

   modules/index
   modules/utils
   modules/visualization
   modules/data
   modules/exceptions
   modules/infrastructure

.. toctree::
   :maxdepth: 2
   :caption: Infrastructure

   architecture
   s3
   cicd
   tests

.. toctree::
   :maxdepth: 2
   :caption: Quality Standards

   conformite

.. toctree::
   :maxdepth: 2
   :caption: Reference

   faq
   glossaire

Indices
=======

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
