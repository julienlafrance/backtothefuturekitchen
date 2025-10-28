Documentation Code
==================

Documentation des modules Python de l'application Streamlit, générée depuis les docstrings (format Google).

Organisation
------------

* **utils** : Fonctions utilitaires (couleurs, thème graphique)
* **visualization** : Modules d'analyse et génération graphiques
* **data** : Chargement et mise en cache données
* **exceptions** : Hiérarchie exceptions personnalisées
* **infrastructure** : Logging, base de données

Modules Disponibles
-------------------

.. toctree::
   :maxdepth: 2

   utils
   visualization
   data
   exceptions
   infrastructure

Conventions
-----------

Tous les modules respectent :

* Docstrings Google style
* Type hints Python 3.13+
* PEP8 compliance
* Coverage >= 90%
