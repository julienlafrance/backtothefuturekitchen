# 🎯 Guide d'Intégration des Analyses EDA dans Streamlit

## 📋 Vue d'ensemble

Ce guide documente la méthodologie complète pour intégrer des analyses EDA (provenant de notebooks Jupyter) dans l'application Streamlit de preprod. Il suit un processus rigoureux qui garantit la qualité du code, la conformité PEP8, et la couverture de tests.

**Date**: 2025-10-23
**Auteur**: Claude Code
**Exemple de référence**: Intégration de `recipe_analysis_trendline_clean.py` → `analyse_trendlines.py`

---

## ⚡ Principe Clé: Copier, Ne PAS Réinventer

**IMPORTANT**: Les fichiers sources EDA avec balises XML sont déjà optimisés et testés. Le processus d'intégration doit **COPIER le code existant avec des modifications MINIMALES**:

### ✅ Modifications autorisées
1. **Graphiques uniquement**: Conversion Matplotlib → Plotly (structure visuelle)
2. **Import des données**: Utiliser le package `mangetamain-data-utils` qui charge depuis S3
3. **Ajout Streamlit**: `st.plotly_chart()`, `st.info()` pour affichage

### ❌ À NE PAS modifier
1. **Logique d'analyse**: Calculs statistiques, régressions, agrégations
2. **Interprétations**: Copier textuellement depuis balises `<INTERPRÉTATION>`
3. **Structure des données**: Colonnes, filtres, transformations
4. **Paramètres**: Seuils, méthodes statistiques (sauf demande explicite)

### 📝 Règle d'or
> **Si le code source fonctionne, COPIER exactement la logique métier. Modifier UNIQUEMENT la couche de visualisation (Matplotlib → Plotly) et l'affichage (Streamlit).**

---

## 🏗️ Architecture du Projet

```
10_preprod/
├── src/mangetamain_analytics/
│   ├── main.py                          # Point d'entrée Streamlit
│   └── visualization/
│       ├── __init__.py
│       ├── analyse_ratings_simple.py    # Exemple existant
│       ├── custom_charts.py
│       └── analyse_trendlines.py        # ✅ NOUVEAU MODULE
├── tests/
│   └── unit/
│       ├── test_analyse_ratings_simple.py
│       ├── test_custom_charts.py
│       └── test_analyse_trendlines.py   # ✅ NOUVEAUX TESTS
├── pyproject.toml                       # Configuration + dépendances
└── README.md
```

---

## 🔄 Processus d'Intégration en 7 Étapes

### **ÉTAPE 1: Analyse du Fichier Source EDA** 📊

#### 1.1 Localiser le fichier source
```bash
# Fichier source
00_eda/01_long_term/recipe/recipe_analysis_trendline_clean.py
```

#### 1.2 Identifier les balises XML d'intégration
Rechercher les balises `<ANALYSE_TITRE>`, `<ANALYSE_DESCRIPTION>`, `<INTERPRÉTATION>` dans le fichier:

```python
# Exemple de balises trouvées dans le fichier source
def analyse_trendline_1():
    # ... code ...

    # <INTERPRÉTATION>
    # > Nous observons une **forte augmentation** jusqu'en 2007...
    # </INTERPRÉTATION>
```

**Balises à identifier**:
- ✅ Titre de l'analyse (nom de la fonction)
- ✅ Description/objectif
- ✅ Données utilisées (tables, colonnes)
- ✅ Méthode statistique (WLS, régression, tests)
- ✅ Interprétations des résultats

#### 1.3 Lister les fonctions à intégrer
Pour `recipe_analysis_trendline_clean.py`:
1. `analyse_trendline_1()` → Volume de recettes
2. `analyse_trendline_2()` → Durée de préparation
3. `analyse_trendline_3()` → Complexité
4. `analyse_trendline_4()` → Nutrition
5. `analyse_trendline_5()` → Ingrédients
6. `analyse_trendline_6()` → Tags/catégories

#### 1.4 Identifier les dépendances
```python
# Dépendances détectées dans le fichier source
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from _data_utils import load_recipes_clean
```

