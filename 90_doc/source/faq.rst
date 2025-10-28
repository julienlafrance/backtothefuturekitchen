FAQ - Questions Fréquentes
==========================

22 questions courantes organisées en 7 catégories.

**Démarrage rapide** : voir :doc:`quickstart` | **Définitions** : voir :doc:`glossaire`

Installation et Configuration
------------------------------

Comment installer Python 3.13 ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Option 1 - Via uv (recommandé) :**

.. code-block:: bash

   uv python install 3.13

**Option 2 - Depuis python.org :**

Télécharger depuis https://www.python.org/downloads/ et installer manuellement.

**Vérification :**

.. code-block:: bash

   python3 --version
   # Attendu: Python 3.13.3

Pourquoi uv et pas pip ?
^^^^^^^^^^^^^^^^^^^^^^^^^

**uv** est un gestionnaire de paquets moderne Python :

* **10-100x plus rapide** que pip
* Gestion automatique environnements virtuels
* Lock file pour reproductibilité
* Installation Python intégrée
* Compatible pyproject.toml

**Migration pip → uv** :

.. code-block:: bash

   # Ancien
   pip install -r requirements.txt

   # Nouveau
   uv sync

Comment configurer S3 ?
^^^^^^^^^^^^^^^^^^^^^^^^

1. Créer le fichier credentials :

.. code-block:: bash

   mkdir -p 96_keys
   cat > 96_keys/credentials << EOF
   [s3fast]
   aws_access_key_id = VOTRE_CLE
   aws_secret_access_key = VOTRE_SECRET
   EOF
   chmod 600 96_keys/credentials

2. Tester la connexion :

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest test_s3_parquet_files.py -v

**Voir** : :doc:`s3` pour configuration complète.

Données et Performance
----------------------

Combien de données sont chargées ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Recettes** : 178,265 recettes (~250 MB Parquet)
* **Ratings** : 1.1M+ interactions (~180 MB Parquet)
* **Total** : ~450 MB compressé, ~2.5 GB en mémoire

**Première charge** : 5-10 secondes (depuis S3)
**Charges suivantes** : <0.1 seconde (cache Streamlit)

Comment améliorer la performance S3 ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**DNAT Bypass** : Gain 10x performance (50 → 500-917 MB/s)

.. code-block:: bash

   sudo iptables -t nat -A OUTPUT -p tcp -d 192.168.80.202 --dport 80 \\
        -j DNAT --to-destination 192.168.80.202:3910

**Vérifier performance** :

.. code-block:: bash

   time aws s3 cp s3://mangetamain/recipes_clean.parquet /tmp/ --profile s3fast

**Voir** : :doc:`s3` section "DNAT Bypass Performance".

Pourquoi Polars et pas Pandas ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Polars** offre :

* **5-10x plus rapide** pour agrégations
* **Empreinte mémoire réduite** (format columnar)
* Lazy evaluation pour transformations complexes
* Syntaxe expressive et type-safe

**Conversion si nécessaire** :

.. code-block:: python

   recipes_pd = recipes.to_pandas()  # Polars → Pandas

Le cache Streamlit expire quand ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**TTL** : 3600 secondes (1 heure)

**Forcer rechargement** :

1. Menu Streamlit (⋮) → "Clear cache"
2. Recharger la page
3. Ou programmatiquement : ``st.cache_data.clear()``

Développement
-------------

Comment ajouter une nouvelle analyse ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Créer le module** : ``src/mangetamain_analytics/visualization/analyse_nouvelle.py``

.. code-block:: python

   from data.cached_loaders import get_recipes_clean
   import streamlit as st
   import plotly.graph_objects as go
   from utils import chart_theme

   def render_nouvelle_analysis():
       """Render nouvelle analyse."""
       st.header("Nouvelle Analyse")

       # Charger données
       recipes = get_recipes_clean()

       # Créer visualisation
       fig = go.Figure()
       fig.add_trace(go.Bar(x=..., y=...))

       # Appliquer thème
       chart_theme.apply_chart_theme(fig, title="Mon Graphique")

       # Afficher
       st.plotly_chart(fig, use_container_width=True)

