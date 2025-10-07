#!/usr/bin/env python3
"""
Analyse approfondie des données DuckDB avec YData SDK
"""

import os
import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from ydata_profiling import ProfileReport
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

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
        print("⚠️  Token YData non configuré. Fonctionnalités avancées limitées.")
        return False
    return True

# Charger la configuration
ydata_available = load_env_config()

# Chemins
DB_PATH = "/home/dataia25/mangetamain/00_preprod/data/mangetamain.duckdb"
OUTPUT_DIR = "advanced_analysis"

class DuckDBAnalyzer:
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
            
            # Statistiques par colonne
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
                print(f"      Min: {stats[0]}, Max: {stats[1]}, Moyenne: {stats[2]:.2f if stats[2] else 'N/A'}")
                print(f"      Valeurs uniques: {stats[3]}, Nulls: {stats[4]}")
                
            else:  # Colonnes texte/date
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
        
        for col_name, col_type in schema:
            # Colonnes avec type DATE/TIMESTAMP
            if any(word in col_type.upper() for word in ['DATE', 'TIME', 'TIMESTAMP']):
                date_columns.append(col_name)
            
            # Colonnes avec des noms suggérant des dates
            elif any(word in col_name.lower() for word in ['date', 'time', 'created', 'updated', 'timestamp']):
                # Vérifier si c'est parsable comme date
                try:
                    sample = self.conn.execute(f"SELECT {col_name} FROM {table_name} LIMIT 5").fetchall()
                    for row in sample:
                        if row[0]:  # Si pas null
                            pd.to_datetime(str(row[0]))
                            date_columns.append(col_name)
                            break
                except:
                    pass
        
        return date_columns
    
    def generate_advanced_profile(self, table_name, sample_size=None):
        """Générer un profil avancé avec YData Profiling"""
        print(f"🔍 Génération du profil avancé pour '{table_name}'...")
        
        # Charger les données
        if sample_size:
            query = f"SELECT * FROM {table_name} LIMIT {sample_size}"
        else:
            query = f"SELECT * FROM {table_name}"
        
        df = self.conn.execute(query).df()
        
        # Configuration avancée du profil
        profile = ProfileReport(
            df,
            title=f"Analyse Avancée - {table_name}",
            dataset={
                "description": f"Analyse approfondie de la table {table_name}",
                "copyright_holder": "YData Analysis",
                "copyright_year": "2024",
            },
            variables={
                "descriptions": {},
                "types": {}
            },
            # Configuration pour analyse approfondie
            minimal=False,
            explorative=True,
            # Analyses supplémentaires
            correlations={
                "auto": {"calculate": True},
                "pearson": {"calculate": True},
                "spearman": {"calculate": True},
                "kendall": {"calculate": True},
                "phi_k": {"calculate": True},
                "cramers": {"calculate": True},
            },
            missing_diagrams={
                "matrix": True,
                "bar": True,
                "heatmap": True,
                "dendrogram": True,
            },
            interactions={
                "continuous": True,
                "targets": []
            },
            samples={
                "head": 10,
                "tail": 10,
                "random": 10
            }
        )
        
        # Sauvegarder
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, f"{table_name}_advanced_profile.html")
        profile.to_file(output_file)
        
        print(f"✅ Profil avancé sauvegardé: {output_file}")
        return output_file, df
    
    def analyze_data_quality(self, table_name, df):
        """Analyse de qualité des données"""
        print(f"\n🎯 Analyse de qualité pour '{table_name}':")
        
        # Métriques de qualité
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness = (total_cells - missing_cells) / total_cells * 100
        
        print(f"   📊 Complétude globale: {completeness:.2f}%")
        
        # Complétude par colonne
        print("   📊 Complétude par colonne:")
        for col in df.columns:
            col_completeness = (1 - df[col].isnull().sum() / len(df)) * 100
            print(f"      {col}: {col_completeness:.1f}%")
        
        # Détection de doublons
        duplicates = df.duplicated().sum()
        duplicate_rate = duplicates / len(df) * 100
        print(f"   🔄 Doublons: {duplicates} ({duplicate_rate:.2f}%)")
        
        # Détection d'outliers pour les colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            print("   🎯 Outliers détectés (méthode IQR):")
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                outlier_rate = len(outliers) / len(df) * 100
                print(f"      {col}: {len(outliers)} outliers ({outlier_rate:.2f}%)")
        
        return {
            'completeness': completeness,
            'duplicates': duplicates,
            'duplicate_rate': duplicate_rate
        }
    
    def close(self):
        """Fermer la connexion"""
        if self.conn:
            self.conn.close()

def main():
    """Fonction principale d'analyse approfondie"""
    print("🚀 Analyse approfondie des données DuckDB")
    print("=" * 70)
    
    if ydata_available:
        print("🔑 Token YData configuré - Fonctionnalités avancées disponibles")
    else:
        print("⚠️  Mode de base - Configurez votre token dans .env pour plus de fonctionnalités")
    
    # Initialiser l'analyseur
    analyzer = DuckDBAnalyzer(DB_PATH)
    
    if not analyzer.connect():
        return
    
    try:
        # Lister les tables
        tables = analyzer.conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        print(f"📋 Tables trouvées: {table_names}")
        
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
            
            # Générer le profil avancé
            profile_file, df = analyzer.generate_advanced_profile(table_name, sample_size)
            
            # Analyse de qualité
            quality_metrics = analyzer.analyze_data_quality(table_name, df)
            
            print(f"✅ Analyse de '{table_name}' terminée")
            
        print(f"\n{'='*70}")
        print(f"✅ Analyse approfondie terminée!")
        print(f"📂 Rapports sauvegardés dans: {OUTPUT_DIR}/")
        
        # Préparer pour l'analyse time series
        print("\n🕐 Tables avec colonnes temporelles pour analyse time series:")
        timeseries_candidates = []
        for table_name, info in analyzer.tables_info.items():
            if info['date_columns']:
                print(f"   📅 {table_name}: {', '.join(info['date_columns'])}")
                timeseries_candidates.append(table_name)
        
        if timeseries_candidates:
            print(f"\n✨ {len(timeseries_candidates)} table(s) candidate(s) pour l'analyse time series")
        else:
            print("\n⚠️  Aucune colonne temporelle détectée automatiquement")
        
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
