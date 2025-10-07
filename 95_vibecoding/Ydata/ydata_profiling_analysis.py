#!/usr/bin/env python3
"""
Analyse avec ydata-profiling (l'outil de base qui génère de VRAIS rapports HTML)
"""

import duckdb
import pandas as pd
from ydata_profiling import ProfileReport

# Connexion DuckDB
conn = duckdb.connect('/home/dataia25/mangetamain/10_prod/data/mangetamain.duckdb')

# Liste des tables
tables = conn.execute('SHOW TABLES').fetchall()
table_names = [table[0] for table in tables]

print(f"🚀 ANALYSE YDATA-PROFILING DE {len(table_names)} TABLES")
print("=" * 80)

for table_name in table_names:
    try:
        print(f"\n📊 Analyse de {table_name}...")
        
        # Charger les données (échantillon si trop gros)
        count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
        
        if count > 50000:
            df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 50000').df()
            print(f"  Échantillon: 50,000 sur {count:,} lignes")
        else:
            df = conn.execute(f'SELECT * FROM {table_name}').df()
            print(f"  Volume: {count:,} lignes")
        
        # FIX DATETIME: Convertir les colonnes datetime en string
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                print(f"  🔧 Conversion datetime: {col}")
                df[col] = df[col].dt.strftime('%Y-%m-%d')
        
        # PROFILING avec ydata-profiling
        print(f"  🔬 Génération du rapport profiling...")
        profile = ProfileReport(
            df,
            title=f"YData Profiling - {table_name}",
            explorative=True,
            minimal=False
        )
        
        # Sauvegarder le rapport HTML
        output_path = f"ydata_analysis/profiling_{table_name}.html"
        profile.to_file(output_path)
        
        print(f"  ✅ Rapport généré: {output_path}")
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")

conn.close()

print("\n" + "=" * 80)
print("🎉 ANALYSE TERMINÉE - Rapports HTML générés dans ydata_analysis/")
print("=" * 80)