2. **Ajouter au menu** : Modifier ``src/mangetamain_analytics/main.py``

.. code-block:: python

   from visualization import analyse_nouvelle

   # Dans la sidebar
   analysis = st.sidebar.selectbox(
       "Choisir analyse",
       ["Tendances", "Saisonnalité", "Weekend", "Ratings", "Nouvelle"]
   )

   if analysis == "Nouvelle":
       analyse_nouvelle.render_nouvelle_analysis()

3. **Tester localement** :

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py

4. **Ajouter tests** : ``tests/unit/test_analyse_nouvelle.py``

Comment personnaliser les couleurs ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Modifier** : ``src/mangetamain_analytics/utils/colors.py``

.. code-block:: python

   # Changer couleur primaire
   ORANGE_PRIMARY = "#FF8C00"  # Modifier HEX ici

   # Ajouter nouvelle couleur
   MA_COULEUR_PERSO = "#123456"

**Utiliser** :

.. code-block:: python

   from utils import colors

   fig.add_trace(go.Bar(
       x=data['x'],
       y=data['y'],
       marker_color=colors.MA_COULEUR_PERSO
   ))

Comment debugger un graphique Plotly ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**1. Afficher structure figure :**

.. code-block:: python

   print(fig)  # Affiche structure complète

**2. Vérifier données traces :**

.. code-block:: python

   for trace in fig.data:
       print(f"Type: {trace.type}")
       print(f"X: {trace.x}")
       print(f"Y: {trace.y}")

**3. Logs Streamlit :**

.. code-block:: python

   st.write("Debug:", data.head())  # Afficher échantillon données

**4. Export JSON :**

.. code-block:: python

   import json
   fig_json = fig.to_json()
   st.download_button("Télécharger JSON", fig_json, "figure.json")

Tests et CI/CD
--------------

Comment lancer les tests ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Tests unitaires (10_preprod) :**

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv run pytest tests/unit/ -v --cov=src

**Tests infrastructure (50_test) :**

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest -v

**Test spécifique :**

.. code-block:: bash

   uv run pytest tests/unit/test_colors.py::test_get_rgba -v

Comment augmenter le coverage ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**1. Identifier lignes manquantes :**

.. code-block:: bash

   uv run pytest --cov=src --cov-report=html
   xdg-open htmlcov/index.html

**2. Ajouter tests pour lignes rouges**

**3. Marquer code non testable :**

.. code-block:: python

   def display_ui():  # pragma: no cover
       """Fonction Streamlit UI non testable."""
       st.plotly_chart(fig)

**Voir** : :doc:`tests` pour patterns de test complets.

Le CI échoue, comment débugger ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**1. Vérifier localement d'abord :**

.. code-block:: bash

   # PEP8
   uv run flake8 src/ tests/

   # Tests
   uv run pytest tests/unit/ --cov=src --cov-fail-under=90

   # Formatage
   uv run black --check src/ tests/

**2. Voir logs CI GitHub :**

.. code-block:: bash

   gh run list --limit 5
   gh run view <run-id>

**3. Re-run CI :**

Depuis GitHub UI → Actions → Re-run failed jobs

**Voir** : :doc:`cicd` pour troubleshooting CI/CD complet.

Docker
------

Le conteneur Docker ne démarre pas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Diagnostics :**

.. code-block:: bash

   # Vérifier logs
   docker-compose logs mangetamain_preprod

   # Vérifier santé
   docker-compose ps

   # Vérifier images
   docker images | grep mangetamain

**Solutions courantes :**

1. **Port occupé** :

.. code-block:: bash

   lsof -i :8500  # Identifier processus
   # Modifier port dans docker-compose.yml

