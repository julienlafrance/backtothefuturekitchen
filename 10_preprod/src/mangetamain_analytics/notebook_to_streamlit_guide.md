# Guide : Convertir un Notebook Jupyter vers Streamlit avec Minimum d'Effort

## 🎯 Objectif
Créer un système automatisable pour intégrer facilement des analyses de notebooks dans l'application Streamlit.

## 📋 Structure standardisée pour les modules

### 1. Template de base pour vos modules Python

Créez vos fichiers dans `visualization/` avec cette structure :

```python
# <MÉTADONNÉES>
# Nom: mon_analyse.py
# Description: [Description de votre analyse]
# Auteur: [Votre nom]
# Date: [Date de création]
# Version: 1.0
# Catégorie: Analyse exploratoire
# </MÉTADONNÉES>

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# <IMPORTS>
# Ajoutez vos imports spécifiques ici
# import numpy as np
# import seaborn as sns
# </IMPORTS>

def render_analysis(conn):
    """
    Fonction principale qui sera automatiquement détectée et intégrée.
    
    Args:
        conn: Connexion DuckDB
    """
    
    # <TITRE>
    st.subheader("📊 Titre de votre analyse")
    # </TITRE>
    
    # <DESCRIPTION>
    st.markdown("""
    Description de votre analyse en markdown.
    Peut être sur plusieurs lignes.
    
    **Contexte :** Expliquez le contexte de l'analyse
    **Objectif :** Que cherchez-vous à démontrer ?
    """)
    # </DESCRIPTION>
    
    # <REQUÊTE_SQL>
    try:
        data = conn.execute("""
            -- Votre requête SQL principale
            SELECT * FROM votre_table 
            WHERE condition IS NOT NULL
            LIMIT 1000
        """).fetchdf()
    # </REQUÊTE_SQL>
        
        # <TRAITEMENT>
        # Votre code de traitement des données
        # data['nouvelle_colonne'] = data['colonne1'] * data['colonne2']
        # data_filtered = data[data['colonne'] > seuil]
        # </TRAITEMENT>
        
        # <GRAPHIQUE_PRINCIPAL>
        fig = px.scatter(data, 
                        x='col1', 
                        y='col2', 
                        title="Mon graphique principal",
                        hover_data=['col3'])
        st.plotly_chart(fig, use_container_width=True)
        # </GRAPHIQUE_PRINCIPAL>
        
        # <GRAPHIQUES_SECONDAIRES>
        # Graphiques additionnels si nécessaire
        # fig2 = px.histogram(data, x='col1')
        # st.plotly_chart(fig2, use_container_width=True)
        # </GRAPHIQUES_SECONDAIRES>
        
        # <STATISTIQUES>
        # Métriques et statistiques descriptives
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Métrique 1", f"{data['col1'].mean():.2f}")
        with col2:
            st.metric("Métrique 2", f"{data['col2'].sum():,}")
        with col3:
            st.metric("Métrique 3", f"{len(data)}")
        # </STATISTIQUES>
        
        # <INTERPRÉTATION>
        st.markdown("""
        **Résultats principaux :**
        - Point clé 1
        - Point clé 2
        - Point clé 3
        
        **Conclusions :**
        Vos conclusions détaillées ici.
        """)
        # </INTERPRÉTATION>
        
        # <DONNÉES_BRUTES>
        # Optionnel : affichage des données brutes
        with st.expander("Voir les données brutes"):
            st.dataframe(data.head(100))
        # </DONNÉES_BRUTES>
        
    except Exception as e:
        st.error(f"Erreur dans l'analyse : {e}")


# <MODULE_INFO>
MODULE_INFO = {
    "name": "Mon Analyse",
    "description": "Description courte pour l'interface",
    "category": "Analyse exploratoire",  # Analyse exploratoire, ML, Statistiques, Visualisation
    "author": "Votre nom",
    "version": "1.0",
    "tags": ["tag1", "tag2"],  # Tags pour le filtrage
    "data_sources": ["table1", "table2"],  # Tables utilisées
    "created_date": "2024-01-01",
    "last_modified": "2024-01-01"
}
# </MODULE_INFO>
```

## 🤖 Système d'auto-intégration

