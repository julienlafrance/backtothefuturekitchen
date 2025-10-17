# 🍽️ Mangetamain Analytics

Application d'analyse de données pour le dataset Food.com - Dashboard interactif avec DuckDB et Streamlit

## 📁 Architecture du projet

```
mangetamain/
├── 00_preprod/                     # Environnement de développement
│   ├── src/mangetamain_analytics/  # Code source Streamlit
│   ├── data/mangetamain.duckdb     # Base de données (581MB, 2.3M lignes)
│   ├── logs/                       # Logs Loguru (app + erreurs)
│   └── .venv/                      # Environnement Python (uv)
├── 10_prod/                        # Environnement de production ✨
│   ├── streamlit/main.py           # Application optimisée 
│   ├── data/mangetamain.duckdb     # Base production
│   ├── logs/                       # Logs isolés production
│   └── pyproject.toml              # Configuration simplifiée
├── 20_VibeCoding/
│   └── Ydata/                      # Analyse YData SDK
│       ├── ydata_advanced_analysis.py  # Profiling avancé
│       └── profile_reports/        # Rapports HTML
├── 30_docker/                      # Orchestration conteneurs
│   ├── docker-compose.yml          # Docker preprod
│   └── docker-compose-prod.yml     # Docker production ✨
├── 90_doc/                         # Documentation technique
│   └── RESUME_*_V01-V05.md         # Historique des versions
└── README.md                       # Ce fichier
```

## 🚀 Démarrage rapide

### Docker Production (Recommandé)

```bash
cd 30_docker/
docker-compose -f docker-compose-prod.yml up -d
```

**Accès** : http://localhost:8501 (avec badges environnement automatiques)

### Développement local

```bash
cd 00_preprod/
uv sync
uv run streamlit run src/mangetamain_analytics/main.py
```

## 🎯 Fonctionnalités

### Analyses disponibles
- **Distribution des notes** : Visualisation 700K+ ratings Food.com (7 tables)
- **Activité utilisateurs** : Métriques d'engagement (top users (25K total))  
- **Base DuckDB** : Requêtes SQL rapides sur 7 tables
- **Badges environnement** : Détection auto PREPROD/PROD

### Dashboard interactif
- Interface Streamlit responsive
- Graphiques temps réel avec Seaborn/Matplotlib
- Sidebar informative avec metrics base de données
- Logs Loguru avec rotation automatique

## 🐳 Environnements Docker

### Production (mange_prod)
```bash
# Démarrage service persistant
docker-compose -f docker-compose-prod.yml up -d

# Monitoring logs
docker-compose -f docker-compose-prod.yml logs -f

# Santé du service
docker-compose -f docker-compose-prod.yml ps
```

### Maintenance
```bash
# Switch preprod → production
docker-compose down
docker-compose -f docker-compose-prod.yml up -d

# Redémarrage sans interruption
docker-compose -f docker-compose-prod.yml restart
```

## 🔧 Stack technique

- **Backend** : DuckDB 1.4.0 (2.3M lignes analysées)
- **Frontend** : Streamlit 1.50.0 avec badges environnement
- **Visualisation** : Seaborn 0.13.2, Matplotlib 3.10.6
- **Logs** : Loguru 0.7.3 (rotation 1MB, séparation erreurs)
- **Package Manager** : uv 0.8.22 (gestionnaire moderne)
- **Conteneurisation** : Python 3.13.3-slim, Docker Compose
- **Données** : Dataset Food.com (1999-2018, 25K utilisateurs)

## 📊 Données

Le dataset Food.com contient :
- **interactions_train** : 698,901 ratings
- **interactions_test** : 12,455 ratings  
- **interactions_validation** : 7,023 ratings
- **PP_users** : 25,076 utilisateurs
- **PP_recipes** : 178,265 recettes
- **RAW_interactions** : 1,132,367 interactions brutes
- **RAW_recipes** : 231,637 recettes détaillées

> Base DuckDB étendue disponible (581MB) avec 7 tables complètes

## 🎨 Interface utilisateur

### Badges environnement intelligents
- **🔧 PREPROD** : Environnement développement (gris discret)
- **🚀 PRODUCTION** : Environnement production (gris discret)
- **🚀 PROD (Docker)** : Conteneur production automatique

### Navigation
- **Sidebar** : Infos base + métriques + badge environnement
- **Onglets** : Vue d'ensemble, Notes, Temporel, Utilisateurs, Données brutes
- **Responsive** : Layout adaptatif wide format

## 📈 Monitoring

### Logs temps réel
```bash
# Logs production
tail -f ~/mangetamain/10_prod/logs/mangetamain_app.log

# Logs preprod  
tail -f ~/mangetamain/00_preprod/logs/mangetamain_app.log

# Erreurs uniquement
grep "ERROR" ~/mangetamain/*/logs/*.log
```

### Métriques dashboard
- Nombre total interactions analysées
- Utilisateurs les plus actifs (top 5)
- Distribution ratings (0-5 étoiles)
- Moyennes engagement par utilisateur

## 🚀 Accès en production

- **Local** : http://192.168.80.210:8501/8502 (selon environnement)
- **Docker** : http://localhost:8501 (mange_prod)
- **Public** : https://mangetamain.lafrance.io/ (reverse proxy HTTPS)

## 🤝 Développement

### Workflow recommandé
1. **Développer** dans `00_preprod/` (badge PREPROD)
2. **Tester** avec `uv run streamlit run...`  
3. **Copier** vers `10_prod/` pour validation
4. **Déployer** avec Docker production (badge PROD)

### Tests environnements
```bash
# Validation badges
cd ~/mangetamain/00_preprod && uv run python -c "print('✅ PREPROD')"
cd ~/mangetamain/10_prod && uv run python -c "print('✅ PROD')"
docker exec mange_prod python -c "print('✅ DOCKER')"
```

## 📚 Documentation

**Architecture évolutive** documentée dans `90_doc/` :
- **V01-V02** : Setup initial + Docker basique  
- **V03-V04** : Production + Logs Loguru
- **V05** : Environnements séparés + Badges ✨

**Détails techniques** : Voir `RESUME_PROD_20251001_V05.md`

## 🎯 Prochaines étapes

1. **Tests unitaires** : pytest avec couverture >90%
2. **CI/CD** : Pipeline GitHub Actions preprod→prod  
3. **Analyses ML** : Clustering utilisateurs, recommandations
4. **Monitoring** : Métriques Prometheus + Grafana
5. **Scaling** : Load balancing multi-conteneurs

---

**Mangetamain Analytics V05** - Dashboard Food.com avec environnements intelligents! 🍽️📊  
*Architecture production • Logs Loguru • Badges automatiques • Docker optimisé*