2. **Volumes manquants** :

.. code-block:: bash

   # Vérifier paths existent
   ls -la ~/mangetamain/10_preprod/src
   ls -la ~/mangetamain/10_preprod/data

3. **Rebuild image** :

.. code-block:: bash

   docker-compose down
   docker-compose up -d --build

Comment voir les modifications en temps réel ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Le volume Docker est mappé en lecture seule pour le code source :

1. **Modifier** : Éditer fichiers dans ``10_preprod/src/``
2. **Streamlit détecte** : Bouton "Rerun" apparaît automatiquement
3. **Cliquer** : Rerun pour voir changements

**Aucun redémarrage conteneur nécessaire!**

Déploiement
-----------

Comment déployer en PREPROD ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Automatique** : Push vers ``main`` déclenche déploiement auto

.. code-block:: bash

   git add .
   git commit -m "Mon changement"
   git push origin main

**CI/CD s'occupe de** :

1. Tests (PEP8, pytest, coverage ≥90%)
2. Déploiement PREPROD si tests OK
3. Notification Discord

**Vérifier déploiement** :

* URL : https://mangetamain.lafrance.io/
* Badge PREPROD visible dans app

Comment déployer en PRODUCTION ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Manuel avec confirmation** :

1. **Aller sur GitHub Actions** → CD Production
2. **Cliquer** : "Run workflow"
3. **Taper** : "DEPLOY" (exactement)
4. **Confirmer** : Run workflow

**Backup automatique** effectué avant déploiement

**Vérifier** : https://backtothefuturekitchen.lafrance.io/

**Voir** : :doc:`cicd` pour détails complets CD.

Comment rollback en cas d'erreur ?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Sur la VM dataia :**

.. code-block:: bash

   ssh dataia
   cd ~/mangetamain/20_prod

   # Voir backups disponibles
   ls backups/

   # Restaurer backup
   git reset --hard <commit-sha-stable>

   # Redémarrer
   cd ../30_docker
   docker-compose -f docker-compose-prod.yml restart

**Notifications Discord** contiennent SHA du commit à restaurer.

Erreurs Courantes
-----------------

"ImportError: No module named 'streamlit'"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause** : Environnement virtuel non activé ou dépendances manquantes

**Solution** :

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv sync  # Réinstaller dépendances
   uv run streamlit --version  # Vérifier

"DuckDB database is locked"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause** : Plusieurs processus accèdent simultanément à DuckDB

**Solution** :

.. code-block:: bash

   # Arrêter tous les processus Streamlit
   pkill -f streamlit

   # Ou redémarrer conteneur Docker
   docker-compose restart

"S3 connection timeout"
^^^^^^^^^^^^^^^^^^^^^^^

**Causes possibles** :

1. Credentials invalides → Vérifier ``96_keys/credentials``
2. Endpoint inaccessible → ``ping s3fast.lafrance.io``
3. Performance lente → Configurer DNAT bypass

**Solution DNAT** : :doc:`s3` section "DNAT Bypass"

"Coverage below 90%"
^^^^^^^^^^^^^^^^^^^^

**CI bloque si coverage < 90%**

**Solution** :

1. Identifier lignes manquantes :

.. code-block:: bash

   uv run pytest --cov=src --cov-report=term-missing

2. Ajouter tests pour lignes rouges
3. Ou marquer code non testable : ``# pragma: no cover``

**Voir** : :doc:`tests` pour patterns.

Ressources Supplémentaires
---------------------------

* :doc:`installation` - Guide installation complet
* :doc:`usage` - Utilisation de l'application
* :doc:`s3` - Configuration S3 Garage
* :doc:`architecture` - Stack technique détaillée
* :doc:`cicd` - Pipeline CI/CD
* :doc:`tests` - Tests et coverage
* :doc:`api/index` - Référence API complète

**Support** : Issues GitHub → https://github.com/julienlafrance/backtothefuturekitchen/issues
