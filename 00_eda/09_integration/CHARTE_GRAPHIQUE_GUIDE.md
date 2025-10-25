# Guide Charte Graphique "Back to the Kitchen"

**Date de création:** 2025-10-24
**Dernière mise à jour:** 2025-10-25 (Synchronisé avec implémentation réelle)
**Projet:** Mangetamain Analytics - Application Streamlit Preprod
**Conformité:** ✅ 100% synchronisé avec le code en production

---

## 🎨 Vue d'ensemble

Charte graphique dark theme inspirée du logo "Back to the Kitchen" avec palette orange/noir/gris.

---

## 📁 Architecture des fichiers

```
10_preprod/src/mangetamain_analytics/
├── utils/
│   ├── colors.py              # Palette de couleurs centralisée
│   ├── chart_theme.py         # Thème Plotly réutilisable
│   └── __init__.py
├── assets/
│   ├── custom.css             # Styles CSS Streamlit (externe)
│   ├── back_to_the_kitchen_logo.png  # Logo 200x200
│   ├── favicon.ico            # Favicon multi-résolution (16/32/48)
│   └── favicon.png            # Favicon 32x32 pour web
├── .streamlit/
│   └── config.toml            # Configuration thème Streamlit
└── main.py                    # Application principale
```

---

## 🎨 Palette de couleurs (`utils/colors.py`)

### Couleurs principales (logo)
```python
ORANGE_PRIMARY = "#FF8C00"    # Orange vif - couleur principale du logo
ORANGE_SECONDARY = "#E24E1B"  # Rouge/Orange profond - base dégradé logo
ORANGE_LIGHT = "#FFA07A"      # Saumon - teinte douce du dégradé
```

### Fonds et surfaces
```python
BACKGROUND_MAIN = "#1e1e1e"     # Gris foncé - zone principale
BACKGROUND_SIDEBAR = "#000000"  # Noir pur - sidebar
BACKGROUND_CARD = "#333333"     # Gris moyen - cards et widgets
```

### Texte (hiérarchie)
```python
TEXT_PRIMARY = "#e0e0e0"    # Gris clair - texte principal
TEXT_SECONDARY = "#888888"  # Gris moyen - texte secondaire
TEXT_WHITE = "#ffffff"      # Blanc - texte important
```

### Couleurs graphiques
```python
CHART_COLORS = [
    "#FF8C00",  # Base Orange (du milieu du dégradé du logo)
    "#FFD700",  # Base Jaune (du point lumineux du dégradé du logo)
    "#E24E1B",  # Rouge/Orange Profond (de la base du dégradé du logo)
    "#1E90FF",  # Bleu Vif (du contour et des effets de vitesse)
    "#00CED1",  # Cyan (accent technologique du logo)
    "#FFA07A",  # Saumon (teinte plus douce du dégradé orange)
    "#B0E0E6",  # Bleu Clair (teinte plus claire du contour bleu)
    "#DAA520",  # Jaune Doré (pour une variation riche du jaune)
]
```

### États
```python
SUCCESS = "#28A745"   # Vert - succès, PROD badge
WARNING = "#FFC107"   # Jaune - warnings, PREPROD badge
ERROR = "#DC3545"     # Rouge - erreurs
INFO = "#17A2B8"      # Cyan - informations
```

---

## 📊 Thème Plotly (`utils/chart_theme.py`)

### Fonction principale: `apply_chart_theme(fig, title=None)`

Applique le thème dark sur une figure Plotly:

```python
from utils import chart_theme

fig = go.Figure()
# ... ajout traces ...
chart_theme.apply_chart_theme(fig, title="Mon graphique")
st.plotly_chart(fig)
```

**Configuration appliquée:**
- Fonds transparents (plot_bgcolor, paper_bgcolor)
- Police: Inter sans-serif, 12px, couleur TEXT_PRIMARY
- Titres: orange (ORANGE_PRIMARY), 16px, Michroma, centrés
- Grilles: #444444, 1px
- Axes: labels 12px, titres 13px ✅ (Corrigé le 2025-10-25)
- Légende: fond rgba(42,42,42,0.8) avec bordure
- Hover: fond BACKGROUND_CARD, bordure orange, texte blanc

