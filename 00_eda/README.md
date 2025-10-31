# 00_eda — Exploratory Data Analysis (EDA)

Ce dossier contient toutes les analyses statistiques et exploratoires du projet Mangetamain, réalisées à partir du dataset Food.com.

## Structure

- `main.py` : Script principal pour lancer l’EDA.
- `_data_utils/` : Fonctions utilitaires pour l’analyse des données.
- `01_long_term/`, `02_seasonality/`, `03_week_end_effect/` : Sous-dossiers pour chaque thème d’analyse (tendances long terme, saisonnalité, effet week-end), chacun avec des analyses par ingrédient et recette.
- `09_integration/` : Intégration des résultats EDA dans l’application Streamlit preprod, avec documentation et scripts Python.
- `pyproject.toml` : Dépendances du projet (pandas, numpy, matplotlib, plotly, scikit-learn, etc.) et configuration build.

## Points clés

- Toutes les analyses statistiques du projet sont développées et stockées ici.
- Les résultats sont intégrés progressivement dans l’application Streamlit preprod (`10_preprod`).
- Documentation et notes d’intégration disponibles dans `09_integration/` (voir son README pour les détails).
- Dossier modulaire, code réutilisable et séparation claire par type d’analyse.

## Démarrage rapide

1. Installer les dépendances :
   ```bash
   pip install -r requirements.txt

2. Lancer le script principal :
   ```bash
   python main.py

## Pour aller plus loin

- Voir `09_integration/README.md` pour l’intégration et la documentation.
- Se référer au README principal du projet pour le contexte global.
