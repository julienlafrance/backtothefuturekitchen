# 🍽️ Mangetamain Analytics

Application d'analyse de données pour le dataset Food.com - Dashboard interactif avec DuckDB et Streamlit

## 📁 Architecture du projet

```
mangetamain/
├── 00_eda/                         # Analyse exploratoire des données 🔍
│   ├── 01_long_term/               # Analyses long terme
│   ├── 02_seasonality/             # Analyses saisonnières  
│   ├── 03_week_end_effect/         # Analyses effet week-end
│   └── main.py                     # Script principal EDA
├── 10_preprod/                     # Environnement de pré-production 🔧
│   ├── src/mangetamain_analytics/  # Code source Streamlit
│   ├── data/                       # Base de données DuckDB
│   ├── logs/                       # Logs Loguru (app + erreurs)
│   ├── tests/                      # Tests unitaires et intégration
│   └── pyproject.toml              # Configuration projet
├── 20_prod/                        # Environnement de production 🚀
│   ├── streamlit/main.py           # Application optimisée 
│   ├── data/                       # Base production
│   ├── logs/                       # Logs isolés production
│   └── pyproject.toml              # Configuration simplifiée
├── 20_vibecoding/                  # Expérimentations active
│   └── Ydata/                      # Analyse YData SDK
├── 30_docker/                      # Orchestration conteneurs 🐳
│   ├── docker-compose-preprod.yml  # Docker pré-production
│   └── docker-compose-prod.yml     # Docker production
├── 90_doc/                         # Documentation technique 📚
│   └── RESUME_*.md                 # Historique des versions
└── 95_vibecoding/                  # Archives analyses YData
    └── Ydata/                      # Rapports et analyses archivées
```

## 🚀 Démarrage rapide

### Docker Production (Recommandé)

```bash
cd 30_docker/

# Lancer production
docker-compose -f docker-compose-prod.yml up -d

# Lancer pré-production  
docker-compose -f docker-compose-preprod.yml up -d
```

**Accès** : 
- **Production** : http://localhost:8501 (badge 🚀 PROD)
- **Pré-production** : http://localhost:8500 (badge 🔧 PREPROD)

### Développement local

```bash
# Pré-production
cd 10_preprod/
uv sync
uv run streamlit run src/mangetamain_analytics/main.py

# Production
cd 20_prod/
uv sync  
uv run streamlit run streamlit/main.py
```

## 🎯 Fonctionnalités

### Analyses disponibles
- **Vue d'ensemble** : Métriques globales des 7 tables DuckDB
- **Distribution des notes** : Visualisation 700K+ ratings Food.com
- **Analyse temporelle** : Évolution des interactions dans le temps
- **Activité utilisateurs** : Métriques d'engagement (25K utilisateurs)
- **Explorateur de données** : Interface interactive pour toutes les tables

### Dashboard interactif
- Interface Streamlit responsive avec onglets
- Graphiques interactifs Plotly/Seaborn/Matplotlib
- **Badges d'environnement intelligents** : détection automatique PREPROD/PROD
- Sidebar informative avec métriques base de données
- Logs Loguru avec rotation automatique

## 🐳 Environnements Docker

### Architecture séparée

| Environnement | Conteneur | Port | Variable | Badge |
|---------------|-----------|------|----------|-------|
| **Pré-production** | `mange_preprod` | 8500 | `APP_ENV=PREPROD` | 🔧 PREPROD |
| **Production** | `mange_prod` | 8501 | `APP_ENV=PROD` | 🚀 PROD |

### Commandes Docker

```bash
cd 30_docker/

# === Pré-production ===
docker-compose -f docker-compose-preprod.yml up -d
docker-compose -f docker-compose-preprod.yml logs -f
docker-compose -f docker-compose-preprod.yml down

# === Production ===
docker-compose -f docker-compose-prod.yml up -d
docker-compose -f docker-compose-prod.yml logs -f  
docker-compose -f docker-compose-prod.yml down

# === Monitoring ===
docker ps                           # État des conteneurs
docker logs mange_preprod          # Logs pré-prod
docker logs mange_prod             # Logs prod
```

### Détection d'environnement intelligente

La fonction `detect_environment()` utilise une logique de priorité :

1. **Variable d'environnement** : `APP_ENV` (Docker)
2. **Détection Docker** : `/.dockerenv` (fallback)  
3. **Détection chemin** : `10_preprod` ou `20_prod` (local)

## 🔧 Stack technique

- **Backend** : DuckDB 1.4.0+ (2.3M+ lignes analysées)
- **Frontend** : Streamlit 1.28.0+ avec badges environnement  
- **Visualisation** : Plotly 5.17.0+, Seaborn 0.13.2+, Matplotlib
- **Logs** : Loguru 0.7.0+ (rotation 1MB, séparation erreurs)
- **Package Manager** : uv 0.8.22+ (gestionnaire moderne Python)
- **Conteneurisation** : Python 3.13-slim, Docker Compose 3.8
- **Données** : Dataset Food.com (1999-2018, 25K utilisateurs)

