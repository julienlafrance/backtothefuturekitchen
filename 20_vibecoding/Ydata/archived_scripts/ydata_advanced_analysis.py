#!/usr/bin/env python3
"""
Analyse approfondie avec YData SDK
"""

import os
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import YData SDK
from ydata.dataset.filetype import FileType
from ydata.metadata import Metadata
from ydata.connectors import LocalConnector
from ydata.profiling import ProfileReport

# Charger la configuration depuis .env
def load_env_config():
    """Charger la configuration depuis le fichier .env"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Vérifier si le token est disponible
    if 'YDATA_LICENSE_KEY' not in os.environ or os.environ['YDATA_LICENSE_KEY'] == '{add-your-token}':
        print("⚠️  Token YData non configuré.")
        return False
    return True

# Charger la configuration
ydata_available = load_env_config()

# Chemins
DB_PATH = "/home/dataia25/mangetamain/00_preprod/data/mangetamain.duckdb"
OUTPUT_DIR = "ydata_analysis"

class YDataAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path
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
    
    def analyze_table_structure(self, table_name):
        """Analyse détaillée de la structure d'une table"""
        print(f"\n📋 Analyse détaillée de la table: {table_name}")
        print("-" * 60)
        
        # Informations de base
        count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        schema = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
        
        print(f"📊 Nombre de lignes: {count:,}")
        print(f"📊 Nombre de colonnes: {len(schema)}")
        
        # Analyse des colonnes
        print("\n🔍 Structure des colonnes:")
        for col in schema:
            col_name, col_type = col[0], col[1]
            
            if 'INT' in col_type.upper() or 'DOUBLE' in col_type.upper() or 'FLOAT' in col_type.upper():
                stats = self.conn.execute(f"""
                    SELECT 
                        MIN({col_name}) as min_val,
                        MAX({col_name}) as max_val,
                        AVG({col_name}) as mean_val,
                        COUNT(DISTINCT {col_name}) as unique_count,
                        COUNT(*) - COUNT({col_name}) as null_count
                    FROM {table_name}
                """).fetchone()
                
                print(f"   📈 {col_name} ({col_type}):")
                mean_val = f"{stats[2]:.2f}" if stats[2] is not None else "N/A"
                print(f"      Min: {stats[0]}, Max: {stats[1]}, Moyenne: {mean_val}")
                print(f"      Valeurs uniques: {stats[3]}, Nulls: {stats[4]}")
            else:
                stats = self.conn.execute(f"""
                    SELECT 
                        COUNT(DISTINCT {col_name}) as unique_count,
                        COUNT(*) - COUNT({col_name}) as null_count
                    FROM {table_name}
                """).fetchone()
                
                print(f"   📝 {col_name} ({col_type}):")
                print(f"      Valeurs uniques: {stats[0]}, Nulls: {stats[1]}")
        
        # Détection des colonnes temporelles
        date_columns = self.detect_date_columns(table_name, schema)
        if date_columns:
            print(f"\n📅 Colonnes temporelles détectées: {', '.join(date_columns)}")
            
        self.tables_info[table_name] = {
            'count': count,
            'schema': schema,
            'date_columns': date_columns
        }
        
        return count, schema, date_columns
    
    def detect_date_columns(self, table_name, schema):
        """Détecter les colonnes de dates"""
        date_columns = []
        
        for col_info in schema:
            col_name, col_type = col_info[0], col_info[1]
            if any(word in col_type.upper() for word in ['DATE', 'TIME', 'TIMESTAMP']):
                date_columns.append(col_name)
            elif any(word in col_name.lower() for word in ['date', 'time', 'created', 'updated', 'timestamp']):
                try:
                    sample = self.conn.execute(f"SELECT {col_name} FROM {table_name} LIMIT 5").fetchall()
                    for row in sample:
                        if row[0]:
                            pd.to_datetime(str(row[0]))
                            date_columns.append(col_name)
                            break
                except:
                    pass
        
        return date_columns
    
    def export_table_to_csv(self, table_name, sample_size=None):
        """Exporter une table vers CSV pour YData"""
        print(f"📤 Export de la table '{table_name}' vers CSV...")
        
        if sample_size:
            query = f"SELECT * FROM {table_name} LIMIT {sample_size}"
        else:
            query = f"SELECT * FROM {table_name}"
        
        df = self.conn.execute(query).df()
        
        # Créer le dossier de sortie
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        csv_path = os.path.join(OUTPUT_DIR, f"{table_name}.csv")
        
        df.to_csv(csv_path, index=False)
        print(f"✅ Table exportée: {csv_path}")
        
        return csv_path, df
    
    def generate_ydata_profile(self, table_name, csv_path):
        """Générer un profil avec YData SDK"""
        if not ydata_available:
            print("⚠️  YData SDK non disponible - Token manquant")
            return None
            
        print(f"🔍 Génération du profil YData pour '{table_name}'...")
        
        try:
            # Utiliser LocalConnector pour lire le CSV
            connector = LocalConnector()
            data = connector.read_file(csv_path, file_type=FileType.CSV)
            
            print(f"📊 Dataset chargé: {len(data)} lignes")
            
            # Calculer les métadonnées
            metadata = Metadata(dataset=data)
            print(f"📋 Métadonnées calculées")
            
            # Afficher le résumé des métadonnées
            print("\n📊 Résumé des métadonnées:")
            for item, values in metadata.summary.items():
                print(f"   {item}: {values}")
            
            # Générer le rapport de profil
            report = ProfileReport(
                dataset=data, 
                title=f'Rapport de Profil YData - {table_name}'
            )
            
            # Sauvegarder le rapport
            report_path = os.path.join(OUTPUT_DIR, f"{table_name}_ydata_profile.html")
            report.to_file(report_path)
            
            print(f"✅ Rapport YData sauvegardé: {report_path}")
            
            return report_path, metadata, data
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération du profil YData: {e}")
            return None
    
    def analyze_temporal_patterns(self, table_name, date_columns, df):
        """Analyser les patterns temporels"""
        print(f"\n🕐 Analyse des patterns temporels pour '{table_name}':")
        
        for date_col in date_columns:
            try:
                # Convertir en datetime
                df[date_col] = pd.to_datetime(df[date_col])
                
                # Statistiques temporelles
                date_range = df[date_col].max() - df[date_col].min()
                print(f"\n   📅 Colonne: {date_col}")
                print(f"      Période: {df[date_col].min()} à {df[date_col].max()}")
                print(f"      Durée: {date_range.days} jours")
                
                # Distribution temporelle
                df['year'] = df[date_col].dt.year
                df['month'] = df[date_col].dt.month
                df['day'] = df[date_col].dt.day
                
                year_counts = df['year'].value_counts().sort_index()
                print(f"      Années: {list(year_counts.index)} (de {year_counts.index.min()} à {year_counts.index.max()})")
                
                # Identifier si c'est une série temporelle
                if len(year_counts) > 1 or date_range.days > 30:
                    print(f"      ✅ Candidat pour analyse time series")
                    
            except Exception as e:
                print(f"      ❌ Erreur analyse temporelle pour {date_col}: {e}")
    
    def close(self):
        """Fermer la connexion"""
        if self.conn:
            self.conn.close()