### Fonction subplots: `apply_subplot_theme(fig, num_rows=1, num_cols=2)`

Pour graphiques avec subplots:

```python
fig = make_subplots(rows=1, cols=2, subplot_titles=("Graph 1", "Graph 2"))
# ... ajout traces ...
chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)
```

**Spécificités:**
- Applique thème global + config par subplot
- Titres subplots en orange (13px)
- Grilles et axes configurés pour chaque subplot

### Fonctions utilitaires

```python
# Couleur principale pour barres
bar_color = chart_theme.get_bar_color()  # → CHART_COLORS[0]

# Couleurs pour lignes multiples
line_colors = chart_theme.get_line_colors()  # → CHART_COLORS (liste)

# Couleur pour scatter plots
scatter_color = chart_theme.get_scatter_color()  # → CHART_COLORS[1]

# Couleur pour lignes de référence (régression, etc)
ref_line_color = chart_theme.get_reference_line_color()  # → ERROR (rouge)
```

---

## 🎯 CSS Streamlit (`assets/custom.css`)

### Chargement dans main.py
```python
with open("src/mangetamain_analytics/assets/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
```

### Éléments stylisés

**Sidebar (fond noir)**
```css
[data-testid="stSidebar"] {
    background-color: #000000;
}
```

**Zone principale (gris foncé)**
```css
.main, .stApp {
    background-color: #1e1e1e;
}
```

**Navigation (radio buttons avec états)**
```css
/* État inactif */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    background-color: rgba(51, 51, 51, 0.5);
    padding: 12px 15px;
    border: 1px solid rgba(240, 240, 240, 0.1);
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}

/* État actif - Gradient orange-jaune */
[data-testid="stSidebar"] .stRadio input:checked + div {
    background: linear-gradient(90deg, #FF8C00 0%, #FFD700 100%);
    color: #1E1E1E;
    border: 1px solid #FFD700;
    box-shadow: 0 2px 8px rgba(255, 140, 0, 0.3);
}

/* État hover */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background-color: rgba(255, 215, 0, 0.1);
    border-color: #FFD700;
}
```

**Boutons primaires (orange)**
```css
.stButton > button {
    background: linear-gradient(90deg, #FF8C00 0%, #FFD700 100%);
    color: #1E1E1E;
    border: 1px solid #FFD700;
    font-family: 'Inter', sans-serif;
    width: 100%;
}
```

**Messages info (warm kitchen theme)**
```css
[data-baseweb="notification"] {
    background: #333333 !important;
    border-left: 4px solid #FF8C00 !important;
    box-shadow: 0 2px 8px rgba(255, 140, 0, 0.15) !important;
    color: #F0F0F0 !important;
}

[data-baseweb="notification"] svg {
    fill: #FFD700 !important;
}
```

---

## 📐 Tailles de police

### Tailles appliquées (depuis correction 10px → 12px)

**Graphiques Plotly:**
- Labels axes (tick labels): **12px**
- Titres axes: **13px**
- Valeurs sur barres: **12px**
- Titre principal: **16px**

**Interface Streamlit:**
- Texte général: **12px** (défini dans font.size)
- Headers H1/H2/H3: tailles par défaut Streamlit
- Métriques: 2rem (valeur) / 0.875rem (label)

---

## 🔧 Configuration Streamlit (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#FF8C00"
backgroundColor = "#1E1E1E"
secondaryBackgroundColor = "#333333"
textColor = "#F0F0F0"
font = "sans serif"
```

---

## 🎨 Favicon

### Création du favicon

Le favicon a été créé depuis le logo principal avec ImageMagick :

```bash
# Favicon multi-résolution .ico (16x16, 32x32, 48x48)
convert back_to_the_kitchen_logo.png -resize 16x16 /tmp/favicon_16.png
convert back_to_the_kitchen_logo.png -resize 32x32 /tmp/favicon_32.png
convert back_to_the_kitchen_logo.png -resize 48x48 /tmp/favicon_48.png
convert /tmp/favicon_16.png /tmp/favicon_32.png /tmp/favicon_48.png favicon.ico

