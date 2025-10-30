# Résumé Environnement Preprod - MangetaMain Analytics V3

**Date :** 30 septembre 2025 - 19:11  
**Environnement :** `/home/dataia25/mangetamain/`  
**Statut :** ✅ Production avec Docker Compose

---

## 🚀 Application Streamlit

### Configuration Actuelle
- **Framework :** Streamlit 1.50.0
- **Gestionnaire de paquets :** uv (version 0.8.22)
- **Python :** 3.13
- **Conteneurisation :** Docker Compose
- **Base de données :** DuckDB (`mangetamain.duckdb`)

### Accès
- **Local :** http://localhost:8501
- **Réseau :** http://192.168.80.210:8501
- **Port :** 8501 (mappé depuis le conteneur)
- **Status :** ✅ Fonctionnel avec données

---

## 📁 Structure du Projet

```
mangetamain/
├── 00_preprod/                        # Environnement de développement
│   ├── src/mangetamain_analytics/
│   │   ├── main.py                    # Application Streamlit principale
│   │   └── __init__.py
│   ├── data/
│   │   ├── mangetamain.duckdb         # Base de données DuckDB (20MB)
│   │   ├── PP_recipes.csv             # Données des recettes
│   │   ├── PP_users.csv               # Données des utilisateurs
│   │   ├── interactions_*.csv         # Données d'interactions
│   │   └── ...                        # Autres fichiers de données
│   ├── pyproject.toml                 # Configuration uv/Python
│   ├── uv.lock                        # Lock file des dépendances
│   ├── .venv/                         # Environnement virtuel local
│   ├── config/                        # Configuration
│   ├── assets/                        # Ressources
│   ├── logs/                          # Logs
│   ├── tests/                         # Tests
│   └── docs/                          # Documentation
├── 30_docker/                         # 🆕 Configuration Docker
│   ├── docker-compose.yml             # Docker Compose principal
│   ├── README_DOCKER.md               # Documentation Docker
│   └── .env.example                   # Variables d'environnement
└── 90_doc/                           # Documentation
    ├── RESUME_PREPROD_*_V01.md
    ├── RESUME_PREPROD_*_V02.md
    └── RESUME_PREPROD_*_V03.md        # Ce document
```

---

## 🐳 Déploiement Docker Compose

### Configuration Docker
```yaml
# docker-compose.yml
services:
  mangetamain-web:
    image: python:3.13-slim
    container_name: mange_web
    ports:
      - "8501:8501"
    volumes:
      - ../00_preprod/src:/app/src:ro          # Code source (RO)
      - ../00_preprod/data:/app/data           # Base DuckDB (RW)
      - ../00_preprod/pyproject.toml:/app/pyproject.toml:ro
      - ../00_preprod/uv.lock:/app/uv.lock:ro
      - ../00_preprod/README.md:/app/README.md:ro
    restart: unless-stopped
    healthcheck: intégré
```

### Volumes Mappés
| Local | Container | Mode | Description |
|-------|-----------|------|-------------|
| `00_preprod/src/` | `/app/src/` | RO | Code source (temps réel) |
| `00_preprod/data/` | `/app/data/` | RW | Base DuckDB + fichiers |
| `00_preprod/pyproject.toml` | `/app/pyproject.toml` | RO | Config uv |
| `00_preprod/uv.lock` | `/app/uv.lock` | RO | Lock dépendances |
| `00_preprod/README.md` | `/app/README.md` | RO | Doc (requis hatchling) |

### Avantages Docker Compose
- ✅ **Environnements séparés** : pas de conflit local/conteneur
- ✅ **Redémarrage automatique** : `restart: unless-stopped`
- ✅ **Health check intégré** : surveillance automatique
- ✅ **Réseau dédié** : `mangetamain-network`
- ✅ **Gestion simplifiée** : une seule commande

---

## 📦 Dépendances Installées

### Principales
- `streamlit>=1.28.0` - Interface web
- `duckdb>=0.9.0` - Base de données (✅ connectée)
- `pandas>=2.0.0` - Manipulation de données
- `plotly>=5.17.0` - Graphiques interactifs
- `numpy>=1.24.0` - Calculs numériques
- `altair>=5.0.0` - Visualisations
- `loguru>=0.7.0` - Logging
- `python-dotenv>=1.0.0` - Variables d'environnement

### Ajouts récents
- `seaborn` - Visualisations statistiques
- `matplotlib` - Graphiques

---

