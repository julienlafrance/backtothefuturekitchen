Module data
===========

Le module ``data`` gère le chargement et la mise en cache des données.

data.cached_loaders
-------------------

Fonctions de chargement des données avec cache Streamlit.

.. automodule:: mangetamain_analytics.data.cached_loaders
   :members:
   :undoc-members:
   :show-inheritance:

Fonctions Principales
^^^^^^^^^^^^^^^^^^^^^

* ``get_recipes_clean()`` : Charge les recettes depuis S3
* ``get_ratings_longterm()`` : Charge les ratings pour analyse long-terme

Mécanisme de Cache
^^^^^^^^^^^^^^^^^^

Les fonctions utilisent le décorateur ``@st.cache_data`` avec :

* **TTL** : 3600 secondes (1 heure)
* **Spinner** : Message de chargement visible
* **Lazy imports** : Compatibilité tests locaux

Exemple d'Utilisation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Chargé une seule fois par heure depuis S3
   recipes = get_recipes_clean()

   # Chargé avec options
   ratings, metadata = get_ratings_longterm(
       min_interactions=100,
       return_metadata=True,
       verbose=True
   )

Performance
^^^^^^^^^^^

* Premier chargement : 5-10 secondes (depuis S3 Parquet)
* Chargements suivants : <0.1 seconde (cache mémoire Streamlit)
* Gain : 50-100x sur navigations répétées

Pour forcer le rechargement :

1. Menu Streamlit → "Clear cache"
2. Recharger la page
