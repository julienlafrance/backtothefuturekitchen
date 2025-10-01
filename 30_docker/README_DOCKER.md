# Docker Setup - MangetaMain Analytics

## 🐳 Docker Compose

### Démarrage
```bash
# Depuis le dossier 30_docker
docker-compose up -d

# Ou depuis n'importe où
docker-compose -f ~/mangetamain/30_docker/docker-compose.yml up -d
```

### Gestion
```bash
# Voir les logs
docker-compose logs -f

# Redémarrer après modification des dépendances
docker-compose restart

# Arrêter
docker-compose down

# Reconstruire et redémarrer
docker-compose up -d --force-recreate
```

### Accès
- **Local:** http://localhost:8501
- **Réseau:** http://192.168.80.210:8501
- **Public** https://mangetain.lafrance.io

## 📁 Volumes mappés

| Local | Container | Mode | Description |
|-------|-----------|------|-------------|
| `../00_preprod/src/` | `/app/src/` | RO | Code source (modifications en temps réel) |
| `../00_preprod/data/` | `/app/data/` | RW | Base de données DuckDB |
| `../00_preprod/pyproject.toml` | `/app/pyproject.toml` | RO | Configuration uv |
| `../00_preprod/uv.lock` | `/app/uv.lock` | RO | Lock des dépendances |
| `../00_preprod/README.md` | `/app/README.md` | RO | Documentation (requis par hatchling) |

## 🔄 Workflow de développement

### Modification du code
1. Modifier les fichiers dans `00_preprod/src/`
2. Les changements sont visibles immédiatement (volume en temps réel)

### Nouvelle dépendance
1. Dans `00_preprod/` : `uv add nouvelle_dependance`
2. Dans `30_docker/` : `docker-compose restart`

### Debug
```bash
# Logs en temps réel
docker-compose logs -f mangetamain-web

# Entrer dans le conteneur
docker-compose exec mangetamain-web bash

# Vérifier la santé du conteneur
docker-compose ps
```

## ⚠️ Notes importantes

- Le dossier `data/` est en lecture/écriture car DuckDB a besoin d'écrire
- Le code source est en lecture seule pour éviter les modifications accidentelles
- Le conteneur redémarre automatiquement sauf arrêt manuel (`restart: unless-stopped`)
- Health check intégré pour vérifier que Streamlit répond

## 🗑️ Nettoyage

```bash
# Arrêter et supprimer le conteneur
docker-compose down

# Nettoyer complètement (images, volumes, réseaux)
docker system prune -a
```
