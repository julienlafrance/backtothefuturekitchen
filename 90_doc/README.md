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

## Notes

* Les fichiers `build/` et `.venv/` sont gitignorés
* La documentation suit la charte graphique du projet
* Format des docstrings : Google Style
