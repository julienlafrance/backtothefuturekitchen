# Solution Documentation Sphinx

## Problème
- Générer documentation HTML avec Sphinx
- Documenter automatiquement les classes, fonctions, modules
- Exigence obligatoire du projet

## Solution : Sphinx + autodoc + napoleon + RTD theme

### PHASE 1 : Initialisation (30min)

#### 1.1 Installer Sphinx (déjà fait ✅)
```bash
cd 10_preprod
# Vérifier
uv run python -c "import sphinx; print(sphinx.__version__)"
```

#### 1.2 Créer structure docs/
```bash
cd 10_preprod
mkdir -p docs

# Initialiser Sphinx (mode interactif)
uv run sphinx-quickstart docs \
  --sep \
  --project="Mangetamain Analytics" \
  --author="Mangetamain Team" \
  --release="1.0" \
  --language="fr" \
  --extensions=sphinx.ext.autodoc,sphinx.ext.napoleon,sphinx.ext.viewcode
```

**OU** créer manuellement la structure :

```
10_preprod/docs/
├── source/
│   ├── conf.py           # Configuration Sphinx
│   ├── index.rst         # Page d'accueil
│   ├── installation.rst  # Installation
│   ├── usage.rst         # Utilisation
│   └── api/
│       ├── modules.rst   # Index des modules
│       ├── utils.rst     # Documentation utils
│       └── visualization.rst  # Documentation visualization
├── build/                # Généré automatiquement
└── Makefile             # Pour build HTML
```

---

### PHASE 2 : Configuration (45min)

#### 2.1 Configuration conf.py

Créer/éditer `10_preprod/docs/source/conf.py` :

```python
# Configuration file for the Sphinx documentation builder.

import os
import sys

# Ajouter le chemin vers le code source
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
project = 'Mangetamain Analytics'
copyright = '2025, Mangetamain Team'
author = 'Mangetamain Team'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Documentation automatique
    'sphinx.ext.napoleon',     # Support Google/NumPy docstrings
    'sphinx.ext.viewcode',     # Liens vers le code source
    'sphinx.ext.intersphinx',  # Liens vers autres docs
    'sphinx_rtd_theme',        # Theme Read The Docs
]

# Napoleon settings (pour docstrings Google)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Template path
templates_path = ['_templates']

# List of patterns to ignore
exclude_patterns = []

# Language
language = 'fr'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'titles_only': False,
    'collapse_navigation': False,
}

# Output file base name
htmlhelp_basename = 'MangetamainAnalyticsdoc'

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}
```

#### 2.2 Page d'accueil index.rst

Créer `10_preprod/docs/source/index.rst` :

```rst
Bienvenue dans la documentation Mangetamain Analytics
======================================================

**Mangetamain Analytics** est une plateforme d'analytics culinaires basée sur
un système de recommandations de recettes avec données Food.com.

Architecture moderne Python 3.13.3 + Streamlit + DuckDB + S3 Storage.

🔗 **Liens utiles:**

* Application PREPROD: https://mangetamain.lafrance.io/
* Application PROD: https://backtothefuturekitchen.lafrance.io/
* Repository GitHub: https://github.com/julienlafrance/backtothefuturekitchen

Fonctionnalités Principales
----------------------------

* 📊 **Analyse des tendances** : Évolution des recettes 1999-2018
* 🌸 **Analyse saisonnière** : Patterns saisonniers des recettes
* ⭐ **Analyse des ratings** : Distribution des notes utilisateurs
* 📈 **Visualisations interactives** : Graphiques Plotly dynamiques

Sommaire
--------

.. toctree::
   :maxdepth: 2
   :caption: Guide utilisateur

   installation
   usage

.. toctree::
   :maxdepth: 3
   :caption: Référence API

   api/modules
   api/utils
   api/visualization

Indices et tables
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
```

#### 2.3 Page installation.rst

Créer `10_preprod/docs/source/installation.rst` :

