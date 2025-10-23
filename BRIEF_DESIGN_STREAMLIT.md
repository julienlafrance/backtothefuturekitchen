# Brief Design - Charte Graphique et Wireframes
## Projet : Mangetamain Analytics - Application Streamlit

---

## 📋 Contexte du Projet

**Mangetamain Analytics** ("Back to the Future Kitchen") est une plateforme d'analyse de données culinaires basée sur le dataset Food.com (1999-2018).

### Données disponibles
- **178,265 recettes** de cuisine
- **25,076 utilisateurs**
- **1,1+ million d'interactions/notes**
- **7 tables DuckDB** : PP_recipes, PP_users, interactions_train/test/validation, RAW_interactions, RAW_recipes

### Stack technique
- **Backend** : Python 3.13.3 + DuckDB + S3
- **Frontend** : Streamlit 1.28+
- **Visualisation** : Plotly, Matplotlib, Seaborn, Altair
- **Environnements** : PREPROD (port 8500) et PROD (port 8501)

### Public cible
Data analysts, chercheurs en food tech, équipes marketing culinaire, étudiants en data science

---

## 🎨 PARTIE 1 : CHARTE GRAPHIQUE

### 1.1 Palette de Couleurs à Définir

**FORMAT REQUIS pour implémentation :**
```toml
# Fichier .streamlit/config.toml à générer
[theme]
primaryColor = "#XXXXXX"        # Couleur principale (boutons, liens)
backgroundColor = "#XXXXXX"      # Fond de la page
secondaryBackgroundColor = "#XXXXXX"  # Fond des widgets/sidebar
textColor = "#XXXXXX"            # Couleur du texte
font = "sans serif"              # Options: "sans serif", "serif", "monospace"
```

**Palette additionnelle (pour CSS custom) :**
- Couleur d'accent : `#XXXXXX`
- Couleur success : `#XXXXXX` (pour badges PROD)
- Couleur warning : `#XXXXXX` (pour badges PREPROD)
- Couleur error : `#XXXXXX`
- Couleur info : `#XXXXXX`

**Palette pour graphiques (minimum 8 couleurs distinctes) :**
```python
# À intégrer dans un fichier colors.py
CHART_COLORS = [
    "#XXXXXX",  # Couleur 1
    "#XXXXXX",  # Couleur 2
    "#XXXXXX",  # Couleur 3
    "#XXXXXX",  # Couleur 4
    "#XXXXXX",  # Couleur 5
    "#XXXXXX",  # Couleur 6
    "#XXXXXX",  # Couleur 7
    "#XXXXXX",  # Couleur 8
]
```

**Contraintes :**
- Compatible thème clair ET sombre Streamlit
- Contrastes WCAG AA minimum (4.5:1 pour texte normal)
- Éviter couleurs trop saturées (fatigue visuelle)
- Style : Professionnel, moderne, chaleureux (inspiration culinaire subtile)

### 1.2 Typographie

**Polices Google Fonts à spécifier :**
```python
# À intégrer dans custom CSS
FONTS = {
    "primary": "Nom-de-la-Police",    # Pour textes et contenus
    "heading": "Nom-de-la-Police",    # Pour titres (peut être identique)
    "monospace": "Source Code Pro",   # Pour code et chiffres (fixe)
}
```

**Hiérarchie typographique à définir :**
- H1 (Titres principaux) : XX px, weight XXX
- H2 (Sous-titres) : XX px, weight XXX
- H3 (Sections) : XX px, weight XXX
- Body (Texte courant) : XX px, weight XXX
- Caption (Légendes) : XX px, weight XXX
- Code : XX px, monospace

### 1.3 Système d'Icônes

**Source à spécifier :**
- Bibliothèque d'icônes (ex: Font Awesome, Material Icons, Lucide, etc.)
- Style : outline/filled/duotone

**Icônes requises par catégorie :**

**Navigation :**
- 🏠 Accueil / Dashboard
- 💾 Base de données
- 📊 Analyses
- 📈 Visualisations
- 📖 Documentation
- ⚙️ Paramètres

