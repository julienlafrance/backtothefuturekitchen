# 🔄 Analyse Détaillée - Synchronisation PREPROD → PROD

**Date** : 2025-10-25
**Auteur** : Project team
**Objectif** : Mettre à jour PROD avec la dernière version de PREPROD

---

## 🔍 ANALYSE DES DIFFÉRENCES DE STRUCTURE

### Structure PREPROD (`10_preprod/`)

```
10_preprod/
├── src/
│   └── mangetamain_analytics/          # Code source dans src/
│       ├── main.py                     # 845 lignes (VERSION À JOUR)
│       ├── assets/                     # Logo, CSS, favicon
│       ├── utils/                      # Utilitaires (colors.py, chart_theme.py)
│       ├── visualization/              # 9 modules d'analyse
│       │   ├── analyse_ratings.py      # 41K (nouveau)
│       │   ├── analyse_seasonality.py  # 39K (nouveau)
│       │   ├── analyse_trendlines_v2.py # 75K (nouveau)
│       │   ├── analyse_weekend.py      # 41K (nouveau)
│       │   ├── custom_charts.py        # 3.9K
│       │   └── plotly_config.py        # 4.8K
│       ├── data/                       # Loaders data
│       ├── models/                     # Modèles
│       ├── pages/                      # Pages Streamlit
│       └── templates/                  # Templates
├── data/                               # Base DuckDB + CSV (581 MB)
├── tests/                              # Tests unitaires
├── pyproject.toml                      # Configuration uv
└── uv.lock                             # Lock file
```

### Structure PROD (`20_prod/`)

```
20_prod/
├── streamlit/                          # Code source à la racine streamlit/
│   ├── main.py                         # 512 lignes (ANCIENNE VERSION)
│   ├── logo_btfkitchen.png            # Logo uniquement
│   ├── visualization/                  # Vide (juste __init__.py) ❌
│   ├── data/                           # Loaders data (2 fichiers)
│   │   └── loaders.py
│   ├── models/                         # Vide
│   └── pages/                          # Vide
├── logs/                               # Logs (vide)
├── tests/                              # Tests unitaires
├── pyproject.toml                      # Configuration uv
└── uv.lock                             # Lock file
```

---

## ⚠️ PROBLÈMES IDENTIFIÉS

### 1. **Structure différente**
- PREPROD : Code dans `src/mangetamain_analytics/`
- PROD : Code dans `streamlit/`
- ⚠️ Les imports Python sont différents

### 2. **Fichiers manquants en PROD**

#### Modules de Visualisation (CRITIQUES)
```bash
❌ streamlit/visualization/ est VIDE
```

**Fichiers manquants** :
- `analyse_ratings.py` (41K)
- `analyse_seasonality.py` (39K)
- `analyse_trendlines_v2.py` (75K)
- `analyse_weekend.py` (41K)
- `custom_charts.py` (3.9K)
- `plotly_config.py` (4.8K)

#### Assets (Logo, CSS, Favicon)
```bash
❌ streamlit/assets/ n'existe PAS
```

**Fichiers manquants** :
- `custom.css` (771 lignes de styling)
- `back_to_the_kitchen_logo.png`
- `favicon.ico`

#### Utilitaires (Couleurs & Thème)
```bash
❌ streamlit/utils/ n'existe PAS
```

**Fichiers manquants** :
- `colors.py` (207 lignes - Palette charte graphique)
- `chart_theme.py` (169 lignes - Thème Plotly)
- `__init__.py`

### 3. **main.py obsolète**
- PREPROD : **845 lignes** (intègre 4 analyses complètes)
- PROD : **512 lignes** (version basique)
- ⚠️ PROD n'a PAS les 4 analyses intégrées (Tendances, Saisonnalité, Weekend, Ratings)

### 4. **Imports incompatibles**

**PREPROD (main.py ligne ~10-30)** :
```python
from visualization.analyse_trendlines_v2 import render_trendlines_page
from visualization.analyse_seasonality import render_seasonality_page
from visualization.analyse_weekend import render_weekend_page
from visualization.analyse_ratings import render_ratings_page
from utils.colors import PALETTE
from utils.chart_theme import apply_chart_theme
```

**PROD (main.py ligne ~10)** :
```python
# Aucun import de visualization (dossier vide)
# Aucun import de utils (dossier inexistant)
```

---

## 📋 PLAN DE SYNCHRONISATION

### Étape 1 : Copier les modules de visualisation

