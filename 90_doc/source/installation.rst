Installation
============

**Guide rapide** : voir :doc:`quickstart` (installation en 2 minutes).

**Termes techniques** : voir :doc:`glossaire` pour uv, S3, Docker, etc.

Prérequis
---------

* Python 3.13.3
* uv (gestionnaire de paquets)
* Accès S3 (Garage Storage) - voir :doc:`s3`

Installation Locale
-------------------

1. Cloner le Repository
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git ~/mangetamain
   cd ~/mangetamain/10_preprod

2. Créer l'Environnement Virtuel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv sync

Cette commande installe automatiquement toutes les dépendances définies dans ``pyproject.toml``.

3. Configuration S3
^^^^^^^^^^^^^^^^^^^

Copier les credentials S3 dans ``96_keys/credentials`` :

.. code-block:: ini

   [s3fast]
   aws_access_key_id = YOUR_KEY
   aws_secret_access_key = YOUR_SECRET

Les données sont chargées automatiquement depuis S3 au démarrage de l'application.

4. Lancer l'Application
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py

L'application est accessible sur http://localhost:8501

Installation avec Docker
------------------------

1. Cloner le Repository
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git ~/mangetamain
   cd ~/mangetamain/30_docker

2. Lancer avec Docker Compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Environnement PREPROD (port 8500)
   docker-compose up -d

   # OU Environnement PRODUCTION (port 8501)
   docker-compose -f docker-compose-prod.yml up -d

Accès aux Environnements
^^^^^^^^^^^^^^^^^^^^^^^^^

* **Local PREPROD** : http://localhost:8500
* **Local PRODUCTION** : http://localhost:8501
* **Réseau PREPROD** : http://192.168.80.210:8500
* **Public PREPROD** : https://mangetamain.lafrance.io/
* **Public PRODUCTION** : https://backtothefuturekitchen.lafrance.io/

Volumes Docker
^^^^^^^^^^^^^^

Les volumes Docker mappent le code local vers le conteneur :

=================== =================== ====== ================================
Local               Container           Mode   Description
=================== =================== ====== ================================
``10_preprod/src/`` ``/app/src/``       RO     Code source (hot reload)
``10_preprod/data/`` ``/app/data/``     RW     Base DuckDB
``pyproject.toml``  ``/app/pyproject.``  RO     Configuration uv
=================== =================== ====== ================================

**Avantages** :

* Code source en lecture seule (évite modifications accidentelles)
* Modifications visibles immédiatement (hot reload Streamlit)
* Données DuckDB persistantes

Gestion Docker
^^^^^^^^^^^^^^

**Voir les logs :**

.. code-block:: bash

   docker-compose logs -f mangetamain_preprod

**Redémarrer après nouvelle dépendance :**

.. code-block:: bash

   # 1. Ajouter dépendance localement
   cd ~/mangetamain/10_preprod
   uv add nouvelle-dependance

   # 2. Redémarrer conteneur
   cd ~/mangetamain/30_docker
   docker-compose restart

**Arrêter les services :**

.. code-block:: bash

   docker-compose down

**Reconstruire complètement :**

.. code-block:: bash

   docker-compose up -d --force-recreate --build

Debug Docker
^^^^^^^^^^^^

**Entrer dans le conteneur :**

.. code-block:: bash

   docker-compose exec mangetamain_preprod bash
   # Puis dans le conteneur:
   uv run python -c "import streamlit; print(streamlit.__version__)"

**Vérifier santé du conteneur :**

.. code-block:: bash

   docker-compose ps
   # Doit afficher: healthy

**Logs en temps réel :**

.. code-block:: bash

   docker-compose logs -f --tail=100

Workflow Développement Docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Modifier code** : Éditer fichiers dans ``10_preprod/src/``
2. **Voir changements** : Streamlit recharge automatiquement
3. **Ajouter dépendance** : ``uv add package`` puis ``docker-compose restart``
4. **Debug** : ``docker-compose logs -f`` ou entrer dans conteneur

Nettoyage
^^^^^^^^^

**Arrêter et supprimer conteneur :**

.. code-block:: bash

   docker-compose down

**Nettoyage complet (images, volumes, réseaux) :**

.. code-block:: bash

   docker system prune -a
   # Attention: Supprime TOUTES les images Docker inutilisées

Tests
-----

Lancer les Tests Unitaires
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv run pytest tests/unit/ -v --cov=src

Résultat attendu : 93% coverage (118 tests)

Vérifier la Qualité du Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # PEP8
   uv run flake8 src/ tests/ --config=../.flake8

   # Formatage
   uv run black --check src/ tests/

   # Docstrings
   uv run pydocstyle src/ --config=../.pydocstyle

Dépendances Principales
-----------------------

* streamlit >= 1.50.0
* plotly >= 5.24.1
* pandas >= 2.2.3
* numpy >= 2.2.6
* duckdb >= 1.4.0
* polars >= 1.19.0
* loguru >= 0.7.3
* pytest >= 8.5.0 (dev)
* pytest-cov >= 6.0.0 (dev)

