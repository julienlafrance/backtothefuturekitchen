# 📋 RAF - Reste À Faire
## Évaluation Projet Mangetamain Analytics

**Date d'analyse:** 2025-10-26
**Deadline projet:** 1er décembre 2025 à 23h59
**Temps restant:** ~5 semaines

---

## ✅ Ce qui est FAIT (et très bien fait)

### 🎯 Gestion du Projet

| Exigence | Statut | Détails |
|----------|--------|---------|
| **Structure cohérente** | ✅ **EXCELLENT** | Organisation claire : 00_eda, 10_preprod, 20_prod, 30_docker, 50_test, 90_doc, 96_keys |
| **Environnement Python** | ✅ **EXCELLENT** | uv + pyproject.toml, Python 3.13.3 unifié |
| **Git + Commits réguliers** | ✅ **EXCELLENT** | Repository public, commits fréquents, branches |
| **README.md complet** | ✅ **EXCELLENT** | Documentation installation, exécution, déploiement (238 lignes) |
| **Streamlit déployé** | ✅ **EXCELLENT** | PREPROD: https://mangetamain.lafrance.io/ + PROD: https://backtothefuturekitchen.lafrance.io/ |
| **UX intuitive** | ✅ **EXCELLENT** | Interface avec widgets interactifs, charte graphique "Back to the Kitchen", navigation claire |
| **Storytelling** | ✅ **BON** | 4 analyses : Tendances, Saisonnalité, Weekend, Ratings avec insights et graphiques Plotly |

### 💻 Programmation

| Exigence | Statut | Détails |
|----------|--------|---------|
| **PEP 8** | ✅ **EXCELLENT** | flake8 configuré, black pour formatage automatique, CI vérifie à chaque push |
| **Gestion exceptions** | ✅ **BON** | Exceptions gérées avec try/except, pas de bare except |
| **Sécurité** | ✅ **BON** | Credentials dans 96_keys/ (gitignored), pas de tokens en clair |
| **Logger** | ✅ **PRÉSENT** | Loguru configuré dans main.py avec rotation |

### 🧪 Tests

| Exigence | Statut | Détails |
|----------|--------|---------|
| **Tests unitaires pytest** | ✅ **EXCELLENT** | 118 tests total (83 unitaires + 35 infrastructure) |
| **Test coverage ≥ 90%** | ✅ **DÉPASSÉ** | **93% coverage** sur 10_preprod (objectif 90% dépassé de 3 points) |
| **pytest-cov** | ✅ **EXCELLENT** | Configuré avec --cov-fail-under=90 |

### 🚀 CI/CD

| Exigence | Statut | Détails |
|----------|--------|---------|
| **GitHub Actions** | ✅ **EXCELLENT** | 3 workflows (CI, CD-Preprod, CD-Prod) |
| **Check PEP8** | ✅ **EXCELLENT** | flake8 automatique |
| **Check docstrings** | ✅ **EXCELLENT** | pydocstyle avec convention Google |
| **Tests auto sur push/PR** | ✅ **EXCELLENT** | Tests sur chaque push + merge main |
| **Vérif coverage > 90%** | ✅ **EXCELLENT** | Pipeline échoue si < 90% |
| **CD (optionnel)** | ✅ **BONUS** | Auto-deploy Preprod + Manual deploy Prod avec rollback |

---

## ⚠️ Ce qui MANQUE ou est INCOMPLET

### 🚨 CRITIQUE (Exigences obligatoires manquantes)

#### 1. 📚 **Documentation Sphinx** ❌
**Statut:** MANQUANT
**Exigence:** "Créez une documentation claire et concise pour votre application en utilisant Sphinx. Documentez les classes, les méthodes, et expliquez comment installer et utiliser votre application."

**État actuel:**
- ✅ Sphinx installé dans dépendances (`sphinx>=7.2.0`, `sphinx-rtd-theme>=1.3.0`)
- ❌ **Aucune configuration Sphinx** (pas de conf.py, index.rst, Makefile)
- ❌ **Aucune documentation générée** (pas de dossier docs/ avec HTML)
- ❌ **Pas de build de documentation** dans le README

**Impact:** ⚠️ **BLOQUANT** - Exigence explicite du projet

