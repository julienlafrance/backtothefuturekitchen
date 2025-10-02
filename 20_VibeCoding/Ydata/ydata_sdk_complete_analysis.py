#!/usr/bin/env python3
"""
Analyse complète avec le vrai YData SDK
Utilise les fonctionnalités avancées du YData SDK avec le token
"""

import os
import sys
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration YData SDK
def configure_ydata():
    """Configuration du YData SDK avec la licence"""
    # Charger .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                    except ValueError:
                        continue
    
    # Configuration YData
    license_key = os.environ.get('YDATA_LICENSE_KEY')
    if not license_key:
        raise ValueError("YDATA_LICENSE_KEY non trouvé dans .env")
    
    # Configuration du SDK
    from ydata import configure
    configure(license_key=license_key)
    
    print(f"✅ YData SDK configuré avec la licence: {license_key[:10]}...")
    return license_key

# Imports YData SDK
def import_ydata_components():
    """Import des composants YData SDK"""
    try:
        # YData SDK - Connectors
        from ydata.connectors import LocalConnector
        from ydata.connectors.filetype import FileType
        
        # YData SDK - Profiling
        from ydata.profiling import ProfileReport
        
        # YData SDK - Metadata et Dataset
        from ydata.metadata import Metadata
        from ydata.dataset import Dataset
        
        # YData SDK - Synthesizers
        from ydata.synthesizers.regular.model import RegularSynthesizer
        from ydata.synthesizers.timeseries.model import TimeSeriesSynthesizer
        
        # YData SDK - Reports
        from ydata.report import SyntheticDataProfile
        
        print("✅ Composants YData SDK importés avec succès")
        
        return {
            'LocalConnector': LocalConnector,
            'FileType': FileType,
            'ProfileReport': ProfileReport,
            'Metadata': Metadata,
            'Dataset': Dataset,
            'RegularSynthesizer': RegularSynthesizer,
            'TimeSeriesSynthesizer': TimeSeriesSynthesizer,
            'SyntheticDataProfile': SyntheticDataProfile
        }
        
    except ImportError as e:
        print(f"❌ Erreur import YData SDK: {e}")
        # Fallback vers ydata-profiling
        print("🔄 Utilisation de ydata-profiling comme fallback")
        from ydata_profiling import ProfileReport
        return {'ProfileReport': ProfileReport}

def connect_to_duckdb():
    """Connexion à la base DuckDB"""
    db_path = '/home/dataia25/mangetamain/10_prod/data/mangetamain.duckdb'
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Base DuckDB non trouvée: {db_path}")
    
    conn = duckdb.connect(db_path)
    print(f"✅ Connexion DuckDB: {db_path}")
    return conn

def analyze_with_ydata_sdk(df, table_name, ydata_components):
    """Analyse avec YData SDK"""
    
    print(f"🔬 Analyse YData SDK pour {table_name}...")
    
    if 'LocalConnector' in ydata_components and 'Dataset' in ydata_components:
        # Analyse avancée avec YData SDK complet
        print("  📊 Utilisation des fonctionnalités YData SDK avancées")
        
        # Exporter temporairement en CSV pour le connector
        csv_path = f"ydata_analysis/{table_name}_temp.csv"
        df.to_csv(csv_path, index=False)
        
        try:
            # Connexion locale
            connector = ydata_components['LocalConnector'](csv_path)
            
            # Création du dataset
            dataset = ydata_components['Dataset'](
                connector=connector,
                filetype=ydata_components['FileType'].CSV
            )
            
            # Profiling avec SDK
            profile = ydata_components['ProfileReport'](
                dataset=dataset,
                title=f"YData SDK Analysis - {table_name}"
            )
            
            # Sauvegarde
            output_path = f"ydata_analysis/{table_name}_ydata_sdk_profile.html"
            profile.to_file(output_path)
            
            print(f"  ✅ Rapport YData SDK: {output_path}")
            
            # Nettoyage
            os.remove(csv_path)
            
            return profile
            
        except Exception as e:
            print(f"  ⚠️ Erreur YData SDK pour {table_name}: {e}")
            # Fallback vers profiling basique
            return analyze_with_basic_profiling(df, table_name, ydata_components)
    
    else:
        # Utilisation de ydata-profiling basique
        return analyze_with_basic_profiling(df, table_name, ydata_components)

def analyze_with_basic_profiling(df, table_name, ydata_components):
    """Analyse avec profiling de base (fallback)"""
    print(f"  📊 Profiling basique pour {table_name}")
    
    ProfileReport = ydata_components['ProfileReport']
    
    # Configuration optimisée
    config = {}
    if len(df) > 50000:
        config['minimal'] = True
        print(f"  ⚡ Mode minimal activé pour {len(df):,} lignes")
    
    profile = ProfileReport(
        df,
        title=f"Profile - {table_name}",
        **config
    )
    
    output_path = f"ydata_analysis/{table_name}_profile.html"
    profile.to_file(output_path)
    
    print(f"  ✅ Rapport basique: {output_path}")
    return profile