# Favicon PNG 32x32 pour web
convert back_to_the_kitchen_logo.png -resize 32x32 favicon.png
```

### Intégration dans Streamlit

```python
# Dans main.py
st.set_page_config(
    page_title="Mangetamain Analytics",
    page_icon="src/mangetamain_analytics/assets/favicon.png",
    layout="wide"
)
```

### Fichiers générés

- **favicon.ico** : 8.5 KB (multi-résolution pour navigateurs)
- **favicon.png** : 1.8 KB (32x32 pour Streamlit)

---

## 📊 Exemples d'intégration

### Exemple 1: Graphique simple (Volume de recettes)

```python
from utils import chart_theme
import plotly.graph_objects as go

# Récupérer couleur
bar_color = chart_theme.get_bar_color()

# Créer figure
fig = go.Figure()

# Ajouter trace avec thème
fig.add_trace(
    go.Bar(
        x=years,
        y=counts,
        marker=dict(
            color=bar_color,
            opacity=0.85,
            line=dict(width=0)
        ),
        text=[f"{val:,}" for val in counts],
        textposition="outside",
        textfont=dict(size=12, color=chart_theme.colors.TEXT_PRIMARY),
        hovertemplate="<b>Année %{x}</b><br>Recettes: %{y:,}<extra></extra>",
    )
)

# Appliquer thème
chart_theme.apply_chart_theme(fig, title="Volume de recettes")

# Afficher
st.plotly_chart(fig, use_container_width=True)
```

### Exemple 2: Subplots (Bar + Q-Q plot)

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Créer subplots
fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("Nombre de recettes par année", "Q-Q Plot"),
    horizontal_spacing=0.12,
)

# SUBPLOT 1: Bar chart
fig.add_trace(
    go.Bar(
        x=data["year"],
        y=data["count"],
        marker=dict(color=chart_theme.get_bar_color(), opacity=0.85),
        textfont=dict(size=12, color=chart_theme.colors.TEXT_PRIMARY),
    ),
    row=1,
    col=1,
)

# SUBPLOT 2: Q-Q plot
fig.add_trace(
    go.Scatter(
        x=quantiles_theo,
        y=quantiles_obs,
        mode="markers",
        marker=dict(
            color=chart_theme.get_scatter_color(),
            size=8,
            opacity=0.7
        ),
    ),
    row=1,
    col=2,
)

# Ligne de référence (régression)
fig.add_trace(
    go.Scatter(
        x=quantiles_theo,
        y=regression_line,
        mode="lines",
        line=dict(
            color=chart_theme.get_reference_line_color(),
            width=2,
            dash="dash"
        ),
        name="Régression",
    ),
    row=1,
    col=2,
)

# Appliquer thème subplots
chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)

# Afficher
st.plotly_chart(fig, use_container_width=True)
```

### Exemple 3: Ligne + scatter avec couleurs multiples

```python
line_colors = chart_theme.get_line_colors()

fig = go.Figure()

# Plusieurs lignes avec couleurs différentes
for i, metric in enumerate(metrics):
    fig.add_trace(
        go.Scatter(
            x=years,
            y=values[metric],
            mode="lines+markers",
            name=metric,
            line=dict(color=line_colors[i % len(line_colors)], width=2),
            marker=dict(size=6),
        )
    )

chart_theme.apply_chart_theme(fig, title="Évolution temporelle")
st.plotly_chart(fig, use_container_width=True)
```

---

## 🚀 Workflow de transformation d'un graphique

### Étape 1: Import du thème
```python
from utils import chart_theme
```

### Étape 2: Remplacer couleurs hardcodées
**Avant:**
```python
marker=dict(color="#ff8c42", ...)
```

**Après:**
```python
marker=dict(color=chart_theme.get_bar_color(), ...)
```

### Étape 3: Appliquer le thème
**Avant:**
```python
fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    # ... config manuelle ...
)
```

**Après:**
```python
chart_theme.apply_chart_theme(fig, title="Mon titre")
# ou pour subplots:
chart_theme.apply_subplot_theme(fig, num_rows=1, num_cols=2)
```

### Étape 4: Vérifier les tailles de police
- Tick labels: 12px minimum
- Valeurs sur barres/points: 12px minimum
- Titres axes: 13px minimum

