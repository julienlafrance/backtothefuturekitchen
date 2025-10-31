# 🍳 Mangetamain Analytics

[![CI Pipeline - Quality & Tests](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml/badge.svg)](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml)
![Tests](https://img.shields.io/badge/tests-118_total-success)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.13.7-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📋 Vue d'ensemble

Plateforme d'analytics culinaires basée sur un système de recommandations de recettes avec données Food.com. Architecture moderne Python 3.13.7 + Streamlit + DuckDB + S3 Storage.

## 🎯 Configuration S3 Simplifiée (2025-10-09)

### Architecture Ultra-Simple
```
🔗 Endpoint unique    : http://s3fast.lafrance.io
🗂️ Bucket            : mangetamain  
🔑 Credentials        : 96_keys/credentials
🦆 DuckDB + S3        : garage_s3.duckdb (secret intégré)
⚡ Performance        : 500+ MB/s (DNAT bypass)
🐍 Python cohérent    : 3.13.7 partout
```

### Usage

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

### Configuration Locale (pour développement)

Pour que les chemins Docker fonctionnent aussi en local, créer un lien symbolique :
```bash
sudo ln -s /home/julien/code/mangetamain/000_dev /app
```

Cela permet à `pyproject.toml` d'utiliser le chemin `/app/40_utils` en Docker ET en local.

## 🏗️ Architecture du Projet

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
├── 95_vibecoding/    # 🎨 Vibe coding
└── 96_keys/          # 🔑 Credentials S3 (ignoré par git)
```

## 🚀 Démarrage Rapide

### 1. Installation S3 (une seule fois)
[Guide Installation S3](https://julienlafrance.github.io/backtothefuturekitchen/s3.html#installation) | [Guide Utilisation S3](https://julienlafrance.github.io/backtothefuturekitchen/s3.html#utilisation-aws-cli)

### 2. Lancement PREPROD
```bash
cd 10_preprod
uv run streamlit run src/mangetamain_analytics/main.py
```

### 3. Lancement PROD
```bash
cd 20_prod  
uv run streamlit run streamlit/main.py
```

### 4. Containers Docker
```bash
cd 30_docker
docker-compose -f docker-compose-preprod.yml up -d
docker-compose -f docker-compose-prod.yml up -d
```

## 🧪 Tests et Coverage

### Pipeline CI/CD Automatisé

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

📚 **Documentation complète:** [Pipeline CI/CD](https://julienlafrance.github.io/backtothefuturekitchen/cicd.html) | [Workflows](https://julienlafrance.github.io/backtothefuturekitchen/cicd.html#workflows-github-actions)

### Tests d'infrastructure (50_test/)
**Test complet S3 + DuckDB**
```bash
cd 50_test
pytest -v
```

**Résultats :** 35 tests (14-16 en local, 35 sur serveur avec Docker)

### Tests unitaires avec coverage

**10_preprod - Code Source (93% coverage)**
```bash
cd 10_preprod
uv run pytest tests/unit/ -v --cov=src --cov-report=html
```
**Résultat:** 83 tests (79 passent, 4 skipped), 93% coverage

### Métriques globales
- **Total tests:** 118 tests (83 unitaires + 35 infrastructure)
- **Coverage code source:** 93% (10_preprod)
- **Temps d'exécution:** ~6 secondes
- **Taux de réussite:** 99%
- **Objectif 90% dépassé de 3 points** ✅

### ⚠️ Note sur 20_prod
**20_prod n'est pas testé séparément** car c'est un artefact de build de 10_preprod :
- 📦 Même code source que 10_preprod
- ✅ Couvert par les tests de 10_preprod (93%)
- 🚀 Déployé automatiquement si les tests passent

Tester 20_prod serait redondant. **Stratégie** : tester le source avant build.

📚 **Documentation complète:** [Tests et Coverage](https://julienlafrance.github.io/backtothefuturekitchen/tests.html) (118 tests, 93% coverage)

## 📊 Données

### Datasets
- **PP_recipes.csv** (205MB) - 178,265 recettes Food.com
- **PP_users.csv** (14MB) - Profils utilisateurs
- **interactions_train.csv** (28MB) - Interactions d'entraînement
- **mangetamain.duckdb** (582MB) - Base DuckDB complète

### Stockage S3
- **Bucket** : `mangetamain` sur Garage S3
- **Performance** : 500-917 MB/s (selon environnement)
- **Accès** : Endpoint unique avec DNAT transparent

## 🔧 Environnements

| Environnement | Port | URL | Status | CD |
|---------------|------|-----|--------|-----|
| **PREPROD** | 8500 | https://mangetamain.lafrance.io/ | ✅ | Auto-deploy |
| **PROD** | 8501 | https://backtothefuturekitchen.lafrance.io/ | ✅ | Manuel |
| **Self-hosted Runner** | - | dataia (VPN) | ✅ | Active |

## 📈 Performance

- **S3 Download** : 507-917 MB/s
- **DuckDB COUNT** : 178K recettes en 0.53s  
- **DuckDB GROUP BY** : Analyse en 0.54s
- **Cohérence Python** : 100% sur tous environnements

## 🔒 Sécurité

- **Credentials** : `96_keys/` ignoré par git
- **DNAT** : Bypass reverse proxy pour performance
- **Secrets DuckDB** : Intégrés dans garage_s3.duckdb
- **Logging** : utils_logger.py pour monitoring

## 📚 Documentation

**Documentation complète hébergée sur GitHub Pages :**
🌐 **https://julienlafrance.github.io/backtothefuturekitchen/**

### Guides Complets
- [Installation & Configuration](https://julienlafrance.github.io/backtothefuturekitchen/installation.html)
- [Guide S3 Garage](https://julienlafrance.github.io/backtothefuturekitchen/s3.html) - Installation, usage, performance
- [Architecture Technique](https://julienlafrance.github.io/backtothefuturekitchen/architecture.html) - Stack, infrastructure, logging
- [Pipeline CI/CD](https://julienlafrance.github.io/backtothefuturekitchen/cicd.html) - Workflows, déploiements, documentation
- [Tests & Coverage](https://julienlafrance.github.io/backtothefuturekitchen/tests.html) - 118 tests, 93% coverage
- [Quick Start](https://julienlafrance.github.io/backtothefuturekitchen/quickstart.html) - Démarrage rapide

## 🏷️ Version

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