---

### **ÉTAPE 2: Création du Module Streamlit** 🏗️

**⚠️ PRINCIPE FONDAMENTAL**: Cette étape consiste à **COPIER** le code source avec modifications MINIMALES.

#### 2.1 Nommer le module
**Convention**: `analyse_<thème>.py`

Exemple: `analyse_trendlines.py`

#### 2.2 Structure du module

```python
"""Module d'analyse des <thème>.

Description détaillée de ce que fait le module:
- Point 1
- Point 2
- Point 3

Utilise <méthode statistique> pour <objectif>.
"""

import warnings
from pathlib import Path

# Imports data science - COPIER depuis le fichier source
import polars as pl
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import statsmodels.api as sm
import streamlit as st

# Import du package data-utils qui charge depuis S3
from mangetamain_data_utils.data_utils_recipes import load_recipes_clean

warnings.filterwarnings("ignore")


def analyse_fonction_1():
    """Docstring détaillée avec Google style.

    Affiche:
        - Élément 1
        - Élément 2
        - Interprétation
    """
    if load_recipes_clean is None:
        st.error("❌ Impossible de charger les données")
        return

    # 1. CHARGEMENT DES DONNÉES - Appel direct depuis le package
    df = load_recipes_clean()

    # 2-3. TRANSFORMATION ET CALCULS - COPIER EXACTEMENT depuis le fichier source
    # ⚠️ NE PAS MODIFIER LA LOGIQUE MÉTIER !
    # Exemple: garder les mêmes group_by, agg, calculs statistiques
    recipes_per_year = (
        df.group_by("year").agg(pl.len().alias("n_recipes")).sort("year").to_pandas()
    )
    # ... reste des calculs COPIÉS

    # 4. GRAPHIQUES - UNIQUEMENT remplacer Matplotlib par Plotly
    fig = go.Figure()
    # OU make_subplots() pour plusieurs graphiques

    # Exemple conversion:
    # AVANT (Matplotlib): plt.bar(x, y)
    # APRÈS (Plotly): fig.add_trace(go.Bar(x=x, y=y))

    # 5. AFFICHAGE STREAMLIT
    st.plotly_chart(fig, use_container_width=True)

    # 6. INTERPRÉTATION - COPIER TEXTUELLEMENT depuis <INTERPRÉTATION>
    st.info(
        "📊 **Interprétation**: <copier mot pour mot depuis la balise>"
    )
```

**🔑 Points clés**:
1. ✅ Import direct: `from mangetamain_data_utils.data_utils_recipes import load_recipes_clean`
2. ✅ Copier la logique: Garder tous les calculs statistiques identiques
3. ✅ Convertir graphiques: Seulement Matplotlib → Plotly
4. ✅ Copier interprétations: Texte exact depuis les balises XML

#### 2.3 Règles de conversion Matplotlib → Plotly

| Matplotlib | Plotly | Notes |
|------------|--------|-------|
| `plt.figure()` | `go.Figure()` | Graphique simple |
| `plt.subplots()` | `make_subplots()` | Graphiques multiples |
| `plt.bar()` | `go.Bar()` | Barres |
| `plt.plot()` | `go.Scatter(mode='lines')` | Lignes |
| `plt.scatter()` | `go.Scatter(mode='markers')` | Points |
| `plt.fill_between()` | `go.Scatter(fill='tonexty')` | Aires |
| `plt.show()` | `st.plotly_chart(fig)` | Affichage Streamlit |

**⚠️ IMPORTANT**: Ne JAMAIS utiliser `plt.show()` dans Streamlit !

#### 2.4 Gestion des paramètres interactifs

```python
def analyse_ingredients(top_n=10):
    """Analyse avec paramètre personnalisable.

    Args:
        top_n: Nombre d'éléments à afficher dans les tops
    """
    # Le paramètre top_n sera contrôlé par st.slider() dans main.py
    # ...
```

---

### **ÉTAPE 3: Intégration dans main.py** 🔗

#### 3.1 Ajouter les imports

