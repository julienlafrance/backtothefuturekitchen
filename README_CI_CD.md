# Pipeline CI/CD - Mangetamain Analytics

## Vue d'ensemble

Le pipeline CI/CD automatise la validation de la qualité du code, les tests unitaires et le déploiement de l'application Mangetamain Analytics. Il répond aux exigences académiques suivantes :

✅ Vérification du respect de PEP8
✅ Validation des docstrings sur fonctions/méthodes/classes/modules
✅ Exécution automatique des tests unitaires
✅ Vérification du coverage >= 90%
✅ Déclenchement sur push et merge vers `main`
✅ Phase de déploiement automatisée avec runner self-hosted

---

## Architecture du Pipeline

### Pipeline Séquentiel

```
┌─────────────────────────────────────────────────────────┐
│  1. CI Pipeline - Quality & Tests                      │
│     (GitHub-hosted runners)                             │
│     - PEP8, Black, Docstrings, Tests                    │
│     - Déclenché sur push/PR vers main                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼ (si succès)
┌─────────────────────────────────────────────────────────┐
│  2. CD Preprod - Auto Deploy                           │
│     (Self-hosted runner sur VM dataia)                  │
│     - Pull code, restart container, health check        │
│     - Notifications Discord                             │
│     - URL: https://mangetamain.lafrance.io/             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. CD Production - Manuel avec confirmation            │
│     (Self-hosted runner sur VM dataia)                  │
│     - Backup, deploy_preprod_to_prod.sh, restart        │
│     - Notifications Discord avec rollback si échec      │
│     - URL: https://backtothefuturekitchen.lafrance.io/  │
└─────────────────────────────────────────────────────────┘
```

**Avantage clé**: Si le CI échoue, le déploiement PREPROD est automatiquement bloqué.

---

## 1. CI Pipeline (`.github/workflows/ci.yml`)

Workflow principal exécuté lors des PR vers main et lors du merge vers main.

### Déclencheurs
```yaml
on:
  push:
    branches:
      - main  # Uniquement lors des push/merge vers main
  pull_request:
    branches:
      - main  # PRs vers main (branches en review)
```

### Jobs du Pipeline CI

#### **Job 1: Quality Checks** ✅
Vérifie la qualité du code selon les standards Python.

**Checks effectués:**
- **PEP8 compliance** (flake8)
  - Ligne max: 88 caractères (compatibilité Black)
  - Exclusions intelligentes (venv, cache, credentials)
  - Configuration: `.flake8`

- **Code formatting** (black)
  - Vérification du formatage automatique
  - Style cohérent dans tout le projet

- **Docstrings validation** (pydocstyle)
  - Convention: Google docstring format
  - Vérifie les docstrings sur classes, fonctions, méthodes
  - Configuration: `.pydocstyle`
  - **Mode: warning** (continue-on-error: true)

- **Type checking** (mypy) - optionnel
  - Vérification des types Python
  - **Mode: warning** (continue-on-error: true)

**Exemple de sortie:**
```
=== Vérification PEP8 avec flake8 ===
src/mangetamain_analytics/main.py:45:1: E302 expected 2 blank lines, found 1
tests/test_loaders.py: 0 errors

=== Vérification des docstrings avec pydocstyle ===
src/data/loaders.py:10: D103: Missing docstring in public function
```

#### **Job 2: Tests Preprod** ✅
Exécute les tests de l'environnement `10_preprod/` avec coverage >= 90%.

**Configuration:**
- Environnement: Python 3.13
- Gestionnaire: uv (moderne, rapide)
- Coverage minimum: **90%** (--cov-fail-under=90)
- Rapport: HTML + Terminal

**Commande:**
```bash
cd 10_preprod
pytest tests/ -v \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=90
```

**Artefacts:**
- Rapport HTML de coverage uploadé (30 jours de rétention)
- Accessible dans l'onglet "Actions" > "Artifacts"

**Note importante:** Les tests PROD sont désactivés car `20_prod/` est maintenant un **artifact généré** par le script de déploiement. PREPROD (`10_preprod/`) est la seule source de vérité dans git.

#### **Job 3: Infrastructure Tests** ⚠️
Teste l'infrastructure (S3, DuckDB, Docker).

**Note:** Continue même en cas d'échec (continue-on-error: true) car nécessite credentials S3.

#### **Job 4: Summary** 📊
Résumé final de tous les jobs.

