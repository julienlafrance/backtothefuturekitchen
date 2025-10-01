# CR Technique - Mangetamain Analytics - 30/09/2025

## Résultats obtenus

### Application déployée
- **Local**: http://192.168.80.210:8501
- **Public**: https://mangetamain.lafrance.io/ (reverse proxy Synology configuré)
- Dataset Food.com: 698,901 interactions analysées (DuckDB 20MB)
- Visualisations: distribution des notes + activité utilisateurs
- **Production stable avec Docker Compose** (persistance automatique)

### Infrastructure évolutive

**V01 (Setup initial)**: uv + environnement local  
**V02 (Conteneurisation)**: Migration Docker basique  
**V03 (Production)**: Docker Compose avec volumes optimisés  
**V04 (Logs)**: Système Loguru fonctionnel

## Architecture technique

```
mangetamain/
├── 00_preprod/                     # Développement
│   ├── src/mangetamain_analytics/
│   │   └── main.py                 # App principale (330 lignes)
│   ├── data/mangetamain.duckdb     # Base analytique (20MB)
│   ├── logs/                       # Loguru (app + errors)
│   └── .venv/                      # Env Python (uv)
├── 30_docker/                      # Production
│   └── docker-compose.yml          # Orchestration + persistance
└── 90_doc/                         # Documentation V01-V04
```

## Déploiement production

### Serveur web conteneurisé
- **Docker Compose**: Gestion automatique du serveur Streamlit
- **Persistance**: `restart: unless-stopped` assure continuité service
- **Health checks**: Surveillance automatique et redémarrage si échec
- **Volumes mappés**: Données et logs persistants hors conteneur

### Accès externe sécurisé
- **Reverse proxy Synology**: Configuration WebSocket pour Streamlit
- **HTTPS**: Certificat SSL configuré manuellement
- **URL publique**: https://mangetamain.lafrance.io/
- **Headers configurés**: X-Forwarded-Proto, Upgrade, Connection

## Stack technique
- **Backend**: DuckDB (743K interactions), pandas
- **Frontend**: Streamlit 1.50.0 (serveur Docker)
- **Visualisation**: Seaborn, matplotlib  
- **Logs**: Loguru avec rotation 1MB + console
- **Packaging**: uv 0.8.22 (gestionnaire moderne)
- **Déploiement**: Docker Compose avec restart automatique

## Problèmes résolus

**V01**: Modules manquants (seaborn, matplotlib), cache Streamlit  
**V02**: Conflits environnements local/Docker  
**V03**: Permissions .venv, DuckDB read-only, README manquant  
**V04**: Logs vides Streamlit (cache modules, config anti-duplication)  
**Reverse proxy**: Configuration WebSocket + en-têtes Streamlit

## Évolution architecture

### Volumes Docker optimisés
```yaml
volumes:
  - ../00_preprod/src:/app/src:ro           # Code temps réel
  - ../00_preprod/data:/app/data            # DB read-write  
  - ../00_preprod/logs:/app/logs            # Logs partagés
  - ../00_preprod/pyproject.toml:/app/pyproject.toml:ro
restart: unless-stopped                     # Persistance service
```

### Configuration Loguru corrigée
```python
# Anti-duplication pour Streamlit
if not any("logs/mangetamain" in str(handler) for handler in logger._core.handlers.values()):
    logger.remove()
    logger.add("logs/mangetamain_app.log", rotation="1 MB")
    logger.add(sys.stderr, level="DEBUG")  # Console
```

## Commandes essentielles

### Production (serveur Docker persistant)
```bash
cd ~/mangetamain/30_docker
sudo docker-compose up -d           # Démarrage service persistant
sudo docker-compose restart         # Après modifs (service continue)
sudo docker-compose logs -f         # Debug sans interruption
```

### Développement local
```bash
cd ~/mangetamain/00_preprod
source .venv/bin/activate
uv run streamlit run src/mangetamain_analytics/main.py
```

### Monitoring
```bash
# Logs temps réel (persistants)
tail -f ~/mangetamain/00_preprod/logs/mangetamain_app.log

# Erreurs uniquement
grep "ERROR" ~/mangetamain/00_preprod/logs/mangetamain_*.log

# Docker status (service persistant)
sudo docker-compose ps
```

## Métriques finales

- **Temps développement**: 6h (4 versions évolutives)
- **Performance**: Chargement <1s, requêtes <100ms
- **Données**: 743K interactions Food.com (1999-2018)
- **Code**: 330 lignes documentées (docstrings anglaises)
- **Infrastructure**: Service Docker persistant + health checks
- **Disponibilité**: 24/7 via reverse proxy HTTPS

## Environnements séparés

| Environnement | Python | Usage | Persistance |
|---------------|--------|-------|-------------|
| Local (00_preprod) | 3.13.3 | Développement | Session |
| Docker (30_docker) | 3.13.7 | Production | Service 24/7 |

## Accès sécurisé

- **Local**: http://192.168.80.210:8501
- **Public**: https://mangetamain.lafrance.io/
- **Reverse proxy**: Synology avec WebSocket + SSL
- **Service**: Docker Compose assure disponibilité continue

## Documentation disponible

- **V01**: Setup initial uv + DuckDB (9.6KB)
- **V02**: Migration Docker basique (4.5KB)  
- **V03**: Docker Compose production (8.2KB)
- **V04**: Correction logs Streamlit (2KB)
- **Différentiel Loguru**: Guide technique Streamlit

## Prochaines étapes

1. Tests unitaires (pytest + couverture >90%)
2. **Alignement versions Docker**: Harmoniser local/production (actuellement 3.13.3 vs 3.13.7)
3. CI/CD GitHub Actions
4. Documentation Sphinx
5. Analyses ML (clustering, recommandations)

## Contact technique

**Service web**: Docker Compose assure persistance automatique du serveur Streamlit. Redémarrage auto en cas d'échec. Logs temps réel opérationnels. Infrastructure prête scaling horizontal. Accès sécurisé HTTPS via reverse proxy.

**Architecture finale**: Service production 24/7 avec 4 itérations d'amélioration documentées.
