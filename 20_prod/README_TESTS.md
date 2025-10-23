# Tests et Coverage pour 20_prod

## Configuration pytest-cov

Pour ajouter le coverage au projet de production Streamlit:

### 1. Créer pyproject.toml

```toml
[project]
name = "mangetamain-prod"
version = "1.0.0"
requires-python = ">=3.11,<3.14"
dependencies = [
    "streamlit>=1.28.0",
    "duckdb>=1.4.1",
    "pandas>=2.3.3",
    # ... autres dépendances
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=7.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=streamlit --cov-report=html --cov-report=term-missing --cov-fail-under=90"

[tool.coverage.run]
omit = [
    "*/main.py",          # Fichier d'entrée Streamlit
    "*/pages/*",          # Pages Streamlit (UI)
    "*/__pycache__/*",
    "*/.venv/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### 2. Créer structure tests/

```
20_prod/
├── streamlit/
│   ├── main.py
│   ├── data/
│   ├── models/
│   └── visualization/
├── tests/
│   ├── unit/
│   │   ├── test_data_loaders.py
│   │   └── test_visualizations.py
│   └── integration/
│       └── test_end_to_end.py
└── pyproject.toml
```

### 3. Lancer les tests

```bash
cd 20_prod
uv sync --extra dev
uv run pytest tests/ -v --cov=streamlit --cov-report=html
```

## Stratégie de test pour Streamlit

### Ce qu'on teste (coverage inclus):
- ✅ Fonctions de chargement de données
- ✅ Fonctions de transformation
- ✅ Logique métier
- ✅ Utilitaires

### Ce qu'on exclut (pragma: no cover):
- ❌ main.py (point d'entrée Streamlit)
- ❌ Fonctions avec st.* (UI Streamlit)
- ❌ Pages Streamlit
- ❌ Callbacks UI

## Exemple de test

```python
import pytest
from unittest.mock import Mock, patch

def test_load_data_from_duckdb():
    """Test chargement données depuis DuckDB"""
    mock_conn = Mock()
    mock_conn.execute.return_value.fetchdf.return_value = pd.DataFrame({
        'id': [1, 2, 3],
        'value': [10, 20, 30]
    })

    result = load_data(mock_conn, "test_table")

    assert len(result) == 3
    assert 'value' in result.columns
```

## Objectif: 90% de coverage minimum

Pour atteindre 90%:
1. Tester toutes les fonctions de données
2. Tester toutes les transformations
3. Exclure les fichiers UI avec `pragma: no cover` ou dans pyproject.toml
4. Utiliser mocks pour DuckDB et S3