**Sortie exemple:**
```
=== Résumé du pipeline CI/CD ===
Quality Checks: success ✅
Tests Preprod: success ✅
Tests Infrastructure: success ✅
✅ Tous les tests sont passés avec succès
```

---

## 2. CD Pipeline - Preprod (`.github/workflows/cd-preprod.yml`)

Workflow de déploiement automatique vers PREPROD.

### Déclencheurs
```yaml
on:
  workflow_run:
    workflows: ["CI Pipeline - Quality & Tests"]
    types:
      - completed
    branches:
      - main
  workflow_dispatch:  # Permet déclenchement manuel
```

**Comportement:** Ne se déclenche QUE si le CI a réussi (`if: github.event.workflow_run.conclusion == 'success'`).

### Job: Deploy Preprod

**Runner:** `runs-on: self-hosted` (VM dataia, pas besoin de VPN)

**Étapes:**
1. 📢 **Notification Discord** - Déploiement démarré
2. 🔄 **Pull latest code** - `git reset --hard origin/main`
3. 🐳 **Restart container** - `docker-compose restart`
4. ⏳ **Wait 60s** - Temps pour Streamlit de démarrer
5. 🔍 **Health check** - 10 tentatives sur https://mangetamain.lafrance.io/
6. ✅ **Notification Discord** - Succès ou échec

**Exemple de notification Discord:**
```
✅ **Déploiement Preprod réussi!**
🌐 URL: https://mangetamain.lafrance.io/
📦 Commit: `abc1234`
💬 Fix bug in authentication
🕐 2025-10-25 14:30:15
```

---

## 3. CD Pipeline - Production (`.github/workflows/cd-prod.yml`)

Workflow de déploiement manuel vers PRODUCTION avec confirmation obligatoire.

### Déclencheurs
```yaml
on:
  workflow_dispatch:  # Déclenchement MANUEL uniquement
    inputs:
      confirm:
        description: 'Taper "DEPLOY" pour confirmer le déploiement en production'
        required: true
```

**Commande pour déclencher:**
```bash
# Méthode 1: GitHub Web UI
# Actions → CD - Production Deployment → Run workflow → Taper "DEPLOY"

# Méthode 2: GitHub CLI (recommandée)
gh workflow run cd-prod.yml -f confirm=DEPLOY --repo julienlafrance/backtothefuturekitchen
```

### Job: Deploy Production

**Runner:** `runs-on: self-hosted` (VM dataia)

**Condition:** `if: github.event.inputs.confirm == 'DEPLOY'`

**Étapes:**
1. 📢 **Notification Discord** - Déploiement PROD démarré
2. 💾 **Backup automatique** - Copie complète de `20_prod/` avec timestamp
3. 🔄 **Pull latest code** - `git reset --hard origin/main`
4. 🚀 **Exécution script** - `./deploy_preprod_to_prod.sh`
5. 🐳 **Restart container** - `docker-compose down && up` (nouveaux mounts)
6. ⏳ **Wait 90s** - Installation dépendances + démarrage Streamlit
7. 🔍 **Health check** - 10 tentatives sur https://backtothefuturekitchen.lafrance.io/
8. ✅/❌ **Notification Discord** - Résultat avec instructions rollback si échec

### Script de Déploiement

Le fichier `deploy_preprod_to_prod.sh` (63 lignes) effectue :

**Étapes du script:**
1. 💾 **Backup** de `20_prod/streamlit/` (si existe)
2. 🗑️ **Nettoyage** de `20_prod/` (garde .gitkeep)
3. 📋 **Copie 3 éléments** :
   - `streamlit/` (code source depuis `10_preprod/src/mangetamain_analytics/`)
   - `pyproject.toml`
   - `README.md`

**Pourquoi cette simplicité ?**
- Données chargées depuis **S3 Parquet** (pas de fichiers locaux)
- `uv.lock` régénéré automatiquement par `uv sync` dans le container
- PROD = artifact pur, PREPROD = source de vérité

**Exemple d'exécution:**
```bash
cd /home/dataia25/mangetamain
./deploy_preprod_to_prod.sh

# Sortie:
🚀 Déploiement PREPROD → PROD
================================
📦 Backup 20_prod/
✅ Backup → backups/prod_20251025_143012/streamlit/

🗑️  Nettoyage 20_prod/
✅ Répertoire nettoyé

📋 Copie PREPROD → PROD
✅ streamlit/ (code source)
✅ pyproject.toml
✅ README.md

✅ DÉPLOIEMENT TERMINÉ
================================
Backup  : backups/prod_20251025_143012
PROD    : /home/dataia25/mangetamain/20_prod

Prochaine étape: GitHub Actions redémarrera le container
```