### Étape 5: Tester le thème dark
- Vérifier lisibilité sur fond #1e1e1e
- Vérifier contraste des textes
- Vérifier hover labels

---

## 🎨 Menu Sidebar - Navigation et Badges

### Vue d'ensemble

La sidebar contient 3 zones principales :
1. **Logo** - "Back to the Kitchen" en haut
2. **Navigation** - Menu avec titre, intro et options analysées
3. **Badges** - Statut S3 et environnement (PREPROD/PROD) en bas

### CSS Variables

Toutes les couleurs sont centralisées dans `:root` pour faciliter la maintenance :

```css
:root {
    --primary-color: #FF8C00;
    --secondary-accent: #FFD700;
    --background-color: #1E1E1E;
    --secondary-background-color: #333333;
    --text-color: #F0F0F0;
    --text-secondary-color: #888888;
    --font-heading: 'Michroma', sans-serif;
    --font-body: 'Inter', sans-serif;
    --success-color: #28A745;
    --warning-color: #FFC107;
    --error-color: #DC3545;
    --info-color: #17A2B8;
}
```

### Titre "ANALYSES"

**HTML Python:**
```python
st.markdown('<h3 class="sidebar-category-title">ANALYSES</h3>', unsafe_allow_html=True)
```

**CSS:**
```css
[data-testid="stSidebar"] h3.sidebar-category-title {
    font-family: var(--font-heading);  /* Michroma */
    color: var(--primary-color);        /* #FF8C00 */
    font-size: 1.2em;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding-top: 20px;
    margin-bottom: 5px;
}
```

### Texte Introductif

**HTML Python:**
```python
st.markdown('<p class="sidebar-subtitle">CHOISIR UNE ANALYSE:</p>', unsafe_allow_html=True)
```

**CSS:**
```css
[data-testid="stSidebar"] .sidebar-subtitle {
    font-family: var(--font-body);  /* Inter */
    color: var(--text-color);       /* #F0F0F0 */
    font-size: 0.9em;
    margin-bottom: 15px;
    font-weight: 400;
}
```

### Navigation - États des Boutons

Les boutons de navigation ont 3 états : **inactif**, **hover**, **actif**.

**Structure HTML:**
```python
selected_page = st.radio(
    "Navigation",
    ["Analyses Saisonnières", "Effet Jour/Week-end", "Recommandations", "Tendances 1999-2018 - test"],
    index=0,
    label_visibility="collapsed"
)
```

**CSS - État Inactif:**
```css
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    background-color: rgba(51, 51, 51, 0.5);
    padding: 12px 15px;
    border-radius: 8px;
    margin: 6px 0;
    transition: all 0.3s ease;
    border: 1px solid rgba(240, 240, 240, 0.1);
    font-family: 'Inter', sans-serif;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}
```

**CSS - État Hover:**
```css
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background-color: rgba(255, 215, 0, 0.1);
    border-color: #FFD700;
}
```

**CSS - État Actif:**
```css
[data-testid="stSidebar"] .stRadio input:checked + div {
    background: linear-gradient(90deg, #FF8C00 0%, #FFD700 100%);
    border-radius: 8px;
    padding: 12px 15px;
    font-weight: bold;
    color: #1E1E1E;  /* Texte noir sur fond orange */
    border: 1px solid #FFD700;
    box-shadow: 0 2px 8px rgba(255, 140, 0, 0.3);
}
```

### Icônes Lucide

Les icônes sont injectées via CSS `::before` avec SVG en data URL :

| Option | Icône Lucide | Usage |
|--------|--------------|-------|
| Analyses Saisonnières | `calendar-days` | Analyses par saison |
| Effet Jour/Week-end | `sun` | Analyses week-end |
| Recommandations | `sparkles` | Système recommandations |
| Tendances 1999-2018 | `bar-chart-2` | Analyses temporelles |

**Exemple CSS icône:**
```css
/* Icône calendar-days - blanc quand inactif */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:nth-child(1)::before {
    content: "";
    display: inline-block;
    width: 18px;
    height: 18px;
    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"...stroke="%23F0F0F0"...</svg>');
    background-size: contain;
    background-repeat: no-repeat;
}

/* Icône calendar-days - noir quand actif */
[data-testid="stSidebar"] .stRadio input:checked + div[data-baseweb="radio"]:nth-child(1)::before {
    background-image: url('data:image/svg+xml,...stroke="%231E1E1E"...');
}
```