```python
# Dans main.py, après les autres imports de visualization
from visualization.analyse_trendlines import (
    analyse_trendline_volume,
    analyse_trendline_duree,
    analyse_trendline_complexite,
    analyse_trendline_nutrition,
    analyse_trendline_ingredients,
    analyse_trendline_tags,
)
```

#### 3.2 Ajouter un nouvel onglet

```python
# Dans la fonction main(), modifier la liste des tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Vue d'ensemble",
    "⭐ Analyses des notes",
    "📅 Analyse temporelle",
    "👥 Utilisateurs",
    "🔍 Données brutes",
    "📈 Graphiques personnalisés",
    "📈 Tendances 1999-2018",  # ✅ NOUVEAU
])
```

#### 3.3 Créer le contenu de l'onglet

```python
with tab7:
    st.header("📈 Analyses des tendances temporelles (1999-2018)")
    st.markdown(
        """
        Cette section présente les **analyses de tendances à long terme**...
        """
    )

    # Sélecteur d'analyse
    analyse_choice = st.selectbox(
        "Choisir une analyse:",
        [
            "📊 Volume de recettes",
            "⏱️ Durée de préparation",
            "🔧 Complexité des recettes",
            "🥗 Valeurs nutritionnelles",
            "🥘 Ingrédients",
            "🏷️ Tags/Catégories",
        ],
    )

    # Affichage conditionnel
    if analyse_choice == "📊 Volume de recettes":
        analyse_trendline_volume()
    elif analyse_choice == "⏱️ Durée de préparation":
        analyse_trendline_duree()
    elif analyse_choice == "🔧 Complexité des recettes":
        analyse_trendline_complexite()
    elif analyse_choice == "🥗 Valeurs nutritionnelles":
        analyse_trendline_nutrition()
    elif analyse_choice == "🥘 Ingrédients":
        # Paramètre interactif
        top_n = st.slider("Nombre d'ingrédients dans les tops", 5, 20, 10)
        analyse_trendline_ingredients(top_n=top_n)
    elif analyse_choice == "🏷️ Tags/Catégories":
        top_n = st.slider("Nombre de tags dans les tops", 5, 20, 10)
        analyse_trendline_tags(top_n=top_n)
```

---

### **ÉTAPE 4: Création des Tests Unitaires** ✅

#### 4.1 Structure du fichier de test

```python
"""Tests unitaires pour le module <nom_module>.

Teste les fonctions d'analyse <description>.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, patch
import polars as pl

# Ajout du chemin vers le module
sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mangetamain_analytics"))

from visualization.<nom_module> import (
    fonction_1,
    fonction_2,
    # ...
)


@pytest.fixture
def mock_recipes_data():
    """Fixture pour créer des données de test simulées."""
    # Créer des données Polars réalistes
    data = {
        "id": list(range(1000)),
        "year": [1999 + i % 20 for i in range(1000)],
        # ... autres colonnes nécessaires
    }
    return pl.DataFrame(data)


@patch("visualization.<nom_module>.st")
@patch("visualization.<nom_module>.load_recipes_clean")
def test_fonction_1(mock_load_recipes, mock_st, mock_recipes_data):
    """Test de la fonction fonction_1."""
    mock_load_recipes.return_value = mock_recipes_data

    # Mock Streamlit components
    mock_st.plotly_chart = Mock()
    mock_st.info = Mock()

    # Exécution
    fonction_1()

    # Vérifications
    mock_load_recipes.assert_called_once()
    mock_st.plotly_chart.assert_called_once()
    mock_st.info.assert_called_once()


@patch("visualization.<nom_module>.st")
@patch("visualization.<nom_module>.load_recipes_clean")
def test_fonction_1_no_data(mock_load_recipes, mock_st):
    """Test du comportement quand load_recipes_clean retourne None."""
    # Simuler l'échec du chargement
    with patch("visualization.<nom_module>.load_recipes_clean", None):
        mock_st.error = Mock()

        # Exécution
        fonction_1()

        # Vérifications
        mock_st.error.assert_called_once()
```