## 🔧 Environnements de Développement

### Local (00_preprod)
- **Python :** 3.13.3 (system)
- **uv :** 0.8.22
- **Environnement virtuel :** `.venv/` (propre)
- **Usage :** Développement et tests

### Docker (30_docker)
- **Python :** 3.13.7 (conteneur)
- **uv :** 0.8.22 (installé via pip)
- **Environnement virtuel :** `/app/.venv` (isolé)
- **Usage :** Production et démo

---

## 🚦 Commandes de Gestion

### Docker Compose (Production)
```bash
cd ~/mangetamain/30_docker

# Démarrer
sudo docker-compose up -d

# Voir les logs
sudo docker-compose logs -f

# Redémarrer (après nouvelles dépendances)
sudo docker-compose restart

# Arrêter
sudo docker-compose down

# Status
sudo docker-compose ps
```

### Développement Local
```bash
cd ~/mangetamain/00_preprod

# Activer l'environnement
source .venv/bin/activate

# Lancer Streamlit
streamlit run src/mangetamain_analytics/main.py

# Ou avec uv directement
uv run streamlit run src/mangetamain_analytics/main.py

# Ajouter une dépendance
uv add nom_du_paquet
uv sync
```

---

## 📋 Historique des Actions V3

### Résolution des Problèmes Docker
1. ✅ **Conflit environnements** : séparation local/Docker résolue
2. ✅ **Permissions .venv** : nettoyage avec `sudo rm -rf .venv`
3. ✅ **Variable VIRTUAL_ENV** : `unset VIRTUAL_ENV` pour nettoyer
4. ✅ **Base DuckDB manquante** : ajout mapping volume `data/`
5. ✅ **Erreur "Read-only"** : DuckDB en RW sur volume `data/`
6. ✅ **README manquant** : ajout mapping `README.md` (requis hatchling)

### Organisation Docker
1. ✅ **Dossier dédié** : création `30_docker/`
2. ✅ **Docker Compose** : migration de `docker run` vers compose
3. ✅ **Documentation** : `README_DOCKER.md` complet
4. ✅ **Configuration** : `.env.example` pour personnalisation
5. ✅ **Health check** : surveillance automatique intégrée

---

## 🎯 État Actuel V3

### ✅ Fonctionnel
- Application Streamlit accessible et stable
- Base de données DuckDB connectée et fonctionnelle
- Docker Compose opérationnel avec restart automatique
- Environnements local et Docker séparés proprement
- Volumes mappés correctement (code en temps réel)
- Health check et monitoring intégré

### 🔄 Améliorations Apportées
- Organisation professionnelle avec dossier Docker dédié
- Documentation complète pour l'équipe
- Gestion simplifiée via docker-compose
- Workflow de développement optimisé
- Résolution complète des conflits d'environnements

### 📝 Prochaines Étapes Suggérées
- Tests automatisés de l'application
- CI/CD pipeline avec GitHub Actions
- Monitoring avancé (Prometheus/Grafana)
- Backup automatique de la base DuckDB
- Configuration multi-environnements (dev/staging/prod)

---

## 🚀 Workflow de Production V3

### Développement
1. **Code** : Modifier dans `00_preprod/src/`
2. **Test local** : `uv run streamlit run ...` 
3. **Validation** : Tester les changements

### Déploiement
1. **Nouvelles dépendances** : `uv add package` dans `00_preprod/`
2. **Redémarrage** : `docker-compose restart` dans `30_docker/`
3. **Vérification** : `docker-compose logs -f`

### Monitoring
1. **Status** : `docker-compose ps`
2. **Logs** : `docker-compose logs -f mangetamain-web`
3. **Health** : Health check automatique intégré

---

## 📊 Métriques de Performance

### Base de Données
- **DuckDB** : 20MB (mangetamain.duckdb)
- **Données CSV** : ~900MB total
- **Performance** : Connexion stable, pas d'erreur

### Application
- **Démarrage** : ~45-60 secondes (installation dépendances)
- **Mémoire** : Optimisée via Docker slim
- **Réseau** : Accessible local + réseau

### Infrastructure
- **Conteneur** : python:3.13-slim (base légère)
- **Volumes** : 6 mappings (5 RO, 1 RW)
- **Réseau** : mangetamain-network dédié

---

**Dernière mise à jour :** 30/09/2025 - 19:11  
**Responsable :** dataia25  
**Version :** V3 - Production Docker Compose  
**Statut :** ✅ Stable et documenté
