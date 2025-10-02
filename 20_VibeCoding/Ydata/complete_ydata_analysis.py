#!/usr/bin/env python3
"""
Analyse complète de toutes les tables DuckDB avec YData SDK
Basé sur ydata_sdk_documentation_complete.md
"""

import os
import sys
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import YData SDK components
from ydata_profiling import ProfileReport

def load_env_config():
    """Charger la configuration depuis le fichier .env"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                    except ValueError:
                        continue
    
    # Vérifier si le token est disponible
    token = os.environ.get('YDATA_LICENSE_KEY')
    if not token:
        print("⚠️ YDATA_LICENSE_KEY non trouvé dans .env")
    else:
        print(f"✅ YDATA_LICENSE_KEY configuré: {token[:10]}...")
    
    return token

def connect_to_duckdb():
    """Connexion à la base DuckDB de production"""
    db_path = '/home/dataia25/mangetamain/10_prod/data/mangetamain.duckdb'
    
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Base DuckDB non trouvée: {db_path}")
    
    conn = duckdb.connect(db_path)
    print(f"✅ Connexion DuckDB: {db_path}")
    return conn

def get_table_info(conn):
    """Récupérer les informations sur toutes les tables"""
    tables = conn.execute('SHOW TABLES').fetchall()
    table_info = {}
    
    print("\n🔍 Tables disponibles:")
    for table in tables:
        table_name = table[0]
        count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
        
        # Récupérer le schéma
        schema = conn.execute(f'DESCRIBE {table_name}').fetchall()
        columns = [col[0] for col in schema]
        
        table_info[table_name] = {
            'count': count,
            'columns': columns,
            'schema': schema
        }
        
        print(f"  📊 {table_name}: {count:,} lignes, {len(columns)} colonnes")
    
    return table_info

def detect_temporal_columns(df, table_name):
    """Détecter les colonnes temporelles dans le DataFrame"""
    temporal_columns = []
    
    for col in df.columns:
        # Vérifier si c'est une colonne datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            temporal_columns.append(col)
            continue
            
        # Vérifier si c'est une colonne qui pourrait être temporelle
        if col.lower() in ['date', 'timestamp', 'time', 'submitted', 'created', 'modified']:
            # Essayer de parser comme date
            try:
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    if parsed.notna().sum() > len(sample) * 0.8:  # 80% de parsing réussi
                        temporal_columns.append(col)
            except:
                continue
    
    if temporal_columns:
        print(f"  ⏰ Colonnes temporelles détectées dans {table_name}: {temporal_columns}")
    
    return temporal_columns

def create_profile_report(df, table_name, temporal_columns=None):
    """Créer un rapport de profiling YData avec configuration optimisée"""
    
    print(f"📊 Génération du profil pour {table_name}...")
    
    # Configuration de base
    config = {
        'title': f'Analyse YData - {table_name}',
        'dataset': {
            'description': f'Profil complet de la table {table_name}',
            'creator': 'YData SDK Analysis'
        },
        'variables': {
            'descriptions': {},
            'num': {
                'low_categorical_threshold': 10
            }
        },
        'correlations': {
            'pearson': {'calculate': True},
            'spearman': {'calculate': True},
            'kendall': {'calculate': False}  # Trop lent pour gros datasets
        },
        'missing_diagrams': {
            'bar': True,
            'matrix': True,
            'heatmap': True
        },
        'interactions': {
            'targets': []
        }
    }
    
    # Configuration spéciale pour time series si colonnes temporelles détectées
    if temporal_columns:
        config['tsmode'] = True
        if len(temporal_columns) > 0:
            config['sortby'] = temporal_columns[0]  # Utiliser la première colonne temporelle
        print(f"  🕒 Mode time series activé pour {temporal_columns}")
    
    # Adapter la configuration selon la taille du dataset
    if len(df) > 100000:
        # Pour les gros datasets, simplifier l'analyse
        config['correlations']['spearman']['calculate'] = False
        config['interactions']['calculate'] = False
        print(f"  ⚡ Configuration optimisée pour dataset large ({len(df):,} lignes)")
    
    try:
        # Créer le rapport
        profile = ProfileReport(
            df, 
            **config
        )
        
        # Sauvegarder
        output_path = f"ydata_analysis/{table_name}_complete_profile.html"
        profile.to_file(output_path)
        
        print(f"  ✅ Rapport sauvegardé: {output_path}")
        return profile
        
    except Exception as e:
        print(f"  ❌ Erreur lors du profiling de {table_name}: {e}")
        return None

def export_table_to_csv(conn, table_name):
    """Exporter la table vers CSV pour analyse complémentaire"""
    try:
        # Pour les gros datasets, limiter l'export
        count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
        
        if count > 500000:
            # Échantillon pour très gros datasets
            df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 100000').df()
            csv_path = f"ydata_analysis/{table_name}_sample.csv"
            print(f"  📁 Export échantillon (100k lignes sur {count:,}): {csv_path}")
        else:
            # Export complet pour datasets raisonnables
            df = conn.execute(f'SELECT * FROM {table_name}').df()
            csv_path = f"ydata_analysis/{table_name}.csv"
            print(f"  📁 Export complet: {csv_path}")
        
        df.to_csv(csv_path, index=False)
        return df, csv_path
        
    except Exception as e:
        print(f"  ❌ Erreur export CSV {table_name}: {e}")
        return None, None

def analyze_all_tables():
    """Analyse complète de toutes les tables"""
    
    print("🚀 Démarrage de l'analyse complète YData SDK")
    print("=" * 60)
    
    # Configuration
    load_env_config()
    
    # Connexion base
    conn = connect_to_duckdb()
    
    # Information tables
    table_info = get_table_info(conn)
    
    print(f"\n📋 Analyse de {len(table_info)} tables:")
    print("=" * 60)
    
    results = {}
    
    for table_name in table_info.keys():
        print(f"\n🔄 Traitement de {table_name}...")
        
        try:
            # Export vers CSV
            df, csv_path = export_table_to_csv(conn, table_name)
            
            if df is not None:
                # Détection colonnes temporelles
                temporal_columns = detect_temporal_columns(df, table_name)
                
                # Génération profil YData
                profile = create_profile_report(df, table_name, temporal_columns)
                
                results[table_name] = {
                    'status': 'success',
                    'rows': len(df),
                    'columns': len(df.columns),
                    'temporal_columns': temporal_columns,
                    'csv_path': csv_path,
                    'profile': profile is not None
                }
                
                print(f"  ✅ {table_name} analysé avec succès")
            else:
                results[table_name] = {
                    'status': 'error',
                    'error': 'Export CSV échoué'
                }
                
        except Exception as e:
            print(f"  ❌ Erreur {table_name}: {e}")
            results[table_name] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE L'ANALYSE")
    print("=" * 60)
    
    total_rows = 0
    successful_tables = 0
    temporal_tables = []
    
    for table_name, result in results.items():
        if result['status'] == 'success':
            successful_tables += 1
            total_rows += result['rows']
            
            if result['temporal_columns']:
                temporal_tables.append({
                    'table': table_name,
                    'temporal_columns': result['temporal_columns']
                })
            
            print(f"✅ {table_name}: {result['rows']:,} lignes, {result['columns']} colonnes")
        else:
            print(f"❌ {table_name}: {result['error']}")
    
    print(f"\n📈 Statistiques globales:")
    print(f"  - Tables analysées: {successful_tables}/{len(table_info)}")
    print(f"  - Total lignes: {total_rows:,}")
    print(f"  - Tables avec données temporelles: {len(temporal_tables)}")
    
    if temporal_tables:
        print(f"\n🕒 Tables temporelles identifiées:")
        for item in temporal_tables:
            print(f"  - {item['table']}: {item['temporal_columns']}")
    
    conn.close()
    print(f"\n🎯 Analyse terminée ! Rapports disponibles dans: ydata_analysis/")
    
    return results

if __name__ == "__main__":
    results = analyze_all_tables()
