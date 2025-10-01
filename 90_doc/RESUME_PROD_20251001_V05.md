# CR Technique - Mangetamain Analytics - 01/10/2025 - V05

## Résultats obtenus

### Environnement de production déployé
- **Environnement séparé** : `10_prod/` opérationnel avec structure optimisée
- **Application Streamlit** : http://192.168.80.210:8502 fonctionnelle
- **Docker Compose** : Production alignée avec Python 3.13.3 (cohérence système)
- **Badges environnement** : Détection auto PREPROD/PROD avec affichage discret
- **Logs Loguru** : Fonctionnels dans `~/mangetamain/10_prod/logs/` (relatifs)

### Infrastructure évolutive

**V01-V04** : Base preprod opérationnelle (30/09/2025)  
**V05 (Production séparée)** : Environnement production dédié + badges environnement

## Architecture technique mise à jour

```
mangetamain/
├── 00_preprod/                     # Développement
│   ├── src/mangetamain_analytics/
│   │   └── main.py                 # App avec badges environnement
│   ├── data/mangetamain.duckdb     # Base analytique (20MB)
│   ├── logs/                       # Loguru (app + errors)
│   └── .venv/                      # Env Python (uv)
├── 10_prod/                        # Production ✨ NOUVEAU
│   ├── streamlit/
│   │   └── main.py                 # App production (badges intégrés)
│   ├── data/mangetamain.duckdb     # Base production (20MB)
│   ├── logs/                       # Logs production (relatifs)
│   ├── pyproject.toml              # Config corrigée (packages streamlit)
│   ├── uv.lock                     # Dépendances lockées
│   └── .venv/                      # Env production (Python 3.13.3)
├── 30_docker/                      # Orchestration
│   ├── docker-compose.yml          # Preprod (legacy)
│   └── docker-compose-prod.yml     # Production ✨ NOUVEAU
└── 90_doc/                         # Documentation V01-V05
```

## Nouveautés V05

### 1. Environnement production séparé
- **Structure distincte** : `10_prod/` avec organisation `streamlit/main.py`
- **Configuration corrigée** : `pyproject.toml` sans packaging complexe
- **Logs isolés** : Répertoire `logs/` dédié à la production
- **Base de données** : Copie indépendante du dataset

### 2. Docker Compose production aligné
- **Python cohérent** : Image `python:3.13.3-slim` (identique au système)
- **Volumes adaptés** : Pointage vers `../10_prod/` au lieu de `../00_preprod/`
- **Structure corrigée** : `streamlit/main.py` au lieu de `src/mangetamain_analytics/main.py`
- **Réseau dédié** : `mangetamain-prod-network`

### 3. Badges environnement intelligents
- **Détection automatique** : Via répertoire courant et présence `/.dockerenv`
- **Affichage discret** : Bas de sidebar, fond gris (#6c757d)
- **Différenciation claire** : 🔧 PREPROD vs 🚀 PRODUCTION
- **Style adaptatif** : Petit format, texte blanc, marges réduites

## Métriques V05

- **Temps développement V05** : 2h (environnement production + badges)
- **Environnements séparés** : 2 (preprod + production indépendants)
- **Docker aligné** : Python 3.13.3 cohérent système ↔ conteneur  
- **Code badges** : +50 lignes (détection + affichage discret)
- **Configuration corrigée** : pyproject.toml simplifié fonctionnel

## Architecture des environnements

| Environnement | Python | Chemin app | Docker | Badge | Logs |
|---------------|--------|------------|--------|-------|------|
| Preprod | 3.13.3 | `src/mangetamain_analytics/main.py` | compose.yml | 🔧 PREPROD | `00_preprod/logs/` |
| Production | 3.13.3 | `streamlit/main.py` | compose-prod.yml | 🚀 PRODUCTION | `10_prod/logs/` |
| Docker Prod | 3.13.3 | `/app/streamlit/main.py` | mange_prod | 🚀 PROD (Docker) | Volume mappé |

## Accès mis à jour

- **Preprod direct** : http://192.168.80.210:8501 (si lancé manuellement)
- **Production direct** : http://192.168.80.210:8502 (si lancé manuellement)  
- **Docker production** : http://192.168.80.210:8501 (conteneur mange_prod)
- **Public HTTPS** : https://mangetamain.lafrance.io/ (reverse proxy)

## Évolutions V05

### Structure modulaire
- **Environnements séparés** : Développement et production indépendants
- **Configuration adaptée** : Structure de projet différente par environnement
- **Logs isolés** : Chaque environnement a ses propres logs
- **Docker optimisé** : Image et configuration cohérentes

### Interface utilisateur
- **Badges discrets** : Identification environnement sans surcharge visuelle
- **Détection intelligente** : Automatique selon contexte d'exécution
- **Style cohérent** : Gris neutre, placement bas sidebar

## Prochaines étapes post-V05

1. **Tests environnement** : Validation badges dans tous les contextes
2. **CI/CD séparé** : Pipeline distinct preprod → production
3. **Monitoring différentiel** : Métriques par environnement
4. **Documentation utilisateur** : Guide badges et environnements
5. **Backup différentiel** : Stratégie données preprod vs production

## Contact technique V05

**Environnement production** : Opérationnel avec détection automatique via badges. Docker aligné Python 3.13.3. Logs isolés fonctionnels. Structure `streamlit/main.py` optimisée.

**Configuration finale** : 2 environnements indépendants (preprod + production) avec identification visuelle automatique et infrastructure Docker cohérente.

**Status badges** : Détection automatique opérationnelle - PREPROD (gris), PRODUCTION (gris), Docker (auto-détection /.dockerenv).
