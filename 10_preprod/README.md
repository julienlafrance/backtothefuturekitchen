# 🍽️ Mangetamain Analytics

![Tests](https://img.shields.io/badge/tests-118_passing-success)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.13.3-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.50.0-red)

Application web d'analyse de données culinaires basée sur le dataset Food.com. Dashboard interactif avec pipeline complet d'exploration, développement et déploiement.

## 🌐 Environnements Déployés

- **PREPROD** : https://mangetamain.lafrance.io/ (port 8500)
- **PRODUCTION** : https://backtothefuturekitchen.lafrance.io/ (port 8501)

## 📊 Dataset Food.com

- **178,265 recettes** avec nutrition, étapes et ingrédients
- **1.1M+ ratings** utilisateurs (1999-2018)
- **25,076 contributeurs** actifs
- **Stockage S3** : données parquet optimisées DuckDB

## 🏗️ Architecture du Projet

```
000_dev/
├── 00_eda/                         # Exploration de données
│   ├── 01_long_term/               # Notebooks analyses temporelles
│   ├── 02_seasonality/             # Notebooks saisonnalité
│   ├── 03_week_end_effect/         # Notebooks effet weekend
│   └── _data_utils/                # Utilitaires chargement données
│
├── 10_preprod/                     # ⭐ Application Streamlit
│   ├── src/mangetamain_analytics/
│   │   ├── main.py                 # Point d'entrée
│   │   ├── visualization/          # Modules analyses (tendances, saisonnalité, ratings)
│   │   ├── utils/                  # Utilitaires (data_loader, chart_theme, color_theme)
│   │   ├── data/                   # Gestion données DuckDB/S3
│   │   ├── exceptions.py           # Exceptions personnalisées
│   │   └── infrastructure/         # Config et logging
│   ├── tests/unit/                 # 118 tests unitaires
│   └── pyproject.toml              # Dépendances uv
│
├── 20_prod/                        # Production (synchronisé depuis preprod)
├── 30_docker/                      # Orchestration Docker
├── 40_utils/                       # Package partagé mangetamain-data-utils
├── 90_doc/                         # Documentation Sphinx
│   ├── source/*.rst                # Documentation complète
│   └── build/html/                 # Documentation générée
└── 96_keys/                        # Credentials S3 (gitignored)
```

## 🚀 Démarrage Rapide

### Installation en 2 minutes

```bash
# Cloner le repo
git clone https://github.com/julienlafrance/backtothefuturekitchen.git ~/mangetamain
cd ~/mangetamain/10_preprod

# Installer dépendances
uv sync

# Lancer l'application
uv run streamlit run src/mangetamain_analytics/main.py
```

**Accès** : http://localhost:8501

### Docker (Recommandé pour Production)

```bash
cd ~/mangetamain/30_docker
docker-compose up -d
```

## 🔧 Stack Technique

| Composant | Technologie | Version |
|-----------|------------|---------|
| **Frontend** | Streamlit | 1.50.0 |
| **Base de données** | DuckDB | 1.4.0 |
| **Traitement données** | Polars | 1.19.0 |
| **Visualisation** | Plotly | 5.24.1 |
| **Stockage** | MinIO S3 | Compatible AWS S3 |
| **Package manager** | uv | 0.8.22 |
| **Python** | CPython | 3.13.3 |

## 📈 Analyses Disponibles

### 🎯 Vue d'ensemble
- Métriques clés du dataset
- Distribution des recettes et ratings
- Statistiques utilisateurs

### ⭐ Analyse des Ratings
- Distribution des notes (0-5 étoiles)
- Évolution temporelle des ratings
- Patterns de notation par utilisateur

### 📅 Tendances Temporelles (1999-2018)
- Volume de recettes par année
- Durée de préparation et complexité
- Évolution des valeurs nutritionnelles
- Tendances ingrédients et catégories

### 🌸 Analyse Saisonnalité
- Heatmap calendrier annuel
- Patterns saisonniers par mois
- Ingrédients et tags saisonniers

### 📅 Effet Weekend
- Comparaison weekend vs semaine
- Différences comportementales utilisateurs
- Patterns temporels hebdomadaires

### 👥 Utilisateurs
- Top contributeurs actifs
- Analyse comportementale
- Métriques d'engagement

## 🧪 Qualité & Tests

### Validation continue

```bash
# Tests unitaires
uv run pytest tests/unit/ -v --cov=src

# Vérification PEP8
uv run flake8 src/ tests/

# Formatage automatique
uv run black src/ tests/

# Type checking
uv run mypy src/
```

### Métriques

- **118 tests** unitaires
- **93% coverage** de code
- **Type hinting** complet
- **Docstrings** Google style
- **Pipeline CI/CD** automatisé

## 🔄 Workflow Développement

### 1. Exploration (00_eda/)
Notebooks Jupyter pour analyses exploratoires :
- Statistiques descriptives
- Visualisations exploratoires
- Tests d'hypothèses
- Identification de patterns

### 2. Développement (10_preprod/)
Transformation analyses → modules Python :
- Copie logique métier depuis notebooks
- Conversion Matplotlib → Plotly
- Tests unitaires (2 par fonction minimum)
- Validation PEP8, black, coverage

### 3. Déploiement (20_prod/)
Pipeline CI/CD automatisé :
- Push GitHub → Déclenche CI
- Tests + validation qualité
- Déploiement automatique si succès

**Guide complet** : `GUIDE_INTEGRATION_ANALYSES.md`

## 📚 Documentation

Documentation Sphinx complète disponible :

```bash
cd ~/mangetamain/90_doc
make html
# Ouvrir build/html/index.html
```

**Sections** :
- Architecture système
- Guide installation
- API reference (modules auto-documentés)
- Configuration S3
- CI/CD pipeline
- Standards qualité
- FAQ

## 🛠️ Commandes Essentielles

```bash
# Développement
uv run streamlit run src/mangetamain_analytics/main.py
uv add nouvelle-dependance

# Tests
uv run pytest tests/unit/ -v
uv run pytest --cov=src --cov-report=html

# Qualité code
uv run flake8 src/
uv run black src/
uv run mypy src/

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose restart

# Git
git add .
git commit -m "Description"
git push origin main
gh run list  # Voir status CI/CD
```

## 🗄️ Stockage S3

Les données parquet sont stockées sur MinIO S3 compatible :

```python
# Configuration
from mangetamain_data_utils import load_recipes_clean, load_ratings

# Chargement automatique depuis S3
recipes_df = load_recipes_clean()
ratings_df = load_ratings()
```

**Documentation** : Voir `90_doc/source/s3.rst`

## 🎨 Visualisations

Bibliothèque Plotly avec thème personnalisé :
- **Graphiques interactifs** (zoom, pan, hover)
- **Palette de couleurs** cohérente
- **Responsive** (use_container_width=True)
- **Export** PNG/SVG intégré

Configuration centralisée : `src/mangetamain_analytics/utils/chart_theme.py`

## 🐳 Docker

```bash
# Lancer preprod
cd 30_docker
docker-compose up -d

# Logs temps réel
docker-compose logs -f

# Redémarrer
docker-compose restart

# Arrêter
docker-compose down
```

## 🔐 Configuration S3

Credentials stockés dans `96_keys/load_credentials.py` (gitignored).

Structure attendue :
```python
def load_s3_credentials():
    return {
        'aws_access_key_id': 'votre_key',
        'aws_secret_access_key': 'votre_secret',
        'endpoint_url': 'http://s3.example.com',
        'bucket': 'mangetamain',
        'region_name': 'us-east-1'
    }
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers branche (`git push origin feature/AmazingFeature`)
5. Ouvrir Pull Request

**Standards** :
- Tests unitaires obligatoires (coverage >= 90%)
- PEP8 validé avec flake8
- Code formaté avec black
- Docstrings Google style
- Type hints complets

## 📄 License

Ce projet est sous licence privée - voir le fichier LICENSE pour détails.

## 🙏 Remerciements

- Dataset Food.com original
- Communauté Streamlit
- Équipe DuckDB
- Contributors Polars et Plotly

---

**Mangetamain Analytics** - Analyse culinaire intelligente avec pipeline complet 🍽️📊
*Stack moderne • Tests automatisés • Documentation complète • CI/CD intégré*