---

## Configuration des Outils

### `.flake8` - Configuration PEP8
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = .git, __pycache__, .venv, build, dist, 96_keys
```

**Règles ignorées:**
- `E203`: Whitespace before ':' (conflit avec Black)
- `W503`: Line break before binary operator (style moderne)
- `E501`: Line too long (géré par Black)

### `.pydocstyle` - Configuration Docstrings
```ini
[pydocstyle]
convention = google
add-ignore = D100, D104, D107, D202, D205, D212, D415
```

**Convention:** Google docstring format
```python
def calculate_mean(values: list) -> float:
    """Calculate the mean of a list of values.

    Args:
        values: List of numeric values.

    Returns:
        The mean value as a float.

    Raises:
        ValueError: If values list is empty.
    """
    if not values:
        raise ValueError("Cannot calculate mean of empty list")
    return sum(values) / len(values)
```

**Erreurs ignorées:**
- `D100`: Module docstring manquant (flexibility)
- `D104`: Package docstring manquant
- `D107`: `__init__` docstring manquant
- `D202`, `D205`, `D212`, `D415`: Cosmetic (ajouté 2025-10-25)

### `pyproject.toml` - Configuration Tests
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=html --cov-fail-under=90"

[tool.coverage.run]
omit = [
    "*/main.py",      # UI Streamlit exclu
    "*/pages/*",      # Pages Streamlit exclues
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
]
```

---

## Utilisation Locale

### Vérifier PEP8
```bash
cd 10_preprod
source .venv/bin/activate
flake8 src/ tests/ --config=../.flake8 --statistics
```

### Vérifier le formatage
```bash
cd 10_preprod
source .venv/bin/activate
black --check --diff src/ tests/
```

### Appliquer le formatage automatique
```bash
cd 10_preprod
source .venv/bin/activate
black src/ tests/
```

### Vérifier les docstrings
```bash
cd 10_preprod
source .venv/bin/activate
pydocstyle src/ --config=../.pydocstyle
```

### Lancer les tests avec coverage
```bash
cd 10_preprod
source .venv/bin/activate
pytest tests/ -v --cov=src --cov-report=html --cov-fail-under=90

# Ouvrir le rapport HTML
firefox htmlcov/index.html
```

### Tout vérifier d'un coup (simulation CI locale)
```bash
#!/bin/bash
# Script: run_ci_checks.sh

set -e  # Exit on error

echo "=== 1. PEP8 Compliance ==="
cd 10_preprod
source .venv/bin/activate
flake8 src/ tests/ --config=../.flake8 --statistics

echo ""
echo "=== 2. Code Formatting ==="
black --check --diff src/ tests/

echo ""
echo "=== 3. Docstrings Validation ==="
pydocstyle src/ --config=../.pydocstyle || true

echo ""
echo "=== 4. Tests + Coverage >= 90% ==="
pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=90

echo ""
echo "✅ Tous les checks CI ont passé localement !"
```

---

## Workflow de Développement

### Cycle de développement standard

1. **Créer une branche de feature**
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```

2. **Développer et tester localement**
   ```bash
   # Écrire du code
   # Ajouter des tests
   cd 10_preprod
   pytest tests/ -v --cov=src --cov-fail-under=90
   ```

3. **Vérifier qualité avant push**
   ```bash
   black src/ tests/  # Auto-format
   flake8 src/ tests/ --config=../.flake8
   pydocstyle src/ --config=../.pydocstyle
   ```

4. **Push et création PR**
   ```bash
   git add .
   git commit -m "feat: ajout nouvelle fonctionnalité"
   git push origin feature/nouvelle-fonctionnalite
   ```

   → **CI s'exécute automatiquement** sur GitHub Actions

5. **Vérifier les résultats CI**
   - Aller sur GitHub > Actions
   - Vérifier que tous les jobs sont ✅
   - Corriger si nécessaire

6. **Merge vers main**
   ```bash
   # Via GitHub PR ou en local
   git checkout main
   git merge feature/nouvelle-fonctionnalite
   git push origin main
   ```

   → **CI + CD Preprod s'exécutent automatiquement**

   **Résultat:** Application déployée sur https://mangetamain.lafrance.io/ en 3-5 minutes

---

## Notifications Discord

### Configuration

**Secret GitHub:** `DISCORD_WEBHOOK_URL`
- Stocké dans: Settings → Secrets and variables → Actions
- Format: `https://discord.com/api/webhooks/{id}/{token}`