**Types de données :**
- 🍽️ Recettes
- 👤 Utilisateurs
- ⭐ Notes / Ratings
- 🥕 Ingrédients
- 🕒 Temps

**Actions :**
- 🔍 Rechercher
- 🎯 Filtrer
- 📥 Télécharger
- 📤 Exporter
- 🔄 Rafraîchir
- ➕ Ajouter
- ✏️ Modifier
- 🗑️ Supprimer

**Statuts :**
- ✅ Succès
- ⚠️ Warning
- ❌ Erreur
- ℹ️ Info
- ⏳ Chargement
- 🟢 PROD (environnement)
- 🟠 PREPROD (environnement)

**IMPORTANT : Fournir les codes unicode ou noms de classe CSS pour chaque icône**

### 1.4 Composants UI à Designer

**Badges d'environnement :**
```python
# Badge PROD : fond vert, texte blanc
# Badge PREPROD : fond orange, texte blanc
# Format : pill/rounded rectangle
# Taille : height 24px, padding 8px 12px
```

**Boutons :**
- Primaire : Couleur principale, texte blanc
- Secondaire : Bordure, fond transparent
- Tertiaire : Texte seul (link style)
- États : default, hover, active, disabled

**Cards (conteneurs) :**
- Border radius : XX px
- Shadow : XX
- Padding : XX px
- Background : secondaryBackgroundColor

**Métriques (KPI cards) :**
- Layout : Valeur en grand (XX px), label en petit (XX px)
- Icône optionnelle
- Delta avec flèche (↑ vert / ↓ rouge)

---

## 📐 PARTIE 2 : WIREFRAMES - SPÉCIFICATIONS TECHNIQUES

### Page 1 : Dashboard Principal (main.py - page Accueil)

**URL/Route :** `/` (page par défaut)

**Layout Structure :**
```
┌─────────────────────────────────────────────────────────┐
│ SIDEBAR (width: 280px)                                  │
│ - Logo + Titre projet                                   │
│ - Badge environnement (PROD/PREPROD)                    │
│ - Navigation (radio buttons ou menu)                    │
│ - Info DB (nom fichier, taille)                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ HEADER                                                   │
│ H1: "🏠 Dashboard Principal"                            │
│ Sous-titre: "Vue d'ensemble des données Food.com"       │
└─────────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬───────────┐
│ METRIC 1     │ METRIC 2     │ METRIC 3     │ METRIC 4  │
│ 178,265      │ 25,076       │ 1,132,367    │ 4.3 ⭐    │
│ Recettes     │ Utilisateurs │ Interactions │ Note moy. │
└──────────────┴──────────────┴──────────────┴───────────┘

┌─────────────────────────────┬───────────────────────────┐
│ GRAPHIQUE 1                 │ GRAPHIQUE 2               │
│ "Distribution des notes"    │ "Top 10 Ingrédients"      │
│ Type: Pie chart (Plotly)    │ Type: Horizontal bar      │
│ Interactif, hover tooltips  │ Couleurs graduées         │
└─────────────────────────────┴───────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ GRAPHIQUE 3                                           │
│ "Évolution temporelle des recettes publiées"         │
│ Type: Line chart (Plotly)                            │
│ X: Année, Y: Nombre de recettes                      │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ TABLEAU "Dernières recettes"                         │
│ 10 dernières recettes ajoutées                       │
│ Colonnes: Nom, Minutes, Note, N_ingrédients          │
│ Scrollable, sortable                                 │
└───────────────────────────────────────────────────────┘
```

**Code Streamlit requis :**
- `st.sidebar` pour navigation
- `st.columns(4)` pour les 4 métriques
- `st.metric()` pour afficher KPIs
- `st.columns(2)` pour les 2 graphiques côte à côte
- `st.plotly_chart()` pour visualisations
- `st.dataframe()` pour le tableau

---

### Page 2 : Explorateur de Base de Données

**URL/Route :** Page "Base de données" dans sidebar