**Source** : `10_preprod/src/mangetamain_analytics/visualization/`
**Destination** : `20_prod/streamlit/visualization/`

**Fichiers à copier** :
```bash
analyse_ratings.py           (41K)
analyse_seasonality.py       (39K)
analyse_trendlines_v2.py     (75K)
analyse_weekend.py           (41K)
analyse_ratings_simple.py    (8.5K)
analyse_trendlines.py        (35K - backup)
custom_charts.py             (3.9K)
plotly_config.py             (4.8K)
__init__.py
```

**Commande** :
```bash
cp -r 10_preprod/src/mangetamain_analytics/visualization/*.py \
      20_prod/streamlit/visualization/
```

---

### Étape 2 : Créer et copier le dossier utils

**Source** : `10_preprod/src/mangetamain_analytics/utils/`
**Destination** : `20_prod/streamlit/utils/`

**Fichiers à copier** :
```bash
colors.py        (6.3K - Palette charte graphique)
chart_theme.py   (4.4K - Thème Plotly)
__init__.py      (132 bytes)
```

**Commandes** :
```bash
mkdir -p 20_prod/streamlit/utils
cp -r 10_preprod/src/mangetamain_analytics/utils/*.py \
      20_prod/streamlit/utils/
```

---

### Étape 3 : Créer et copier le dossier assets

**Source** : `10_preprod/src/mangetamain_analytics/assets/`
**Destination** : `20_prod/streamlit/assets/`

**Fichiers à copier** :
```bash
custom.css                      (771 lignes - Styling complet)
back_to_the_kitchen_logo.png   (Logo charte graphique)
favicon.ico                     (Favicon)
```

**Commandes** :
```bash
mkdir -p 20_prod/streamlit/assets
cp -r 10_preprod/src/mangetamain_analytics/assets/* \
      20_prod/streamlit/assets/
```

---

### Étape 4 : Remplacer main.py

**Source** : `10_preprod/src/mangetamain_analytics/main.py` (845 lignes)
**Destination** : `20_prod/streamlit/main.py` (512 lignes)

**Action** :
1. ✅ Sauvegarder l'ancien : `cp main.py main.py.old_$(date +%Y%m%d_%H%M%S)`
2. ✅ Copier le nouveau : `cp 10_preprod/.../main.py 20_prod/streamlit/main.py`

**⚠️ ATTENTION** : Vérifier les imports après copie (pas de `src.`)

---

### Étape 5 : Vérifier et ajuster les imports

**Problème** : PREPROD utilise `src/mangetamain_analytics/` mais PROD utilise `streamlit/`

**Imports PREPROD (à vérifier)** :
```python
from visualization.analyse_trendlines_v2 import ...
from utils.colors import PALETTE
```

**Imports PROD (doivent rester identiques car même structure relative)** :
```python
from visualization.analyse_trendlines_v2 import ...
from utils.colors import PALETTE
```

✅ **Bonne nouvelle** : Les imports relatifs fonctionneront car la structure relative est identique !

---

### Étape 6 : Synchroniser data/ (optionnel)

**Source** : `10_preprod/data/mangetamain.duckdb` (581 MB)
**Destination** : `20_prod/data/mangetamain.duckdb`

**Note** : Vérifier si PROD a déjà la base à jour ou si elle doit être copiée.

---

### Étape 7 : Redéployer PROD

**Sur dataia** :
```bash
cd ~/mangetamain/30_docker
docker-compose -f docker-compose-prod.yml restart
```

**Health check** :
```bash
# Attendre 60s (start_period)
sleep 60
docker logs mange_prod --tail=50
curl -f http://localhost:8501
```

---

## 🎯 RÉSUMÉ DES ACTIONS

### Fichiers à Copier (Total : ~250 KB code)

| Source | Destination | Taille | Status |
|--------|-------------|--------|--------|
| `visualization/*.py` (9 fichiers) | `streamlit/visualization/` | ~250 KB | ❌ À copier |
| `utils/*.py` (3 fichiers) | `streamlit/utils/` | ~11 KB | ❌ À créer + copier |
| `assets/*` (3 fichiers) | `streamlit/assets/` | ~30 KB | ❌ À créer + copier |
| `main.py` | `streamlit/main.py` | 33 KB | ❌ À remplacer |

**Total estimé** : ~324 KB de code à synchroniser

---

## ⚠️ RISQUES ET PRÉCAUTIONS

### Risques Identifiés

