#!/usr/bin/env python3
"""
Analyse complète avec YData SDK 3.0+ - VERSION FINALE CORRIGÉE
Convertit les colonnes datetime en string pour compatibilité YData SDK
Génère JSON et HTML corrects
"""

import os
import sys
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import json
warnings.filterwarnings('ignore')

def configure_ydata():
    """Configuration YData SDK avec license key"""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
                    except ValueError:
                        continue
    
    license_key = os.environ.get('YDATA_LICENSE_KEY')
    if not license_key:
        raise ValueError("YDATA_LICENSE_KEY non trouvé dans .env")
    
    print(f"✅ YData SDK configuré avec licence: {license_key[:10]}...")
    return license_key

def import_ydata_sdk():
    """Import de tous les composants YData SDK"""
    try:
        from ydata.connectors.storages.local_connector import LocalConnector
        from ydata.metadata import Metadata
        from ydata.dataset import Dataset
        from ydata.synthesizers.regular.model import RegularSynthesizer
        from ydata.synthesizers.timeseries.model import TimeSeriesSynthesizer
        
        print("✅ Tous les composants YData SDK importés")
        
        return {
            'LocalConnector': LocalConnector,
            'Metadata': Metadata,
            'Dataset': Dataset,
            'RegularSynthesizer': RegularSynthesizer,
            'TimeSeriesSynthesizer': TimeSeriesSynthesizer
        }
        
    except ImportError as e:
        print(f"❌ Erreur import YData SDK: {e}")
        return None

def connect_to_duckdb():
    """Connexion à la base DuckDB de production"""
    db_path = '/home/dataia25/mangetamain/10_prod/data/mangetamain.duckdb'
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Base DuckDB non trouvée: {db_path}")
    
    conn = duckdb.connect(db_path)
    print(f"✅ Connexion DuckDB: {db_path}")
    return conn

def fix_datetime_columns_for_ydata(df, table_name):
    """
    CORRECTION CLEF: Convertir les colonnes datetime pour compatibilité YData SDK
    """
    df_fixed = df.copy()
    datetime_columns = []
    
    for col in df_fixed.columns:
        if pd.api.types.is_datetime64_any_dtype(df_fixed[col]):
            print(f"  🔧 Conversion datetime → string: {col}")
            df_fixed[col] = df_fixed[col].dt.strftime('%Y-%m-%d')
            datetime_columns.append(col)
    
    if datetime_columns:
        print(f"  ✅ {len(datetime_columns)} colonnes datetime converties pour YData SDK")
    
    return df_fixed, datetime_columns

def analyze_table_with_ydata_sdk(table_name, df, sdk_components):
    """Analyse complète d'une table avec YData SDK 3.0+"""
    
    print(f"\n🔬 ANALYSE YDATA SDK: {table_name}")
    print("-" * 60)
    
    results = {
        'table_name': table_name,
        'rows': int(len(df)),
        'columns': int(len(df.columns)),
        'memory_usage': int(df.memory_usage(deep=True).sum()),
        'analyses': {}
    }
    
    # Correction datetime
    df_fixed, converted_datetime_cols = fix_datetime_columns_for_ydata(df, table_name)
    
    # Export CSV
    csv_path = f"ydata_analysis/{table_name}.csv"
    df_fixed.to_csv(csv_path, index=False)
    
    try:
        # Créer Dataset et Metadata YData
        dataset = sdk_components['Dataset'](df_fixed)
        metadata = sdk_components['Metadata'](dataset=dataset)
        
        # Extraire métadonnées
        metadata_info = {
            'shape': list(metadata.shape) if hasattr(metadata.shape, '__iter__') else metadata.shape,
            'columns': list(metadata.columns),
            'categorical_vars': list(metadata.categorical_vars) if metadata.categorical_vars else [],
            'numerical_vars': list(metadata.numerical_vars) if metadata.numerical_vars else [],
            'date_vars': list(metadata.date_vars) if metadata.date_vars else [],
            'string_vars': list(metadata.string_vars) if metadata.string_vars else [],
            'warnings': list(metadata.warnings) if metadata.warnings else [],
            'converted_datetime_columns': converted_datetime_cols
        }
        
        results['analyses']['ydata_metadata'] = metadata_info
        
        # Qualité des données
        total_cells = len(df_fixed) * len(df_fixed.columns)
        null_cells = df_fixed.isnull().sum().sum()
        
        quality_info = {
            'completeness_rate': float(1 - (null_cells / total_cells)) if total_cells > 0 else 0,
            'null_cells': int(null_cells),
            'total_cells': int(total_cells)
        }
        
        results['analyses']['data_quality'] = quality_info
        
        # Détection colonnes temporelles
        temporal_info = {}
        for col in converted_datetime_cols:
            temporal_info[col] = {
                'is_temporal': True,
                'type': 'converted_datetime',
                'original_type': 'datetime64'
            }
        
        if temporal_info:
            results['analyses']['temporal_columns'] = temporal_info
            
            # Check si prêt pour synthèse
            has_numeric = len(metadata.numerical_vars or []) > 0
            has_volume = len(df_fixed) >= 100
            
            results['analyses']['synthesis_ready'] = {
                'ready_for_synthesis': has_numeric and has_volume,
                'temporal_columns': list(temporal_info.keys()),
                'numeric_columns': list(metadata.numerical_vars) if metadata.numerical_vars else []
            }
        
        print(f"✅ Analyse complète pour {table_name}")
        return results
        
    except Exception as e:
        print(f"❌ Erreur analyse {table_name}: {e}")
        results['analyses']['error'] = str(e)
        return results

