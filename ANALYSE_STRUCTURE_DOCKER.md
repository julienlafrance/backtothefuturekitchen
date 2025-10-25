# 🐳 Analyse Structure Docker - PREPROD vs PROD

**Date** : 2025-10-25
**Auteur** : Project team

---

## 📊 COMPARAISON DES MONTAGES DOCKER

### PREPROD Docker (`docker-compose-preprod.yml`)

```yaml
volumes:
  - ../10_preprod/src:/app/src:ro              # ⚠️ Monte tout src/
  - ../10_preprod/data:/app/data
  - ../10_preprod/logs:/app/logs

command:
  uv run streamlit run src/mangetamain_analytics/main.py

working_dir: /app
```

**Structure DANS le container PREPROD** :
```
/app/
├── src/
│   └── mangetamain_analytics/          # ← Chemin complet
│       ├── main.py
│       ├── visualization/
│       ├── utils/
│       └── assets/
├── data/
│   └── mangetamain.duckdb
└── logs/
```

**Commande de lancement** : `streamlit run src/mangetamain_analytics/main.py`
**Working directory** : `/app`

---

### PROD Docker (`docker-compose-prod.yml`)

```yaml
volumes:
  - ../20_prod/streamlit:/app/streamlit:ro    # ⚠️ Monte streamlit/ directement
  - ../20_prod/data:/app/data
  - ../20_prod/logs:/app/logs

command:
  uv run streamlit run streamlit/main.py

working_dir: /app
```

**Structure DANS le container PROD** :
```
/app/
├── streamlit/                           # ← Pas de niveau mangetamain_analytics
│   ├── main.py
│   ├── visualization/
│   ├── utils/
│   └── assets/
├── data/
│   └── mangetamain.duckdb
└── logs/
```

**Commande de lancement** : `streamlit run streamlit/main.py`
**Working directory** : `/app`

---

## ⚠️ PROBLÈME IDENTIFIÉ

### Chemins dans main.py PREPROD (actuels)

```python
# Ligne 123 - Favicon
page_icon="src/mangetamain_analytics/assets/favicon.png"

# Ligne 130 - Base de données
db_path = "data/mangetamain.duckdb"  # ✅ OK (relatif à /app)

# Ligne 538 - CSS
css_path = Path("src/mangetamain_analytics/assets/custom.css")

# Ligne 552 - Logo
logo_path = Path("src/mangetamain_analytics/assets/back_to_the_kitchen_logo.png")
```

### Ce qui se passe dans les containers

**PREPROD** :
- Working dir : `/app`
- Streamlit lancé depuis : `/app`
- Chemin `src/mangetamain_analytics/assets/favicon.png` → `/app/src/mangetamain_analytics/assets/favicon.png` ✅

**PROD** :
- Working dir : `/app`
- Streamlit lancé depuis : `/app`
- Chemin `src/mangetamain_analytics/assets/favicon.png` → `/app/src/mangetamain_analytics/assets/favicon.png` ❌ N'EXISTE PAS
- Le bon chemin serait : `streamlit/assets/favicon.png` → `/app/streamlit/assets/favicon.png`

---

## 🎯 SOLUTION : Utiliser des Chemins Relatifs au fichier main.py

### Principe

Au lieu de chemins relatifs à `/app` (working dir), utiliser des chemins relatifs à `main.py` lui-même avec `__file__`.

### Code à modifier dans main.py

#### Avant (chemins en dur)
```python
# Ligne 123
page_icon="src/mangetamain_analytics/assets/favicon.png"

# Ligne 538
css_path = Path("src/mangetamain_analytics/assets/custom.css")

# Ligne 552
logo_path = Path("src/mangetamain_analytics/assets/back_to_the_kitchen_logo.png")
```

#### Après (chemins relatifs)
```python
# En haut du fichier, après les imports
SCRIPT_DIR = Path(__file__).parent  # Répertoire contenant main.py
ASSETS_DIR = SCRIPT_DIR / "assets"

# Ligne 123
page_icon=str(ASSETS_DIR / "favicon.png")

# Ligne 538
css_path = ASSETS_DIR / "custom.css"

# Ligne 552
logo_path = ASSETS_DIR / "back_to_the_kitchen_logo.png"
```

### Pourquoi ça fonctionne ?

**PREPROD** :
- `__file__` = `/app/src/mangetamain_analytics/main.py`
- `Path(__file__).parent` = `/app/src/mangetamain_analytics/`
- `ASSETS_DIR` = `/app/src/mangetamain_analytics/assets/` ✅

**PROD** :
- `__file__` = `/app/streamlit/main.py`
- `Path(__file__).parent` = `/app/streamlit/`
- `ASSETS_DIR` = `/app/streamlit/assets/` ✅

