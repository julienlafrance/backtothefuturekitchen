Glossaire
=========

Termes Techniques
-----------------

CI/CD
   Continuous Integration / Continuous Deployment. Pratique DevOps d'automatisation du test et déploiement du code.

Coverage
   Mesure du pourcentage de code testé par les tests unitaires. Objectif projet: ≥90%.

DuckDB
   Base de données OLAP (Online Analytical Processing) columnar haute performance. Alternative SQLite pour analytics.

DNAT
   Destination Network Address Translation. Technique iptables pour rediriger trafic réseau directement vers port 3910, bypass reverse proxy pour gain performance 10x.

Flake8
   Outil Python vérifiant conformité PEP8 (style code Python standard).

Parquet
   Format fichier columnar compressé optimisé pour analytics. 5-10x plus performant que CSV.

Polars
   Bibliothèque Python DataFrame haute performance, alternative Pandas. Moteur Rust, format Arrow.

Pytest
   Framework tests unitaires Python le plus populaire.

S3 Garage
   Implémentation self-hosted protocole Amazon S3. Utilisé pour stockage datasets projet.

Streamlit
   Framework Python pour créer apps web interactives data science sans JavaScript.

TTL
   Time To Live. Durée cache avant expiration (projet: 3600s = 1h).

uv
   Gestionnaire paquets Python moderne ultra-rapide. Remplaçant pip, 10-100x plus rapide.

Termes Projet
-------------

PREPROD
   Environnement pre-production pour tests avant déploiement PROD. URL: https://mangetamain.lafrance.io/, port 8500.

PRODUCTION
   Environnement production stable. URL: https://backtothefuturekitchen.lafrance.io/, port 8501.

Recipes Clean
   Dataset nettoyé 178,265 recettes Food.com (1999-2018). Fichier: recipes_clean.parquet (250 MB).

Ratings Longterm
   Dataset 1.1M+ interactions utilisateurs. Fichier: ratings_longterm.parquet (180 MB).

Back to the Kitchen
   Nom projet et charte graphique (palette orange/noir).

Runner Self-Hosted
   Machine GitHub Actions exécutant CI/CD directement sur VM dataia (évite VPN).

Termes Analytics
----------------

Analyse Tendances
   Module ``analyse_trendlines_v2`` étudiant évolution recettes 1999-2018 (volume, durée, complexité).

Analyse Saisonnière
   Module ``analyse_seasonality`` identifiant patterns saisonniers (hiver/été, pics décembre).

Analyse Weekend
   Module ``analyse_weekend`` comparant publications semaine vs weekend (lundi +45%, samedi -49%).

Analyse Ratings
   Module ``analyse_ratings`` étudiant distribution notes utilisateurs (biais positif 78% = 5★).

Complexity Score
   Score 0-10 calculé depuis nombre étapes + ingrédients + temps préparation.

Charte Graphique
   Palette couleurs unifiée: ``ORANGE_PRIMARY`` (#FF8C00), ``BACKGROUND_MAIN`` (#1E1E1E).

Termes Infrastructure
---------------------

Dataia
   VM hébergeant services PREPROD/PROD, Garage S3, runner GitHub Actions. IP: 192.168.80.202.

Docker Compose
   Outil orchestration conteneurs Docker. Fichiers: docker-compose.yml (PREPROD), docker-compose-prod.yml (PROD).

Health Check
   Endpoint HTTP vérifiant santé application. URL: ``/_stcore/health``. Retry 3 fois, timeout 10s.

Loguru
   Bibliothèque logging Python moderne. Config: 2 fichiers (debug.log, errors.log), rotation automatique.

Webhook Discord
   Notifications temps réel CI/CD dans channel #deployments.

Acronymes
---------

API
   Application Programming Interface. Référence modules Python documentés.

ASCII
   American Standard Code for Information Interchange. Diagrammes texte utilisés dans documentation.

CSV
   Comma-Separated Values. Format fichier tabulaire (remplacé par Parquet pour performance).

EDA
   Exploratory Data Analysis. Notebooks Jupyter exploration données (``00_eda/``).

FAQ
   Frequently Asked Questions. Page questions courantes.

JSON
   JavaScript Object Notation. Format échange données.

OLAP
   Online Analytical Processing. Type base données optimisé analytics (DuckDB).

PEP8
   Python Enhancement Proposal 8. Guide style code Python standard.

PR
   Pull Request. Demande fusion code GitHub.

REST
   Representational State Transfer. Architecture API (non utilisé projet, app web).

RST
   reStructuredText. Format markup Sphinx documentation.

SQL
   Structured Query Language. Langage requêtes bases données.

SSH
   Secure Shell. Protocole connexion sécurisée VM dataia.

TTL
   Time To Live. Durée cache.

UI
   User Interface. Interface utilisateur Streamlit.

URL
   Uniform Resource Locator. Adresse web.

VPN
   Virtual Private Network. Réseau privé virtuel (dataia accessible via VPN).

Commandes Courantes
-------------------

``uv sync``
   Installe toutes dépendances projet depuis pyproject.toml.

``uv run streamlit run``
   Lance application Streamlit en mode développement.

``pytest``
   Exécute tests unitaires.

``flake8``
   Vérifie conformité PEP8.

``black``
   Formate code Python automatiquement (style opinioné).

``docker-compose up -d``
   Démarre conteneurs Docker en arrière-plan.

``git push origin main``
   Pousse commits vers branche main, déclenche CI/CD.

``gh run watch``
   Surveille exécution workflow GitHub Actions temps réel.

``ssh dataia``
   Connexion SSH vers VM dataia.

``aws s3 cp --profile s3fast``
   Copie fichiers depuis/vers S3 Garage.

Valeurs Clés
------------

Objectifs Qualité
^^^^^^^^^^^^^^^^^

* **Coverage**: ≥90% (atteint: 93%)
* **Tests**: 118 tests (83 unitaires + 35 infrastructure)
* **PEP8**: 100% compliance
* **Docstrings**: Google Style, 100% fonctions

Métriques Performance
^^^^^^^^^^^^^^^^^^^^^

* **S3 sans DNAT**: 50-100 MB/s
* **S3 avec DNAT**: 500-917 MB/s (10x)
* **Cache Streamlit**: <0.1s (après 1er chargement 5-10s)
* **CI build**: ~2-3 minutes
* **CD PREPROD**: ~40 secondes
* **CD PROD**: ~1 minute

Données Projet
^^^^^^^^^^^^^^

* **Recettes**: 178,265 recettes
* **Ratings**: 1,132,367 interactions
* **Utilisateurs**: 25,076 contributeurs
* **Période**: 1999-2018 (20 ans)
* **Tags**: ~500 tags uniques
* **Stockage**: ~450 MB Parquet compressé

Configurations
^^^^^^^^^^^^^^

* **Python**: 3.13.7
* **Streamlit**: 1.50.0
* **Plotly**: 5.24.1
* **DuckDB**: 1.4.0
* **Polars**: 1.19.0
* **Cache TTL**: 3600s (1h)

Voir Aussi
----------

* :doc:`quickstart` - Guide démarrage rapide
* :doc:`faq` - Questions fréquentes
* :doc:`architecture` - Architecture technique détaillée
* :doc:`api/index` - Référence API complète
