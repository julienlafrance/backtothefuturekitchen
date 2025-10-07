#!/usr/bin/env python3
"""
Analyse temporelle avec ydata-profiling - Configuration TimeSeries activée
"""

import duckdb
import pandas as pd
from ydata_profiling import ProfileReport

# Tables avec colonnes temporelles
temporal_tables = {
    'RAW_interactions': 'date',
    'RAW_recipes': 'submitted',
    'interactions_test': 'date',
    'interactions_train': 'date',
    'interactions_validation': 'date'
}

# Connexion DuckDB
conn = duckdb.connect('/home/dataia25/mangetamain/10_prod/data/mangetamain.duckdb')

print("🚀 ANALYSE TEMPORELLE YDATA-PROFILING")
print("=" * 80)

for table_name, date_column in temporal_tables.items():
    try:
        print(f"\n📊 Analyse temporelle de {table_name} (colonne: {date_column})...")
        
        # Charger données
        count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
        
        if count > 50000:
            df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 50000').df()
            print(f"  Échantillon: 50,000 sur {count:,} lignes")
        else:
            df = conn.execute(f'SELECT * FROM {table_name}').df()
            print(f"  Volume: {count:,} lignes")
        
        # IMPORTANT: Garder les datetime en datetime (pas de conversion en string!)
        # ydata-profiling détecte automatiquement les séries temporelles
        
        # Trier par date pour l'analyse temporelle
        if date_column in df.columns:
            df = df.sort_values(by=date_column)
            print(f"  🕒 Période: {df[date_column].min()} → {df[date_column].max()}")
        
        # Configuration ProfileReport avec analyse temporelle
        print(f"  🔬 Génération rapport avec analyse temporelle...")
        profile = ProfileReport(
            df,
            title=f"TimeSeries Analysis - {table_name}",
            tsmode=True,  # ACTIVE MODE SÉRIE TEMPORELLE
            sortby=date_column,  # Trier par la colonne temporelle
            explorative=True,
            minimal=False
        )
        
        # Sauvegarder
        output_path = f"ydata_analysis/timeseries_{table_name}.html"
        profile.to_file(output_path)
        
        print(f"  ✅ Rapport temporel: {output_path}")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

conn.close()

print("\n" + "=" * 80)
print("🎉 ANALYSES TEMPORELLES TERMINÉES")
print("=" * 80)
print("\n📁 Rapports générés:")
print("  - timeseries_RAW_interactions.html")
print("  - timeseries_RAW_recipes.html")
print("  - timeseries_interactions_test.html")
print("  - timeseries_interactions_train.html")
print("  - timeseries_interactions_validation.html")
print("\n🔍 Ces rapports incluent:")
print("  - Analyse de saisonnalité")
print("  - Détection de tendances")
print("  - Patterns temporels")
print("  - Autocorrélations")
print("  - Graphiques temporels interactifs")
