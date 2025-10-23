# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnement Sémantique](https://semver.org/lang/fr/).

---

## [1.0.0] - 2025-10-23

### ✨ Ajouté

#### Pipeline CI/CD
- **Pipeline CI complet avec GitHub Actions** (`.github/workflows/ci.yml`)
  - Vérification PEP8 automatique (flake8)
  - Vérification du formatage de code (black)
  - Validation des docstrings (pydocstyle - style Google)
  - Tests unitaires automatisés sur PR et merge vers main
  - Coverage minimum 90% obligatoire
  - Exécution parallèle des tests (prod, preprod, infra)
- **Documentation CI/CD complète**
  - `README_CI_CD.md` - Guide détaillé (450+ lignes)
  - `SYNTHESE_CI_CD_ACADEMIC.md` - Réponse aux exigences académiques (630+ lignes)
  - `.github/workflows/README.md` - Documentation des workflows
- **Script de test local** (`run_ci_checks.sh`) - Vérifie le code avant push
- **Configuration des outils**
  - `.flake8` - Configuration PEP8
  - `.pydocstyle` - Configuration docstrings (convention Google)

#### Tests et Coverage
- **Tests unitaires production** (31 tests, 100% coverage)
  - Tests des data loaders (`test_loaders.py`)
  - Tests du module principal (`test_main.py`)
- **Tests unitaires preprod** (22 tests, 96% coverage)
  - Tests d'analyse de ratings (`test_analyse_ratings_simple.py`)
  - Tests de graphiques personnalisés (`test_custom_charts.py`)
- **Tests d'infrastructure** (35 tests)
  - Tests S3 + DuckDB + Docker
  - Scan automatique des fichiers parquet
  - Validation des requêtes SQL
- **Documentation des tests**
  - `README_COVERAGE.md` - Documentation du coverage
  - `RESUME_COVERAGE_FINAL.md` - Résumé final
  - `README_TESTS.md` - Guide des tests

#### Modules de Visualisation
- **Module d'analyse de ratings** (`analyse_ratings_simple.py`)
  - Distribution des notes
  - Statistiques agrégées
  - Graphiques interactifs Plotly
- **Module de graphiques personnalisés** (`custom_charts.py`)
  - Création de visualisations réutilisables
  - Support Plotly et Matplotlib

#### Data Utilities
- **Utilitaires partagés** (`_data_utils/`)
  - `data_utils_common.py` - Connexion DuckDB, overview tables
  - `data_utils_ratings.py` - Traitement des ratings
  - `data_utils_recipes.py` - Traitement des recettes
  - Auto-localisation du fichier DuckDB
  - Support Polars pour performance

#### Documentation
- **Guide de transformation notebook → Streamlit** (`notebook_to_streamlit_guide.md`)
- **Badge CI dans README principal** - Statut en temps réel du pipeline
- **CHANGELOG.md** (ce fichier) - Historique des versions

### 🔧 Modifié

#### Configuration Git
- **Amélioration du .gitignore**
  - Exclusion des rapports de coverage (`htmlcov/`, `.coverage`)
  - Exclusion des fichiers DuckDB (`*.duckdb`, `**/data/*.duckdb`)
  - Exclusion des fichiers binaires

#### Dépendances
- **Ajout de pydocstyle>=6.3.0** dans `10_preprod` et `20_prod`
- **Unification Python 3.13.3** dans tous les environnements

#### Code
- **Formatage automatique avec black** sur tout le codebase
- **Correction des imports inutilisés** (Optional, sns, plt, go, datetime, Mock, patch)
- **Correction des docstrings** selon le style Google (D212, D415)
- **Correction des violations PEP8**
  - Remplacement des `bare except` par `except Exception`
  - Suppression des trailing whitespaces
  - Correction des f-strings sans placeholders

### 🗑️ Supprimé

- **Fichier binaire DuckDB** (10_preprod/src/mangetamain_analytics/data/mangetamain.duckdb)
  - 582MB, causait UnicodeDecodeError dans le CI
- **Workflow CD** (`.github/workflows/deploy.yml`)
  - Non nécessaire pour les exigences académiques
  - Simplifie le pipeline à CI uniquement
- **Référence README corrompue** dans `50_test/pyproject.toml`
  - Contenait des caractères non-UTF8

### 🐛 Corrigé

- **Configuration setuptools pour 50_test**
  - Ajout de `py-modules = []` pour éviter l'erreur "Multiple top-level modules discovered"
- **Encodage des fichiers**
  - Correction du caractère non-UTF8 dans `50_test/README.md`
- **Exceptions E402** pour les tests
  - Ajout dans `.flake8` pour les imports après `sys.path.insert`

---

## [0.5.0] - 2025-10-09

### ✨ Ajouté

#### Configuration S3 Simplifiée
- **Architecture ultra-simple** avec endpoint unique
  - Endpoint: `http://s3fast.lafrance.io`
  - Bucket: `mangetamain`
  - Performance: 500-917 MB/s (DNAT bypass)
- **DuckDB avec S3 intégré** (`garage_s3.duckdb`)
  - Credentials S3 embarqués
  - Requêtes directes sur fichiers parquet S3
- **Documentation S3**
  - `S3_INSTALL.md` - Guide d'installation
  - `S3_USAGE.md` - Guide d'utilisation

#### Environnements
- **Environnement 10_preprod** (port 8500)
  - Développement et expérimentation
  - Badge environnement dans Streamlit
- **Environnement 20_prod** (port 8501)
  - Production ready
  - Logging avec Loguru
- **Environnement 30_docker**
  - Orchestration Docker Compose
  - Redirection DNAT pour performance S3
  - Health checks automatiques

#### Base de Données
- **DuckDB intégré** (582MB)
  - 7 tables préchargées
  - 178,265 recettes
  - 25,076 utilisateurs
  - 1,1M+ interactions

### 🔧 Modifié

- **Unification Python 3.13.3** dans tous les environnements
- **Migration vers uv** comme gestionnaire de paquets
- **Optimisation des performances S3**

---

## [0.1.0] - 2024-XX-XX

### ✨ Ajouté

- **Initialisation du projet**
- **Structure de base des notebooks EDA** (`00_eda/`)
- **Application Streamlit initiale**
- **Configuration initiale du projet**

---

## Légende des Types de Changements

- **✨ Ajouté** : Nouvelles fonctionnalités
- **🔧 Modifié** : Changements dans des fonctionnalités existantes
- **🗑️ Supprimé** : Fonctionnalités supprimées
- **🐛 Corrigé** : Corrections de bugs
- **🔒 Sécurité** : Corrections de vulnérabilités
- **📚 Documentation** : Changements dans la documentation
- **⚡ Performance** : Améliorations de performance
- **♻️ Refactoring** : Refactorisation du code sans changement de fonctionnalité

---

## Liens Utiles

- **Repository**: https://github.com/julienlafrance/backtothefuturekitchen
- **CI/CD Pipeline**: https://github.com/julienlafrance/backtothefuturekitchen/actions
- **Documentation CI/CD**: [README_CI_CD.md](README_CI_CD.md)
- **Documentation Tests**: [README_COVERAGE.md](README_COVERAGE.md)

---

**Projet académique** - Mangetamain Analytics Team - 2025