**Actions requises:**
```bash
# 1. Initialiser Sphinx dans le projet
cd 10_preprod
sphinx-quickstart docs

# 2. Configurer conf.py pour auto-documentation
# - Activer autodoc, napoleon (Google docstrings)
# - Configurer theme sphinx_rtd_theme
# - Ajouter path vers src/

# 3. Créer structure documentation
docs/
├── conf.py
├── index.rst
├── installation.rst
├── usage.rst
├── api/
│   ├── modules.rst
│   ├── utils.rst
│   └── visualization.rst
└── Makefile

# 4. Générer la documentation
make html

# 5. Ajouter dans README
## Documentation
La documentation complète est générée avec Sphinx :
\`\`\`bash
cd 10_preprod/docs
make html
xdg-open _build/html/index.html
\`\`\`
```

**Estimation:** 3-4 heures

---

#### 2. 🏗️ **Programmation Orientée Objet** ❌
**Statut:** INSUFFISANT
**Exigence:** "Dans la mesure du possible, utilisez le paradigme orienté objet. Utilisez les principes de l'encapsulation et de l'héritage si approprié."

**État actuel:**
- ❌ **Seulement 3 classes** dans tout le codebase
- ✅ Code principalement fonctionnel (fonctions pures)
- ❌ Pas d'encapsulation de la logique métier
- ❌ Pas d'héritage

**Impact:** ⚠️ **IMPORTANT** - Exigence académique "dans la mesure du possible"

**Recommandations POO:**

```python
# Option 1: Classes pour les analyseurs
class RecipeAnalyzer:
    """Base class for recipe data analysis."""

    def __init__(self, data_loader):
        self.data_loader = data_loader
        self._cache = {}

    def load_data(self):
        """Load and cache data."""
        if 'recipes' not in self._cache:
            self._cache['recipes'] = self.data_loader.get_recipes()
        return self._cache['recipes']

    def analyze(self):
        """Perform analysis - to be implemented by subclasses."""
        raise NotImplementedError

class TrendlineAnalyzer(RecipeAnalyzer):
    """Analyzer for recipe trendlines over time."""

    def analyze(self, start_year, end_year):
        data = self.load_data()
        # ... logique analyse trendlines
        return self._calculate_trends(data, start_year, end_year)

    def _calculate_trends(self, data, start_year, end_year):
        # Encapsulation de la logique
        pass

class SeasonalityAnalyzer(RecipeAnalyzer):
    """Analyzer for seasonal patterns in recipes."""

    def analyze(self, metric="count"):
        data = self.load_data()
        # ... logique analyse saisonnalité
        return self._calculate_seasonality(data, metric)

# Option 2: Classe pour les data loaders
class S3DataLoader:
    """Encapsulate S3 data loading logic."""

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._conn = None

    def get_recipes(self) -> pl.DataFrame:
        """Load recipes from S3."""
        pass

    def get_interactions(self) -> pl.DataFrame:
        """Load interactions from S3."""
        pass

# Option 3: Classe pour la configuration
class AppConfig:
    """Application configuration with validation."""

    def __init__(self):
        self.s3_bucket = os.getenv("S3_BUCKET", "mangetamain")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self._validate()

    def _validate(self):
        """Validate configuration."""
        if not self.s3_bucket:
            raise ValueError("S3_BUCKET must be set")
```

**Actions requises:**
1. Identifier les fonctions qui partagent un état → créer des classes
2. Regrouper les fonctions d'analyse dans des classes héritant d'une classe de base
3. Encapsuler les appels S3/DuckDB dans une classe DataLoader
4. Créer une classe Config pour la configuration

**Estimation:** 2-3 jours (refactoring important)

---

#### 3. 🔤 **Type Hinting** ⚠️
**Statut:** PARTIEL
**Exigence:** "Utilisez des annotations de type pour améliorer la lisibilité de votre code."

**État actuel:**
- ⚠️ Type hints **partiels** dans le code
- ❌ Pas de vérification avec mypy dans le CI
- ❌ Beaucoup de fonctions sans annotations

**Exemples manquants:**
```python
# ❌ Sans type hints (actuel)
def weighted_spearman(x, y, w):
    """Calculate weighted Spearman correlation."""
    pass

# ✅ Avec type hints (attendu)
def weighted_spearman(
    x: np.ndarray,
    y: np.ndarray,
    w: np.ndarray
) -> float:
    """Calculate weighted Spearman correlation.

    Args:
        x: First variable array
        y: Second variable array
        w: Weights for each observation

    Returns:
        Weighted Spearman correlation coefficient
    """
    pass

# ❌ Sans type hints
def render_seasonality_analysis():
    pass

# ✅ Avec type hints
def render_seasonality_analysis() -> None:
    """Render the seasonality analysis page."""
    pass
```