### 2. Fonction de découverte automatique

Ajoutez dans `main.py` cette fonction qui découvre automatiquement tous vos modules :

```python
import importlib
import os
from pathlib import Path

def parse_xml_tags_from_file(file_path):
    """Parse les balises XML depuis le fichier source."""
    import re
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parser les différentes sections
    sections = {}
    
    # Métadonnées du header
    metadata_match = re.search(r'# <MÉTADONNÉES>(.*?)# </MÉTADONNÉES>', content, re.DOTALL)
    if metadata_match:
        metadata_lines = metadata_match.group(1).strip().split('\n')
        metadata = {}
        for line in metadata_lines:
            if ':' in line and line.startswith('#'):
                key, value = line.replace('#', '').strip().split(':', 1)
                metadata[key.strip()] = value.strip()
        sections['metadata'] = metadata
    
    # Autres sections importantes
    for tag in ['IMPORTS', 'REQUÊTE_SQL', 'TRAITEMENT', 'GRAPHIQUE_PRINCIPAL', 'INTERPRÉTATION']:
        pattern = f'# <{tag}>(.*?)# </{tag}>'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            sections[tag.lower()] = match.group(1).strip()
    
    return sections

def discover_custom_modules():
    """Découvre automatiquement tous les modules d'analyse avec parsing XML."""
    modules = []
    viz_dir = Path("visualization")
    
    for file_path in viz_dir.glob("*.py"):
        if file_path.name.startswith("__") or file_path.name == "custom_charts.py":
            continue
            
        module_name = file_path.stem
        try:
            # Parse les balises XML du fichier source
            xml_sections = parse_xml_tags_from_file(file_path)
            
            # Import dynamique
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Vérifier que le module a les fonctions requises
            if hasattr(module, 'render_analysis') and hasattr(module, 'MODULE_INFO'):
                module_info = module.MODULE_INFO.copy()
                
                # Enrichir avec les infos du parsing XML si disponibles
                if 'metadata' in xml_sections:
                    metadata = xml_sections['metadata']
                    if 'Description' in metadata:
                        module_info['file_description'] = metadata['Description']
                    if 'Date' in metadata:
                        module_info['creation_date'] = metadata['Date']
                
                modules.append({
                    'module': module,
                    'info': module_info,
                    'render': module.render_analysis,
                    'xml_sections': xml_sections,
                    'file_path': str(file_path)
                })
        except Exception as e:
            st.sidebar.error(f"Erreur lors du chargement de {module_name}: {e}")
    
    return modules

def create_auto_custom_visualizations(conn):
    """Interface automatique pour tous les modules découverts."""
    st.subheader("🤖 Analyses automatiquement détectées")
    
    modules = discover_custom_modules()
    
    if not modules:
        st.warning("Aucun module d'analyse trouvé dans visualization/")
        return
    
    # Sélecteur de module
    module_names = [f"{m['info']['name']} ({m['info']['category']})" for m in modules]
    selected_idx = st.selectbox("Choisir une analyse:", range(len(modules)), 
                               format_func=lambda x: module_names[x])
    
    if selected_idx is not None:
        selected_module = modules[selected_idx]
        
        # Afficher les métadonnées
        with st.expander("ℹ️ Informations sur cette analyse"):
            st.write(f"**Auteur :** {selected_module['info']['author']}")
            st.write(f"**Version :** {selected_module['info']['version']}")
            st.write(f"**Description :** {selected_module['info']['description']}")
        
        # Exécuter l'analyse
        selected_module['render'](conn)
```

## 🔄 Workflow de conversion d'un notebook

### 3. Étapes simplifiées

1. **Copiez votre notebook** dans le dossier `notebooks/` (optionnel, pour archivage)

2. **Créez un nouveau fichier** : `visualization/mon_analyse_[date].py`

3. **Copiez le template** ci-dessus et remplissez :
   - Les métadonnées en haut
   - Votre requête SQL dans la section DONNÉES
   - Votre code de traitement
   - Votre graphique (adaptez pour Plotly si nécessaire)
   - Vos textes explicatifs

4. **Conversion automatique des éléments** :

