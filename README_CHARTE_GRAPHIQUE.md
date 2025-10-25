# 🎨 Charte Graphique "Back to the Kitchen"

> **Documentation officielle mise à jour : 2025-10-25**

## 📍 Localisation de la documentation

La charte graphique complète et à jour se trouve ici :

```
00_eda/09_integration/CHARTE_GRAPHIQUE_GUIDE.md
```

## 📊 Conformité

✅ **100% synchronisé** avec l'implémentation en production (`10_preprod/`)

## 📁 Fichiers de la charte

### 1. Documentation
- **Guide principal :** `00_eda/09_integration/CHARTE_GRAPHIQUE_GUIDE.md` (840+ lignes)

### 2. Implémentation
- **Palette couleurs :** `10_preprod/src/mangetamain_analytics/utils/colors.py` (207 lignes)
- **Thème Plotly :** `10_preprod/src/mangetamain_analytics/utils/chart_theme.py` (169 lignes)
- **CSS personnalisé :** `10_preprod/src/mangetamain_analytics/assets/custom.css` (771 lignes)
- **Config Streamlit :** `10_preprod/.streamlit/config.toml` (61 lignes)
- **Logo :** `10_preprod/src/mangetamain_analytics/assets/back_to_the_kitchen_logo.png`

## 🎯 Sections du guide

1. **Palette de couleurs** - Couleurs principales, fonds, texte, états
2. **Thème Plotly** - Fonctions pour styliser les graphiques
3. **CSS Streamlit** - 771 lignes de styles personnalisés
4. **Menu Sidebar** - Navigation avec icônes Lucide, badges
5. **Config Streamlit** - Thème global `.streamlit/config.toml`
6. **Éléments Bonus** - Scrollbars, dataframes, responsive, etc.

## 🚀 Quick Start

### Utiliser la palette de couleurs
```python
from utils import colors

# Couleurs principales
primary = colors.ORANGE_PRIMARY  # #FF8C00
background = colors.BACKGROUND_MAIN  # #1E1E1E
text = colors.TEXT_PRIMARY  # #F0F0F0

# Palette graphiques
chart_colors = colors.CHART_COLORS  # Liste de 8 couleurs
```

### Appliquer le thème Plotly
```python
from utils import chart_theme
import plotly.graph_objects as go

fig = go.Figure()
# ... ajout traces ...
chart_theme.apply_chart_theme(fig, title="Mon graphique")
st.plotly_chart(fig, use_container_width=True)
```

### Utiliser les couleurs pour graphiques
```python
# Barres
bar_color = chart_theme.get_bar_color()  # #FF8C00

# Lignes multiples
line_colors = chart_theme.get_line_colors()  # Liste 8 couleurs

# Scatter
scatter_color = chart_theme.get_scatter_color()  # #FFD700

# Ligne de référence
ref_color = chart_theme.get_reference_line_color()  # Rouge
```

## 📈 Statistiques

- **Total lignes CSS :** 771
- **Couleurs palette :** 8 couleurs cohérentes avec le logo
- **Polices Google Fonts :** Michroma (titres) + Inter (corps)
- **Icônes :** Lucide Icons (inline SVG)
- **Score conformité :** 100%

## 🔗 Liens utiles

- Guide complet : `00_eda/09_integration/CHARTE_GRAPHIQUE_GUIDE.md`
- Application main.py : `10_preprod/src/mangetamain_analytics/main.py`
- Modules visualisation : `10_preprod/src/mangetamain_analytics/visualization/`

---

**Projet :** Mangetamain Analytics
**Date :** 2025-10-25
**Status :** ✅ Production
