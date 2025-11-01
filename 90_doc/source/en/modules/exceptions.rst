Module exceptions
=================

Custom exception hierarchy for robust error handling.

Architecture
------------

Base exception **MangetamainError** with 5 specialized exceptions:

* DataLoadError: S3/DuckDB loading errors
* AnalysisError: Statistical calculation errors
* ConfigurationError: Configuration errors
* DatabaseError: DuckDB operation errors
* ValidationError: Data validation errors

DataLoadError Class
-------------------

Main exception for data loading.

.. code-block:: python

   class DataLoadError(MangetamainError):
       def __init__(self, source: str, detail: str):
           self.source = source
           self.detail = detail
           self.message = f"Loading failed from {source}: {detail}"

**Attributes**:

* source: Error origin (S3, DuckDB, file)
* detail: Detailed description

**Example**:

.. code-block:: python

   from mangetamain_analytics.exceptions import DataLoadError
   from mangetamain_analytics.data.loaders import DataLoader

   loader = DataLoader()
   try:
       recipes = loader.load_recipes()
   except DataLoadError as e:
       print(f"Source: {e.source}")
       print(f"Detail: {e.detail}")

Other Exceptions
----------------

**AnalysisError**

Raised when statistical calculation fails.

**ConfigurationError**

Raised when configuration is invalid.

**DatabaseError**

Raised when DuckDB query error occurs.

**ValidationError**

Raised when data is invalid.

All inherit from **MangetamainError**, allowing global capture:

.. code-block:: python

   from mangetamain_analytics.exceptions import MangetamainError

   try:
       # Various operations
       pass
   except MangetamainError as e:
       # Catch all project exceptions
       logger.error(f"Application error: {e}")

Tests
-----

100% coverage of the exceptions module.

* test_exceptions.py: 25 tests (hierarchy, attributes, messages)
* test_loaders.py: 10 tests (DataLoader integration)