La liste complète est disponible dans ``10_preprod/pyproject.toml``.

Vérification de l'Installation
-------------------------------

Vérifier uv
^^^^^^^^^^^

.. code-block:: bash

   uv --version
   # Attendu: uv 0.8.22 ou supérieur

Si ``uv`` n'est pas installé :

.. code-block:: bash

   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

Vérifier Python
^^^^^^^^^^^^^^^

.. code-block:: bash

   python3 --version
   # Attendu: Python 3.13.3

Le projet nécessite Python 3.13+ pour compatibility avec toutes les dépendances.

Vérifier l'Environnement
^^^^^^^^^^^^^^^^^^^^^^^^^

Après ``uv sync``, vérifier que l'environnement est activé :

.. code-block:: bash

   uv run python --version
   # Attendu: Python 3.13.3

   uv run python -c "import streamlit; print(streamlit.__version__)"
   # Attendu: 1.50.0 ou supérieur

Vérifier S3
^^^^^^^^^^^

Tester la connexion S3 :

.. code-block:: bash

   cd ~/mangetamain/50_test
   pytest test_s3_parquet_files.py -v

Si le test échoue, vérifier :

1. Le fichier ``96_keys/credentials`` existe et contient les bonnes clés
2. L'endpoint S3 est accessible : ``ping s3fast.lafrance.io``
3. Les règles iptables DNAT sont configurées (si applicable)

**Voir** : :doc:`s3` pour configuration détaillée S3 Garage.

Troubleshooting
---------------

Erreur : "uv: command not found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution** : Installer uv avec le script officiel :

.. code-block:: bash

   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env  # Recharger le PATH

Erreur : "Python 3.13 not found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution** : uv peut installer Python automatiquement :

.. code-block:: bash

   uv python install 3.13

Ou installer manuellement depuis https://www.python.org/downloads/

Erreur : "No credentials found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptôme** : Message "Credentials S3 introuvables" dans l'app

**Solution** :

1. Créer le répertoire : ``mkdir -p 96_keys``
2. Créer le fichier ``96_keys/credentials`` avec format INI :

.. code-block:: ini

   [s3fast]
   aws_access_key_id = VOTRE_CLE
   aws_secret_access_key = VOTRE_SECRET

3. Vérifier les permissions : ``chmod 600 96_keys/credentials``

Erreur : "Connection timeout" S3
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Causes possibles** :

1. **Réseau** : Vérifier la connectivité : ``curl -I http://s3fast.lafrance.io``
2. **Firewall** : Vérifier que le port 80 est ouvert
3. **DNAT** : Configurer le bypass pour performance maximale

**Solution DNAT** (optionnelle, gain 10x performance) :

.. code-block:: bash

   sudo iptables -t nat -A OUTPUT -p tcp -d 192.168.80.202 --dport 80 \\
        -j DNAT --to-destination 192.168.80.202:3910

**Voir** : :doc:`s3` section "Optimisation Performance DNAT".

Erreur : Tests pytest échouent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution** :

1. Vérifier que l'environnement est à jour :

.. code-block:: bash

   cd ~/mangetamain/10_preprod
   uv sync
   uv run pytest --version  # Attendu: pytest 8.5.0+

2. Lancer les tests avec verbosité :

.. code-block:: bash

   uv run pytest tests/unit/ -vv

3. Si un module spécifique échoue, tester isolément :

.. code-block:: bash

   uv run pytest tests/unit/test_colors.py -v

Port 8501 déjà utilisé
^^^^^^^^^^^^^^^^^^^^^^^

**Symptôme** : "Address already in use" au démarrage

**Solution** :

1. Identifier le processus utilisant le port :

.. code-block:: bash

   # Linux/macOS
   lsof -i :8501

   # Windows
   netstat -ano | findstr :8501

2. Arrêter le processus ou utiliser un autre port :

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py --server.port 8502

Application charge lentement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Premier lancement** : 5-10 secondes (chargement S3 normal)

**Lancements suivants lents** : Vérifier le cache Streamlit

**Solution** :

1. Dans l'app, cliquer menu (⋮) > "Clear cache"
2. Ou supprimer le cache manuellement :

.. code-block:: bash

   rm -rf ~/.streamlit/cache

Performance S3 < 100 MB/s
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution** : Configurer DNAT bypass pour atteindre 500-917 MB/s

**Voir** : :doc:`s3` section "DNAT Bypass Performance".

Ressources Supplémentaires
---------------------------

* **Documentation S3** : :doc:`s3` - Configuration stockage Garage
* **Tests** : :doc:`tests` - Guide complet tests et coverage
* **CI/CD** : :doc:`cicd` - Pipeline automatisé
* **Architecture** : :doc:`architecture` - Stack technique détaillée
* **API** : :doc:`api/index` - Référence complète des modules