### Types de Notifications

#### Preprod - Démarrage
```
🚀 **Déploiement Preprod démarré**
📦 Commit: `abc1234`
💬 Message: Fix bug in login
👤 Par: julienlafrance
```

#### Preprod - Succès
```
✅ **Déploiement Preprod réussi!**
🌐 URL: https://mangetamain.lafrance.io/
📦 Commit: `abc1234`
💬 Fix bug in login
🕐 2025-10-25 14:30:15
```

#### Preprod - Échec
```
❌ **ÉCHEC Déploiement Preprod**
📦 Commit: `abc1234`
💬 Fix bug in login
⚠️ **Container dans état cassé - intervention manuelle requise**
📋 Vérifier les logs: `docker-compose -f docker-compose-preprod.yml logs`
👤 Commit par: julienlafrance
```

#### Production - Succès
```
✅ **Déploiement PRODUCTION réussi!**
🌐 URL: https://backtothefuturekitchen.lafrance.io/
📦 Commit: `def5678`
💬 New feature

Détails:
✅ Backup créé: `backups/prod/backup-20251025_143012`
✅ Script deploy_preprod_to_prod.sh exécuté
✅ Container redémarré (down && up)
✅ Health checks passés
✅ Données chargées depuis S3 Parquet

🕐 2025-10-25 14:35:42
👤 Déployé par: julienlafrance
```

#### Production - Échec (avec instructions rollback)
```
🚨 **ÉCHEC - Déploiement PRODUCTION**
❌ Health check échoué
📦 Commit tenté: `def5678`
💬 New feature
⚠️ **PRODUCTION POTENTIELLEMENT CASSÉE**

**Rollback manuel recommandé:**
```bash
ssh dataia
cd /home/dataia25/mangetamain/20_prod

# Restaurer le backup complet
rm -rf streamlit pyproject.toml README.md
cp -r backups/prod/backup-20251025_143012/streamlit .
cp backups/prod/backup-20251025_143012/pyproject.toml .
cp backups/prod/backup-20251025_143012/README.md .

# Redémarrer le container
cd /home/dataia25/mangetamain/30_docker
docker-compose -f docker-compose-prod.yml down
docker-compose -f docker-compose-prod.yml up -d
```

📂 Backup: `backups/prod/backup-20251025_143012`
🌐 Vérifier: https://backtothefuturekitchen.lafrance.io/
👤 Tenté par: julienlafrance
🕐 2025-10-25 14:37:23
```

---

## Performance et Optimisation

### Streamlit Caching

Toutes les fonctions de chargement de données utilisent `@st.cache_data` pour améliorer les performances :

```python
# Fichier: 10_preprod/src/mangetamain_analytics/data/cached_loaders.py

@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des recettes depuis S3...")
def get_recipes_clean():
    """Charge les recettes depuis S3 avec cache (1h)."""
    from mangetamain_data_utils.data_utils_recipes import load_recipes_clean
    return load_recipes_clean()

@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des ratings depuis S3...")
def get_ratings_longterm(min_interactions=100, return_metadata=False, verbose=False):
    """Charge les ratings pour analyse long-terme depuis S3 avec cache (1h)."""
    from mangetamain_data_utils.data_utils_ratings import (
        load_ratings_for_longterm_analysis,
    )
    return load_ratings_for_longterm_analysis(
        min_interactions=min_interactions,
        return_metadata=return_metadata,
        verbose=verbose,
    )
```

**Avantages:**
- ✅ Données chargées une seule fois par heure
- ✅ Navigation entre pages instantanée
- ✅ Pas de reload S3 inutile
- ✅ Spinner visible pendant le chargement

---

## Runner Self-Hosted

### Avantage Principal: Plus Besoin de VPN ! 🚀

**Avant (manuel):**
1. Connexion VPN
2. SSH vers dataia
3. cd /home/dataia25/mangetamain/10_preprod
4. git pull
5. docker-compose restart
6. Vérification manuelle
7. Déconnexion VPN

**Après (automatisé):**
1. `git push` → Déploiement automatique complet

**Gain:** 7 étapes manuelles → 1 simple push (⏱️ 5-10 min → 30 sec)

### Configuration

**Serveur:** VM dataia (accessible via VPN uniquement)
**Chemin:** `/home/dataia25/actions-runner/`
**User:** `dataia25`
**Service:** `systemd` (démarrage automatique)

