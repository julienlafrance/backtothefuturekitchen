# 📋 ROADMAP PROJET MANGETAMAIN - Respect des directives

## 🎯 Vue d'ensemble

Cette roadmap vous guide pour respecter **toutes** les exigences du projet tout en étant efficace et innovant.

## 📅 Planning suggéré (5 semaines restantes)

### Semaine 1 : Fondations (26 Sept - 2 Oct)
### Semaine 2 : Développement core (3-9 Oct) 
### Semaine 3 : Tests et documentation (10-16 Oct)
### Semaine 4 : CI/CD et déploiement (17-23 Oct)
### Semaine 5 : Finalisation (24 Oct - 1 Dec)

---

## 🏗️ PHASE 1 : FONDATIONS (Semaine 1)

### ✅ Déjà fait
- [x] Structure du projet avec UV
- [x] Configuration Loguru pour les logs
- [x] Base DuckDB avec Streamlit
- [x] Application de base fonctionnelle
- [x] pyproject.toml configuré

### 🎯 À compléter cette semaine

#### 1. **Choix de l'axe d'analyse** (PRIORITÉ 1)
```
Options recommandées selon vos données :
□ Recommandation de recettes par similarité (RECOMMANDÉ)
□ Profils utilisateurs et segmentation
□ Évolution des tendances culinaires dans le temps
□ Prédiction de popularité des recettes
```

#### 2. **Setup complet du projet**
```bash
□ Télécharger le dataset Kaggle complet
□ Initialiser le git repository
□ Configurer UV et environnement
□ Tester le chargement des données réelles
```

#### 3. **Structure orientée objet**
```python
□ Créer les classes principales :
  - DatabaseManager (déjà fait)
  - DataProcessor 
  - RecipeAnalyzer
  - UserAnalyzer
  - RecommendationEngine
```

---

## 🔧 PHASE 2 : DÉVELOPPEMENT CORE (Semaine 2)

### 📊 Analyse de données

#### **Module data/processor.py**
```python
class DataProcessor:
    def clean_interactions_data(self) -> pd.DataFrame
    def extract_recipe_features(self) -> pd.DataFrame  
    def compute_user_profiles(self) -> pd.DataFrame
    def generate_similarity_matrix(self) -> np.ndarray
```

#### **Module models/analytics.py**
```python
class RecipeAnalyzer:
    def analyze_popularity_trends(self) -> Dict
    def find_ingredient_patterns(self) -> Dict
    def compute_recipe_complexity(self) -> pd.DataFrame
    
class UserAnalyzer:
    def segment_users(self) -> Dict
    def analyze_behavior_patterns(self) -> Dict
    def compute_user_similarity(self) -> np.ndarray
```

### 🎨 Visualisations

#### **Module visualization/charts.py**
```python
def create_recipe_trends_chart(data: pd.DataFrame) -> go.Figure
def create_user_segmentation_plot(data: pd.DataFrame) -> go.Figure  
def create_ingredient_network(data: pd.DataFrame) -> go.Figure
def create_recommendation_heatmap(matrix: np.ndarray) -> go.Figure
```

### 🔍 Type Hinting (EXIGENCE)
```python
# Exemple obligatoire
from typing import List, Dict, Optional, Tuple, Union
import pandas as pd
import numpy as np

def analyze_recipes(
    data: pd.DataFrame, 
    min_ratings: int = 5,
    features: Optional[List[str]] = None
) -> Tuple[Dict[str, float], pd.DataFrame]:
    """Analyze recipe data with proper type hints."""
    pass
```

---

## 🧪 PHASE 3 : TESTS & DOCUMENTATION (Semaine 3)

### 🧪 Tests unitaires (EXIGENCE: 90% coverage)

#### **tests/unit/test_database.py**
```python
import pytest
from models.database import DatabaseManager

class TestDatabaseManager:
    def test_connection_creation(self):
    def test_csv_loading(self):
    def test_query_execution(self):
    def test_error_handling(self):
```

#### **tests/unit/test_analytics.py**
```python  
class TestRecipeAnalyzer:
    def test_popularity_calculation(self):
    def test_ingredient_extraction(self):
    def test_complexity_scoring(self):
```

#### **tests/integration/test_streamlit_app.py**
```python
def test_app_loads_successfully():
def test_data_loading_workflow():
def test_visualization_generation():
```

### 📚 Documentation Sphinx (EXIGENCE)

#### Configuration docs/conf.py
```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode', 
    'sphinx.ext.napoleon'  # Pour Google/NumPy docstrings
]
```

#### Docstrings obligatoires (TOUTES les fonctions/classes)
```python
class RecipeAnalyzer:
    """
    Analyzer for recipe data patterns and insights.
    
    This class provides methods to analyze recipe popularity,
    ingredient patterns, and complexity metrics.
    
    Attributes:
        db_manager: Database connection manager
        logger: Application logger instance
    """
    
    def analyze_popularity(self, min_interactions: int = 5) -> Dict[str, Any]:
        """
        Analyze recipe popularity based on user interactions.
        
        Args:
            min_interactions: Minimum number of interactions required
            
        Returns:
            Dictionary containing popularity metrics and rankings
            
        Raises:
            ValueError: If min_interactions is negative
            DatabaseError: If database connection fails
        """
```

---

## ⚙️ PHASE 4 : CI/CD & DÉPLOIEMENT (Semaine 4)

### 🔄 GitHub Actions (EXIGENCE)

