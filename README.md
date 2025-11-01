# 🍳 Mangetamain Analytics / Back to the Future Kitchen

**[English](#english-version) | [Français](#version-française)**

---

## English Version

[![CI Pipeline - Quality & Tests](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml/badge.svg)](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml)
![Tests](https://img.shields.io/badge/tests-118_total-success)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.13.7-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

### 📋 Overview

Culinary analytics platform based on a recipe recommendation system with Food.com data. Modern Python 3.13.7 + Streamlit + DuckDB + S3 Storage architecture.

### 🎯 Simplified S3 Configuration (2025-10-09)

#### Ultra-Simple Architecture
```
🔗 Single endpoint    : http://s3fast.lafrance.io
🗂️ Bucket            : mangetamain
🔑 Credentials        : 96_keys/credentials
🦆 DuckDB + S3        : garage_s3.duckdb (integrated secret)
⚡ Performance        : 500+ MB/s (DNAT bypass)
🐍 Consistent Python  : 3.13.7 everywhere
```

#### Usage

**DuckDB (Recommended)**
```bash
duckdb ~/mangetamain/96_keys/garage_s3.duckdb
SELECT * FROM 's3://mangetamain/PP_recipes.csv' LIMIT 10;
```

**Python**
```python
import boto3
from configparser import ConfigParser

config = ConfigParser()
config.read('96_keys/credentials')

s3 = boto3.client('s3', endpoint_url='http://s3fast.lafrance.io',
                  aws_access_key_id=config['s3fast']['aws_access_key_id'],
                  aws_secret_access_key=config['s3fast']['aws_secret_access_key'],
                  region_name='garage-fast')
```

**AWS CLI**
```bash
aws s3 ls s3://mangetamain/ --endpoint-url http://s3fast.lafrance.io --region garage-fast
```

#### Local Configuration (for development)

For Docker paths to work locally too, create a symbolic link:
```bash
sudo ln -s /home/julien/code/mangetamain/000_dev /app
```

This allows `pyproject.toml` to use the `/app/40_utils` path in both Docker AND local environments.

### 🏗️ Project Architecture

```
mangetamain/
├── 00_eda/           # 📊 EDA Notebooks - Exploratory analysis
├── 10_preprod/       # 🚀 Preprod environment (source of truth)
├── 20_prod/          # 📦 Prod environment (generated artifact)
├── 30_docker/        # 🐳 Docker Containers
├── 40_utils/         # 🔧 Data utilities (mangetamain_data_utils)
├── 50_test/          # 🧪 Infrastructure tests (S3/DuckDB)
├── 70_scripts/       # 📜 Shell scripts (deploy, CI checks)
├── 90_doc/           # 📚 Sphinx Documentation
└── 96_keys/          # 🔑 S3 Credentials (ignored by git)
```

### 🚀 Quick Start

#### 1. S3 Installation (one time only)
[S3 Installation Guide](https://julienlafrance.github.io/backtothefuturekitchen/en/s3.html#installation) | [S3 Usage Guide](https://julienlafrance.github.io/backtothefuturekitchen/en/s3.html#utilisation-aws-cli)

#### 2. Launch PREPROD
```bash
cd 10_preprod
uv run streamlit run src/mangetamain_analytics/main.py
```

#### 3. Launch PROD
```bash
cd 20_prod
uv run streamlit run streamlit/main.py
```

#### 4. Docker Containers
```bash
cd 30_docker
docker-compose -f docker-compose-preprod.yml up -d
docker-compose -f docker-compose-prod.yml up -d
```

### 🧪 Tests and Coverage

#### Automated CI/CD Pipeline

**Complete pipeline with self-hosted runner:**
- ✅ **CI** - Automatic tests on every push/PR
- ✅ **CD Preprod** - Auto-deploy to https://mangetamain.lafrance.io/
- ✅ **CD Prod** - Manual deploy to https://backtothefuturekitchen.lafrance.io/
- 📬 **Discord Notifications** - Real-time alerts for each deployment

**Local verification before push**
```bash
./70_scripts/run_ci_checks.sh prod    # Test 20_prod
./70_scripts/run_ci_checks.sh preprod # Test 10_preprod
```

**GitHub Actions automatically verifies:**
- ✅ **PEP8 compliance** (flake8)
- ✅ **Code formatting** (black)
- ✅ **Docstrings** (pydocstyle - Google style)
- ✅ **Unit tests** with coverage >= 90%
- ✅ **Type checking** (mypy - optional)

**Automated deployment:**
- 🚀 **Preprod** - Auto-deploy on push to `main`
- 🔒 **Prod** - Manual deployment with "DEPLOY" confirmation
- 🏥 **Health checks** - Automatic URL verification
- 📬 **Discord** - Success/failure notifications with rollback instructions

📚 **Complete documentation:** [CI/CD Pipeline](https://julienlafrance.github.io/backtothefuturekitchen/en/cicd.html) | [Workflows](https://julienlafrance.github.io/backtothefuturekitchen/en/cicd.html#workflows-github-actions)

#### Infrastructure Tests (50_test/)
**Complete S3 + DuckDB Test**
```bash
cd 50_test
pytest -v
```

**Results:** 35 tests (14-16 local, 35 on server with Docker)

#### Unit Tests with Coverage

**10_preprod - Source Code (93% coverage)**
```bash
cd 10_preprod
uv run pytest tests/unit/ -v --cov=src --cov-report=html
```
**Result:** 83 tests (79 passed, 4 skipped), 93% coverage

#### Global Metrics
- **Total tests:** 118 tests (83 unit + 35 infrastructure)
- **Source code coverage:** 93% (10_preprod)
- **Execution time:** ~6 seconds
- **Success rate:** 99%
- **90% target exceeded by 3 points** ✅

#### ⚠️ Note on 20_prod
**20_prod is not tested separately** because it's a build artifact of 10_preprod:
- 📦 Same source code as 10_preprod
- ✅ Covered by 10_preprod tests (93%)
- 🚀 Automatically deployed if tests pass

Testing 20_prod would be redundant. **Strategy**: test source before build.

📚 **Complete documentation:** [Tests and Coverage](https://julienlafrance.github.io/backtothefuturekitchen/en/tests.html) (118 tests, 93% coverage)

### 📊 Data

#### Datasets
- **PP_recipes.csv** (205MB) - 178,265 Food.com recipes
- **PP_users.csv** (14MB) - User profiles
- **interactions_train.csv** (28MB) - Training interactions
- **mangetamain.duckdb** (582MB) - Complete DuckDB database

#### S3 Storage
- **Bucket**: `mangetamain` on Garage S3
- **Performance**: 500-917 MB/s (depending on environment)
- **Access**: Single endpoint with transparent DNAT

### 🔧 Environments

| Environment | Port | URL | Status | CD |
|-------------|------|-----|--------|-----|
| **PREPROD** | 8500 | https://mangetamain.lafrance.io/ | ✅ | Auto-deploy |
| **PROD** | 8501 | https://backtothefuturekitchen.lafrance.io/ | ✅ | Manual |
| **Self-hosted Runner** | - | dataia (VPN) | ✅ | Active |

### 📈 Performance

- **S3 Download**: 507-917 MB/s
- **DuckDB COUNT**: 178K recipes in 0.53s
- **DuckDB GROUP BY**: Analysis in 0.54s
- **Python Consistency**: 100% across all environments

### 🔒 Security

- **Credentials**: `96_keys/` ignored by git
- **DNAT**: Reverse proxy bypass for performance
- **DuckDB Secrets**: Integrated in garage_s3.duckdb
- **Logging**: utils_logger.py for monitoring

### 📚 Documentation

**Complete documentation hosted on GitHub Pages:**
🌐 **https://julienlafrance.github.io/backtothefuturekitchen/**

#### Complete Guides
- [Installation & Configuration](https://julienlafrance.github.io/backtothefuturekitchen/en/installation.html)
- [S3 Garage Guide](https://julienlafrance.github.io/backtothefuturekitchen/en/s3.html) - Installation, usage, performance
- [Technical Architecture](https://julienlafrance.github.io/backtothefuturekitchen/en/architecture.html) - Stack, infrastructure, logging
- [CI/CD Pipeline](https://julienlafrance.github.io/backtothefuturekitchen/en/cicd.html) - Workflows, deployments, documentation
- [Tests & Coverage](https://julienlafrance.github.io/backtothefuturekitchen/en/tests.html) - 118 tests, 93% coverage
- [Quick Start](https://julienlafrance.github.io/backtothefuturekitchen/en/quickstart.html) - Quick start guide

### 🏷️ Version

**Current version**: 2025-10-31
- ✅ Simplified and optimized S3 configuration
- ✅ **Python 3.13.7 fixed** (resolved CI/CD venv cache corruption)
- ✅ Maximized S3 performance (DNAT bypass)
- ✅ DuckDB with integrated secrets
- ✅ **Organized architecture** (numbered folders 00-96)
  - 70_scripts/ for shell scripts (deploy, CI checks)
  - Centralized documentation in 90_doc/ (Sphinx)
  - Cleaned root (README.md + projet_mangetamain.pdf)
- ✅ **GitHub Pages documentation**
  - Automatic build via GitHub Actions
  - HTML removed from repo (38 MB saved)
  - Clean URL: julienlafrance.github.io/backtothefuturekitchen
  - Workflow isolated from preprod/prod CI/CD
- ✅ **Improved type annotations** (mypy errors reduced from 75 → 43)
- ✅ **Complete tests and coverage (118 tests, 93% coverage)**
- ✅ **Complete CI/CD pipeline with GitHub Actions**
  - Automatic PEP8 verification (flake8)
  - Code formatting validation (black)
  - Docstrings validation (pydocstyle)
  - Type checking (mypy)
  - Automated tests on PR and merge to main
  - Mandatory 90% minimum coverage
- ✅ **Automated Deployment (CD)**
  - Self-hosted runner on dataia (VPN)
  - CD Preprod: auto-deploy on main push
  - CD Prod: manual deployment with confirmation
  - Automatic health checks on public URLs
  - Real-time Discord notifications
- ✅ **External monitoring** (UptimeRobot, checks every 5 min)

---

**Team**: Data Analytics Team
**Last updated**: 2025-10-31

---

## Version Française

[![CI Pipeline - Quality & Tests](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml/badge.svg)](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml)
![Tests](https://img.shields.io/badge/tests-118_total-success)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.13.7-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

### 📋 Vue d'ensemble

Plateforme d'analytics culinaires basée sur un système de recommandations de recettes avec données Food.com. Architecture moderne Python 3.13.7 + Streamlit + DuckDB + S3 Storage.

### 🎯 Configuration S3 Simplifiée (2025-10-09)

#### Architecture Ultra-Simple
```
🔗 Endpoint unique    : http://s3fast.lafrance.io
🗂️ Bucket            : mangetamain
🔑 Credentials        : 96_keys/credentials
🦆 DuckDB + S3        : garage_s3.duckdb (secret intégré)
⚡ Performance        : 500+ MB/s (DNAT bypass)
🐍 Python cohérent    : 3.13.7 partout
```

#### Usage

**DuckDB (Recommandé)**
```bash
duckdb ~/mangetamain/96_keys/garage_s3.duckdb
SELECT * FROM 's3://mangetamain/PP_recipes.csv' LIMIT 10;
```

**Python**
```python
import boto3
from configparser import ConfigParser

config = ConfigParser()
config.read('96_keys/credentials')

s3 = boto3.client('s3', endpoint_url='http://s3fast.lafrance.io',
                  aws_access_key_id=config['s3fast']['aws_access_key_id'],
                  aws_secret_access_key=config['s3fast']['aws_secret_access_key'],
                  region_name='garage-fast')
```

**AWS CLI**
```bash
aws s3 ls s3://mangetamain/ --endpoint-url http://s3fast.lafrance.io --region garage-fast
```

#### Configuration Locale (pour développement)

Pour que les chemins Docker fonctionnent aussi en local, créer un lien symbolique :
```bash
sudo ln -s /home/julien/code/mangetamain/000_dev /app
```

Cela permet à `pyproject.toml` d'utiliser le chemin `/app/40_utils` en Docker ET en local.

### 🏗️ Architecture du Projet

```
mangetamain/
├── 00_eda/           # 📊 Notebooks EDA - Analyses exploratoires
├── 10_preprod/       # 🚀 Environnement preprod (source de vérité)
├── 20_prod/          # 📦 Environnement prod (artifact généré)
├── 30_docker/        # 🐳 Containers Docker
├── 40_utils/         # 🔧 Utilitaires data (mangetamain_data_utils)
├── 50_test/          # 🧪 Tests infrastructure S3/DuckDB
├── 70_scripts/       # 📜 Scripts shell (deploy, CI checks)
├── 90_doc/           # 📚 Documentation Sphinx
└── 96_keys/          # 🔑 Credentials S3 (ignoré par git)
```

### 🚀 Démarrage Rapide

#### 1. Installation S3 (une seule fois)
[Guide Installation S3](https://julienlafrance.github.io/backtothefuturekitchen/fr/s3.html#installation) | [Guide Utilisation S3](https://julienlafrance.github.io/backtothefuturekitchen/fr/s3.html#utilisation-aws-cli)

#### 2. Lancement PREPROD
```bash
cd 10_preprod
uv run streamlit run src/mangetamain_analytics/main.py
```

#### 3. Lancement PROD
```bash
cd 20_prod
uv run streamlit run streamlit/main.py
```

#### 4. Containers Docker
```bash
cd 30_docker
docker-compose -f docker-compose-preprod.yml up -d
docker-compose -f docker-compose-prod.yml up -d
```

### 🧪 Tests et Coverage

#### Pipeline CI/CD Automatisé

**Pipeline complet avec self-hosted runner:**
- ✅ **CI** - Tests automatiques sur chaque push/PR
- ✅ **CD Preprod** - Déploiement auto sur https://mangetamain.lafrance.io/
- ✅ **CD Prod** - Déploiement manuel sur https://backtothefuturekitchen.lafrance.io/
- 📬 **Notifications Discord** - Alertes temps réel pour chaque déploiement

**Vérification locale avant push**
```bash
./70_scripts/run_ci_checks.sh prod    # Teste 20_prod
./70_scripts/run_ci_checks.sh preprod # Teste 10_preprod
```

**GitHub Actions vérifie automatiquement:**
- ✅ **PEP8 compliance** (flake8)
- ✅ **Code formatting** (black)
- ✅ **Docstrings** (pydocstyle - Google style)
- ✅ **Tests unitaires** avec coverage >= 90%
- ✅ **Type checking** (mypy - optionnel)

**Déploiement automatique:**
- 🚀 **Preprod** - Auto-deploy sur push vers `main`
- 🔒 **Prod** - Déploiement manuel avec confirmation "DEPLOY"
- 🏥 **Health checks** - Vérification automatique des URLs
- 📬 **Discord** - Notifications succès/échec avec instructions rollback

📚 **Documentation complète:** [Pipeline CI/CD](https://julienlafrance.github.io/backtothefuturekitchen/fr/cicd.html) | [Workflows](https://julienlafrance.github.io/backtothefuturekitchen/fr/cicd.html#workflows-github-actions)

#### Tests d'infrastructure (50_test/)
**Test complet S3 + DuckDB**
```bash
cd 50_test
pytest -v
```

**Résultats :** 35 tests (14-16 en local, 35 sur serveur avec Docker)

#### Tests unitaires avec coverage

**10_preprod - Code Source (93% coverage)**
```bash
cd 10_preprod
uv run pytest tests/unit/ -v --cov=src --cov-report=html
```
**Résultat:** 83 tests (79 passent, 4 skipped), 93% coverage

#### Métriques globales
- **Total tests:** 118 tests (83 unitaires + 35 infrastructure)
- **Coverage code source:** 93% (10_preprod)
- **Temps d'exécution:** ~6 secondes
- **Taux de réussite:** 99%
- **Objectif 90% dépassé de 3 points** ✅

#### ⚠️ Note sur 20_prod
**20_prod n'est pas testé séparément** car c'est un artefact de build de 10_preprod :
- 📦 Même code source que 10_preprod
- ✅ Couvert par les tests de 10_preprod (93%)
- 🚀 Déployé automatiquement si les tests passent

Tester 20_prod serait redondant. **Stratégie** : tester le source avant build.

📚 **Documentation complète:** [Tests et Coverage](https://julienlafrance.github.io/backtothefuturekitchen/fr/tests.html) (118 tests, 93% coverage)

### 📊 Données

#### Datasets
- **PP_recipes.csv** (205MB) - 178,265 recettes Food.com
- **PP_users.csv** (14MB) - Profils utilisateurs
- **interactions_train.csv** (28MB) - Interactions d'entraînement
- **mangetamain.duckdb** (582MB) - Base DuckDB complète

#### Stockage S3
- **Bucket** : `mangetamain` sur Garage S3
- **Performance** : 500-917 MB/s (selon environnement)
- **Accès** : Endpoint unique avec DNAT transparent

### 🔧 Environnements

| Environnement | Port | URL | Status | CD |
|---------------|------|-----|--------|-----|
| **PREPROD** | 8500 | https://mangetamain.lafrance.io/ | ✅ | Auto-deploy |
| **PROD** | 8501 | https://backtothefuturekitchen.lafrance.io/ | ✅ | Manuel |
| **Self-hosted Runner** | - | dataia (VPN) | ✅ | Active |

### 📈 Performance

- **S3 Download** : 507-917 MB/s
- **DuckDB COUNT** : 178K recettes en 0.53s
- **DuckDB GROUP BY** : Analyse en 0.54s
- **Cohérence Python** : 100% sur tous environnements

### 🔒 Sécurité

- **Credentials** : `96_keys/` ignoré par git
- **DNAT** : Bypass reverse proxy pour performance
- **Secrets DuckDB** : Intégrés dans garage_s3.duckdb
- **Logging** : utils_logger.py pour monitoring

### 📚 Documentation

**Documentation complète hébergée sur GitHub Pages :**
🌐 **https://julienlafrance.github.io/backtothefuturekitchen/**

#### Guides Complets
- [Installation & Configuration](https://julienlafrance.github.io/backtothefuturekitchen/fr/installation.html)
- [Guide S3 Garage](https://julienlafrance.github.io/backtothefuturekitchen/fr/s3.html) - Installation, usage, performance
- [Architecture Technique](https://julienlafrance.github.io/backtothefuturekitchen/fr/architecture.html) - Stack, infrastructure, logging
- [Pipeline CI/CD](https://julienlafrance.github.io/backtothefuturekitchen/fr/cicd.html) - Workflows, déploiements, documentation
- [Tests & Coverage](https://julienlafrance.github.io/backtothefuturekitchen/fr/tests.html) - 118 tests, 93% coverage
- [Quick Start](https://julienlafrance.github.io/backtothefuturekitchen/fr/quickstart.html) - Démarrage rapide

### 🏷️ Version

**Version actuelle** : 2025-10-31
- ✅ Configuration S3 simplifiée et optimisée
- ✅ **Python 3.13.7 fixé** (résolu corruption cache venv CI/CD)
- ✅ Performance S3 maximisée (DNAT bypass)
- ✅ DuckDB avec secrets intégrés
- ✅ **Architecture organisée** (dossiers numérotés 00-96)
  - 70_scripts/ pour scripts shell (deploy, CI checks)
  - Documentation centralisée dans 90_doc/ (Sphinx)
  - Racine nettoyée (README.md + projet_mangetamain.pdf)
- ✅ **Documentation GitHub Pages**
  - Build automatique via GitHub Actions
  - HTML retiré du repo (38 MB économisés)
  - URL propre : julienlafrance.github.io/backtothefuturekitchen
  - Workflow isolé du CI/CD preprod/prod
- ✅ **Type annotations améliorées** (erreurs mypy réduites de 75 → 43)
- ✅ **Tests et coverage complets (118 tests, 93% coverage)**
- ✅ **Pipeline CI/CD complet avec GitHub Actions**
  - Vérification PEP8 automatique (flake8)
  - Validation formatage code (black)
  - Validation docstrings (pydocstyle)
  - Type checking (mypy)
  - Tests automatisés sur PR et merge vers main
  - Coverage minimum 90% obligatoire
- ✅ **Déploiement automatisé (CD)**
  - Self-hosted runner sur dataia (VPN)
  - CD Preprod: auto-deploy sur push main
  - CD Prod: déploiement manuel avec confirmation
  - Health checks automatiques sur URLs publiques
  - Notifications Discord temps réel
- ✅ **Monitoring externe** (UptimeRobot, checks toutes les 5 min)

---

**Équipe** : Data Analytics Team
**Dernière mise à jour** : 2025-10-31
