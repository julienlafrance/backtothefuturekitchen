# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Versionnement Sémantique](https://semver.org/lang/fr/).

---

## [1.1.0] - 2025-10-25

### ✨ Ajouté

#### Charte Graphique "Back to the Kitchen"
- **CSS Variables centralisées** dans `custom.css`
  - `:root` avec `--primary-color`, `--secondary-accent`, `--font-heading`, `--font-body`
  - Variables pour couleurs d'état : `--success-color`, `--warning-color`, `--error-color`, `--info-color`
  - Facilite la maintenance et la cohérence visuelle

#### Menu Sidebar Amélioré
- **Titre "ANALYSES"** avec classe CSS `analyses-title`
  - Police Michroma, couleur PRIMARY (#FF8C00)
  - Text-transform uppercase, letter-spacing 1px
- **Texte introductif** "Choisir une analyse :" avec classe `intro-text`
  - Police Inter, couleur TEXT (#F0F0F0)
- **Navigation avec 3 états** (inactif/hover/actif)
  - Inactif : Fond gris semi-transparent, bordure fine
  - Hover : Fond jaune transparent (10%), bordure jaune doré
  - Actif : Gradient orange → jaune, texte noir, shadow orange
- **Icônes Lucide** injectées via CSS `::before`
  - `calendar-days`, `sun`, `sparkles`, `bar-chart-2`
  - Couleur adaptée : blanc (inactif), noir (actif)

#### Badges Pill Stylisés
- **Badge S3 Ready/Error** avec classes CSS
  - `.badge-s3` avec modificateurs `.success` / `.error`
  - Couleurs : Cyan (INFO), Vert (SUCCESS), Rouge (ERROR)
  - Style pill avec border-radius 50px
- **Badge PREPROD/PROD** avec classes CSS
  - `.badge-preprod` : Jaune (WARNING), texte foncé
  - `.badge-prod` : Vert (SUCCESS), texte clair
  - Icône circle-dot avec classe `.badge-icon`
- **Container `.sidebar-badges`** en bas de sidebar
  - Flexbox avec `margin-top: auto`
  - Border-top subtil, gap entre badges

### 🔄 Modifié

#### Palette de Couleurs Harmonisée
- **Mise à jour complète** de `utils/colors.py`
  - PRIMARY : `#d97b3a` → `#FF8C00` (Orange vif)
  - SECONDARY : `#c66a2f` → `#E24E1B` (Rouge/Orange profond)
  - CHART_COLORS : 8 couleurs du logo (vs 5 anciennes)
- **Documentation synchronisée**
  - CHARTE_GRAPHIQUE_GUIDE.md
  - NOTES_INTEGRATION.md
  - PROGRESSION_INTEGRATION.md
  - RECAPITULATIF_FINAL.md
- **Commentaires code mis à jour**
  - `analyse_seasonality.py` : 3 occurrences corrigées
  - Commentaires HEX alignés avec vraies valeurs

#### Navigation Sidebar
- **Titre** : Passage de `<p>` inline à `<h3>` avec classe CSS
- **Container badges** : Renommé `sidebar-bottom-buttons` → `sidebar-badges`
- **Border subtle** : `#333` → `rgba(240, 240, 240, 0.1)`

### ❌ Supprimé

#### Menu Sidebar
- **Bouton "Rafraîchir"** retiré (inutile avec Streamlit)
  - 24 lignes supprimées dans `main.py`
  - Gradient orange, onclick reload() non nécessaire

### 📚 Documentation

#### Nouvelle Section CHARTE_GRAPHIQUE_GUIDE.md
- **Section "Menu Sidebar - Navigation et Badges"** (300+ lignes)
  - Vue d'ensemble avec 3 zones principales
  - CSS Variables expliquées
  - Titre et texte introductif (HTML + CSS)
  - Navigation avec 3 états détaillés
  - Icônes Lucide avec tableau de mapping
  - Badges Pill (S3 et ENV) avec code complet
  - Structure finale sidebar en ASCII art
  - Checklist menu sidebar (10 points)

#### Fichiers Mis à Jour
- **CHARTE_GRAPHIQUE_GUIDE.md** : Section menu sidebar ajoutée
- **NOTES_INTEGRATION.md** : Mapping couleurs mis à jour
- **PROGRESSION_INTEGRATION.md** : Palette cohérente
- **RECAPITULATIF_FINAL.md** : Nouvelles couleurs
- **Date** : Ajout "Dernière mise à jour: 2025-10-25"

### 🐛 Corrections

#### Commentaires Code
- **analyse_seasonality.py** : 3 palettes de couleurs corrigées
  - Commentaires HEX alignés avec nouvelles valeurs
  - `#6ec1e4` → `#FFD700`, `#e89050` → `#E24E1B`, etc.

### 🎨 Amélioration UX

#### Cohérence Visuelle
- **CSS Variables** : Toutes les couleurs utilisent `var(--*)`
- **Classes réutilisables** : `.badge-s3`, `.badge-preprod`, `.analyses-title`, `.intro-text`
- **États navigation** : Transitions fluides (0.3s ease)
- **Accessibilité** : Contraste texte/fond respecté (noir sur orange actif)

---

## [1.0.0] - 2025-10-23

### ✨ Ajouté

#### Pipeline CI/CD
- **Pipeline CI complet avec GitHub Actions** (`.github/workflows/ci.yml`)
  - Vérification PEP8 automatique (flake8)
  - Vérification du formatage de code (black)
  - Validation des docstrings (pydocstyle - style Google)
  - Tests unitaires automatisés sur PR et merge vers main
  - Coverage minimum 90% obligatoire
  - Exécution parallèle des tests (prod, preprod, infra)
- **Documentation CI/CD complète**
  - `README_CI_CD.md` - Guide détaillé (450+ lignes)
  - `SYNTHESE_CI_CD_ACADEMIC.md` - Réponse aux exigences académiques (630+ lignes)
  - `.github/workflows/README.md` - Documentation des workflows
- **Script de test local** (`run_ci_checks.sh`) - Vérifie le code avant push
- **Configuration des outils**
  - `.flake8` - Configuration PEP8
  - `.pydocstyle` - Configuration docstrings (convention Google)

#### Tests et Coverage
- **Tests unitaires production** (31 tests, 100% coverage)
  - Tests des data loaders (`test_loaders.py`)
  - Tests du module principal (`test_main.py`)
- **Tests unitaires preprod** (22 tests, 96% coverage)
  - Tests d'analyse de ratings (`test_analyse_ratings_simple.py`)
  - Tests de graphiques personnalisés (`test_custom_charts.py`)
- **Tests d'infrastructure** (35 tests)
  - Tests S3 + DuckDB + Docker
  - Scan automatique des fichiers parquet
  - Validation des requêtes SQL
- **Documentation des tests**
  - `README_COVERAGE.md` - Documentation du coverage
  - `RESUME_COVERAGE_FINAL.md` - Résumé final
  - `README_TESTS.md` - Guide des tests

#### Modules de Visualisation
- **Module d'analyse de ratings** (`analyse_ratings_simple.py`)
  - Distribution des notes
  - Statistiques agrégées
  - Graphiques interactifs Plotly
- **Module de graphiques personnalisés** (`custom_charts.py`)
  - Création de visualisations réutilisables
  - Support Plotly et Matplotlib

#### Data Utilities
- **Utilitaires partagés** (`_data_utils/`)
  - `data_utils_common.py` - Connexion DuckDB, overview tables
  - `data_utils_ratings.py` - Traitement des ratings
  - `data_utils_recipes.py` - Traitement des recettes
  - Auto-localisation du fichier DuckDB
  - Support Polars pour performance

#### Documentation
- **Guide de transformation notebook → Streamlit** (`notebook_to_streamlit_guide.md`)
- **Badge CI dans README principal** - Statut en temps réel du pipeline
- **CHANGELOG.md** (ce fichier) - Historique des versions

### 🔧 Modifié

#### Configuration Git
- **Amélioration du .gitignore**
  - Exclusion des rapports de coverage (`htmlcov/`, `.coverage`)
  - Exclusion des fichiers DuckDB (`*.duckdb`, `**/data/*.duckdb`)
  - Exclusion des fichiers binaires

#### Dépendances
- **Ajout de pydocstyle>=6.3.0** dans `10_preprod` et `20_prod`
- **Unification Python 3.13.3** dans tous les environnements

#### Code
- **Formatage automatique avec black** sur tout le codebase
- **Correction des imports inutilisés** (Optional, sns, plt, go, datetime, Mock, patch)
- **Correction des docstrings** selon le style Google (D212, D415)
- **Correction des violations PEP8**
  - Remplacement des `bare except` par `except Exception`
  - Suppression des trailing whitespaces
  - Correction des f-strings sans placeholders

### 🗑️ Supprimé

- **Fichier binaire DuckDB** (10_preprod/src/mangetamain_analytics/data/mangetamain.duckdb)
  - 582MB, causait UnicodeDecodeError dans le CI
- **Workflow CD** (`.github/workflows/deploy.yml`)
  - Non nécessaire pour les exigences académiques
  - Simplifie le pipeline à CI uniquement
- **Référence README corrompue** dans `50_test/pyproject.toml`
  - Contenait des caractères non-UTF8

### 🐛 Corrigé

- **Configuration setuptools pour 50_test**
  - Ajout de `py-modules = []` pour éviter l'erreur "Multiple top-level modules discovered"
- **Encodage des fichiers**
  - Correction du caractère non-UTF8 dans `50_test/README.md`
- **Exceptions E402** pour les tests
  - Ajout dans `.flake8` pour les imports après `sys.path.insert`

---

## [0.5.0] - 2025-10-09

### ✨ Ajouté

#### Configuration S3 Simplifiée
- **Architecture ultra-simple** avec endpoint unique
  - Endpoint: `http://s3fast.lafrance.io`
  - Bucket: `mangetamain`
  - Performance: 500-917 MB/s (DNAT bypass)
- **DuckDB avec S3 intégré** (`garage_s3.duckdb`)
  - Credentials S3 embarqués
  - Requêtes directes sur fichiers parquet S3
- **Documentation S3**
  - `S3_INSTALL.md` - Guide d'installation
  - `S3_USAGE.md` - Guide d'utilisation

#### Environnements
- **Environnement 10_preprod** (port 8500)
  - Développement et expérimentation
  - Badge environnement dans Streamlit
- **Environnement 20_prod** (port 8501)
  - Production ready
  - Logging avec Loguru
- **Environnement 30_docker**
  - Orchestration Docker Compose
  - Redirection DNAT pour performance S3
  - Health checks automatiques

#### Base de Données
- **DuckDB intégré** (582MB)
  - 7 tables préchargées
  - 178,265 recettes
  - 25,076 utilisateurs
  - 1,1M+ interactions

### 🔧 Modifié

- **Unification Python 3.13.3** dans tous les environnements
- **Migration vers uv** comme gestionnaire de paquets
- **Optimisation des performances S3**

---

## [0.1.0] - 2024-XX-XX

### ✨ Ajouté

- **Initialisation du projet**
- **Structure de base des notebooks EDA** (`00_eda/`)
- **Application Streamlit initiale**
- **Configuration initiale du projet**

---

## Légende des Types de Changements

- **✨ Ajouté** : Nouvelles fonctionnalités
- **🔧 Modifié** : Changements dans des fonctionnalités existantes
- **🗑️ Supprimé** : Fonctionnalités supprimées
- **🐛 Corrigé** : Corrections de bugs
- **🔒 Sécurité** : Corrections de vulnérabilités
- **📚 Documentation** : Changements dans la documentation
- **⚡ Performance** : Améliorations de performance
- **♻️ Refactoring** : Refactorisation du code sans changement de fonctionnalité

---

## Liens Utiles

- **Repository**: https://github.com/julienlafrance/backtothefuturekitchen
- **CI/CD Pipeline**: https://github.com/julienlafrance/backtothefuturekitchen/actions
- **Documentation CI/CD**: [README_CI_CD.md](README_CI_CD.md)
- **Documentation Tests**: [README_COVERAGE.md](README_COVERAGE.md)

---

**Projet académique** - Mangetamain Analytics Team - 2025
