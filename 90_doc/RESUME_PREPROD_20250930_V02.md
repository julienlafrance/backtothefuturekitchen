# Résumé Environnement Preprod - MangetaMain Analytics

**Date :** 30 septembre 2025 - 18:26  
**Environnement :** `/home/dataia25/mangetamain/00_preprod`  
**Statut :** ✅ Opérationnel en Docker

---

## 🚀 Application Streamlit

### Configuration Actuelle
- **Framework :** Streamlit 1.50.0
- **Gestionnaire de paquets :** uv (version 0.8.22)
- **Python :** 3.13
- **Conteneur Docker :** `mange_web`

### Accès
- **Local :** http://localhost:8501
- **Réseau :** http://192.168.80.210:8501
- **Port :** 8501 (mappé depuis le conteneur)

---

## 📁 Structure du Projet

```
00_preprod/
├── src/mangetamain_analytics/
│   ├── main.py                    # Application Streamlit principale
│   └── __init__.py
├── pyproject.toml                 # Configuration uv/Python
├── uv.lock                        # Lock file des dépendances
├── .venv/                         # Environnement virtuel local
├── data/                          # Données
├── config/                        # Configuration
├── assets/                        # Ressources
├── logs/                          # Logs
├── tests/                         # Tests
└── docs/                          # Documentation
```

---

## 📦 Dépendances Installées

### Principales
- `streamlit>=1.28.0` - Interface web
- `duckdb>=0.9.0` - Base de données
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

## 🐳 Déploiement Docker

### Conteneur Actuel
```bash
# Conteneur en cours d'exécution
CONTAINER ID: db6bdab4daf7
IMAGE: python:3.13-slim
NAME: mange_web
STATUS: Up (depuis 35 secondes)
PORTS: 0.0.0.0:8501->8501/tcp
```

### Configuration Docker
- **Volume mappé :** `/home/dataia25/mangetamain/00_preprod:/app`
- **Répertoire de travail :** `/app`
- **Mode :** Headless (sans interface graphique)
- **Redémarrage :** Manuel

### Commandes Docker Utiles
```bash
# Voir les logs
sudo docker logs mange_web

# Arrêter
sudo docker stop mange_web

# Redémarrer
sudo docker start mange_web

# Supprimer
sudo docker stop mange_web && sudo docker rm mange_web
```

---

## 🔧 Environnement de Développement

### Outils Installés
- **uv** - Gestionnaire de paquets Python moderne
- **tmux** - Multiplexeur de terminal (utilisé précédemment)
- **Docker** - Conteneurisation
- **docker-compose** - Orchestration

### Variables d'Environnement
- `VIRTUAL_ENV=/home/dataia25/mangetamain/00_preprod/.venv`
- `UV_SYSTEM_PYTHON=1` (dans Docker)

---

## 📋 Historique des Actions

### Installation et Configuration
1. ✅ Installation d'uv comme gestionnaire de paquets
2. ✅ Synchronisation des dépendances avec `uv sync`
3. ✅ Résolution des problèmes de modules manquants (seaborn, matplotlib)
4. ✅ Configuration de l'environnement virtuel

### Déploiement
1. ✅ Test initial avec tmux (session "mange_web")
2. ✅ Installation de Docker et docker-compose
3. ✅ Migration vers conteneur Docker pour plus de propreté
4. ✅ Configuration du volume mappé pour le développement

---

## 🎯 État Actuel

### ✅ Fonctionnel
- Application Streamlit accessible
- Environnement Docker stable
- Volume mappé fonctionnel (modifications en temps réel)
- Accès réseau configuré

### 🔄 En Cours
- Documentation du projet
- Tests de l'application

### 📝 À Faire
- Configuration du redémarrage automatique Docker
- Mise en place d'un reverse proxy (optionnel)
- Monitoring et logs centralisés
- Tests automatisés

---

## 🚦 Commandes de Gestion

### Développement Local
```bash
# Activer l'environnement
cd /home/dataia25/mangetamain/00_preprod
source .venv/bin/activate

# Lancer avec uv
uv run streamlit run src/mangetamain_analytics/main.py

# Installer une nouvelle dépendance
uv add nom_du_paquet
```

### Production (Docker)
```bash
# Relancer le conteneur après modifications
sudo docker restart mange_web

# Voir l'état du conteneur
sudo docker ps | grep mange_web

# Monitorer les logs en temps réel
sudo docker logs -f mange_web
```

---

**Dernière mise à jour :** 30/09/2025 - 18:26  
**Responsable :** dataia25  
**Environnement :** Production prête, développement actif