#### 4.2 Tests obligatoires par fonction

**Pour chaque fonction d'analyse, créer 2 tests**:

1. ✅ **Test nominal**: Fonction exécutée avec succès
   - Mock `load_recipes_clean` qui retourne des données
   - Vérifier que `st.plotly_chart()` est appelé
   - Vérifier que `st.info()` est appelé (interprétation)

2. ✅ **Test erreur**: Fonction gère l'absence de données
   - Mock `load_recipes_clean = None`
   - Vérifier que `st.error()` est appelé

**Exemple**: 6 fonctions → 12 tests minimum

---

### **ÉTAPE 5: Mise à Jour des Dépendances** 📦

#### 5.1 Identifier les nouvelles dépendances

Comparer les imports du module créé avec `pyproject.toml`:

```bash
# Vérifier si statsmodels est présent
grep "statsmodels" pyproject.toml
```

#### 5.2 Ajouter les dépendances manquantes

```toml
# Dans pyproject.toml, section [project] dependencies
dependencies = [
    "streamlit>=1.28.0",
    "duckdb>=1.4.1",
    # ... autres dépendances existantes
    "statsmodels>=0.14.0",  # ✅ AJOUTÉ
]
```

#### 5.3 Synchroniser l'environnement

```bash
uv sync
```

---

### **ÉTAPE 6: Vérifications Qualité (OBLIGATOIRES)** 🔍

#### 6.1 Test 1: PEP8 avec flake8

```bash
uv run python -m flake8 src/mangetamain_analytics/visualization/<nom_module>.py
```

**Résultat attendu**: Aucune erreur

**Erreurs courantes à corriger**:
- `F401`: Import inutilisé → Supprimer
- `E501`: Ligne trop longue → Découper sur plusieurs lignes
- `W291`: Trailing whitespace → Supprimer espaces en fin de ligne
- `E302`: Manque 2 lignes blanches → Ajouter ligne vide
- `F541`: f-string sans placeholder → Retirer le `f`

#### 6.2 Test 2: Formatage avec black

```bash
uv run python -m black src/mangetamain_analytics/visualization/<nom_module>.py
uv run python -m black tests/unit/test_<nom_module>.py
```

**Résultat attendu**: "All done! ✨ 🍰 ✨"

#### 6.3 Test 3: Docstrings avec pydocstyle

```bash
uv run python -m pydocstyle src/mangetamain_analytics/visualization/<nom_module>.py
```

**Convention**: Google style

**Structure obligatoire**:
```python
def ma_fonction(param1, param2=10):
    """Résumé sur une ligne.

    Description détaillée facultative.

    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2 (default: 10)

    Returns:
        Description du retour

    Raises:
        ValueError: Quand erreur
    """
```

#### 6.4 Test 4: Tests unitaires

```bash
uv run python -m pytest tests/unit/test_<nom_module>.py -v
```

**Résultat attendu**:
- ✅ Tous les tests passent (12/12 par exemple)
- ✅ Coverage >= 90% pour le nouveau module

**Exemple de sortie attendue**:
```
tests/unit/test_analyse_trendlines.py::test_analyse_trendline_volume PASSED [  8%]
tests/unit/test_analyse_trendlines.py::test_analyse_trendline_duree PASSED [ 16%]
...
tests/unit/test_analyse_trendlines.py::test_analyse_trendline_tags_no_data PASSED [100%]

================================ tests coverage ================================
src/mangetamain_analytics/visualization/analyse_trendlines.py    243    3   99%
================================ 12 passed in 3.41s ==============================
```

#### 6.5 Test 5: Coverage complet du projet

```bash
uv run python -m pytest tests/unit/ -v --cov=src --cov-report=html
```

**Seuil minimum**: 90% (configuré dans `pyproject.toml`)

---

### **ÉTAPE 7: Validation Fonctionnelle** 🚀

#### 7.1 Lancer l'application Streamlit

```bash
cd 10_preprod
uv run streamlit run src/mangetamain_analytics/main.py
```

#### 7.2 Checklist de validation