```rst
Installation
============

Prérequis
---------

* Python 3.13.3
* uv (gestionnaire de paquets)
* Accès S3 (Garage Storage)

Installation locale
-------------------

1. Cloner le repository
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/julienlafrance/backtothefuturekitchen.git
   cd backtothefuturekitchen/000_dev/10_preprod

2. Créer l'environnement virtuel
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv sync

3. Configuration S3
^^^^^^^^^^^^^^^^^^^

Copier les credentials S3 dans ``96_keys/credentials`` :

.. code-block:: ini

   [s3fast]
   aws_access_key_id = YOUR_KEY
   aws_secret_access_key = YOUR_SECRET

4. Lancer l'application
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   uv run streamlit run src/mangetamain_analytics/main.py

L'application est accessible sur http://localhost:8501

Tests
-----

Lancer les tests unitaires :

.. code-block:: bash

   uv run pytest tests/unit/ -v --cov=src

Résultat attendu : **93% coverage** (118 tests)
```

#### 2.4 Page usage.rst

Créer `10_preprod/docs/source/usage.rst` :

```rst
Utilisation
===========

Architecture de l'application
-----------------------------

L'application Mangetamain Analytics est organisée en modules :

* **utils/** : Fonctions utilitaires (couleurs, thème graphique)
* **visualization/** : Modules d'analyse et visualisation
* **data/** : Chargement et cache des données

Modules d'analyse disponibles
------------------------------

1. Analyse des tendances
^^^^^^^^^^^^^^^^^^^^^^^^^

Module : ``visualization.analyse_trendlines_v2``

Analyse l'évolution des recettes de 1999 à 2018 :

* Durée de préparation moyenne/médiane
* Complexité des recettes
* Nombre d'ingrédients

2. Analyse saisonnière
^^^^^^^^^^^^^^^^^^^^^^

Module : ``visualization.analyse_seasonality``

Identifie les patterns saisonniers :

* Recettes par saison
* Ingrédients saisonniers
* Tendances temporelles

3. Analyse des ratings
^^^^^^^^^^^^^^^^^^^^^^

Module : ``visualization.analyse_ratings``

Étudie les notes utilisateurs :

* Distribution des notes
* Corrélations avec caractéristiques recettes
* Analyse des outliers

Personnalisation des graphiques
--------------------------------

Utiliser le module ``chart_theme`` pour appliquer la charte graphique :

.. code-block:: python

   from utils import chart_theme
   import plotly.graph_objects as go

   fig = go.Figure()
   # ... ajouter traces ...
   chart_theme.apply_chart_theme(fig, title="Mon graphique")

Couleurs de la charte :

.. code-block:: python

   from utils import colors

   primary = colors.ORANGE_PRIMARY  # #FF8C00
   background = colors.BACKGROUND_MAIN  # #1E1E1E
   text = colors.TEXT_PRIMARY  # #F0F0F0
```

#### 2.5 Documentation API - modules.rst

Créer `10_preprod/docs/source/api/modules.rst` :

```rst
Référence des Modules
======================

Cette section documente tous les modules Python de Mangetamain Analytics.

.. toctree::
   :maxdepth: 2

   utils
   visualization
```

#### 2.6 Documentation API - utils.rst

Créer `10_preprod/docs/source/api/utils.rst` :

```rst
Module utils
============

Modules utilitaires pour la charte graphique et les couleurs.

utils.colors
------------

.. automodule:: mangetamain_analytics.utils.colors
   :members:
   :undoc-members:
   :show-inheritance:

utils.chart_theme
-----------------

.. automodule:: mangetamain_analytics.utils.chart_theme
   :members:
   :undoc-members:
   :show-inheritance:
```

#### 2.7 Documentation API - visualization.rst

Créer `10_preprod/docs/source/api/visualization.rst` :

```rst
Module visualization
====================

Modules d'analyse et visualisation des données.

visualization.analyse_trendlines_v2
-----------------------------------

.. automodule:: mangetamain_analytics.visualization.analyse_trendlines_v2
   :members:
   :undoc-members:
   :show-inheritance:

visualization.analyse_seasonality
---------------------------------

.. automodule:: mangetamain_analytics.visualization.analyse_seasonality
   :members:
   :undoc-members:
   :show-inheritance:

visualization.analyse_ratings
-----------------------------

.. automodule:: mangetamain_analytics.visualization.analyse_ratings
   :members:
   :undoc-members:
   :show-inheritance:

visualization.custom_charts
---------------------------

.. automodule:: mangetamain_analytics.visualization.custom_charts
   :members:
   :undoc-members:
   :show-inheritance:
```