**Layout Structure :**
```
┌───────────────────────────────────────────────────────┐
│ HEADER                                                │
│ H1: "💾 Explorateur de Base de Données"              │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ SÉLECTION DE TABLE                                    │
│ Dropdown: [PP_recipes ▼]                             │
│ Options: PP_recipes, PP_users, interactions_train,   │
│          interactions_test, interactions_validation,  │
│          RAW_interactions, RAW_recipes                │
└───────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬───────────┐
│ METRIC       │ METRIC       │ METRIC       │ BADGE     │
│ 178,265      │ 23           │ 205 MB       │ Préproc.  │
│ Lignes       │ Colonnes     │ Taille       │ Catégorie │
└──────────────┴──────────────┴──────────────┴───────────┘

┌───────────────────────────────────────────────────────┐
│ TABS                                                  │
│ [Aperçu] [Statistiques] [Requête SQL]                │
└───────────────────────────────────────────────────────┘

┌─ TAB 1: APERÇU ─────────────────────────────────────┐
│ st.dataframe() avec pagination                      │
│ Afficher les 100 premières lignes                  │
│ Scrollable horizontal pour toutes colonnes         │
│ Bouton "Export CSV" en bas                         │
└─────────────────────────────────────────────────────┘

┌─ TAB 2: STATISTIQUES ───────────────────────────────┐
│ Pour chaque colonne (surtout numériques):          │
│ - Nom, Type, Valeurs nulles (%)                    │
│ - Min, Max, Moyenne, Médiane (si numérique)       │
│ - Histogramme de distribution                      │
└─────────────────────────────────────────────────────┘

┌─ TAB 3: REQUÊTE SQL ────────────────────────────────┐
│ st.text_area() pour écrire requête SQL             │
│ Placeholder: "SELECT * FROM PP_recipes LIMIT 10"   │
│ Bouton "Exécuter" (primaire, avec icône ▶️)        │
│ Zone de résultat: st.dataframe() ou st.error()     │
│ Temps d'exécution affiché                          │
└─────────────────────────────────────────────────────┘
```

**Code Streamlit requis :**
- `st.selectbox()` pour choix de table
- `st.columns(4)` pour métriques de table
- `st.tabs()` pour organiser contenu
- `st.dataframe()` pour afficher données
- `st.text_area()` pour SQL input
- `st.button()` pour actions
- Gestion d'erreurs SQL avec `st.error()`

---

### Page 3 : Analyses de Ratings

**URL/Route :** Page "Analyses > Ratings" dans sidebar

**Layout Structure :**
```
┌───────────────────────────────────────────────────────┐
│ HEADER                                                │
│ H1: "⭐ Analyse des Notes et Comportements"          │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ FILTRES (dans un expander ou toujours visibles)      │
│ ┌─────────────────┬─────────────────┬──────────────┐ │
│ │ Table:          │ Plage notes:    │ Période:     │ │
│ │ [interactions_  │ [0 ──●──●── 5]  │ [2010-2018]  │ │
│ │  train ▼]       │ Slider double   │ Date range   │ │
│ └─────────────────┴─────────────────┴──────────────┘ │
│ Bouton "Appliquer filtres" (primaire)                │
└───────────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┬───────────┐
│ METRIC       │ METRIC       │ METRIC       │ METRIC    │
│ 698,901      │ 4.3 ⭐       │ 5 ⭐         │ 45%       │
│ Total notes  │ Moyenne      │ Mode         │ 5 étoiles │
└──────────────┴──────────────┴──────────────┴───────────┘

┌─────────────────────────────┬───────────────────────────┐
│ GRAPHIQUE 1                 │ GRAPHIQUE 2               │
│ "Distribution des notes"    │ "Notes par catégorie"     │
│ Type: Histogram (Plotly)    │ Type: Box plot            │
│ X: Note (0-5), Y: Count     │ Groupé par catégorie      │
└─────────────────────────────┴───────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ GRAPHIQUE 3                                           │
│ "Corrélation: Note vs Nombre d'ingrédients"          │
│ Type: Scatter plot (Plotly)                          │
│ X: N_ingredients, Y: Rating                          │
│ Color: Density heatmap optionnel                     │
│ Taille variable: nombre d'évaluations                │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ GRAPHIQUE 4                                           │
│ "Activité utilisateur: Nb évaluations vs Note moy"   │
│ Type: Scatter plot                                    │
│ X: Nombre d'évaluations par user                     │
│ Y: Note moyenne donnée par user                      │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ INSIGHTS AUTOMATIQUES (st.info() box)                │
│ "📊 Observations clés:"                              │
│ • 45% des notes sont des 5 étoiles                   │
│ • La note moyenne est stable dans le temps           │
│ • Les recettes avec 10-15 ingrédients sont mieux     │
│   notées en moyenne                                   │
└───────────────────────────────────────────────────────┘
```

