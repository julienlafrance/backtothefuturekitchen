# 🍳 Mangetamain Analytics

[![CI Pipeline - Quality & Tests](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml/badge.svg)](https://github.com/julienlafrance/backtothefuturekitchen/actions/workflows/ci.yml)
![Tests](https://img.shields.io/badge/tests-96_passing-success)
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)
![10_preprod](https://img.shields.io/badge/10__preprod-96%25-brightgreen)
![20_prod](https://img.shields.io/badge/20__prod-100%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.13.3-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📋 Vue d'ensemble

Plateforme d'analytics culinaires basée sur un système de recommandations de recettes avec données Food.com. Architecture moderne Python 3.13.3 + Streamlit + DuckDB + S3 Storage.

## 🎯 Configuration S3 Simplifiée (2025-10-09)

### Architecture Ultra-Simple
```
🔗 Endpoint unique    : http://s3fast.lafrance.io
🗂️ Bucket            : mangetamain  
🔑 Credentials        : 96_keys/credentials
🦆 DuckDB + S3        : garage_s3.duckdb (secret intégré)
⚡ Performance        : 500+ MB/s (DNAT bypass)
🐍 Python cohérent    : 3.13.3 partout
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

## 🏗️ Architecture du Projet

```
mangetamain/
├── 00_eda/           # 📊 Notebooks EDA - Analyses exploratoires qui alimentent l'app Streamlit
├── 10_preprod/       # Environnement de pré-production
├── 20_prod/          # Environnement de production  
├── 30_docker/        # Containers Docker
├── 50_test/          # Tests et validation S3
├── 90_doc/           # Documentation
├── 96_keys/          # Credentials S3 (ignoré par git)
└── S3_INSTALL.md     # Guide installation S3
└── S3_USAGE.md       # Guide utilisation S3
```

## 🚀 Démarrage Rapide

### 1. Installation S3 (une seule fois)
Suivre [S3_INSTALL.md](S3_INSTALL.md)

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

**Vérification locale avant push**
```bash
./run_ci_checks.sh prod    # Teste 20_prod
./run_ci_checks.sh preprod # Teste 10_preprod
```

Le pipeline CI/CD GitHub Actions vérifie automatiquement :
- ✅ **PEP8 compliance** (flake8)
- ✅ **Code formatting** (black)
- ✅ **Docstrings** (pydocstyle - Google style)
- ✅ **Tests unitaires** avec coverage >= 90%
- ✅ **Type checking** (mypy - optionnel)

📚 **Documentation complète:** Voir [README_CI_CD.md](README_CI_CD.md)

### Tests d'infrastructure (50_test/)
**Test complet S3 + DuckDB**
```bash
cd 50_test
pytest -v
```

**Résultats :** 35 tests (14-16 en local, 35 sur serveur avec Docker)

### Tests unitaires avec coverage

**10_preprod - Analytics (96% coverage)**
```bash
cd 10_preprod
uv run pytest tests/unit/ -v --cov=src --cov-report=html
```
**Résultat:** 22 tests passent, 96% coverage en 2.10s

**20_prod - Production (100% coverage)**
```bash
cd 20_prod
uv run pytest tests/unit/ -v --cov=streamlit --cov-report=html
```
**Résultat:** 31 tests passent, 100% coverage en 0.94s

### Métriques globales
- **Total tests:** 96 tests configurés
- **Coverage global:** 98% sur code métier
- **Temps d'exécution:** ~6 secondes
- **Taux de réussite:** 100%

📚 **Documentation complète:** Voir [RESUME_COVERAGE_FINAL.md](RESUME_COVERAGE_FINAL.md)

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

| Environnement | Port | Status | Python | Usage |
|---------------|------|--------|--------|--------|
| **PREPROD** | 8500 | ✅ | 3.13.3 | Développement |
| **PROD** | 8501 | ✅ | 3.13.3 | Production |
| **Containers** | 8500/8501 | ✅ | 3.13.3 | Déploiement |

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

### Configuration et utilisation
- **[S3_INSTALL.md](S3_INSTALL.md)** - Guide d'installation S3
- **[S3_USAGE.md](S3_USAGE.md)** - Guide d'utilisation S3
- **[90_doc/](90_doc/)** - Documentation technique complète

### Tests et coverage
- **[RESUME_COVERAGE_FINAL.md](RESUME_COVERAGE_FINAL.md)** - 📊 Résumé complet coverage (96 tests, 98% coverage)
- **[README_COVERAGE.md](README_COVERAGE.md)** - Guide général pytest-cov
- **[50_test/README_TESTS.md](50_test/README_TESTS.md)** - Tests d'infrastructure détaillés
- **[20_prod/README_COVERAGE.md](20_prod/README_COVERAGE.md)** - Guide coverage 20_prod (100%)
- **[00_eda/_data_utils/README_TESTS.md](00_eda/_data_utils/README_TESTS.md)** - Tests data_utils

## 🏷️ Version

**Version actuelle** : 2025-10-23
- ✅ Configuration S3 simplifiée et optimisée
- ✅ Python 3.13.3 unifié sur tous environnements
- ✅ Performance S3 maximisée (DNAT bypass)
- ✅ DuckDB avec secrets intégrés
- ✅ Architecture nettoyée et validée
- ✅ **Tests et coverage complets (96 tests, 98% coverage)**
- ✅ **Pipeline CI/CD avec GitHub Actions**
  - Vérification PEP8 automatique (flake8)
  - Validation des docstrings (pydocstyle)
  - Tests automatisés sur PR et merge vers main
  - Coverage minimum 90% obligatoire

---

**Équipe** : Data Analytics Team
**Dernière mise à jour** : 2025-10-23
