# Guide Charte Graphique "Back to the Kitchen"

**Date:** 2025-10-24
**Projet:** Mangetamain Analytics - Application Streamlit Preprod

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
│   └── custom.css             # Styles CSS Streamlit (externe)
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
BACKGROUND_CARD = "#2a2a2a"     # Gris moyen - cards
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
- Police: sans-serif, 12px, couleur TEXT_PRIMARY
- Titres: orange (ORANGE_PRIMARY), 16px, centrés
- Grilles: #444444, 1px
- Axes: labels 12px, titres 13px
- Légende: fond #2a2a2a avec bordure
- Hover: fond BACKGROUND_CARD, bordure orange

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

## 💡 Notes importantes

1. **Compatibilité**: Le thème fonctionne avec tous les types de graphiques Plotly (Bar, Scatter, Line, Heatmap, etc.)

2. **Performance**: Appliquer le thème en une fois via `apply_chart_theme()` est plus performant que configurer manuellement chaque élément

3. **Cohérence**: Toujours utiliser les couleurs de `colors.py` - jamais de couleurs hardcodées

4. **Extensibilité**: Pour ajouter une nouvelle couleur, l'ajouter dans `colors.py` puis créer une fonction getter dans `chart_theme.py` si nécessaire

5. **CSS externe**: Le fichier `custom.css` est chargé une seule fois au démarrage de l'app - modifications nécessitent redémarrage

6. **Streamlit config**: Le fichier `.streamlit/config.toml` configure le thème global mais CSS externe peut override certains éléments

---

## 🔗 Références

- **Palette originale**: Logo "Back to the Kitchen" (fichier image)
- **Plotly docs**: https://plotly.com/python/
- **Streamlit theming**: https://docs.streamlit.io/library/advanced-features/theming
- **Colors.py**: `/home/julien/code/mangetamain/000_dev/10_preprod/src/mangetamain_analytics/utils/colors.py`
- **Chart_theme.py**: `/home/julien/code/mangetamain/000_dev/10_preprod/src/mangetamain_analytics/utils/chart_theme.py`
