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
ORANGE_PRIMARY = "#d97b3a"    # Orange moyen - titres, accents
ORANGE_SECONDARY = "#c66a2f"  # Orange foncé - dégradés
ORANGE_LIGHT = "#e89050"      # Orange clair - hover
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
    "#d97b3a",  # Orange principal
    "#6ec1e4",  # Bleu clair
    "#e89050",  # Orange clair
    "#54a0c8",  # Bleu moyen
    "#c66a2f",  # Orange foncé
]
```

### États
```python
SUCCESS = "#2ecc71"   # Vert
WARNING = "#f39c12"   # Orange/Jaune
ERROR = "#e74c3c"     # Rouge
INFO = "#3498db"      # Bleu
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

**Navigation (radio buttons sans checkboxes)**
```css
/* Cacher les cercles de radio */
[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none;
}

/* Item sélectionné - Gradient orange */
[data-testid="stSidebar"] .stRadio input:checked + div {
    background: linear-gradient(135deg, #d97b3a 0%, #c66a2f 100%);
    border-radius: 8px;
    padding: 10px 15px;
    font-weight: bold;
}
```

**Boutons primaires (orange)**
```css
.stButton > button {
    background: linear-gradient(135deg, #ff8c42 0%, #ff6b35 100%);
    color: white;
    border-radius: 25px;
    box-shadow: 0 4px 6px rgba(255, 140, 66, 0.3);
}
```

**Messages info (bleu uniforme)**
```css
[data-baseweb="notification"] {
    background: linear-gradient(135deg, #2980b9 0%, #3498db 100%) !important;
    color: #ffffff !important;
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
primaryColor = "#ff8c42"
backgroundColor = "#1e1e1e"
secondaryBackgroundColor = "#2a2a2a"
textColor = "#e0e0e0"
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