**Code Streamlit requis :**
- `st.expander()` pour filtres repliables
- `st.selectbox()` pour table
- `st.slider()` pour plage de notes
- `st.date_input()` pour période
- `st.columns(4)` pour métriques
- `st.plotly_chart()` pour tous les graphiques
- `st.info()` pour insights

---

### Page 4 : Analyses Temporelles

**URL/Route :** Page "Analyses > Temporel" dans sidebar

**Layout Structure :**
```
┌───────────────────────────────────────────────────────┐
│ HEADER                                                │
│ H1: "🕒 Analyses Temporelles"                        │
│ Sous-titre: "Tendances et saisonnalité"              │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ FILTRES                                               │
│ ┌───────────────────┬───────────────────────────────┐ │
│ │ Granularité:      │ Période:                      │ │
│ │ ○ Jour            │ [2010-01-01] à [2018-12-31]   │ │
│ │ ● Mois            │ Date pickers                  │ │
│ │ ○ Année           │                               │ │
│ └───────────────────┴───────────────────────────────┘ │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ GRAPHIQUE 1                                           │
│ "Évolution du nombre de recettes publiées"           │
│ Type: Line chart avec area fill (Plotly)             │
│ X: Temps, Y: Nombre de recettes                      │
│ Marqueurs sur points significatifs                   │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ GRAPHIQUE 2                                           │
│ "Évolution du nombre de notes données"               │
│ Type: Line chart                                      │
│ X: Temps, Y: Nombre de notes                         │
│ Annotation: pics d'activité                          │
└───────────────────────────────────────────────────────┘

┌─────────────────────────────┬───────────────────────────┐
│ GRAPHIQUE 3                 │ GRAPHIQUE 4               │
│ "Activité par jour semaine" │ "Activité par heure"      │
│ Type: Bar chart             │ Type: Line chart          │
│ Lun-Dim, hauteurs = activité│ 0h-23h, activité moyenne  │
└─────────────────────────────┴───────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ CARTE THERMIQUE (Heatmap)                            │
│ "Saisonnalité: Mois vs Année"                        │
│ Type: Heatmap Plotly                                 │
│ X: Mois (Jan-Déc), Y: Année (2010-2018)              │
│ Color: Intensité d'activité                          │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ COMPARAISON WEEK-END vs SEMAINE (columns 2)          │
│ ┌───────────────────┬───────────────────────────────┐ │
│ │ Semaine:          │ Week-end:                     │ │
│ │ 75,234 recettes   │ 32,156 recettes               │ │
│ │ Metric avec icon  │ Metric avec icon              │ │
│ └───────────────────┴───────────────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

**Code Streamlit requis :**
- `st.radio()` pour granularité
- `st.date_input()` pour période
- `st.plotly_chart()` pour tous graphiques
- `st.columns(2)` pour comparaison week-end
- Calculs pandas/polars pour agrégations temporelles

---

### Page 5 : Visualisations Avancées

**URL/Route :** Page "Visualisations" dans sidebar

**Layout Structure :**
```
┌───────────────────────────────────────────────────────┐
│ HEADER                                                │
│ H1: "📈 Visualisations Interactives Avancées"       │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ TYPE DE VISUALISATION (tabs)                         │
│ [Distribution] [Corrélation] [Comparaison] [Custom]  │
└───────────────────────────────────────────────────────┘

