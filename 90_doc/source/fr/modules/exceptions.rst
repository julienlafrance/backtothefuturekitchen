Module exceptions
=================

Hiérarchie d'exceptions personnalisées pour gestion robuste des erreurs.

Architecture
------------

Exception de base **MangetamainError** avec 5 exceptions spécialisées :

* DataLoadError : Erreurs chargement S3/DuckDB
* AnalysisError : Erreurs calculs statistiques
* ConfigurationError : Erreurs configuration
* DatabaseError : Erreurs opérations DuckDB
* ValidationError : Erreurs validation données

Classe DataLoadError
--------------------

Exception principale pour chargement données.

.. code-block:: python

   class DataLoadError(MangetamainError):
       def __init__(self, source: str, detail: str):
           self.source = source
           self.detail = detail
           self.message = f"Échec chargement depuis {source}: {detail}"

**Attributs** :

* source : Origine erreur (S3, DuckDB, fichier)
* detail : Description détaillée

**Exemple** :

.. code-block:: python

   from mangetamain_analytics.exceptions import DataLoadError
   from mangetamain_analytics.data.loaders import DataLoader

   loader = DataLoader()
   try:
       recipes = loader.load_recipes()
   except DataLoadError as e:
       print(f"Source: {e.source}")
       print(f"Détail: {e.detail}")

Autres Exceptions
-----------------

**AnalysisError**

Levée lors d'échec calcul statistique.

**ConfigurationError**

Levée si configuration invalide.

**DatabaseError**

Levée lors d'erreur requête DuckDB.

**ValidationError**

Levée si données invalides.

Toutes héritent de **MangetamainError**, permettant capture globale :

.. code-block:: python

   from mangetamain_analytics.exceptions import MangetamainError

   try:
       # Opérations diverses
       pass
   except MangetamainError as e:
       # Capture toutes les exceptions du projet
       logger.error(f"Erreur application: {e}")

Tests
-----

Couverture 100% du module exceptions.

* test_exceptions.py : 25 tests (hiérarchie, attributs, messages)
* test_loaders.py : 10 tests (intégration DataLoader)