### Badges Pill

Les badges sont positionnés en bas de la sidebar avec classes CSS réutilisables.

**Badge S3 Ready/Error:**

```python
# Python - Utilise icône SVG Lucide check-circle
st.markdown(
    f"""
    <div class="s3-ready-indicator">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <span>S3 {"Ready" if s3_ready else "Error"}</span>
    </div>
    """,
    unsafe_allow_html=True
)
```

```css
/* CSS */
.s3-ready-indicator {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background-color: var(--info-color);  /* #17A2B8 par défaut */
    color: var(--text-color);
    border-radius: 50px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    font-family: var(--font-body);
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.s3-ready-indicator.error {
    background-color: var(--error-color);  /* #DC3545 */
}

.s3-ready-indicator.success {
    background-color: var(--success-color);  /* #28A745 */
}
```

**Badge PREPROD/PROD:**

```python
# Python - Utilise icône SVG Lucide circle-dot
if "PREPROD" in env:
    badge_class = "env-badge preprod-badge"
    label = "PREPROD"
elif "PROD" in env:
    badge_class = "env-badge prod-badge"
    label = "PRODUCTION"

st.markdown(
    f"""
    <div class="{badge_class}">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="2"/>
        </svg>
        <span>{label}</span>
    </div>
    """,
    unsafe_allow_html=True
)
```

```css
/* CSS - Classe générique env-badge */
.env-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border-radius: 50px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 700;
    font-family: var(--font-body);
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.preprod-badge {
    background-color: var(--warning-color);  /* #FFC107 */
    color: var(--secondary-background-color);  /* #333333 - texte foncé */
}

.prod-badge {
    background-color: var(--success-color);  /* #28A745 */
    color: var(--text-color);  /* #F0F0F0 - texte clair */
}
```

### Container Badges en Bas

```css
.sidebar-badges {
    margin-top: auto;  /* Pousse en bas avec flexbox */
    padding: 15px 0;
    border-top: 1px solid rgba(240, 240, 240, 0.1);
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
}
```

### Structure Finale Sidebar

```
┌─────────────────────────────┐
│  🍳 Back to the Kitchen     │ ← Logo
│  (Image PNG)                │
├─────────────────────────────┤
│  ANALYSES                   │ ← Titre h3 (Michroma, orange)
│  Choisir une analyse :      │ ← Texte p (Inter, gris clair)
│                             │
│  📅 Analyses Saisonnières   │ ← st.radio avec icônes Lucide
│  ☀️ Effet Jour/Week-end     │   États: inactif/hover/actif
│  ✨ Recommandations         │   Gradient orange → jaune actif
│  📊 Tendances 1999-2018     │
│                             │
│         (espace flex)       │
│                             │
├─────────────────────────────┤
│  ● S3 Ready                 │ ← Badge pill (cyan/vert/rouge)
│  ● PREPROD                  │ ← Badge pill (jaune/vert)
└─────────────────────────────┘
```

### Bouton Rafraîchir

**Ajout post-guide :** Un bouton "🔄 Rafraîchir" a été ajouté pour vider le cache Streamlit.

```python
# Python
if st.button("🔄 Rafraîchir", key="btn_refresh", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
```

**CSS :** Le bouton utilise le style primaire avec dégradé orange (défini dans `custom.css` lignes 400-419).

### Checklist Menu Sidebar

- [x] Titre "ANALYSES" avec classe `sidebar-category-title`
- [x] Texte intro avec classe `sidebar-subtitle`
- [x] Navigation `st.radio` avec `label_visibility="collapsed"`
- [x] Icônes Lucide injectées via CSS `::before`
- [x] 3 états navigation (inactif/hover/actif) stylisés
- [x] Badge S3 avec classe `s3-ready-indicator`
- [x] Badge environnement avec classe `env-badge preprod-badge`/`prod-badge`
- [x] Container badges avec flexbox en bas de sidebar
- [x] CSS Variables `:root` utilisées partout
- [x] Bouton "Rafraîchir" ajouté (utile pour vider cache)