def main():
    """Fonction principale d'analyse avec YData SDK"""
    print("🚀 Analyse avancée des données DuckDB avec YData SDK")
    print("=" * 70)
    
    if ydata_available:
        print("🔑 YData SDK configuré - Analyses avancées disponibles")
    else:
        print("⚠️  YData SDK non configuré - Analyses de base uniquement")
    
    # Initialiser l'analyseur
    analyzer = YDataAnalyzer(DB_PATH)
    
    if not analyzer.connect():
        return
    
    try:
        # Lister les tables
        tables = analyzer.conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        print(f"📋 Tables trouvées: {table_names}")
        
        timeseries_candidates = []
        
        # Analyser chaque table
        for table_name in table_names:
            print(f"\n{'='*70}")
            
            # Analyse de structure
            count, schema, date_columns = analyzer.analyze_table_structure(table_name)
            
            # Décider de la taille d'échantillon
            sample_size = None
            if count > 50000:
                sample_size = 25000
                print(f"🎯 Échantillonnage à {sample_size} lignes pour l'analyse")
            
            # Export vers CSV
            csv_path, df = analyzer.export_table_to_csv(table_name, sample_size)
            
            # Générer le profil YData si disponible
            if ydata_available:
                ydata_result = analyzer.generate_ydata_profile(table_name, csv_path)
            
            # Analyser les patterns temporels
            if date_columns:
                analyzer.analyze_temporal_patterns(table_name, date_columns, df.copy())
                timeseries_candidates.append({
                    'table': table_name,
                    'date_columns': date_columns,
                    'row_count': count
                })
            
            print(f"✅ Analyse de '{table_name}' terminée")
            
        print(f"\n{'='*70}")
        print(f"✅ Analyse complète terminée!")
        print(f"📂 Résultats sauvegardés dans: {OUTPUT_DIR}/")
        
        # Résumé des candidats time series
        print(f"\n🕐 Résumé des candidats pour analyse time series:")
        if timeseries_candidates:
            for candidate in timeseries_candidates:
                print(f"   📅 {candidate['table']}: {', '.join(candidate['date_columns'])} ({candidate['row_count']:,} lignes)")
            print(f"\n✨ {len(timeseries_candidates)} table(s) candidate(s) identifiée(s)")
        else:
            print("   ⚠️  Aucune colonne temporelle détectée")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