✅ **Les chemins fonctionnent dans les DEUX environnements !**

---

## 📝 LISTE COMPLÈTE DES MODIFICATIONS À FAIRE

### 1. Ajouter en début de fichier (après imports)
```python
# Configuration des chemins relatifs (fonctionne en PREPROD et PROD)
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / "assets"
```

### 2. Remplacer tous les chemins vers assets/

**Rechercher** : `"src/mangetamain_analytics/assets/`
**Remplacer par** : `str(ASSETS_DIR /`

**Occurrences à modifier** :
- Ligne ~123 : `page_icon=`
- Ligne ~538 : `css_path =`
- Ligne ~552 : `logo_path =`

### 3. Vérifier le chemin data/

Le chemin `data/mangetamain.duckdb` fonctionne déjà car :
- PREPROD : `/app/data/mangetamain.duckdb` ✅
- PROD : `/app/data/mangetamain.duckdb` ✅

Pas de modification nécessaire.

---

## ✅ RÉSULTAT ATTENDU

Après modification, le **même fichier main.py** fonctionnera dans les deux environnements :

### Structure finale identique (vue du code)
```python
from visualization.analyse_trendlines_v2 import ...  # ✅ Imports relatifs OK
from utils.colors import ...                          # ✅ Imports relatifs OK

ASSETS_DIR = Path(__file__).parent / "assets"        # ✅ Chemin dynamique
css_path = ASSETS_DIR / "custom.css"                  # ✅ Fonctionne partout
```

### Copie directe possible
```bash
# Après modification du main.py en PREPROD
cp 10_preprod/src/mangetamain_analytics/main.py \
   20_prod/streamlit/main.py

# ✅ Aucun ajustement nécessaire
# ✅ Fonctionne immédiatement en PROD
```

---

## 🚀 PLAN D'ACTION RÉVISÉ

### Étape 1 : Modifier main.py en PREPROD (local)
1. Ajouter `SCRIPT_DIR` et `ASSETS_DIR`
2. Remplacer les 3 occurrences de chemins assets/
3. Tester localement en PREPROD

### Étape 2 : Vérifier que PREPROD fonctionne toujours
```bash
cd 10_preprod
uv run streamlit run src/mangetamain_analytics/main.py
```

### Étape 3 : Copier vers PROD (comme prévu)
```bash
# Copier tous les fichiers
cp -r 10_preprod/src/mangetamain_analytics/visualization/*.py 20_prod/streamlit/visualization/
cp -r 10_preprod/src/mangetamain_analytics/utils/*.py 20_prod/streamlit/utils/
cp -r 10_preprod/src/mangetamain_analytics/assets/* 20_prod/streamlit/assets/

# Copier le main.py modifié
cp 10_preprod/src/mangetamain_analytics/main.py 20_prod/streamlit/main.py
```

### Étape 4 : Tester en PROD local
```bash
cd 20_prod
uv run streamlit run streamlit/main.py
```

### Étape 5 : Déployer sur dataia
```bash
rsync -avz 20_prod/ dataia:~/mangetamain/20_prod/
ssh dataia "cd ~/mangetamain/30_docker && docker-compose -f docker-compose-prod.yml restart"
```

---

## 📋 MODIFICATIONS PRÉCISES À APPORTER

### Fichier : `10_preprod/src/mangetamain_analytics/main.py`

**Après la ligne 13** (`import os`) :
```python
# Configuration des chemins relatifs (fonctionne en PREPROD et PROD)
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / "assets"
```

**Ligne ~123** (page_icon) :
```python
# AVANT
page_icon="src/mangetamain_analytics/assets/favicon.png",

# APRÈS
page_icon=str(ASSETS_DIR / "favicon.png"),
```

**Ligne ~538** (css_path) :
```python
# AVANT
css_path = Path("src/mangetamain_analytics/assets/custom.css")

# APRÈS
css_path = ASSETS_DIR / "custom.css"
```

**Ligne ~552** (logo_path) :
```python
# AVANT
logo_path = Path("src/mangetamain_analytics/assets/back_to_the_kitchen_logo.png")

# APRÈS
logo_path = ASSETS_DIR / "back_to_the_kitchen_logo.png"
```

---

## ✅ AVANTAGES DE CETTE SOLUTION

1. **Portabilité** : Le code fonctionne partout
2. **Pas de condition if/else** : Pas besoin de tester l'environnement
3. **Copie directe** : Aucun ajustement après copie
4. **Maintenance** : Un seul code source
5. **GitHub Actions** : Le script de déploiement sera simple

---

**Document créé le** : 2025-10-25
**Status** : ✅ Solution identifiée, prête à implémenter