**Workflows utilisant le runner:**
- `cd-preprod.yml` → `runs-on: self-hosted`
- `cd-prod.yml` → `runs-on: self-hosted`

**Vérification:**
```bash
# Sur dataia
systemctl status actions.runner.*

# Voir les logs
journalctl -u actions.runner.* -f
```

### Sécurité

**Protections:**
- ✅ Runner isolé sur VM VPN (pas d'accès public)
- ✅ User dédié non-root (dataia25)
- ✅ Secrets GitHub chiffrés
- ✅ Health checks automatiques (10 tentatives, retry 10s)
- ✅ Backup avant déploiement PROD
- ✅ Rollback manuel documenté en cas d'échec

---

## Dépannage

### Erreur: "flake8 not found"
**Solution:** Installer les dépendances dev
```bash
cd 10_preprod
uv pip install -e ".[dev]"
```

### Erreur: "Coverage < 90%"
**Solution:** Ajouter des tests ou exclure du code non-testable
```python
# Dans le code à exclure
def main():  # pragma: no cover
    st.title("Application")
```

### Erreur: "Docstring manquante"
**Solution:** Ajouter des docstrings Google-style
```python
def my_function():
    """Brief description of the function.

    Detailed description if needed.
    """
    pass
```

### CI échoue mais local fonctionne
**Raisons possibles:**
- Versions Python différentes (CI: 3.13, Local: autre)
- Fichiers non commités
- Dépendances manquantes dans `pyproject.toml`

**Solution:**
```bash
# Vérifier les fichiers non trackés
git status

# S'assurer que pyproject.toml est à jour
git add pyproject.toml
git commit -m "fix: mise à jour dépendances"
```

### CD Preprod bloqué
**Cause:** Le CI a échoué
**Solution:** Vérifier les logs du CI dans GitHub Actions, corriger les erreurs, re-push

### Notifications Discord ne fonctionnent pas
**Vérification:**
```bash
# Tester webhook manuellement
curl -H "Content-Type: application/json" \
  -d '{"content":"Test notification"}' \
  "DISCORD_WEBHOOK_URL"
```

---

## Métriques de Qualité

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| PEP8 compliance | 100% | ✅ 100% |
| Coverage Preprod | >= 90% | ✅ 96% |
| Tests unitaires | Complets | ✅ 22 tests |
| Temps CI | < 5 min | ✅ ~3 min |
| Temps CD Preprod | < 3 min | ✅ ~2 min |
| Temps CD Prod | < 5 min | ✅ ~4 min |

**Note:** Les tests PROD sont désactivés car `20_prod/` est un artifact généré automatiquement. PREPROD est la seule source de vérité.

---

## Évolutions Futures

### Court terme
- [ ] Améliorer coverage docstrings à 100%
- [ ] Activer mypy strict mode
- [ ] Ajouter pre-commit hooks locaux

### Moyen terme
- [ ] Intégration avec SonarQube/CodeClimate
- [ ] Tests de sécurité (bandit, safety)
- [ ] Tests de performance

### Long terme
- [ ] Déploiement Kubernetes
- [ ] Blue-Green deployment
- [ ] Monitoring automatisé (Prometheus/Grafana)

---

## Ressources

### Documentation officielle
- [GitHub Actions](https://docs.github.com/en/actions)
- [Self-Hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [flake8](https://flake8.pycqa.org/)
- [black](https://black.readthedocs.io/)
- [pydocstyle](http://www.pydocstyle.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)

### Standards Python
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

### Documentation Projet
- **Synthèse académique:** [SYNTHESE_CI_CD_ACADEMIC.md](SYNTHESE_CI_CD_ACADEMIC.md)
- **Runner + Discord:** [RUNNER_DISCORD_GUIDE.md](RUNNER_DISCORD_GUIDE.md)
- **Inventaire docs:** [INVENTAIRE_DOCUMENTATION_CI_CD.md](INVENTAIRE_DOCUMENTATION_CI_CD.md)
- **Conventions:** [CONVENTIONS.md](CONVENTIONS.md)

---

## Support

**Questions ou problèmes avec le CI/CD ?**
- Consulter les logs GitHub Actions
- Vérifier cette documentation
- Tester localement avant de push
- Vérifier les notifications Discord

**Auteur:** Équipe Mangetamain Analytics
**Date de création:** 2025-10-23
**Dernière mise à jour:** 2025-10-25
**Version:** 2.0 (Pipeline séquentiel + Runner self-hosted + Script simplifié)
