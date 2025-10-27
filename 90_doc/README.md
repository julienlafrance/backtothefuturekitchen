# Documentation Sphinx - Mangetamain Analytics

Ce répertoire contient la documentation Sphinx du projet Mangetamain Analytics.

## Structure

```
90_doc/
├── source/              # Sources documentation (RST)
│   ├── conf.py          # Configuration Sphinx
│   ├── index.rst        # Page d'accueil
│   ├── installation.rst # Guide installation
│   ├── usage.rst        # Guide utilisation
│   ├── architecture.rst # Architecture technique
│   └── api/             # Documentation API Python
├── build/html/          # Documentation générée (gitignored)
├── md/                  # Fichiers Markdown de session
├── requirements.txt     # Dépendances Sphinx
├── Makefile             # Build automation Linux/Mac
└── make.bat             # Build automation Windows

```

## Génération de la Documentation

### Prérequis

```bash
cd 90_doc
uv venv --python 3.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Build HTML

```bash
# Avec make
make html

# OU directement avec sphinx-build
sphinx-build -b html source build/html
```

### Consulter la Documentation

```bash
# Linux
xdg-open build/html/index.html

# macOS
open build/html/index.html

# Windows
start build/html/index.html
```

## Technologies

* **Sphinx 8.2.3** : Générateur de documentation
* **sphinx-rtd-theme 3.0.2** : Thème Read the Docs
* **myst-parser 4.0.1** : Support Markdown dans Sphinx
* **Python 3.13.3** : Version Python du projet

## Documentation Automatique

La documentation des modules Python est générée automatiquement depuis les docstrings (format Google) via `sphinx.ext.autodoc`.

Modules documentés :
* `utils.colors` : Palette de couleurs
* `utils.chart_theme` : Thème graphique
* `visualization.*` : Modules d'analyse
* `data.cached_loaders` : Chargement données

## Maintenance

### Ajouter une Page

1. Créer un fichier `.rst` dans `source/`
2. Ajouter la référence dans `index.rst` (toctree)
3. Rebuild : `make html`

### Mettre à Jour l'API

La documentation API est auto-générée. Après modification des docstrings Python :

```bash
make html
```

## Statistiques

* **5073 lignes RST** (15 fichiers) - +2333 lignes vs version initiale (+85%)
* **10 guides utilisateur** : quickstart, installation, usage, faq, s3, architecture, cicd, tests, conformite
* **5 références API** : utils, visualization, data, infrastructure
* **Nouveaux guides** : Quick Start (426L), FAQ (458L)
* **7-9 warnings Sphinx** (autodoc, acceptables)
* **Build time** : ~15 secondes
* **Date dernière maj** : 2025-10-27 (itérations 21-34)

## Pages Créées

**Guides** (4140 lignes total):
- `index.rst` - Page d'accueil avec démarrage rapide (84L)
- `quickstart.rst` - **NOUVEAU** Guide démarrage rapide + cheat sheet (426L)
- `installation.rst` - Installation + Docker + troubleshooting (426L ↑310L)
- `usage.rst` - Utilisation application + insights analyses (203L ↑82L)
- `faq.rst` - **NOUVEAU** FAQ 22 questions courantes (458L)
- `s3.rst` - Configuration S3 + benchmarks performance (658L ↑165L)
- `architecture.rst` - Stack technique + logging complet (438L ↑165L)
- `cicd.rst` - Pipeline CI/CD + workflows concrets (694L ↑262L)
- `tests.rst` - Tests et coverage 93% (416L)
- `conformite.rst` - Conformité académique + logging (321L ↑18L)

**API** (933 lignes total):
- `api/index.rst` - Index référence API (14L)
- `api/utils.rst` - Couleurs et thème graphique + exemples (242L ↑158L)
- `api/visualization.rst` - 8 modules analyse + insights (264L ↑146L)
- `api/data.rst` - Loaders données + schémas + troubleshooting (230L ↑171L)
- `api/infrastructure.rst` - Logging, DB, utils EDA (197L)

**Total enrichi**: +2333 lignes depuis version initiale (+85%) (itérations 21-34)

## Notes

* Les fichiers `build/` et `.venv/` sont gitignorés
* La documentation suit la charte graphique du projet
* Format des docstrings : Google Style
* Coverage documentation : 100% modules principaux 10_preprod/src
* Warnings autodoc visualization : attendus (modules Streamlit)