┌─ CONFIGURATEUR (sidebar ou colonne gauche) ─────────┐
│ Sélection des données:                              │
│ • Table source: [Dropdown]                          │
│ • Colonne X: [Dropdown]                             │
│ • Colonne Y: [Dropdown]                             │
│ • Colonne Couleur (opt): [Dropdown]                 │
│ • Colonne Taille (opt): [Dropdown]                  │
│                                                      │
│ Type de graphique:                                  │
│ ○ Scatter plot                                      │
│ ○ Bar chart                                         │
│ ○ Line chart                                        │
│ ○ Box plot                                          │
│ ○ Violin plot                                       │
│ ○ Heatmap                                           │
│                                                      │
│ Options:                                            │
│ ☑ Afficher ligne de tendance                       │
│ ☑ Log scale                                         │
│ ☐ Normaliser données                                │
│                                                      │
│ [Bouton "Générer graphique"]                        │
└─────────────────────────────────────────────────────┘

┌─ ZONE DE GRAPHIQUE (colonne principale) ────────────┐
│                                                      │
│    [Graphique Plotly interactif]                    │
│    - Zoom, pan, reset                               │
│    - Tooltips détaillés au survol                   │
│    - Légende interactive (clic pour hide/show)      │
│                                                      │
│    Boutons d'action en dessous:                     │
│    [📥 Export PNG] [📋 Export Data CSV]             │
│                                                      │
└─────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ STATISTIQUES DU GRAPHIQUE (expander replié)          │
│ Quand ouvert, affiche:                               │
│ • Nombre de points                                    │
│ • Statistiques descriptives (min, max, mean, std)    │
│ • Corrélation (si scatter)                           │
└───────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────┐
│ ANNOTATIONS / NOTES (text_area)                       │
│ Zone pour que l'utilisateur ajoute des commentaires  │
│ sur le graphique (non persistent pour MVP)           │
└───────────────────────────────────────────────────────┘
```

**Code Streamlit requis :**
- `st.tabs()` pour types de viz
- `st.sidebar` ou `st.columns([1,3])` pour configurateur
- `st.selectbox()` multiple pour choix colonnes
- `st.radio()` pour type de graphique
- `st.checkbox()` pour options
- `st.button()` pour générer
- `st.plotly_chart()` pour affichage
- `st.download_button()` pour exports
- Logique conditionnelle pour générer graphiques dynamiques

---

## 🧩 Composants Communs (Toutes les Pages)

### Sidebar Persistant

```python
# Structure du sidebar (à intégrer dans chaque page)
with st.sidebar:
    # Logo + Titre
    st.image("assets/logo.png", width=100)  # Logo à créer
    st.title("Mangetamain Analytics")

    # Badge environnement
    env = detect_environment()  # Fonction existante
    if env == "PROD":
        st.success("🟢 PRODUCTION")
    else:
        st.warning("🟠 PREPROD")

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "💾 Base de données", "⭐ Analyses Ratings",
         "🕒 Analyses Temporelles", "📈 Visualisations", "📖 Documentation"],
        label_visibility="collapsed"
    )

    st.divider()

    # Info DB
    st.caption("📊 Base de données")
    st.text("mangetamain.duckdb")
    st.text("Taille: 582 MB")

    # Bouton refresh
    if st.button("🔄 Rafraîchir", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
```

### Footer

```python
# À placer en bas de chaque page
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("📅 Dernière màj: 2025-10-23")
with col2:
    st.caption("📦 Version 1.0.0")
with col3:
    st.caption("[📚 Documentation](README_CI_CD.md)")
```

### États de Chargement

```python
# Pattern pour chargement
with st.spinner("⏳ Chargement des données..."):
    data = load_data()  # Fonction de chargement

# Ou progress bar pour longues opérations
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
    time.sleep(0.01)
progress_bar.empty()
```

### Notifications

```python
# Success
st.success("✅ Données chargées avec succès!")

# Warning
st.warning("⚠️ Certaines données sont manquantes")

# Error
st.error("❌ Erreur de connexion à la base de données")

# Info
st.info("ℹ️ Cette analyse porte sur 178,265 recettes")
```

---

## 🎨 ASSETS À CRÉER

### Logo du Projet

**Spécifications :**
- Format : PNG avec transparence
- Dimensions : 200x200 px (haute résolution)
- Style : Minimaliste, moderne
- Éléments : Mixer thème culinaire (fourchette, couteau, plat) avec data/tech (graphique, data points)
- Couleurs : Utiliser palette principale définie
- Fichier : `assets/logo.png`

**Variantes optionnelles :**
- `logo_light.png` (pour fond clair)
- `logo_dark.png` (pour fond sombre)
- `favicon.ico` (16x16, 32x32, 48x48)

### Icônes Personnalisées

Si icônes custom nécessaires (au-delà des bibliothèques standard) :
- Format : SVG
- Style : Cohérent avec logo
- Dossier : `assets/icons/`

---

## 📦 FICHIERS À LIVRER PAR L'IA

### 1. Charte Graphique (Document)

**Format :** Markdown ou PDF

**Contenu :**
```markdown
# Charte Graphique - Mangetamain Analytics

## Palette de Couleurs
- Primaire: #XXXXXX (Nom: XXX)
- Secondaire: #XXXXXX (Nom: XXX)
- Background: #XXXXXX
- ...

## Typographie
- Heading: Nom Police, weights [400, 600, 700]
- Body: Nom Police, weight 400
- Monospace: Source Code Pro

## Iconographie
- Bibliothèque: Font Awesome 6
- Style: Regular (outline)
- Liste des icônes utilisées: ...

## Composants UI
[Exemples visuels des boutons, cards, badges, etc.]

## Guidelines d'Utilisation
...
```

### 2. Fichier de Configuration Streamlit

**Fichier :** `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#XXXXXX"
backgroundColor = "#XXXXXX"
secondaryBackgroundColor = "#XXXXXX"
textColor = "#XXXXXX"
font = "sans serif"

[server]
headless = true
port = 8500
```

### 3. Fichier de Couleurs Python

**Fichier :** `utils/colors.py`

```python
"""Palette de couleurs du projet Mangetamain Analytics."""

# Couleurs principales
PRIMARY = "#XXXXXX"
SECONDARY = "#XXXXXX"
BACKGROUND = "#XXXXXX"
TEXT = "#XXXXXX"

# Couleurs d'état
SUCCESS = "#XXXXXX"
WARNING = "#XXXXXX"
ERROR = "#XXXXXX"
INFO = "#XXXXXX"

# Palette pour graphiques
CHART_COLORS = [
    "#XXXXXX",
    "#XXXXXX",
    "#XXXXXX",
    "#XXXXXX",
    "#XXXXXX",
    "#XXXXXX",
    "#XXXXXX",
    "#XXXXXX",
]

# Badges environnement
ENV_PROD = {"bg": SUCCESS, "text": "#FFFFFF"}
ENV_PREPROD = {"bg": WARNING, "text": "#FFFFFF"}
```

### 4. CSS Custom (Optionnel)

**Fichier :** `assets/custom.css`

```css
/* Styles personnalisés pour Streamlit */

/* Import des fonts Google */
@import url('https://fonts.googleapis.com/css2?family=NOM-FONT:wght@400;600;700&display=swap');

/* Personnalisation des titres */
h1 {
    font-family: 'NOM-FONT', sans-serif;
    color: #XXXXXX;
    font-weight: 700;
}

/* Badges personnalisés */
.badge-prod {
    background-color: #XXXXXX;
    color: #FFFFFF;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 600;
}

/* ... autres styles ... */
```

### 5. Wireframes (Images)

**Format :** PNG haute résolution (1920x1080)

**Fichiers à fournir :**
- `wireframe_1_dashboard.png`
- `wireframe_2_database.png`
- `wireframe_3_ratings.png`
- `wireframe_4_temporal.png`
- `wireframe_5_visualizations.png`

**Annotations :**
- Ajouter labels sur wireframes pour identifier composants
- Indiquer dimensions importantes (colonnes, spacing)
- Spécifier types de graphiques Plotly

### 6. Logo et Assets

**Fichiers :**
- `assets/logo.png` (200x200 px)
- `assets/logo_light.png` (optionnel)
- `assets/logo_dark.png` (optionnel)
- `assets/favicon.ico`

---

## ✅ CHECKLIST DE VALIDATION

Avant de me transmettre les fichiers pour implémentation, vérifier que :

### Charte Graphique
- [ ] Tous les codes couleur HEX sont fournis
- [ ] Noms de polices Google Fonts spécifiés
- [ ] Bibliothèque d'icônes identifiée avec noms/codes
- [ ] Contrastes vérifiés (WCAG AA minimum)
- [ ] Compatible thème clair ET sombre
- [ ] Style cohérent et professionnel

### Wireframes
- [ ] Les 5 pages sont wireframées
- [ ] Composants Streamlit identifiés et réalisables
- [ ] Layout responsive (adaptable colonnes)
- [ ] Hiérarchie visuelle claire
- [ ] Annotations techniques présentes
- [ ] Dimensions et spacing indiqués

### Assets
- [ ] Logo au format PNG transparent
- [ ] Favicon créé (multi-résolution)
- [ ] Tous les fichiers requis présents

### Fichiers de Code
- [ ] config.toml complet et valide
- [ ] colors.py avec toutes constantes
- [ ] CSS custom (si nécessaire) fourni

---

## 🚀 PROCHAINES ÉTAPES (Après Livraison)

Une fois que vous me fournirez tous ces éléments, je procéderai à :

1. **Création de l'arborescence** dans `10_preprod/`
   - Dossier `assets/`
   - Dossier `.streamlit/`
   - Dossier `utils/`

2. **Intégration de la charte graphique**
   - Copie du `config.toml`
   - Création de `colors.py`
   - Import du CSS custom

3. **Restructuration des pages Streamlit**
   - Création de pages séparées (multipage app)
   - Implémentation du sidebar commun
   - Intégration des composants selon wireframes

4. **Implémentation page par page**
   - Page 1: Dashboard
   - Page 2: Database Explorer
   - Page 3: Ratings Analysis
   - Page 4: Temporal Analysis
   - Page 5: Advanced Visualizations

5. **Tests et ajustements**
   - Vérification responsive
   - Test thème clair/sombre
   - Performance des graphiques
   - Navigation fluide

---

## 📞 Questions pour l'IA Multimodale

Si vous utilisez ce brief avec une IA, posez-lui ces questions pour obtenir des résultats optimaux :

1. **Pour la palette :** "Peux-tu proposer 3 variations de palette (classique, moderne, audacieuse) et m'expliquer le ressenti de chacune ?"

2. **Pour les wireframes :** "Peux-tu créer des wireframes annotés avec les dimensions exactes et les noms des composants Streamlit à utiliser ?"

3. **Pour le logo :** "Peux-tu créer plusieurs concepts de logo (minimaliste, détaillé, typographique) pour que je choisisse ?"

4. **Pour validation :** "Est-ce que cette palette respecte les contrastes WCAG AA entre texte et fond ?"

---

**Projet :** Mangetamain Analytics
**Framework :** Streamlit 1.28+
**Environnement cible :** 10_preprod (port 8500)
**Date :** 2025-10-23

**Contact :** Data Analytics Team
**Repo :** https://github.com/julienlafrance/backtothefuturekitchen

---

_Ce brief est prêt à être utilisé avec Claude, ChatGPT, Midjourney, ou tout autre outil d'IA multimodale pour générer la charte graphique et les wireframes._