1. **Imports cassés** : Si les imports ne fonctionnent pas après copie
   - Solution : Vérifier les imports relatifs dans main.py

2. **Dépendances manquantes** : Si PROD n'a pas les mêmes packages
   - Solution : Vérifier pyproject.toml identique, puis `uv sync`

3. **Base de données obsolète** : Si PROD utilise une vieille base
   - Solution : Copier mangetamain.duckdb depuis PREPROD

4. **Assets non trouvés** : Si les chemins CSS/logo sont incorrects
   - Solution : Vérifier les chemins dans main.py

### Précautions Obligatoires

1. ✅ **Backup avant sync** :
   ```bash
   tar -czf backup_prod_$(date +%Y%m%d_%H%M%S).tar.gz 20_prod/
   ```

2. ✅ **Test en local avant push** :
   ```bash
   cd 20_prod
   uv run streamlit run streamlit/main.py
   ```

3. ✅ **Vérifier les logs Docker** après redémarrage

4. ✅ **Rollback plan** : Garder `main.py.old` et archives backup

---

## 📝 CHECKLIST DE VALIDATION

### Avant Synchronisation
- [ ] Backup complet de 20_prod/ créé
- [ ] Vérifier que PREPROD fonctionne correctement
- [ ] Lire ce document en entier

### Pendant Synchronisation
- [ ] Copier visualization/ (9 fichiers)
- [ ] Créer et copier utils/ (3 fichiers)
- [ ] Créer et copier assets/ (3 fichiers)
- [ ] Sauvegarder puis remplacer main.py
- [ ] Vérifier pyproject.toml identique

### Après Synchronisation (sur dataia)
- [ ] Rsync local → dataia (si nécessaire)
- [ ] Redémarrer container PROD
- [ ] Attendre health check (60s)
- [ ] Vérifier logs : aucune erreur import
- [ ] Tester URL : http://localhost:8501
- [ ] Vérifier les 4 analyses s'affichent
- [ ] Vérifier CSS/logo appliqués

---

## 🚀 COMMANDES RÉSUMÉES

```bash
# 1. Backup PROD
cd /home/julien/code/mangetamain/000_dev
tar -czf backup_prod_$(date +%Y%m%d_%H%M%S).tar.gz 20_prod/

# 2. Créer dossiers manquants
mkdir -p 20_prod/streamlit/utils
mkdir -p 20_prod/streamlit/assets

# 3. Copier visualization
cp 10_preprod/src/mangetamain_analytics/visualization/*.py \
   20_prod/streamlit/visualization/

# 4. Copier utils
cp 10_preprod/src/mangetamain_analytics/utils/*.py \
   20_prod/streamlit/utils/

# 5. Copier assets
cp 10_preprod/src/mangetamain_analytics/assets/* \
   20_prod/streamlit/assets/

# 6. Sauvegarder et remplacer main.py
cp 20_prod/streamlit/main.py \
   20_prod/streamlit/main.py.old_$(date +%Y%m%d_%H%M%S)
cp 10_preprod/src/mangetamain_analytics/main.py \
   20_prod/streamlit/main.py

# 7. Rsync vers dataia (si nécessaire)
rsync -avz --progress 20_prod/ dataia:~/mangetamain/20_prod/

# 8. Redémarrer PROD sur dataia
ssh dataia "cd ~/mangetamain/30_docker && \
            docker-compose -f docker-compose-prod.yml restart"

# 9. Vérifier après 60s
sleep 60
ssh dataia "docker logs mange_prod --tail=100"
```

---

## 📊 IMPACT ESTIMÉ

### Avant Synchronisation (PROD actuel)
- ❌ main.py : 512 lignes (basique)
- ❌ Aucune analyse intégrée
- ❌ Pas de charte graphique
- ❌ Logo basique uniquement

### Après Synchronisation (PROD mis à jour)
- ✅ main.py : 845 lignes (complet)
- ✅ 4 analyses intégrées (Tendances, Saisonnalité, Weekend, Ratings)
- ✅ Charte graphique "Back to the Kitchen" complète
- ✅ 9 modules de visualisation (250 KB)
- ✅ Utilitaires couleurs + thème Plotly
- ✅ Assets (CSS 771 lignes + logo + favicon)

**Résultat** : PROD aura exactement la même version que PREPROD ✅

---

**Document créé le** : 2025-10-25
**Prêt pour exécution** : ⏳ En attente validation utilisateur