## 📊 Base de données

Le dataset Food.com contient 7 tables DuckDB :

| Table | Lignes | Description |
|-------|---------|-------------|
| **interactions_train** | 698,901 | Données d'entraînement ML |
| **interactions_test** | 12,455 | Données de test ML |
| **interactions_validation** | 7,023 | Données de validation ML |
| **PP_users** | 25,076 | Utilisateurs préprocessés |
| **PP_recipes** | 178,265 | Recettes préprocessées |
| **RAW_interactions** | 1,132,367 | Interactions brutes |
| **RAW_recipes** | 231,637 | Recettes détaillées |

> **Total** : ~2.3M lignes • Base DuckDB : ~581MB

## 🎨 Interface utilisateur

### Badges environnement automatiques

- **🔧 PREPROD** : Environnement de développement (gris)
- **🚀 PROD** : Environnement de production (vert)  
- **🐳 PROD (Docker)** : Détection Docker automatique (gris)

### Navigation par onglets

1. **📊 Vue d'ensemble** : Graphiques et métriques globales
2. **⭐ Analyses des notes** : Distribution des ratings  
3. **📅 Analyse temporelle** : Évolution dans le temps
4. **👥 Utilisateurs** : Activité et corrélations
5. **🔍 Données brutes** : Explorateur interactif

## 📈 Monitoring et logs

### Logs temps réel

```bash
# Logs applications
tail -f 10_preprod/logs/mangetamain_app.log    # Pré-prod
tail -f 20_prod/logs/mangetamain_app.log       # Prod

# Logs erreurs uniquement  
tail -f 10_preprod/logs/mangetamain_errors.log
tail -f 20_prod/logs/mangetamain_errors.log

# Recherche d'erreurs
grep "ERROR" */logs/*.log
```

### Métriques dashboard

- Nombre total d'interactions analysées  
- Répartition par type de table (RAW, PP, ML)
- Utilisateurs les plus actifs
- Distribution des notes (0-5 étoiles)
- Corrélations utilisateurs/recettes

## 🧪 Tests et qualité

### Structure de tests (10_preprod/tests/)

```
tests/
├── unit/                   # Tests unitaires
│   ├── test_database.py    # Tests connexions DuckDB
│   ├── test_logger.py      # Tests configuration Loguru  
│   └── test_main.py        # Tests fonctions principales
├── integration/            # Tests d'intégration
│   ├── test_app.py         # Tests application complète
│   └── test_docker.py      # Tests conteneurs
└── conftest.py             # Configuration pytest
```

### Lancer les tests

```bash
cd 10_preprod/
uv run pytest                          # Tous les tests
uv run pytest tests/unit/              # Tests unitaires
uv run pytest --cov=src --cov-report=html  # Avec couverture
```

## 🤝 Workflow développement

### Processus recommandé

1. **Développer** dans `10_preprod/` (badge 🔧 PREPROD)
2. **Tester** localement avec `uv run streamlit run...`
3. **Valider** avec Docker preprod sur port 8500
4. **Copier** vers `20_prod/` les modifications validées  
5. **Déployer** en production avec Docker sur port 8501

### Migration preprod → prod

```bash
# 1. Arrêter les services
cd 30_docker/
docker-compose -f docker-compose-preprod.yml down
docker-compose -f docker-compose-prod.yml down

# 2. Synchroniser le code validé
# (copie manuelle des fichiers modifiés 10_preprod/ → 20_prod/)

# 3. Relancer production
docker-compose -f docker-compose-prod.yml up -d

# 4. Vérifier badges et fonctionnalités
curl -I http://localhost:8501
```

## 📚 Documentation

**Évolution architecturale** dans `90_doc/` :
- **V01-V02** : Setup initial + Docker basique
- **V03-V04** : Production + Logs Loguru  
- **V05** : Environnements séparés + Badges automatiques ✨
- **V06** : Architecture 10_preprod/20_prod + Tests ⚡

## 🎯 Prochaines étapes

1. **Tests automatisés** : Couverture >90% avec pytest ✅
2. **CI/CD Pipeline** : GitHub Actions preprod→prod automatique
3. **Analyses ML avancées** : Clustering utilisateurs, recommandations
4. **Monitoring avancé** : Métriques Prometheus + Grafana
5. **Scaling horizontal** : Load balancing multi-conteneurs

## 🚀 Accès

- **Local preprod** : http://localhost:8500 (🔧 badge PREPROD)
- **Local production** : http://localhost:8501 (🚀 badge PROD) 
- **Docker Health Check** : Surveillance automatique des conteneurs
- **Logs centralisés** : Loguru avec rotation et niveaux séparés

---

**Mangetamain Analytics V06** - Architecture moderne avec environnements séparés! 🍽️📊  
*10_preprod • 20_prod • Variables d'environnement • Badges automatiques • Docker intelligent*
