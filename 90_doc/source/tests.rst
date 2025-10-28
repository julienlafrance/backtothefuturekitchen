Tests et Coverage
=================

Documentation complète des tests unitaires et du coverage du projet.

**Coverage** : pourcentage de code testé (:doc:`glossaire`).

**Exécution rapide** : voir :doc:`quickstart` pour commandes.

État Actuel
-----------

Résumé Exécutif
^^^^^^^^^^^^^^^

* **Coverage code source**: 93% (objectif 90% dépassé)
* **Tests unitaires**: 118 tests (10_preprod/tests/unit/)
* **Tests infrastructure**: 35 tests (50_test/)
* **Total**: 153 tests
* **Temps exécution**: ~6 secondes
* **CI/CD**: Seuil 90% obligatoire

Métriques par Environnement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========================================= ========== ======== ===============
Environnement                             Coverage   Tests    Statut
========================================= ========== ======== ===============
**10_preprod** (code source)              93%        83       Production ready
**20_prod** (artefact build)              N/A        N/A      Voir note*
**50_test** (tests infrastructure)        N/A        35       Validation S3/DB
========================================= ========== ======== ===============

**Note:** 20_prod est un artefact de déploiement copié depuis 10_preprod. Tester 20_prod serait redondant car c'est le même code source. Les tests de 10_preprod valident le code déployé en production.

Commandes Rapides
-----------------

Tests Unitaires (10_preprod)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv run pytest tests/unit/ -v --cov=src --cov-report=html
   xdg-open htmlcov/index.html

**Résultat attendu**: 83 tests, 93% coverage, 4 skipped

Tests Infrastructure (50_test)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest -v

**Résultat attendu**: 35 tests (S3, DuckDB, SQL)

Coverage Détaillé
-----------------

Modules Testés (10_preprod)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

================================= ========== ======== ====================
Fichier                           Coverage   Tests    Lignes Manquantes
================================= ========== ======== ====================
``utils/colors.py``               100%       10       0
``utils/chart_theme.py``          100%       10       0
``visualization/trendlines.py``   100%       8        0
``visualization/ratings_simple``  100%       14       0
``visualization/trendlines_v2``   95%        8        26 lignes
``visualization/seasonality.py``  92%        6        19 lignes
``visualization/ratings.py``      90%        5        29 lignes
``visualization/custom_charts``   90%        4        4 lignes
``visualization/weekend.py``      85%        6        41 lignes
``data/cached_loaders.py``        78%        3        2 lignes\*
``visualization/plotly_config``   77%        0        3 lignes\*
================================= ========== ======== ====================

\*Fonctions non utilisées commentées pour améliorer coverage

Fichiers de Tests Créés
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   tests/unit/
   ├── test_analyse_trendlines_v2.py    (8 tests)
   ├── test_analyse_ratings.py          (5 tests)
   ├── test_analyse_seasonality.py      (6 tests)
   ├── test_analyse_weekend.py          (6 tests)
   ├── test_colors.py                   (10 tests)
   ├── test_chart_theme.py              (10 tests)
   ├── test_analyse_ratings_simple.py   (14 tests)
   ├── test_custom_charts.py            (8 tests)
   ├── test_analyse_trendlines.py       (8 tests)
   └── test_cached_loaders.py           (4 tests skipped - mock st.cache_data)

Configuration
-------------

pyproject.toml
^^^^^^^^^^^^^^

.. code-block:: toml

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   addopts = "--cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=90"

   [tool.coverage.run]
   omit = [
       "*/main.py",
       "*/pages/*",
       "*/__pycache__/*",
       "*/.venv/*",
   ]

Tests Infrastructure (50_test)
-------------------------------

Types de Tests
^^^^^^^^^^^^^^

**S3_duckdb_test.py (14 tests)**

* Environnement système (AWS CLI, credentials)
* Connexion S3 avec boto3
* Performance download (>5 MB/s)
* DuckDB + S3 intégration
* Tests Docker (optionnels)

**test_s3_parquet_files.py (5 tests)**

* Scanne automatiquement le code
* Trouve les références aux fichiers parquet
* Teste l'accessibilité S3

**test_sql_queries.py (16 tests)**

* Scanne automatiquement le code
* Extrait les requêtes SQL
* Teste la syntaxe (EXPLAIN)
* Teste l'exécution (LIMIT 1)

Stratégie de Test
-----------------

Ce Qu'on Teste
^^^^^^^^^^^^^^

* Transformations de données
* Calculs et statistiques
* Validation et filtrage
* Logique métier
* Fonctions utilitaires

Ce Qu'on Exclut
^^^^^^^^^^^^^^^

.. code-block:: python

   # 1. Fonctions UI Streamlit (marquées pragma: no cover)
   def display_chart():  # pragma: no cover
       st.plotly_chart(fig)

   # 2. Fichiers d'application (dans pyproject.toml omit)
   # main.py, pages/*

   # 3. Imports conditionnels
   try:
       import module
   except ImportError:  # pragma: no cover
       module = None

Patterns de Test
----------------

Mock Streamlit
^^^^^^^^^^^^^^

