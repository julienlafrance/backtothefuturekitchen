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

* ``get_recipes_clean()`` : Charge les recettes depuis S3 Parquet
* ``get_ratings_longterm()`` : Charge les ratings pour analyse long-terme

Schéma des Données
^^^^^^^^^^^^^^^^^^

**get_recipes_clean() retourne**:

* ``id`` : Identifiant unique recette (int)
* ``name`` : Nom de la recette (str)
* ``minutes`` : Temps de préparation en minutes (int)
* ``submitted`` : Date soumission (date)
* ``year`` : Année soumission (int)
* ``n_ingredients`` : Nombre d'ingrédients (int)
* ``complexity_score`` : Score complexité 0-10 (float)
* ``calories``, ``protein``, ``fat``, ``sodium`` : Infos nutritionnelles (float)
* ``tags`` : Liste tags recette (list[str])
* ``day_of_week`` : Jour semaine (0=Lundi, 6=Dimanche)
* ``season`` : Saison (Automne, Hiver, Printemps, Été)

**Taille**: 178,265 recettes, ~250 MB Parquet compressé

**get_ratings_longterm() retourne**:

* ``user_id`` : Identifiant utilisateur (int)
* ``recipe_id`` : Identifiant recette (int)
* ``date`` : Date du rating (date)
* ``rating`` : Note 0-5 étoiles (int)
* ``review`` : Texte commentaire optionnel (str)

**Taille**: 1.1M+ ratings, ~180 MB Parquet compressé

Options Avancées
^^^^^^^^^^^^^^^^

**get_ratings_longterm() accepte**:

* ``min_interactions`` (int, défaut 100) : Filtrer recettes avec minimum interactions
* ``return_metadata`` (bool, défaut False) : Retourner tuple (data, metadata)
* ``verbose`` (bool, défaut False) : Afficher logs détaillés chargement

Metadata contient:

* ``total_ratings`` : Nombre total ratings
* ``total_users`` : Nombre utilisateurs uniques
* ``total_recipes`` : Nombre recettes notées
* ``date_range`` : Plage temporelle (min, max)
* ``load_time_ms`` : Temps chargement en millisecondes

Mécanisme de Cache
^^^^^^^^^^^^^^^^^^

Les fonctions utilisent le décorateur ``@st.cache_data`` avec :

* **TTL** : 3600 secondes (1 heure)
* **Spinner** : Message de chargement visible
* **Lazy imports** : Compatibilité tests locaux

Exemples d'Utilisation
^^^^^^^^^^^^^^^^^^^^^^^

**Chargement basique :**

.. code-block:: python

   from data.cached_loaders import get_recipes_clean, get_ratings_longterm

   # Chargé une seule fois par heure depuis S3
   recipes = get_recipes_clean()  # DataFrame 178K recettes
   ratings = get_ratings_longterm()  # DataFrame 1.1M+ ratings

   print(f"Loaded {len(recipes)} recipes, {len(ratings)} ratings")

**Avec options avancées :**

.. code-block:: python

   # Filtrer recettes populaires + metadata
   ratings, metadata = get_ratings_longterm(
       min_interactions=100,  # Minimum 100 ratings
       return_metadata=True,
       verbose=True
   )

   print(f"Total users: {metadata['total_users']:,}")
   print(f"Date range: {metadata['date_range']}")
   print(f"Load time: {metadata['load_time_ms']} ms")

**Analyser les données :**

.. code-block:: python

   import polars as pl

   # Filtrer recettes par année
   recipes_2018 = recipes.filter(pl.col('year') == 2018)

   # Recettes rapides (< 30 min)
   quick_recipes = recipes.filter(pl.col('minutes') < 30)

   # Recettes par saison
   winter_recipes = recipes.filter(pl.col('season') == 'Hiver')

   # Top recettes notées
   top_ratings = ratings.filter(pl.col('rating') == 5)

**Joindre recettes et ratings :**

.. code-block:: python

   # Join pour analyse combinée
   recipes_with_ratings = recipes.join(
       ratings,
       left_on='id',
       right_on='recipe_id',
       how='inner'
   )

   # Calculer moyenne rating par recette
   avg_ratings = recipes_with_ratings.group_by('id').agg([
       pl.col('rating').mean().alias('avg_rating'),
       pl.col('rating').count().alias('num_ratings')
   ])

**Gestion du cache :**

.. code-block:: python

   import streamlit as st

   # Forcer rechargement programmatique
   st.cache_data.clear()

   # Recharger données fraîches
   recipes = get_recipes_clean()

   # Afficher info cache
   st.info(f"Cache TTL: 1 heure. Dernière maj: {datetime.now()}")

Performance
^^^^^^^^^^^

* Premier chargement : 5-10 secondes (depuis S3 Parquet)
* Chargements suivants : <0.1 seconde (cache mémoire Streamlit)
* Gain : 50-100x sur navigations répétées

Pour forcer le rechargement :

1. Menu Streamlit → "Clear cache"
2. Recharger la page

Optimisation Mémoire
^^^^^^^^^^^^^^^^^^^^

Les données sont chargées en **Polars** (format columnar) pour:

* Empreinte mémoire réduite vs Pandas
* Performance filtres/agrégations 5-10x plus rapide
* Lazy evaluation pour transformations complexes

Conversion Pandas si nécessaire:

.. code-block:: python

   recipes_pd = recipes.to_pandas()  # Polars → Pandas

Troubleshooting
^^^^^^^^^^^^^^^

**Erreur: "No S3 credentials"**

Solution: Vérifier fichier ``96_keys/credentials`` existe avec format INI valide.

**Voir**: :doc:`/s3` pour configuration S3 complète.

**Erreur: "Cache data too large"**

Si l'app consomme trop de mémoire:

1. Réduire TTL cache dans code: ``@st.cache_data(ttl=1800)`` (30 min)
2. Filtrer données avant mise en cache
3. Augmenter RAM serveur (actuel: 32 GB dataia)

**Chargement lent (> 30 secondes)**

Causes possibles:

1. Connexion S3 lente → Vérifier DNAT bypass (:doc:`/s3`)
2. Premier chargement normal (création cache)
3. Cache expiré → Rechargé toutes les heures

**Colonnes manquantes dans DataFrame**

Certaines colonnes sont calculées:

* ``season`` : Dérivé de ``submitted`` (mois → saison)
* ``day_of_week`` : Dérivé de ``submitted`` (0-6)
* ``complexity_score`` : Calculé depuis ``n_steps``, ``n_ingredients``

Si absentes: vérifier version Parquet S3 est à jour.

Source des Données
^^^^^^^^^^^^^^^^^^

* **Dataset original**: Food.com (Kaggle)
* **Période**: 1999-2018 (20 ans)
* **Preprocessing**: Nettoyage, enrichissement, feature engineering
* **Format**: Parquet compressé Snappy
* **Stockage**: S3 Garage (s3fast.lafrance.io)
* **Total**: ~450 MB compressé, ~2.5 GB décompressé

**Voir**: Documentation projet EDA (``00_eda/``) pour détails preprocessing.
