#!/usr/bin/env python3
"""
Import des tables CSV manquantes dans DuckDB (noms originaux)
"""

import os
import duckdb
import glob
from datetime import datetime

DB_PATH = "/home/dataia25/mangetamain/00_preprod/data/mangetamain.duckdb"
CSV_DIR = "/home/dataia25/mangetamain/00_preprod/data/"

def main():
    print("🚀 Import des tables CSV manquantes dans DuckDB")
    print("=" * 60)
    
    # Connexion à DuckDB
    conn = duckdb.connect(DB_PATH)
    
    try:
        # Tables existantes
        existing_tables = set()
        tables = conn.execute("SHOW TABLES").fetchall()
        for table in tables:
            existing_tables.add(table[0])
        
        print(f"📋 Tables existantes: {sorted(existing_tables)}")
        
        # CSV disponibles
        csv_files = glob.glob(os.path.join(CSV_DIR, "*.csv"))
        csv_names = {os.path.basename(f).replace('.csv', '') for f in csv_files}
        
        print(f"📁 CSV disponibles: {sorted(csv_names)}")
        
        # Tables à importer (CSV qui ne sont pas déjà des tables)
        # Note: PP_users correspond à 'users' donc on l'exclut
        to_import = csv_names - existing_tables - {'PP_users'}  # Exclure PP_users car c'est 'users'
        
        print(f"🎯 Tables à importer: {sorted(to_import)}")
        
        if not to_import:
            print("✅ Toutes les tables sont déjà importées!")
            return
        
        # Importer chaque table manquante
        for csv_name in to_import:
            csv_path = os.path.join(CSV_DIR, f"{csv_name}.csv")
            
            print(f"\n📥 Import de '{csv_name}'...")
            
            # Taille du fichier
            size_mb = os.path.getsize(csv_path) / 1024 / 1024
            print(f"   📊 Taille: {size_mb:.1f} MB")
            
            try:
                start_time = datetime.now()
                
                # Import avec DuckDB (très rapide)
                import_query = f"""
                CREATE TABLE {csv_name} AS 
                SELECT * FROM read_csv_auto('{csv_path}')
                """
                
                conn.execute(import_query)
                
                # Vérification
                count = conn.execute(f"SELECT COUNT(*) FROM {csv_name}").fetchone()[0]
                columns = conn.execute(f"DESCRIBE {csv_name}").fetchall()
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print(f"   ✅ Import réussi: {count:,} lignes, {len(columns)} colonnes en {duration:.1f}s")
                
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        # État final
        print(f"\n📊 État final de DuckDB:")
        final_tables = conn.execute("SHOW TABLES").fetchall()
        for table in sorted(final_tables):
            count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
            print(f"   ✅ {table[0]}: {count:,} lignes")
        
    finally:
        conn.close()
        print(f"\n✅ Import terminé!")

if __name__ == "__main__":
    main()
