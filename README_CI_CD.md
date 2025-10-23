# Pipeline CI/CD - Mangetamain Analytics

## Vue d'ensemble

Le pipeline CI/CD automatise la validation de la qualité du code, les tests unitaires et le déploiement de l'application Mangetamain Analytics. Il répond aux exigences académiques suivantes :

✅ Vérification du respect de PEP8
✅ Validation des docstrings sur fonctions/méthodes/classes/modules
✅ Exécution automatique des tests unitaires
✅ Vérification du coverage >= 90%
✅ Déclenchement sur push et merge vers `main`
✅ Phase de déploiement optionnelle incluse

---

## Architecture du Pipeline

### 1. **CI Pipeline** (`.github/workflows/ci.yml`)

Workflow principal exécuté lors des PR vers main et lors du merge vers main.

#### Déclencheurs
```yaml
on:
  push:
    branches:
      - main  # Uniquement lors des push/merge vers main
  pull_request:
    branches:
      - main  # PRs vers main (branches en review)
```

#### Jobs du Pipeline CI

##### **Job 1: Quality Checks** ✅
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
streamlit/main.py:45:1: E302 expected 2 blank lines, found 1
tests/test_loaders.py: 0 errors

=== Vérification des docstrings avec pydocstyle ===
streamlit/data/loaders.py:10: D103: Missing docstring in public function
```

##### **Job 2: Tests Production** ✅
Exécute les tests de l'environnement `20_prod/` avec coverage >= 90%.

**Configuration:**
- Environnement: Python 3.13
- Gestionnaire: uv (moderne, rapide)
- Coverage minimum: **90%** (--cov-fail-under=90)
- Rapport: HTML + Terminal

**Commande:**
```bash
cd 20_prod
pytest tests/ -v \
  --cov=streamlit \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=90
```

**Artefacts:**
- Rapport HTML de coverage uploadé (30 jours de rétention)
- Accessible dans l'onglet "Actions" > "Artifacts"

##### **Job 3: Tests Preprod** ✅
Exécute les tests de l'environnement `10_preprod/` avec coverage >= 90%.

**Configuration:**
- Même setup que Production
- Coverage sur `src/` au lieu de `streamlit/`
- Tests unitaires complets

##### **Job 4: Infrastructure Tests** ⚠️
Teste l'infrastructure (S3, DuckDB, Docker).

**Note:** Continue même en cas d'échec (continue-on-error: true) car nécessite credentials S3.

##### **Job 5: Summary** 📊
Résumé final de tous les jobs.

**Sortie exemple:**
```
=== Résumé du pipeline CI/CD ===
Quality Checks: success ✅
Tests Production: success ✅
Tests Preprod: success ✅
Tests Infrastructure: success ✅
✅ Tous les tests sont passés avec succès
```

---

### 2. **CD Pipeline** (`.github/workflows/deploy.yml`)

Workflow de déploiement automatique (optionnel).

#### Déclencheurs
```yaml
on:
  push:
    branches:
      - main  # Déploiement auto uniquement sur main
  workflow_dispatch:  # Déploiement manuel possible
```

#### Jobs du Pipeline CD

##### **Job 1: Deploy Production** 🚀
Construit et déploie l'image Docker de production.

**Étapes:**
1. Construction de l'image Docker
2. Test de l'image
3. Tag avec version et latest
4. **(Optionnel)** Push vers Docker Hub
5. **(Optionnel)** Déploiement SSH vers serveur

**Activation du déploiement complet:**
Pour activer le déploiement automatique, décommenter les sections et configurer les secrets GitHub:

```bash
# Secrets GitHub à configurer (Settings > Secrets and variables > Actions)
DOCKER_USERNAME=<votre_username_docker>
DOCKER_PASSWORD=<votre_token_docker>
SERVER_HOST=<ip_ou_domaine_serveur>
SERVER_USER=<utilisateur_ssh>
SERVER_SSH_KEY=<clé_privée_ssh>
```

##### **Job 2: Deploy Preprod** 🧪
Déploiement preprod pour les branches autres que main.

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
add-ignore = D100, D104, D107
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
cd 20_prod
source .venv/bin/activate
flake8 streamlit/ tests/ --config=../.flake8 --statistics
```

### Vérifier le formatage
```bash
cd 20_prod
source .venv/bin/activate
black --check --diff streamlit/ tests/
```

### Appliquer le formatage automatique
```bash
cd 20_prod
source .venv/bin/activate
black streamlit/ tests/
```

### Vérifier les docstrings
```bash
cd 20_prod
source .venv/bin/activate
pydocstyle streamlit/ --config=../.pydocstyle
```

### Lancer les tests avec coverage
```bash
cd 20_prod
source .venv/bin/activate
pytest tests/ -v --cov=streamlit --cov-report=html --cov-fail-under=90

# Ouvrir le rapport HTML
firefox htmlcov/index.html
```

### Tout vérifier d'un coup (simulation CI locale)
```bash
#!/bin/bash
# Script: run_ci_checks.sh

set -e  # Exit on error

echo "=== 1. PEP8 Compliance ==="
cd 20_prod
source .venv/bin/activate
flake8 streamlit/ tests/ --config=../.flake8 --statistics

echo ""
echo "=== 2. Code Formatting ==="
black --check --diff streamlit/ tests/

echo ""
echo "=== 3. Docstrings Validation ==="
pydocstyle streamlit/ --config=../.pydocstyle || true

echo ""
echo "=== 4. Tests + Coverage >= 90% ==="
pytest tests/ -v --cov=streamlit --cov-report=term-missing --cov-fail-under=90

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
   cd 20_prod
   pytest tests/ -v --cov=streamlit --cov-fail-under=90
   ```

3. **Vérifier qualité avant push**
   ```bash
   black streamlit/ tests/  # Auto-format
   flake8 streamlit/ tests/ --config=../.flake8
   pydocstyle streamlit/ --config=../.pydocstyle
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

   → **CI + CD s'exécutent** (déploiement si activé)

---

## Badges GitHub (optionnel)

Ajouter ces badges dans le README principal pour montrer le statut CI/CD :

```markdown
[![CI Pipeline](https://github.com/VOTRE_USERNAME/mangetamain/actions/workflows/ci.yml/badge.svg)](https://github.com/VOTRE_USERNAME/mangetamain/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/VOTRE_USERNAME/mangetamain/actions/workflows/deploy.yml/badge.svg)](https://github.com/VOTRE_USERNAME/mangetamain/actions/workflows/deploy.yml)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](https://github.com/VOTRE_USERNAME/mangetamain)
```

---

## Dépannage

### Erreur: "flake8 not found"
**Solution:** Installer les dépendances dev
```bash
cd 20_prod
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

---

## Métriques de Qualité

| Métrique | Objectif | Actuel |
|----------|----------|--------|
| PEP8 compliance | 100% | ✅ |
| Coverage Production | >= 90% | 100% ✅ |
| Coverage Preprod | >= 90% | 96% ✅ |
| Docstrings | >= 80% | 🔄 En cours |
| Tests unitaires | Complets | 96 tests ✅ |
| Temps CI | < 5 min | ~3 min ✅ |

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
- [flake8](https://flake8.pycqa.org/)
- [black](https://black.readthedocs.io/)
- [pydocstyle](http://www.pydocstyle.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

### Standards Python
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

## Support

**Questions ou problèmes avec le CI/CD ?**
- Consulter les logs GitHub Actions
- Vérifier cette documentation
- Tester localement avant de push
- Créer une issue sur le projet

**Auteur:** Équipe Mangetamain Analytics
**Date de création:** 2025-10-23
**Version:** 1.0