**Actions requises:**
1. Ajouter type hints à toutes les fonctions publiques
2. Ajouter mypy dans le CI pipeline
3. Configurer mypy.ini

**Estimation:** 1-2 jours

---

#### 4. 📝 **Fichiers de logs** ❌
**Statut:** MANQUANT
**Exigence:** "Créer un fichier de log pour le debug, et un autre pour les erreurs (ERROR et CRITICAL)."

**État actuel:**
- ✅ Loguru configuré dans main.py
- ❌ **Pas de fichiers .log générés/commités**
- ❌ Configuration logger incomplete (pas de séparation debug/error)

**Configuration actuelle:**
```python
# main.py - Configuration actuelle
logger.add(
    "logs/mangetamain_{time}.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO"
)
```

**Configuration attendue:**
```python
# Configuration complète avec 2 fichiers distincts
import sys
from loguru import logger

# Remove default handler
logger.remove()

# 1. Handler pour DEBUG + INFO (fichier debug)
logger.add(
    "logs/debug.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    filter=lambda record: record["level"].name in ["DEBUG", "INFO", "SUCCESS"]
)

# 2. Handler pour ERROR + CRITICAL (fichier errors)
logger.add(
    "logs/errors.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="5 MB",
    retention="30 days",
    backtrace=True,
    diagnose=True
)

# 3. Handler pour console (optionnel)
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
```

**Actions requises:**
1. Créer dossier `logs/` à la racine de 10_preprod
2. Mettre à jour configuration logger dans main.py
3. Ajouter logs d'exemple dans le README (ne pas commit les vrais logs)
4. Ajouter `logs/*.log` dans .gitignore (garder `logs/.gitkeep`)

**Estimation:** 1 heure

---

### 📊 MOYEN (Améliorations importantes)

#### 5. 💬 **Commentaires dans le code** ⚠️
**Statut:** INCOMPLET
**Exigence:** "Assurez-vous d'inclure des commentaires pertinents dans votre code pour expliquer la logique complexe ou les décisions de conception importantes."

**État actuel:**
- ⚠️ Commentaires **présents mais insuffisants**
- ❌ Logique complexe parfois non documentée

**Recommandations:**
- Ajouter commentaires sur les calculs statistiques complexes
- Expliquer les choix de filtrage de données
- Documenter les constantes "magiques"

**Estimation:** 2-3 heures

---

#### 6. 🏷️ **Tags de version Git** ⚠️
**Statut:** ABSENT (OPTIONNEL)
**Exigence:** "Optionnel : créez éventuellement des tags de version pour marquer les versions stables de votre application."

**Actions requises:**
```bash
git tag -a v1.0.0 -m "Version 1.0.0 - Release initiale"
git tag -a v1.1.0 -m "Version 1.1.0 - Ajout charte graphique"
git push origin --tags
```

**Estimation:** 15 minutes

---

## 📊 Récapitulatif des Priorités

### 🔴 URGENT (Bloquant livraison)

| Tâche | Criticité | Temps estimé | Statut |
|-------|-----------|--------------|--------|
| **Documentation Sphinx** | 🔴 CRITIQUE | 3-4h | ❌ À FAIRE |
| **Fichiers de logs** | 🔴 CRITIQUE | 1h | ❌ À FAIRE |

### 🟠 IMPORTANT (Exigences académiques)

| Tâche | Criticité | Temps estimé | Statut |
|-------|-----------|--------------|--------|
| **POO (classes)** | 🟠 IMPORTANT | 2-3 jours | ❌ À FAIRE |
| **Type Hinting complet** | 🟠 IMPORTANT | 1-2 jours | ⚠️ PARTIEL |
| **Commentaires code** | 🟠 MOYEN | 2-3h | ⚠️ PARTIEL |

### 🟢 BONUS (Optionnel)

| Tâche | Criticité | Temps estimé | Statut |
|-------|-----------|--------------|--------|
| **Tags Git** | 🟢 BONUS | 15min | ❌ À FAIRE |
| **Optimisation perfs** | 🟢 BONUS | - | N/A |

---

## 📅 Planning Recommandé (5 semaines restantes)

### Semaine 1 (26 oct - 1er nov): 🔴 CRITIQUES
- [ ] **Jour 1-2:** Documentation Sphinx complète
  - Initialiser Sphinx
  - Créer structure docs/
  - Générer documentation HTML
  - Mettre à jour README