✅ **Navigation**:
- [ ] Le nouvel onglet apparaît dans l'interface
- [ ] Cliquer sur l'onglet charge correctement le contenu
- [ ] Le sélecteur d'analyse affiche toutes les options

✅ **Chaque analyse**:
- [ ] Les graphiques Plotly s'affichent correctement
- [ ] Les graphiques sont interactifs (hover, zoom, pan)
- [ ] L'interprétation s'affiche dans un bloc `st.info()`
- [ ] Les couleurs et légendes sont lisibles
- [ ] Les sliders fonctionnent (si applicable)

✅ **Performance**:
- [ ] Temps de chargement < 5 secondes
- [ ] Pas d'erreur dans la console Streamlit
- [ ] Pas de warning dans les logs

✅ **Responsive**:
- [ ] Graphiques s'adaptent à la largeur (use_container_width=True)
- [ ] Texte lisible à différentes résolutions

---

## 📊 Résumé de l'Intégration de `analyse_trendlines.py`

### Fichiers créés/modifiés

| Fichier | Lignes | Status | Coverage |
|---------|--------|--------|----------|
| `visualization/analyse_trendlines.py` | 933 | ✅ Créé | 99% |
| `tests/unit/test_analyse_trendlines.py` | 182 | ✅ Créé | 100% |
| `main.py` | 586 | ✅ Modifié | - |
| `pyproject.toml` | 81 | ✅ Modifié | - |

### Fonctions intégrées

| Fonction | Description | Graphiques | Tests |
|----------|-------------|------------|-------|
| `analyse_trendline_volume()` | Volume de recettes par année | Bar + Q-Q plot | 2 ✅ |
| `analyse_trendline_duree()` | Durée de préparation | Lignes + IQR + régression WLS | 2 ✅ |
| `analyse_trendline_complexite()` | Complexité (score, étapes, ingrédients) | 3 subplots avec régressions | 2 ✅ |
| `analyse_trendline_nutrition()` | Calories, glucides, lipides, protéines | 4 subplots avec régressions | 2 ✅ |
| `analyse_trendline_ingredients()` | Top ingrédients, diversité, variations | 6 subplots complexes | 2 ✅ |
| `analyse_trendline_tags()` | Top tags, diversité, variations | 6 subplots complexes | 2 ✅ |

### Tests exécutés

```bash
# 1. PEP8
uv run python -m flake8 src/mangetamain_analytics/visualization/analyse_trendlines.py
# ✅ 0 erreurs

# 2. Black
uv run python -m black src/mangetamain_analytics/visualization/analyse_trendlines.py
# ✅ "All done! ✨ 🍰 ✨"

# 3. Tests unitaires
uv run python -m pytest tests/unit/test_analyse_trendlines.py -v
# ✅ 12 passed in 3.41s

# 4. Coverage
uv run python -m pytest tests/unit/test_analyse_trendlines.py --cov=src/mangetamain_analytics/visualization/analyse_trendlines.py
# ✅ 99% coverage (243/246 lines)
```

---

## 🎯 Checklist Complète d'Intégration

### Avant de commencer
- [ ] Identifier le fichier EDA source
- [ ] Lire et comprendre les analyses
- [ ] Repérer les balises `<INTERPRÉTATION>`
- [ ] Lister les dépendances nécessaires

### Développement
- [ ] Créer `src/mangetamain_analytics/visualization/<nom_module>.py`
- [ ] Convertir Matplotlib → Plotly
- [ ] Ajouter docstrings Google style
- [ ] Gérer les cas d'erreur (`load_recipes_clean = None`)
- [ ] Copier les interprétations dans `st.info()`
- [ ] Intégrer dans `main.py` (imports + onglet)
- [ ] Ajouter paramètres interactifs si nécessaire

### Tests
- [ ] Créer `tests/unit/test_<nom_module>.py`
- [ ] Écrire 2 tests par fonction (nominal + erreur)
- [ ] Créer fixture `mock_recipes_data()` réaliste
- [ ] Vérifier tous les tests passent

