#!/usr/bin/env python3
"""
Import des CSV manquants dans DuckDB et analyse complète
"""

import os
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import glob
warnings.filterwarnings('ignore')

# Import YData SDK
from ydata.dataset.filetype import FileType
from ydata.metadata import Metadata
from ydata.connectors import LocalConnector
from ydata.profiling import ProfileReport

# Charger la configuration depuis .env
def load_env_config():
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    return 'YDATA_LICENSE_KEY' in os.environ

# Charger la configuration
ydata_available = load_env_config()

# Chemins
DB_PATH = "/home/dataia25/mangetamain/00_preprod/data/mangetamain.duckdb"
CSV_DIR = "/home/dataia25/mangetamain/00_preprod/data/"
OUTPUT_DIR = "complete_analysis"

class CompleteDuckDBAnalyzer:
    def __init__(self, db_path, csv_dir):
        self.db_path = db_path
        self.csv_dir = csv_dir
        self.conn = None
        self.tables_info = {}
        
    def connect(self):
        """Connexion à DuckDB"""
        try:
            self.conn = duckdb.connect(self.db_path)
            print(f"✅ Connexion réussie à {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def get_existing_tables(self):
        """Obtenir les tables existantes"""
        tables = self.conn.execute("SHOW TABLES").fetchall()
        return [table[0] for table in tables]
    
    def get_csv_files(self):
        """Obtenir la liste des fichiers CSV"""
        csv_files = glob.glob(os.path.join(self.csv_dir, "*.csv"))
        return {os.path.basename(f).replace('.csv', ''): f for f in csv_files}
    
    def import_missing_csvs(self):
        """Importer les CSV manquants dans DuckDB"""
        print("🔄 Import des CSV manquants dans DuckDB...")
        
        existing_tables = set(self.get_existing_tables())
        csv_files = self.get_csv_files()
        
        print(f"📋 Tables existantes: {existing_tables}")
        print(f"📁 CSV disponibles: {set(csv_files.keys())}")
        
        # Mapping des noms (au cas où ils sont différents)
        name_mapping = {
            'PP_users': 'users',  # PP_users correspond probablement à users
        }
        
        imported_count = 0
        for csv_name, csv_path in csv_files.items():
            # Vérifier si cette table existe déjà (en tenant compte du mapping)
            table_name = csv_name
            if csv_name in name_mapping and name_mapping[csv_name] in existing_tables:
                print(f"⏭️  {csv_name} correspond à la table existante '{name_mapping[csv_name]}'")
                continue
                
            if table_name in existing_tables:
                print(f"⏭️  Table '{table_name}' existe déjà")
                continue
            
            print(f"📥 Import de {csv_name} depuis {csv_path}...")
            
            try:
                # Obtenir la taille du fichier
                size_mb = os.path.getsize(csv_path) / 1024 / 1024
                print(f"   📊 Taille: {size_mb:.1f} MB")
                
                # Importer avec DuckDB (plus rapide que pandas pour gros fichiers)
                if size_mb > 100:
                    print(f"   🔄 Gros fichier détecté, import par chunks...")
                
                # Import direct avec DuckDB
                import_query = f"""
                CREATE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{csv_path}')
                """
                
                start_time = datetime.now()
                self.conn.execute(import_query)
                end_time = datetime.now()
                
                # Vérifier l'import
                count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                duration = (end_time - start_time).total_seconds()
                
                print(f"   ✅ Import réussi: {count:,} lignes en {duration:.1f}s")
                imported_count += 1
                
            except Exception as e:
                print(f"   ❌ Erreur lors de l'import de {csv_name}: {e}")
        
        print(f"🎯 {imported_count} nouvelle(s) table(s) importée(s)")
        return imported_count > 0
    
    def analyze_all_tables(self):
        """Analyser toutes les tables de la base"""
        print("\n🔍 Analyse de toutes les tables DuckDB...")
        
        tables = self.get_existing_tables()
        print(f"📋 Tables à analyser: {tables}")
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        timeseries_candidates = []
        
        for table_name in tables:
            print(f"\n{'='*70}")
            print(f"📊 Analyse de la table: {table_name}")
            print(f"{'='*70}")
            
            try:
                # Informations de base
                count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                schema = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
                
                print(f"📊 Lignes: {count:,}")
                print(f"📊 Colonnes: {len(schema)}")
                
                # Analyser un échantillon des colonnes pour identifier les dates
                date_columns = self.detect_date_columns_smart(table_name, schema, count)
                if date_columns:
                    print(f"📅 Colonnes temporelles: {', '.join(date_columns)}")
                    timeseries_candidates.append({
                        'table': table_name,
                        'date_columns': date_columns,
                        'row_count': count
                    })
                
                # Export et analyse avec YData
                sample_size = min(50000, count) if count > 50000 else None
                if sample_size:
                    print(f"🎯 Échantillonnage: {sample_size:,} lignes")
                
                csv_path = self.export_table_sample(table_name, sample_size)
                
                if ydata_available and csv_path:
                    self.generate_ydata_profile(table_name, csv_path)
                
                print(f"✅ Analyse de '{table_name}' terminée")
                
            except Exception as e:
                print(f"❌ Erreur lors de l'analyse de {table_name}: {e}")
        
        return timeseries_candidates
    
    def detect_date_columns_smart(self, table_name, schema, total_count):
        """Détection intelligente des colonnes de dates"""
        date_columns = []
        sample_size = min(1000, total_count)
        
        for col_info in schema:
            col_name = col_info[0]
            col_type = col_info[1]
            
            # Types explicites de dates
            if any(word in col_type.upper() for word in ['DATE', 'TIME', 'TIMESTAMP']):
                date_columns.append(col_name)
                continue
            
            # Noms suggestifs + vérification
            if any(word in col_name.lower() for word in ['date', 'time', 'created', 'updated', 'timestamp']):
                try:
                    sample = self.conn.execute(f"SELECT {col_name} FROM {table_name} LIMIT {sample_size}").fetchall()
                    date_like_count = 0
                    
                    for row in sample[:100]:  # Tester seulement les 100 premières
                        if row[0]:
                            try:
                                pd.to_datetime(str(row[0]))
                                date_like_count += 1
                            except:
                                pass
                    
                    # Si au moins 80% des valeurs sont des dates
                    if date_like_count > 80:
                        date_columns.append(col_name)
                        
                except Exception as e:
                    pass
        
        return date_columns
    
    def export_table_sample(self, table_name, sample_size=None):
        """Exporter un échantillon de table"""
        try:
            if sample_size:
                query = f"SELECT * FROM {table_name} LIMIT {sample_size}"
            else:
                query = f"SELECT * FROM {table_name}"
            
            df = self.conn.execute(query).df()
            csv_path = os.path.join(OUTPUT_DIR, f"{table_name}.csv")
            df.to_csv(csv_path, index=False)
            
            print(f"📤 Export: {csv_path}")
            return csv_path
            
        except Exception as e:
            print(f"❌ Erreur export {table_name}: {e}")
            return None
    
    def generate_ydata_profile(self, table_name, csv_path):
        """Générer un profil YData"""
        if not ydata_available:
            return
            
        try:
            print(f"🔍 Profil YData pour '{table_name}'...")
            
            connector = LocalConnector()
            data = connector.read_file(csv_path, file_type=FileType.CSV)
            
            metadata = Metadata(dataset=data)
            
            # Afficher quelques stats importantes
            print(f"   📊 Lignes: {metadata.summary['nrows']}")
            print(f"   📊 Cardinalité: {len([k for k, v in metadata.summary['cardinality'].items() if v > 1000])}/{len(metadata.summary['cardinality'])} colonnes avec >1000 valeurs uniques")
            print(f"   📊 Doublons: {metadata.summary['duplicates']}")
            
            # Générer le rapport
            report = ProfileReport(dataset=data, title=f'Profil Complet - {table_name}')
            report_path = os.path.join(OUTPUT_DIR, f"{table_name}_complete_profile.html")
            report.to_file(report_path)
            
            print(f"   ✅ Rapport: {report_path}")
            
        except Exception as e:
            print(f"   ❌ Erreur profil YData: {e}")
    
    def close(self):
        if self.conn:
            self.conn.close()

def main():
    """Fonction principale"""
    print("🚀 Import et Analyse Complète DuckDB avec YData")
    print("=" * 70)
    
    analyzer = CompleteDuckDBAnalyzer(DB_PATH, CSV_DIR)
    
    if not analyzer.connect():
        return
    
    try:
        # 1. Import des CSV manquants
        imported_new = analyzer.import_missing_csvs()
        if imported_new:
            print("\n🎯 Nouvelles données importées dans DuckDB!")
        
        # 2. Analyse complète
        timeseries_candidates = analyzer.analyze_all_tables()
        
        # 3. Résumé final
        print(f"\n{'='*70}")
        print("🎯 RÉSUMÉ FINAL")
        print(f"{'='*70}")
        
        final_tables = analyzer.get_existing_tables()
        print(f"📊 Total tables dans DuckDB: {len(final_tables)}")
        for table in final_tables:
            count = analyzer.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"   ✅ {table}: {count:,} lignes")
        
        print(f"\n🕐 Tables candidates pour Time Series: {len(timeseries_candidates)}")
        for candidate in timeseries_candidates:
            print(f"   📅 {candidate['table']}: {', '.join(candidate['date_columns'])} ({candidate['row_count']:,} lignes)")
        
        print(f"\n📂 Rapports disponibles dans: {OUTPUT_DIR}/")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
