# Tests et Coverage pour data_utils

## Installation

```bash
uv sync --extra dev
```

## Lancer les tests

```bash
# Tests seuls
uv run pytest tests/ -v

# Tests avec coverage
uv run pytest tests/ -v --cov=. --cov-report=term-missing

# Tests avec rapport HTML
uv run pytest tests/ -v --cov=. --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

## Objectif coverage

- **Objectif minimum**: 90% de couverture
- **Configuration**: pyproject.toml section `[tool.coverage.run]`
- **Exclusions**: notebooks, __init__.py, tests

## Structure

```
_data_utils/
├── data_utils_common.py      # Utilitaires communs
├── data_utils_ratings.py     # Utilitaires ratings
├── data_utils_recipes.py     # Utilitaires recettes
├── tests/
│   ├── test_data_utils_common.py
│   ├── test_data_utils_ratings.py
│   └── test_data_utils_recipes.py
└── pyproject.toml            # Configuration pytest et coverage
```

## Notes

- Les tests unitaires utilisent des mocks pour les connexions DuckDB
- Les données de test sont générées synthétiquement avec Polars
- Coverage HTML disponible dans `htmlcov/`