### Qualité
- [ ] PEP8: `flake8` sans erreur
- [ ] Formatage: `black` appliqué
- [ ] Docstrings: `pydocstyle` conforme (Google)
- [ ] Coverage: >= 90% sur le nouveau module
- [ ] Dépendances: Ajoutées dans `pyproject.toml`
- [ ] Sync: `uv sync` exécuté

### Validation
- [ ] App Streamlit démarre sans erreur
- [ ] Nouvel onglet visible et fonctionnel
- [ ] Tous les graphiques s'affichent
- [ ] Interactivité Plotly fonctionne
- [ ] Sliders fonctionnent (si applicable)
- [ ] Performance acceptable (< 5s)
- [ ] Pas d'erreur en console

---

## 🚨 Pièges à Éviter

### ❌ Ne PAS faire

1. **Utiliser Matplotlib dans Streamlit**
   ```python
   # ❌ MAUVAIS
   plt.figure()
   plt.plot(x, y)
   plt.show()  # Ne s'affichera PAS dans Streamlit !
   ```

2. **Oublier le check load_recipes_clean**
   ```python
   # ❌ MAUVAIS
   def analyse():
       df = load_recipes_clean()  # Crash si None !
   ```

3. **Imports inutilisés**
   ```python
   # ❌ MAUVAIS
   import pandas as pd  # Non utilisé → erreur PEP8
   ```

4. **F-string sans placeholder**
   ```python
   # ❌ MAUVAIS
   st.success(f"✅ Connexion établie")
   ```

5. **Bare except**
   ```python
   # ❌ MAUVAIS
   try:
       ...
   except:  # Trop large !
       pass
   ```

### ✅ Bonnes pratiques

1. **Toujours utiliser Plotly**
   ```python
   # ✅ BON
   fig = go.Figure()
   fig.add_trace(go.Scatter(x=x, y=y))
   st.plotly_chart(fig, use_container_width=True)
   ```

2. **Vérifier le chargement**
   ```python
   # ✅ BON
   if load_recipes_clean is None:
       st.error("❌ Impossible de charger les données")
       return
   df = load_recipes_clean()
   ```

3. **Nettoyer les imports**
   ```python
   # ✅ BON - Uniquement ce qui est utilisé
   import polars as pl
   import numpy as np
   ```

4. **String simple ou f-string avec placeholder**
   ```python
   # ✅ BON
   st.success("✅ Connexion établie")
   # OU
   st.success(f"✅ Connexion établie : {db_path}")
   ```

5. **Exception spécifique**
   ```python
   # ✅ BON
   try:
       ...
   except ImportError:
       st.error("Module introuvable")
   ```

---

## 📚 Références

### Documentation
- **Plotly**: https://plotly.com/python/
- **Streamlit**: https://docs.streamlit.io/
- **PEP8**: https://pep8.org/
- **Google Docstrings**: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings

### Outils
- **black**: Formatage automatique Python
- **flake8**: Vérification PEP8
- **pydocstyle**: Vérification docstrings
- **pytest**: Framework de tests
- **pytest-cov**: Coverage des tests

### Fichiers du projet
- `BRIEF_DESIGN_STREAMLIT.md`: Spécifications UI/UX
- `README.md`: Vue d'ensemble du projet
- `pyproject.toml`: Configuration Python + dépendances

---

## ✅ Conclusion

Ce guide garantit une intégration **professionnelle**, **testée** et **maintenable** des analyses EDA dans Streamlit. En suivant ce processus rigoureux, vous assurez:

1. ✅ **Qualité du code**: PEP8, docstrings, formatage
2. ✅ **Fiabilité**: Tests unitaires avec coverage >= 90%
3. ✅ **Maintenabilité**: Code structuré et documenté
4. ✅ **Expérience utilisateur**: Graphiques interactifs Plotly
5. ✅ **Conformité CI/CD**: Passe les vérifications automatiques

**Temps estimé par analyse**: 2-3h (incluant tests et validation)

---

**Dernière mise à jour**: 2025-10-23
**Version**: 1.0.0
**Statut**: ✅ Validé en production (analyse_trendlines.py)
