# Mangetamain Analytics - Code Application

Application Streamlit d'analyse de données culinaires (environnement de développement preprod).

## Installation

```bash
uv sync
uv run streamlit run src/mangetamain_analytics/main.py
```

## Structure

```
src/mangetamain_analytics/
├── main.py              # Point d'entrée application
├── visualization/       # Modules analyses (tendances, saisonnalité, ratings, weekend)
├── utils/              # Utilitaires (data_loader, chart_theme, color_theme)
├── data/               # Gestion données DuckDB/S3
├── exceptions.py       # Exceptions personnalisées
└── infrastructure/     # Config et logging

tests/unit/             # 118 tests unitaires (93% coverage)
```

## Guides développement

- **GUIDE_INTEGRATION_ANALYSES.md** : Process complet d'intégration analyses EDA
- **CHARTE_GRAPHIQUE.md** : Charte graphique "Back to the Kitchen"

## Documentation complète

Voir documentation Sphinx du projet : `../90_doc/`