---

## 📋 Checklist transformation graphique

- [ ] Import `from utils import chart_theme`
- [ ] Couleurs remplacées par fonctions `get_*_color()`
- [ ] `apply_chart_theme()` ou `apply_subplot_theme()` appelé
- [ ] Tailles police >= 12px
- [ ] `textfont` utilise `chart_theme.colors.TEXT_PRIMARY`
- [ ] Hover template configuré
- [ ] Test visuel sur fond dark
- [ ] `use_container_width=True` dans `st.plotly_chart()`

---

## 🎯 Fichiers à transformer

### Déjà transformés ✅
- `visualization/analyse_trendlines_v2.py` - Volume de recettes (bar + Q-Q)

### À transformer 🔄
Tous les autres graphiques dans:
- `visualization/analyse_trendlines_v2.py` (durée, complexité, nutrition, ingrédients, tags)
- `visualization/custom_charts.py` (correlation heatmap, distribution, time series, scatter)
- Tout autre module de visualisation futur

---

## 🎁 Éléments Bonus (Non prévus initialement)

L'implémentation a ajouté des améliorations au-delà du guide initial :

### 1. Suppression espaces en haut
```css
/* Lignes 34-47 de custom.css */
.main .block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}
```
**Bénéfice :** Maximise l'espace vertical, design plus moderne.

### 2. Scrollbars personnalisées
```css
/* Lignes 742-758 de custom.css */
::-webkit-scrollbar {
    width: 8px;
    background: #1a1a1a;
}
::-webkit-scrollbar-thumb {
    background: #444444;
    border-radius: 4px;
}
```
**Bénéfice :** Cohérence visuelle avec la charte sombre.

### 3. Dataframes stylisés
```css
/* Lignes 494-531 de custom.css */
[data-testid="stDataFrame"] thead tr th {
    background-color: #1a1a1a !important;
    color: #FF8C00 !important;
}
```
**Bénéfice :** Tableaux lisibles sur fond sombre avec headers orange.

### 4. Responsive design
```css
/* Lignes 764-770 de custom.css */
@media (max-width: 768px) {
    .footer { flex-direction: column; }
}
```
**Bénéfice :** Adaptation mobile/tablette.

### 5. Messages style "warm kitchen"
```css
/* Lignes 538-593 de custom.css */
[data-baseweb="notification"] {
    background: #333333 !important;
    border-left: 4px solid #FF8C00 !important;
    box-shadow: 0 2px 8px rgba(255, 140, 0, 0.15) !important;
}
```
**Bénéfice :** Messages stylisés avec bordure orange chaleureuse.

---

## 💡 Notes importantes

1. **Compatibilité**: Le thème fonctionne avec tous les types de graphiques Plotly (Bar, Scatter, Line, Heatmap, etc.)

2. **Performance**: Appliquer le thème en une fois via `apply_chart_theme()` est plus performant que configurer manuellement chaque élément

3. **Cohérence**: Toujours utiliser les couleurs de `colors.py` - jamais de couleurs hardcodées

4. **Extensibilité**: Pour ajouter une nouvelle couleur, l'ajouter dans `colors.py` puis créer une fonction getter dans `chart_theme.py` si nécessaire

5. **CSS externe**: Le fichier `custom.css` est chargé une seule fois au démarrage de l'app - modifications nécessitent redémarrage

6. **Streamlit config**: Le fichier `.streamlit/config.toml` configure le thème global mais CSS externe peut override certains éléments

7. **CSS exhaustif**: Avec 771 lignes, le fichier `custom.css` dépasse largement le guide initial et couvre tous les composants Streamlit

---

## 🔗 Références

- **Palette originale**: Logo "Back to the Kitchen" (fichier image)
- **Plotly docs**: https://plotly.com/python/
- **Streamlit theming**: https://docs.streamlit.io/library/advanced-features/theming
- **Colors.py**: `/home/julien/code/mangetamain/000_dev/10_preprod/src/mangetamain_analytics/utils/colors.py`
- **Chart_theme.py**: `/home/julien/code/mangetamain/000_dev/10_preprod/src/mangetamain_analytics/utils/chart_theme.py`