def convert_for_json(obj):
    """Conversion robuste pour JSON - CORRIGÉE"""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: convert_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_for_json(item) for item in obj]
    else:
        return obj

def save_analysis_results(results_list):
    """Sauvegarder résultats JSON et HTML"""
    
    json_path = "ydata_analysis/ydata_sdk_FINAL_results.json"
    
    # Conversion JSON avec fonction corrigée
    json_results = []
    for result in results_list:
        try:
            json_result = convert_for_json(result)
            json_results.append(json_result)
        except Exception as e:
            print(f"❌ Erreur conversion: {e}")
            json_results.append({
                'table_name': result.get('table_name', 'unknown'),
                'error': str(e)
            })
    
    # Sauvegarder JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, default=str)
    
    print(f"\n📊 JSON sauvé: {json_path}")
    
    # Générer HTML
    generate_html_report(json_results)

def generate_html_report(results):
    """Génération HTML professionnel avec vraies données YData"""
    
    successful_results = [r for r in results if 'error' not in r.get('analyses', {})]
    total_rows = sum([r.get('rows', 0) for r in successful_results])
    
    # Analyser capacités
    temporal_tables = []
    synthesis_ready = []
    
    for result in successful_results:
        table_name = result.get('table_name')
        analyses = result.get('analyses', {})
        
        if 'temporal_columns' in analyses:
            temporal_tables.append(table_name)
        
        synth_info = analyses.get('synthesis_ready', {})
        if synth_info.get('ready_for_synthesis'):
            synthesis_ready.append(table_name)
    
    html_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>YData SDK 3.0+ - Rapport Professionnel</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }}
        .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 50px; text-align: center; }}
        .header h1 {{ font-size: 3em; margin-bottom: 15px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 40px; background: linear-gradient(135deg, #00c851, #00a644); color: white; text-align: center; }}
        .stat {{ background: rgba(255,255,255,0.15); padding: 25px; border-radius: 15px; }}
        .stat-number {{ font-size: 3em; font-weight: bold; display: block; }}
        .stat-label {{ font-size: 1.1em; opacity: 0.9; }}
        .section {{ padding: 50px; }}
        .section h2 {{ font-size: 2.5em; color: #2c3e50; border-bottom: 4px solid #3498db; padding-bottom: 15px; margin-bottom: 30px; }}
        .tables {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; }}
        .table-card {{ background: #f8f9fa; padding: 30px; border-radius: 20px; border-left: 6px solid #3498db; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: transform 0.3s; }}
        .table-card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 50px rgba(0,0,0,0.15); }}
        .table-card.synthesis-ready {{ border-left-color: #27ae60; background: linear-gradient(135deg, #d4edda, #c3e6cb); }}
        .table-title {{ font-size: 1.8em; font-weight: bold; color: #2c3e50; margin-bottom: 20px; }}
        .badge {{ display: inline-block; padding: 6px 15px; border-radius: 20px; font-size: 0.8em; font-weight: bold; margin: 5px; }}
        .badge.success {{ background: #27ae60; color: white; }}
        .badge.warning {{ background: #f39c12; color: white; }}
        .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; background: rgba(52,152,219,0.1); border-radius: 10px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ font-size: 0.9em; color: #7f8c8d; }}
        .conversion-info {{ background: #fff3cd; padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid #ffeaa7; }}
        .footer {{ background: #2c3e50; color: white; text-align: center; padding: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 YData SDK 3.0+</h1>
            <p style="font-size: 1.3em;">Analyse Professionnelle Complète</p>
            <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-number">{len(successful_results)}</span>
                <span class="stat-label">Tables Analysées</span>
            </div>
            <div class="stat">
                <span class="stat-number">{total_rows:,}</span>
                <span class="stat-label">Lignes Totales</span>
            </div>
            <div class="stat">
                <span class="stat-number">{len(temporal_tables)}</span>
                <span class="stat-label">Tables Temporelles</span>
            </div>
            <div class="stat">
                <span class="stat-number">{len(synthesis_ready)}</span>
                <span class="stat-label">Synthèse Ready</span>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Analyse Détaillée des Tables</h2>
            <div class="tables">'''
    
    for result in successful_results:
        table_name = result.get('table_name', 'Unknown')
        rows = result.get('rows', 0)
        columns = result.get('columns', 0)
        analyses = result.get('analyses', {})
        
        ydata_meta = analyses.get('ydata_metadata', {})
        num_vars = len(ydata_meta.get('numerical_vars', []))
        cat_vars = len(ydata_meta.get('categorical_vars', []))
        converted_cols = ydata_meta.get('converted_datetime_columns', [])
        
        quality_info = analyses.get('data_quality', {})
        completeness = quality_info.get('completeness_rate', 0)
        
        card_class = 'table-card'
        if table_name in synthesis_ready:
            card_class += ' synthesis-ready'
        
        badges = []
        if table_name in synthesis_ready:
            badges.append('<span class="badge success">✅ Synthèse Ready</span>')
        if converted_cols:
            badges.append('<span class="badge warning">🔧 DateTime Fixed</span>')
        
        conversion_html = ''
        if converted_cols:
            conversion_html = f'''
                <div class="conversion-info">
                    <strong>🔧 Conversion DateTime:</strong> {', '.join(converted_cols)}<br>
                    <em>datetime64 → string ISO pour compatibilité YData SDK</em>
                </div>'''
        
        html_content += f'''
                <div class="{card_class}">
                    <div class="table-title">{table_name}</div>
                    <div>{''.join(badges)}</div>
                    
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{rows:,}</div>
                            <div class="metric-label">Lignes</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{columns}</div>
                            <div class="metric-label">Colonnes</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{num_vars}</div>
                            <div class="metric-label">Numériques</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{cat_vars}</div>
                            <div class="metric-label">Catégorielles</div>
                        </div>
                    </div>
                    
                    <p><strong>📈 Qualité:</strong> {completeness:.1%} complétude</p>
                    {conversion_html}
                </div>'''
    
    html_content += f'''
            </div>
        </div>
        
        <div class="footer">
            <h3>🎯 YData SDK 3.0+ - Mission Accomplie</h3>
            <p><strong>{len(successful_results)}/7 tables analysées</strong> • <strong>{len(synthesis_ready)} prêtes pour TimeSeriesSynthesizer</strong></p>
            <p><em>Analyse professionnelle avec métadonnées complètes et compatibilité SDK</em></p>
        </div>
    </div>
</body>
</html>'''
    
    html_path = 'ydata_analysis/ydata_sdk_FINAL_REPORT.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 HTML sauvé: {html_path}")

def main():
    """Analyse complète YData SDK 3.0+ - VERSION FINALE"""
    
    print("🚀 ANALYSE YDATA SDK 3.0+ - VERSION FINALE CORRIGÉE")
    print("=" * 80)
    
    configure_ydata()
    sdk_components = import_ydata_sdk()
    
    if not sdk_components:
        print("❌ Impossible d'importer YData SDK")
        return
    
    conn = connect_to_duckdb()
    tables = conn.execute('SHOW TABLES').fetchall()
    table_names = [table[0] for table in tables]
    
    print(f"\n📋 Analyse de {len(table_names)} tables")
    print("=" * 80)
    
    results_list = []
    
    for table_name in table_names:
        try:
            count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
            
            if count > 100000:
                df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 50000').df()
                print(f"\n🔄 {table_name}: Échantillon 50k/{count:,} lignes")
            else:
                df = conn.execute(f'SELECT * FROM {table_name}').df()
                print(f"\n🔄 {table_name}: {count:,} lignes complètes")
            
            result = analyze_table_with_ydata_sdk(table_name, df, sdk_components)
            results_list.append(result)
            
        except Exception as e:
            print(f"❌ Erreur {table_name}: {e}")
            results_list.append({
                'table_name': table_name,
                'analyses': {'error': str(e)}
            })
    
    # Sauvegarde JSON et HTML
    save_analysis_results(results_list)
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 80)
    
    successful = [r for r in results_list if 'error' not in r.get('analyses', {})]
    synthesis_ready = [r for r in successful if r.get('analyses', {}).get('synthesis_ready', {}).get('ready_for_synthesis')]
    
    print(f"✅ Tables analysées: {len(successful)}/{len(table_names)}")
    print(f"🎯 Prêtes pour synthèse: {len(synthesis_ready)}")
    print(f"📁 Fichiers:")
    print(f"  - ydata_sdk_FINAL_results.json")
    print(f"  - ydata_sdk_FINAL_REPORT.html")
    
    conn.close()
    print(f"\n🎉 Analyse YData SDK complète et corrigée !")

if __name__ == "__main__":
    main()