---

### PHASE 3 : Génération (15min)

#### 3.1 Créer Makefile

Créer `10_preprod/docs/Makefile` :

```makefile
# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

#### 3.2 Générer la documentation HTML

```bash
cd 10_preprod/docs
uv run sphinx-build -b html source build/html

# OU avec Makefile
uv run make html
```

#### 3.3 Vérifier le résultat

```bash
# Ouvrir dans le navigateur
xdg-open build/html/index.html

# OU
firefox build/html/index.html
```

---

### PHASE 4 : Intégration README (15min)

Ajouter dans `10_preprod/README.md` ou `README.md` principal :

```markdown
## 📚 Documentation

La documentation complète du projet est générée avec Sphinx.

### Générer la documentation

```bash
cd 10_preprod/docs
uv run make html
```

### Consulter la documentation

```bash
xdg-open docs/build/html/index.html
```

Ou directement : [Documentation en ligne](docs/build/html/index.html)
```

---

### PHASE 5 : Commit (10min)

```bash
git add 10_preprod/docs/
git add README.md
git commit -m "Ajouter documentation Sphinx complète

- Initialiser Sphinx avec autodoc + napoleon
- Créer structure docs/ avec guide utilisateur et API
- Générer documentation HTML avec theme RTD
- Documenter modules utils et visualization
- Mettre à jour README avec instructions"

git push origin main
```

---

## Résultat Final

```
10_preprod/docs/
├── source/
│   ├── conf.py              # Configuration
│   ├── index.rst            # Page d'accueil
│   ├── installation.rst     # Guide installation
│   ├── usage.rst            # Guide utilisation
│   └── api/
│       ├── modules.rst      # Index modules
│       ├── utils.rst        # Doc utils
│       └── visualization.rst # Doc visualization
├── build/
│   └── html/
│       ├── index.html       # Documentation HTML
│       ├── installation.html
│       ├── usage.html
│       └── api/
│           ├── utils.html
│           └── visualization.html
└── Makefile
```

## Avantages de cette solution

✅ **Documentation auto** - autodoc génère depuis docstrings
✅ **Google docstrings** - napoleon supporte le format déjà utilisé
✅ **Theme professionnel** - RTD theme utilisé par Python, Django, etc.
✅ **Searchable** - Barre de recherche intégrée
✅ **Liens code source** - viewcode ajoute liens vers GitHub
✅ **Rapide** - 2h max pour tout générer

## Checklist finale

- [ ] Sphinx installé (déjà fait ✅)
- [ ] Structure docs/ créée
- [ ] conf.py configuré (autodoc + napoleon + RTD)
- [ ] index.rst avec sommaire
- [ ] installation.rst avec commandes
- [ ] usage.rst avec exemples
- [ ] api/*.rst pour modules
- [ ] Makefile pour build
- [ ] HTML généré : `make html`
- [ ] README mis à jour
- [ ] Commit + push

## Temps total estimé : 2h15

- 30min : Initialisation structure
- 45min : Configuration + pages RST
- 15min : Génération HTML
- 15min : Intégration README
- 10min : Commit

## ⚠️ Notes importantes

1. **Ne PAS commit build/** - Ajouter dans .gitignore :
   ```gitignore
   **/docs/build/
   ```

2. **Docstrings existantes OK** - autodoc utilise ce qui existe déjà

3. **Erreurs possibles** :
   - Import errors : Vérifier `sys.path` dans conf.py
   - Theme RTD : `pip install sphinx-rtd-theme` si manquant

4. **Pour corriger imports** :
   ```python
   # Dans conf.py
   sys.path.insert(0, os.path.abspath('../../src'))
   sys.path.insert(0, os.path.abspath('../../src/mangetamain_analytics'))
   ```

---

**🎯 PRIORITÉ MAXIMALE : Faire ça DIMANCHE (6h) !**