#### **.github/workflows/ci.yml**
```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install UV
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip install -r requirements.txt -r requirements-dev.txt
    
    - name: Run Black (PEP 8)
      run: black --check src/ tests/
    
    - name: Run Flake8  
      run: flake8 src/ tests/
    
    - name: Run MyPy (type hints)
      run: mypy src/
    
    - name: Run tests with coverage
      run: pytest --cov=src --cov-fail-under=90
    
    - name: Check docstrings
      run: python scripts/check_docstrings.py
    
    - name: Build docs
      run: |
        cd docs/
        make html
```

### 🚀 Déploiement Streamlit Cloud

#### **requirements.txt** (pour Streamlit Cloud)
```
streamlit
duckdb  
pandas
plotly
numpy
scipy
loguru
python-dotenv
```

#### **.streamlit/config.toml**
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"

[server]
maxUploadSize = 200
```

---

## 🎯 PHASE 5 : FINALISATION (Semaine 5)

### 🔒 Sécurité (EXIGENCE)

#### Vérifications obligatoires
```python
# ❌ JAMAIS utiliser eval()
# user_input = "malicious_code"
# eval(user_input)  # INTERDIT

# ✅ Validation sécurisée  
def validate_user_input(user_input: str) -> bool:
    """Validate user input safely."""
    allowed_chars = set('abcdefghijklmnopqrstuvwxyz0123456789 ')
    return all(c.lower() in allowed_chars for c in user_input)

# ❌ Pas de secrets en dur
# API_KEY = "secret123"  # INTERDIT

# ✅ Variables d'environnement
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')
```

### 📊 Storytelling Streamlit

#### Pages recommandées
```python
# main.py - Page d'accueil
# pages/data_exploration.py - EDA interactive
# pages/user_analysis.py - Profils utilisateurs  
# pages/recipe_trends.py - Tendances recettes
# pages/recommendations.py - Système de recommandation
```

### 🏆 Fonctionnalités innovantes (pour se démarquer)

#### Idées recommandées
```python
□ Carte de chaleur des similitudes de recettes
□ Timeline interactive des tendances culinaires
□ Clustering 3D des utilisateurs (plotly)
□ Système de recommandation temps réel
□ Export PDF des analyses
□ Comparaison de recettes côte à côte
□ Prédiction de notes avec ML simple
```

---

## ✅ CHECKLIST FINALE (Avant le 1er décembre)

### 📁 Repository GitHub Public
```
□ Code source Python bien structuré
□ README.md complet avec instructions
□ .gitignore approprié
□ Commits réguliers avec messages clairs
□ Branches et Pull Requests (si équipe)
□ Tags de version (optionnel mais recommandé)
```

### 🧪 Qualité du code
```
□ PEP 8 respecté (Black + Flake8)
□ Type hints sur TOUTES les fonctions
□ Docstrings sur TOUTES les classes/méthodes
□ Gestion d'exceptions appropriée
□ Logs avec Loguru configurés
□ Tests unitaires >90% de couverture
```

### 📚 Documentation
```
□ Documentation Sphinx générée
□ API documentation complète  
□ Guide d'installation dans README
□ Commentaires pertinents dans le code
□ Architecture documentée
```

### ⚙️ CI/CD
```
□ Pipeline GitHub Actions fonctionnel
□ Tests automatisés à chaque push
□ Vérification PEP 8 automatique
□ Vérification docstrings automatique
□ Build documentation automatique
□ Couverture de tests vérifiée
```

### 🚀 Déploiement
```
□ Application déployée et accessible
□ URL publique fonctionnelle
□ Performance acceptable
□ Gestion d'erreurs utilisateur
□ UX intuitive et responsive
```

### 📊 Contenu analytique
```
□ Question/thème principal clairement défini
□ Insights pertinents et actionnables
□ Visualisations interactives et belles
□ Storytelling engageant
□ Réponse à la problématique initiale
```

---

## 🚨 POINTS D'ATTENTION CRITIQUES

### ❌ Erreurs à éviter absolument
```
□ Code non-PEP 8 → Échec automatique
□ Absence de docstrings → Échec CI/CD
□ Tests <90% coverage → Échec automatique  
□ Utilisation d'eval() → Problème sécurité
□ Secrets en dur → Problème sécurité
□ Repository privé → Non conforme
□ Application non déployée → Incomplet
□ Pas de type hints → Non conforme
```

### ✅ Points qui feront la différence
```
□ Innovation dans l'analyse choisie
□ Qualité exceptionnelle des visualisations
□ UX/UI soignée et professionnelle
□ Performance optimisée (cache Streamlit)
□ Gestion d'erreurs élégante
□ Documentation exemplaire
□ Tests exhaustifs et pertinents
□ Architecture modulaire et maintenable
```

---

## 📞 PROCHAINES ÉTAPES IMMÉDIATES

### 🎯 Actions cette semaine
1. **Choisir l'axe d'analyse** (décision d'équipe)
2. **Télécharger les données complètes** 
3. **Initialiser le repository Git**
4. **Tester l'application de base**
5. **Planifier la répartition du travail en équipe**

### 💡 Conseils pour l'équipe
- **Utilisez les Pull Requests** pour tout changement
- **Commitez souvent** avec des messages clairs
- **Testez localement** avant chaque push
- **Documentez au fur et à mesure**
- **Ne laissez rien à la dernière minute**

**Bon courage ! 🚀 Vous avez toutes les cartes en main pour réussir ! 🏆**