| Notebook | Streamlit | Balise XML |
|----------|-----------|------------|
| `# Titre markdown` | `st.subheader("Titre")` | `<TITRE>` |
| `print(variable)` | `st.write(variable)` | `<STATISTIQUES>` |
| `df.head()` | `st.dataframe(df.head())` | `<DONNÉES_BRUTES>` |
| `plt.show()` | `st.plotly_chart(fig)` | `<GRAPHIQUE_PRINCIPAL>` |
| Cellule markdown | `st.markdown(""")` | `<INTERPRÉTATION>` |

## 🏷️ Avantages des balises XML

### **Pour vous (développeur) :**
- **Structure claire** : Chaque section est bien délimitée
- **Navigation rapide** : Facile de retrouver une section spécifique
- **Réutilisabilité** : Template cohérent pour tous vos modules
- **Documentation automatique** : Les balises servent de documentation

### **Pour un robot/parser :**
- **Parsing fiable** : Structure prévisible avec regex simples
- **Métadonnées extraites** : Auteur, date, description automatiquement récupérés
- **Sections identifiées** : Code, requêtes SQL, graphiques séparés
- **Validation automatique** : Vérifier que toutes les sections requises sont présentes

### **Exemples d'utilisation automatique :**

```python
# Générer automatiquement une documentation
def generate_module_doc(file_path):
    sections = parse_xml_tags_from_file(file_path)
    doc = f"""# {sections['metadata']['Nom']}
    
**Auteur :** {sections['metadata']['Auteur']}
**Date :** {sections['metadata']['Date']}
    
## Description
{sections['metadata']['Description']}
    
## Requêtes SQL utilisées
```sql
{sections['requête_sql']}
```
    """
    return doc

# Extraire automatiquement les dépendances
def extract_dependencies(file_path):
    sections = parse_xml_tags_from_file(file_path)
    imports = sections.get('imports', '')
    # Parser les imports pour créer requirements.txt
    
# Valider la structure
def validate_module_structure(file_path):
    sections = parse_xml_tags_from_file(file_path)
    required_sections = ['MÉTADONNÉES', 'REQUÊTE_SQL', 'GRAPHIQUE_PRINCIPAL']
    missing = [s for s in required_sections if s.lower() not in sections]
    return len(missing) == 0, missing
```

## 📁 Structure de fichiers recommandée

```
mangetamain_analytics/
├── visualization/
│   ├── __init__.py
│   ├── custom_charts.py          # Fonctions utilitaires
│   ├── analyse_ratings_2024.py   # Votre analyse 1
│   ├── analyse_temporelle_2024.py # Votre analyse 2
│   └── ...
├── notebooks/                    # Archive des notebooks originaux
│   ├── analyse_ratings.ipynb
│   └── ...
└── main.py
```

## 🚀 Intégration dans main.py

### 4. Modification minimale de main.py

Remplacez la fonction `create_custom_visualizations` par `create_auto_custom_visualizations` :

```python
# Dans les tabs
with tab6:
    create_auto_custom_visualizations(conn)  # Au lieu de create_custom_visualizations
```

## ✅ Checklist de validation

Avant de déployer un nouveau module :

- [ ] Le fichier respecte le template
- [ ] `MODULE_INFO` est défini
- [ ] `render_analysis(conn)` existe
- [ ] Pas d'erreur lors de l'import
- [ ] Les graphiques s'affichent correctement
- [ ] Les textes explicatifs sont présents

## 🎁 Avantages de cette approche

1. **Zéro modification de main.py** pour ajouter une nouvelle analyse
2. **Auto-détection** de tous les modules
3. **Métadonnées standardisées** pour la documentation
4. **Gestion d'erreurs** automatique
5. **Archivage** des notebooks originaux
6. **Structure cohérente** pour tous les modules

## 🔧 Utilisation

1. **Pour ajouter une nouvelle analyse** : Créez un fichier avec le template
2. **Pour retirer une analyse** : Renommez le fichier avec un `_` au début
3. **Pour modifier une analyse** : Éditez directement le fichier Python
4. **Pour versionner** : Utilisez des suffixes de date dans les noms

Cette approche permet d'industrialiser facilement la création d'analyses tout en gardant la flexibilité du développement individuel.