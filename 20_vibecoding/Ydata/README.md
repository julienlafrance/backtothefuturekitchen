# 📊 YData Analysis - MangetaMain

Analyse complète des tables DuckDB avec YData Profiling.

## 📁 Structure du Projet

```
Ydata/
├── final_reports/              ✅ RAPPORTS FINAUX (À UTILISER)
│   ├── index.html             → Page d'accueil avec navigation
│   ├── visualisations.html    → Galerie des graphiques PNG
│   ├── profiling_*.html       → Analyses statistiques (7 rapports)
│   ├── timeseries_*.html      → Analyses temporelles (5 rapports)
│   └── temporal_*.png         → Visualisations détaillées (2 images)
│
├── archived_reports/           📦 ANCIENS RAPPORTS (archivés)
│   └── *.html, *.png          → Rapports et graphiques intermédiaires
│
├── archived_scripts/           📦 SCRIPTS OBSOLÈTES (archivés)
│   ├── test_*.py              → Scripts de test
│   ├── fix_*.py               → Scripts de correction
│   └── *_sdk_*.py             → Anciennes versions SDK
│
└── *.py                        ✅ SCRIPTS ACTIFS (6 scripts)
    ├── complete_ydata_analysis.py       → Analyse complète principale
    ├── import_and_analyze.py            → Import et analyse des données
    ├── temporal_analysis_complete.py    → Génération des PNG temporels
    ├── ydata_profiling_analysis.py      → Génération rapports profiling
    ├── ydata_sdk_complete_analysis.py   → Analyse avec SDK YData
    └── ydata_timeseries_analysis.py     → Génération rapports timeseries
```

## 🚀 Utilisation

### Consulter les Rapports

Ouvrir dans un navigateur :
```bash
firefox final_reports/index.html
# ou
xdg-open final_reports/index.html
```

### Régénérer les Analyses

```bash
# Analyse complète (profiling + timeseries)
python3 complete_ydata_analysis.py

# Seulement profiling
python3 ydata_profiling_analysis.py

# Seulement timeseries
python3 ydata_timeseries_analysis.py

# Génération des graphiques PNG
python3 temporal_analysis_complete.py
```

## 📊 Tables Analysées

| Table                      | Lignes      | Profiling | Timeseries | PNG |
|----------------------------|-------------|-----------|------------|-----|
| PP_recipes                 | 178,265     | ✅        | ❌         | ❌  |
| PP_users                   | 25,076      | ✅        | ❌         | ❌  |
| RAW_interactions           | 1,132,367   | ✅        | ✅         | ✅  |
| RAW_recipes                | 231,637     | ✅        | ✅         | ✅  |
| interactions_test          | 12,455      | ✅        | ✅         | ❌  |
| interactions_train         | 698,901     | ✅        | ✅         | ❌  |
| interactions_validation    | 7,023       | ✅        | ✅         | ❌  |

**Total : 7 tables - 2,284,724 lignes**

## 📈 Types de Rapports

### 1. PROFILING (Analyse Statistique)
- Statistiques descriptives (moyenne, médiane, écart-type)
- Distributions et histogrammes
- Matrices de corrélation
- Détection de valeurs manquantes
- Identification de duplicatas
- Analyse univariée et bivariée

### 2. TIMESERIES (Analyse Temporelle)
- Tendances temporelles
- Saisonnalité
- Autocorrélation (ACF/PACF)
- Patterns d'activité
- Pics et creux temporels

### 3. VISUALISATION (PNG)
- Graphiques détaillés haute résolution
- Analyses multi-facettes temporelles
- Export pour présentations

## 🔧 Configuration

### Base de Données
```
Path: ../00_preprod/data/mangetamain.duckdb
Type: DuckDB
Tables: 7
```

### Dépendances
```bash
pip install duckdb ydata-profiling pandas numpy matplotlib seaborn
```

## 📝 Notes

- Les rapports `profiling_*.html` sont générés pour toutes les tables
- Les rapports `timeseries_*.html` sont générés uniquement pour les tables avec dimension temporelle
- Les visualisations PNG sont générées pour les 2 plus grosses tables temporelles
- Les anciens rapports et scripts sont archivés mais conservés pour référence

## 📅 Dernière Mise à Jour

- **Date** : 7 octobre 2025
- **Version YData** : 4.17.0
- **Statut** : ✅ Complet - Toutes les tables analysées

## 🎯 Prochaines Étapes

- [ ] Analyse des tendances temporelles approfondies
- [ ] Détection d'anomalies dans les interactions
- [ ] Clustering des utilisateurs
- [ ] Système de recommandation basé sur les analyses

---

**Projet** : MangetaMain  
**Équipe** : Data Science  
**Contact** : julien.lafrance@telecom-paris.fr
