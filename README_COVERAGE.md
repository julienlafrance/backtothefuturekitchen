# 📊 Guide du Coverage avec pytest-cov

## Vue d'ensemble

Ce projet utilise **pytest-cov** pour mesurer la couverture des tests avec un **objectif minimum de 90%**.

## État actuel

| Répertoire | Coverage | Tests | État |
|------------|----------|-------|------|
| `10_preprod/` | **96%** ✅ | 22 tests | Configuré et fonctionnel |
| `00_eda/_data_utils/` | Configuration ✅ | 8 tests (partiels) | Prêt à compléter |
| `20_prod/streamlit/` | Documentation ✅ | À créer | Guide disponible |
| `50_test/` | N/A | 35 tests | Tests d'infrastructure (pas besoin coverage) |

## Installation et utilisation

### Pour chaque module

```bash
# Se placer dans le répertoire du module
cd 10_preprod  # ou 00_eda/_data_utils ou 20_prod

# Installer les dépendances de test
uv sync --extra dev

# Lancer les tests avec coverage
uv run pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

# Ouvrir le rapport HTML
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
```

## Configuration type (pyproject.toml)

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=7.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=90"

[tool.coverage.run]
omit = [
    "*/main.py",           # Fichiers d'application
    "*/pages/*",           # Pages UI
    "*/__pycache__/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",     # Marquer lignes à exclure
    "if __name__ == .__main__.:",
]
```

## Stratégie pour atteindre 90%

### ✅ Ce qu'on teste

- Fonctions de transformation de données
- Logique métier
- Utilitaires et helpers
- Fonctions de calcul
- Validation des données

### ❌ Ce qu'on exclut (pragma: no cover)

- Fichiers d'application Streamlit (main.py)
- Pages UI avec st.*
- Imports conditionnels (try/except ImportError)
- Fonctions de plotting/visualisation
- Code __main__

## Exemple 10_preprod (96% coverage atteint!)

### Fichiers testés

- ✅ `src/mangetamain_analytics/visualization/analyse_ratings_simple.py` - 100%
- ✅ `src/mangetamain_analytics/visualization/custom_charts.py` - 91%

### Tests créés

- `tests/unit/test_analyse_ratings_simple.py` - 14 tests
- `tests/unit/test_custom_charts.py` - 8 tests

### Commandes

```bash
cd 10_preprod
uv run pytest tests/unit/ -v --cov=src --cov-report=term

# Résultat: 96% de coverage (22 tests passés)
```

### Techniques utilisées

1. **Mocks pour DuckDB**
   ```python
   from unittest.mock import Mock, MagicMock

   mock_conn = Mock()
   mock_conn.execute.return_value.fetchdf.return_value = test_df
   ```

2. **Mocks pour Streamlit**
   ```python
   import sys
   sys.modules['streamlit'] = MagicMock()
   ```

3. **Tests de transformation de données**
   ```python
   def test_process_data():
       input_df = pd.DataFrame({'rating': [1,2,3,4,5]})
       result, stats = process_data(input_df)
       assert stats['total'] == 5
   ```

4. **Exclusion de code UI**
   ```python
   def render_analysis(conn=None):  # pragma: no cover
       """Fonction Streamlit - exclue du coverage"""
       st.plotly_chart(fig)
   ```

## Bonnes pratiques

### 1. Testez les transformations, pas l'UI

```python
# ✅ BON - Fonction testable
def calculate_stats(data: pd.DataFrame) -> dict:
    return {
        'mean': data['value'].mean(),
        'std': data['value'].std()
    }

# ❌ DIFFICILE - Fonction UI
def show_stats(data: pd.DataFrame):  # pragma: no cover
    stats = calculate_stats(data)
    st.metric("Moyenne", stats['mean'])
```

### 2. Utilisez des fixtures pytest

```python
@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'rating': [1, 2, 3, 4, 5],
        'count': [10, 20, 30, 40, 50]
    })

def test_with_fixture(sample_dataframe):
    result = process_data(sample_dataframe)
    assert len(result) == 5
```

### 3. Marquez le code non-testable

```python
def main():  # pragma: no cover
    """Point d'entrée - pas besoin de tester"""
    app.run()

try:
    import optional_module
except ImportError:  # pragma: no cover
    optional_module = None
```

## Rapports de coverage

### Terminal (résumé)
```
Name                                  Stmts   Miss  Cover
---------------------------------------------------------
src/module/data.py                       45      3    93%
src/module/utils.py                      67      0   100%
---------------------------------------------------------
TOTAL                                   112      3    97%
```

### HTML (détaillé)
- Fichier: `htmlcov/index.html`
- Montre ligne par ligne le code couvert/non-couvert
- Code vert = testé
- Code rouge = non testé
- Code gris = exclu

## Intégration CI/CD

### GitHub Actions

```yaml
- name: Run tests with coverage
  run: |
    uv sync --extra dev
    uv run pytest tests/ --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
    flags: unittests
```

## Dépannage

### "No data was collected"
- Vérifier que `--cov=.` pointe vers le bon répertoire
- Vérifier les chemins dans `[tool.coverage.run]`

### Coverage trop bas
- Ajouter des tests unitaires
- Marquer le code UI avec `pragma: no cover`
- Exclure les fichiers non-testables dans `omit`

### Tests qui passent localement mais pas en CI
- Vérifier les dépendances dev
- Vérifier les versions Python
- Vérifier les mocks et fixtures

## Ressources

- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- Tests d'exemple: `10_preprod/tests/unit/`

## Prochaines étapes

1. ✅ 10_preprod: **96% - Terminé!**
2. ⚠️ 00_eda/_data_utils: Configuration faite, compléter les tests
3. 📝 20_prod: Suivre le guide dans `20_prod/README_TESTS.md`
4. 🚀 Intégrer dans CI/CD