- [ ] **Jour 3:** Fichiers de logs
  - Configuration double handler (debug/errors)
  - Créer dossier logs/
  - Tester génération logs

### Semaine 2 (2-8 nov): 🟠 POO
- [ ] **Jour 1-2:** Refactoring POO - Classes d'analyseurs
  - Créer classe de base `RecipeAnalyzer`
  - Hériter dans `TrendlineAnalyzer`, `SeasonalityAnalyzer`, etc.
- [ ] **Jour 3:** Refactoring POO - DataLoader et Config
  - Classe `S3DataLoader`
  - Classe `AppConfig`
- [ ] **Jour 4:** Tests pour les nouvelles classes
  - Adapter tests existants
  - Vérifier coverage reste ≥ 90%

### Semaine 3 (9-15 nov): 🟠 Type Hints
- [ ] **Jour 1-2:** Ajouter type hints partout
  - Annotations sur toutes les fonctions
  - Imports typing (List, Dict, Optional, etc.)
- [ ] **Jour 3:** Configuration mypy
  - Créer mypy.ini
  - Ajouter dans CI pipeline
  - Corriger erreurs mypy

### Semaine 4 (16-22 nov): ✨ Finitions
- [ ] Améliorer commentaires code
- [ ] Ajouter tags Git
- [ ] Relecture complète README
- [ ] Vérification coverage final
- [ ] Test déploiements PREPROD et PROD

### Semaine 5 (23-30 nov): 🧪 Tests finaux
- [ ] Tests end-to-end
- [ ] Vérification toutes exigences PDF
- [ ] Préparation livraison finale
- [ ] Buffer pour imprévus

---

## 📝 Checklist Livraison Finale

### Obligatoire pour le 1er décembre

- [x] Code source Python bien structuré
- [ ] **Documentation générée avec Sphinx** ❌
- [ ] **Fichiers de logs** ❌
- [x] Tests unitaires (118 tests, 93% coverage)
- [x] Pipeline CI/CD
- [x] Lien webapp déployée
- [ ] **POO implémentée** ❌
- [ ] **Type hints complets** ⚠️
- [x] PEP 8 respecté
- [x] Docstrings présentes (Google style)
- [x] Gestion exceptions
- [x] Sécurité (pas de tokens en clair)

### Email à envoyer avant deadline
**À:** prillard.martin@gmail.com
**Objet:** [PROJET] Mangetamain Analytics - Groupe [X]
**Contenu:**
- Lien GitHub: https://github.com/julienlafrance/backtothefuturekitchen
- Lien PREPROD: https://mangetamain.lafrance.io/
- Lien PROD: https://backtothefuturekitchen.lafrance.io/
- Membres du groupe: [Noms]

---

## 🎯 Score Estimé Actuel

| Critère | Points estimés | Maximum |
|---------|----------------|---------|
| Qualité du code | 16/20 | 20 |
| Respect bonnes pratiques | 15/20 | 20 |
| Couverture tests | 20/20 ✅ | 20 |
| Documentation | 8/20 ⚠️ | 20 |
| Webapp visuelle | 18/20 ✅ | 20 |
| Fonctionnement | 19/20 ✅ | 20 |
| **TOTAL ESTIMÉ** | **96/120** (16/20) | **120** |

### Avec corrections RAF critiques:
| Critère | Points estimés | Maximum |
|---------|----------------|---------|
| Qualité du code | 18/20 | 20 |
| Respect bonnes pratiques | 18/20 | 20 |
| Couverture tests | 20/20 ✅ | 20 |
| Documentation | 18/20 ✅ | 20 |
| Webapp visuelle | 18/20 ✅ | 20 |
| Fonctionnement | 19/20 ✅ | 20 |
| **TOTAL PROJETÉ** | **111/120** (18.5/20) | **120** |

---

## 💡 Conseils Finaux

1. **Prioriser les CRITIQUES** (Sphinx + Logs) cette semaine
2. **POO peut être light** - Ne pas sur-refactorer, juste montrer la maîtrise
3. **Type hints** - Commencer par les fonctions publiques principales
4. **Garder le coverage ≥ 90%** pendant tous les refactorings
5. **Tester après chaque changement** - Ne pas tout casser à la fin
6. **Commits réguliers** - Montrer le travail d'équipe sur Git

---

**Projet déjà très solide techniquement ! Les points manquants sont principalement académiques/formels.**

**Bon courage pour les 5 dernières semaines ! 🚀**