def detect_temporal_columns(df, table_name):
    """Détection des colonnes temporelles"""
    temporal_cols = []
    
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            temporal_cols.append(col)
        elif col.lower() in ['date', 'timestamp', 'time', 'submitted', 'created']:
            try:
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    if parsed.notna().sum() > len(sample) * 0.8:
                        temporal_cols.append(col)
            except:
                continue
    
    if temporal_cols:
        print(f"  🕒 Colonnes temporelles dans {table_name}: {temporal_cols}")
    
    return temporal_cols

def analyze_all_tables():
    """Analyse complète de toutes les tables avec YData SDK"""
    
    print("🚀 ANALYSE COMPLÈTE AVEC YDATA SDK")
    print("=" * 60)
    
    # Configuration YData SDK
    try:
        configure_ydata()
    except Exception as e:
        print(f"⚠️ Configuration YData SDK échouée: {e}")
        print("🔄 Continuons avec les outils disponibles")
    
    # Import des composants
    ydata_components = import_ydata_components()
    
    # Connexion base
    conn = connect_to_duckdb()
    
    # Liste des tables
    tables = conn.execute('SHOW TABLES').fetchall()
    table_names = [table[0] for table in tables]
    
    print(f"\n📋 Analyse de {len(table_names)} tables avec YData SDK:")
    print("=" * 60)
    
    results = {}
    
    for table_name in table_names:
        print(f"\n🔄 Traitement {table_name}...")
        
        try:
            # Récupération des données
            count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
            
            if count > 200000:
                # Échantillonnage pour très gros datasets
                df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 50000').df()
                print(f"  📊 Échantillon: 50k lignes sur {count:,}")
            else:
                df = conn.execute(f'SELECT * FROM {table_name}').df()
                print(f"  📊 Dataset complet: {count:,} lignes")
            
            # Export CSV
            csv_path = f"ydata_analysis/{table_name}.csv"
            df.to_csv(csv_path, index=False)
            
            # Détection temporelle
            temporal_cols = detect_temporal_columns(df, table_name)
            
            # Analyse YData SDK
            profile = analyze_with_ydata_sdk(df, table_name, ydata_components)
            
            results[table_name] = {
                'status': 'success',
                'rows': len(df),
                'total_rows': count,
                'columns': len(df.columns),
                'temporal_columns': temporal_cols,
                'csv_path': csv_path,
                'sampled': count > 200000
            }
            
            print(f"  ✅ {table_name} analysé avec succès")
            
        except Exception as e:
            print(f"  ❌ Erreur {table_name}: {e}")
            results[table_name] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ ANALYSE YDATA SDK")
    print("=" * 60)
    
    successful = 0
    total_analyzed_rows = 0
    total_actual_rows = 0
    temporal_tables = []
    
    for table_name, result in results.items():
        if result['status'] == 'success':
            successful += 1
            total_analyzed_rows += result['rows']
            total_actual_rows += result['total_rows']
            
            status_str = "📊 ÉCHANTILLON" if result.get('sampled') else "📋 COMPLET"
            print(f"✅ {table_name}: {result['rows']:,} lignes analysées sur {result['total_rows']:,} ({status_str})")
            
            if result['temporal_columns']:
                temporal_tables.append({
                    'table': table_name,
                    'temporal_columns': result['temporal_columns']
                })
        else:
            print(f"❌ {table_name}: {result['error']}")
    
    print(f"\n📈 Statistiques:")
    print(f"  - Tables analysées: {successful}/{len(table_names)}")
    print(f"  - Lignes analysées: {total_analyzed_rows:,}")
    print(f"  - Total lignes DB: {total_actual_rows:,}")
    print(f"  - Tables temporelles: {len(temporal_tables)}")
    
    if temporal_tables:
        print(f"\n🕒 Tables avec données temporelles:")
        for item in temporal_tables:
            print(f"  - {item['table']}: {item['temporal_columns']}")
            print(f"    → Candidat pour TimeSeriesSynthesizer")
    
    conn.close()
    print(f"\n🎯 Analyse YData SDK terminée !")
    print(f"📁 Rapports disponibles dans: ydata_analysis/")
    
    return results

if __name__ == "__main__":
    # Créer le dossier de sortie
    os.makedirs("ydata_analysis", exist_ok=True)
    
    # Lancer l'analyse
    results = analyze_all_tables()