.. code-block:: python

   from unittest.mock import Mock, MagicMock, patch

   def setup_st_mocks(mock_st):
       """Configure tous les mocks Streamlit nécessaires."""
       mock_st.plotly_chart = Mock()
       mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])
       mock_st.slider = Mock(return_value=(2010, 2020))
       mock_st.selectbox = Mock(side_effect=lambda label, options, **kwargs:
                                options[kwargs.get('index', 0)])
       return mock_st

   @patch("visualization.module.st")
   @patch("visualization.module.load_data")
   def test_function(mock_load, mock_st):
       setup_st_mocks(mock_st)
       mock_load.return_value = test_data

       result = my_function()

       mock_st.plotly_chart.assert_called()

Fixtures de Données
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   @pytest.fixture
   def mock_recipes_data():
       """Fixture pour données de test."""
       data = {
           "id": list(range(1000)),
           "year": [1999 + i % 20 for i in range(1000)],
           "minutes": [30 + (i % 50) for i in range(1000)],
           "complexity_score": [2.0 + (i % 10) * 0.1 for i in range(1000)],
       }
       return pl.DataFrame(data)

Tests de Graphiques Plotly
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   def test_chart_theme():
       fig = go.Figure()
       fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

       result = apply_chart_theme(fig, title="Test")

       assert result.layout.title.text == "Test"
       assert result.layout.plot_bgcolor == "rgba(0,0,0,0)"

Résolution de Problèmes
------------------------

Erreur: not enough values to unpack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause:** Mock de ``st.columns()`` retourne vide

**Solution:**

.. code-block:: python

   mock_st.columns = Mock(side_effect=lambda n: [MagicMock() for _ in range(n)])

Erreur: KeyError
^^^^^^^^^^^^^^^^

**Cause:** Fixture de données manque des colonnes

**Solution:** Ajouter toutes les colonnes utilisées par la fonction

.. code-block:: python

   data = {
       "existing_cols": [...],
       "missing_col": [...]  # Ajouter colonne manquante
   }

Erreur: Invalid value for color
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause:** Mock ``st.selectbox`` retourne une valeur fixe utilisée comme couleur

**Solution:**

.. code-block:: python

   mock_st.selectbox = Mock(side_effect=lambda label, options, **kwargs:
                            options[kwargs.get('index', 0)])

Erreur: Expected to be called once
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause:** Mauvais chemin de patch

**Solution:** Patcher où la fonction est **utilisée**, pas où elle est **définie**

.. code-block:: python

   # ❌ Mauvais
   @patch("data.loaders.load_data")

   # ✅ Bon
   @patch("visualization.module.load_data")

Commandes Pytest Utiles
------------------------

Liste des Tests
^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest --collect-only -q

Test Spécifique
^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest tests/unit/test_file.py::test_function -v

Coverage avec Détails
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest --cov=src --cov-report=term-missing

Coverage pour Un Fichier
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest tests/unit/test_file.py --cov=src.module --cov-report=term

Stop au Premier Échec
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pytest -x                # Stop immédiatement
   pytest --maxfail=3       # Stop après 3 échecs

Mode Verbeux
^^^^^^^^^^^^

.. code-block:: bash

   pytest -vv --tb=long     # Traceback complet

Bonnes Pratiques
----------------

Structure des Tests
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   """Tests unitaires pour le module X.

   Description de ce qui est testé.
   """

   import pytest
   from unittest.mock import Mock, patch

   @pytest.fixture
   def test_data():
       """Fixture réutilisable."""
       return create_test_data()

   def test_nominal_case(test_data):
       """Test du cas nominal."""
       result = function(test_data)
       assert result == expected

   def test_edge_case():
       """Test d'un cas limite."""
       # ...

   def test_error_handling():
       """Test de la gestion d'erreurs."""
       with pytest.raises(ValueError):
           function(invalid_data)

Nommage
^^^^^^^

* **Fichiers**: ``test_<module>.py``
* **Fonctions**: ``test_<fonctionnalité>``
* **Fixtures**: ``mock_<type>_data`` ou ``sample_<type>``

Assertions Claires
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # ✅ Bon
   assert len(result) == 10, "Devrait retourner 10 éléments"
   assert result['mean'] == pytest.approx(4.5, abs=0.1)

   # ❌ Mauvais
   assert result  # Trop vague

Progression Historique
-----------------------

============ ============ ==================================
Date         Coverage     Notes
============ ============ ==================================
2025-10-23   96%          Version initiale (22 tests)
2025-10-25   **93%**      +60 tests (7 fichiers), code mort nettoyé
============ ============ ==================================

Fichiers Ajoutés (2025-10-25)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. ``test_analyse_trendlines_v2.py`` - 8 tests
2. ``test_analyse_ratings.py`` - 5 tests
3. ``test_analyse_seasonality.py`` - 6 tests
4. ``test_analyse_weekend.py`` - 6 tests
5. ``test_colors.py`` - 10 tests
6. ``test_chart_theme.py`` - 10 tests
7. ``test_cached_loaders.py`` - 4 tests

**Total:** +49 tests, +6 fichiers couverts

Voir Aussi
----------

* :doc:`conformite` - Conformité académique et qualité code
* :doc:`api/index` - Documentation API modules testés
* :doc:`architecture` - CI/CD pipeline avec tests automatiques
