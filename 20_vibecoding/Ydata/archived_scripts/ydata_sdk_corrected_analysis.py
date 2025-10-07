#!/usr/bin/env python3
"""
Analyse complète avec YData SDK 3.0+ - API corrigée
Utilise Dataset → Metadata → Analyses avancées
"""

import os
import sys
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
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

def analyze_table_with_ydata_sdk(table_name, df, sdk_components):
    """Analyse complète d'une table avec YData SDK 3.0+"""
    
    print(f"\n🔬 ANALYSE YDATA SDK COMPLÈTE: {table_name}")
    print("-" * 60)
    
    results = {
        'table_name': table_name,
        'rows': len(df),
        'columns': len(df.columns),
        'memory_usage': int(df.memory_usage(deep=True).sum()),
        'analyses': {}
    }
    
    # 1. Export CSV pour LocalConnector
    csv_path = f"ydata_analysis/{table_name}.csv"
    df.to_csv(csv_path, index=False)
    print(f"📁 Export CSV: {csv_path}")
    
    try:
        # 2. Créer Dataset YData (API 3.0+)
        dataset = sdk_components['Dataset'](df)
        print(f"📊 Dataset YData créé: {table_name}")
        
        # 3. Créer Metadata depuis Dataset (API correcte)
        metadata = sdk_components['Metadata'](dataset=dataset)
        print("🧠 Métadonnées YData générées")
        
        # Extraire informations des métadonnées
        metadata_info = {
            'shape': metadata.shape,
            'columns': list(metadata.columns),
            'categorical_vars': list(metadata.categorical_vars) if metadata.categorical_vars else [],
            'numerical_vars': list(metadata.numerical_vars) if metadata.numerical_vars else [],
            'date_vars': list(metadata.date_vars) if metadata.date_vars else [],
            'string_vars': list(metadata.string_vars) if metadata.string_vars else [],
            'cardinality': dict(metadata.cardinality) if hasattr(metadata.cardinality, 'items') else str(metadata.cardinality),
            'warnings': metadata.warnings if metadata.warnings else []
        }
        
        results['analyses']['ydata_metadata'] = metadata_info
        print(f"  📋 Colonnes: {len(metadata.columns)} ({len(metadata.numerical_vars or [])} num, {len(metadata.categorical_vars or [])} cat)")
        
        # 4. Détection colonnes temporelles avancée
        temporal_columns = detect_temporal_columns_advanced(df, metadata, table_name)
        results['analyses']['temporal_columns'] = temporal_columns
        
        # 5. Analyse de qualité des données
        quality_analysis = analyze_data_quality_advanced(df, metadata, table_name)
        results['analyses']['data_quality'] = quality_analysis
        
        # 6. Si colonnes temporelles → préparation time-series
        if temporal_columns and any(col['is_temporal'] for col in temporal_columns.values()):
            ts_analysis = analyze_timeseries_patterns(df, temporal_columns, table_name)
            results['analyses']['timeseries'] = ts_analysis
            
            # Préparation TimeSeriesSynthesizer
            ts_ready = prepare_for_timeseries_synthesis(df, temporal_columns, metadata, table_name)
            results['analyses']['synthesis_ready'] = ts_ready
        
        # 7. Analyse des corrélations (si colonnes numériques)
        if metadata.numerical_vars and len(metadata.numerical_vars) > 1:
            correlation_analysis = analyze_correlations_advanced(df, metadata, table_name)
            results['analyses']['correlations'] = correlation_analysis
        
        # 8. Détection d'outliers sur colonnes numériques
        if metadata.numerical_vars:
            outlier_analysis = detect_outliers_advanced(df, metadata, table_name)
            results['analyses']['outliers'] = outlier_analysis
        
        # 9. Analyse de cardinalité pour variables catégorielles
        if metadata.categorical_vars:
            cardinality_analysis = analyze_cardinality(df, metadata, table_name)
            results['analyses']['cardinality'] = cardinality_analysis
        
        print(f"✅ Analyse YData SDK complète pour {table_name}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur analyse YData SDK {table_name}: {e}")
        import traceback
        traceback.print_exc()
        results['analyses']['error'] = str(e)
        return results

def detect_temporal_columns_advanced(df, metadata, table_name):
    """Détection avancée des colonnes temporelles avec YData metadata"""
    temporal_info = {}
    
    # D'abord utiliser YData metadata
    if metadata.date_vars:
        for col in metadata.date_vars:
            temporal_info[col] = {
                'is_temporal': True,
                'detected_by': 'ydata_metadata',
                'type': 'date_var',
                'range': [str(df[col].min()), str(df[col].max())] if col in df.columns else None,
                'null_count': int(df[col].isnull().sum()) if col in df.columns else 0
            }
    
    # Compléter avec détection manuelle
    for col in df.columns:
        if col in temporal_info:
            continue
            
        # Test direct datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            temporal_info[col] = {
                'is_temporal': True,
                'detected_by': 'pandas_dtype',
                'type': 'datetime64',
                'range': [str(df[col].min()), str(df[col].max())],
                'null_count': int(df[col].isnull().sum())
            }
            continue
        
        # Test parsing pour colonnes suspectes
        if col.lower() in ['date', 'timestamp', 'time', 'submitted', 'created', 'modified']:
            try:
                sample = df[col].dropna().head(1000)
                if len(sample) > 10:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    success_rate = parsed.notna().sum() / len(sample)
                    
                    if success_rate > 0.8:
                        temporal_info[col] = {
                            'is_temporal': True,
                            'detected_by': 'manual_parsing',
                            'type': 'parseable',
                            'success_rate': float(success_rate),
                            'sample_parsed': str(parsed.iloc[0]) if len(parsed) > 0 else None,
                            'null_count': int(df[col].isnull().sum())
                        }
            except:
                pass
    
    if temporal_info:
        temporal_count = len(temporal_info)
        print(f"  🕒 {temporal_count} colonnes temporelles: {list(temporal_info.keys())}")
    
    return temporal_info

def analyze_data_quality_advanced(df, metadata, table_name):
    """Analyse de qualité avancée avec YData metadata"""
    quality = {
        'ydata_warnings': metadata.warnings if metadata.warnings else [],
        'completeness': {},
        'consistency': {},
        'distribution_quality': {}
    }
    
    # Completeness
    total_cells = len(df) * len(df.columns)
    null_cells = df.isnull().sum().sum()
    quality['completeness'] = {
        'total_cells': int(total_cells),
        'null_cells': int(null_cells),
        'completeness_rate': float(1 - (null_cells / total_cells))
    }
    
    # Consistency basée sur YData metadata
    quality['consistency'] = {
        'numerical_vars_count': len(metadata.numerical_vars or []),
        'categorical_vars_count': len(metadata.categorical_vars or []),
        'date_vars_count': len(metadata.date_vars or []),
        'string_vars_count': len(metadata.string_vars or [])
    }
    
    # Distribution quality pour variables numériques
    if metadata.numerical_vars:
        for col in metadata.numerical_vars:
            if col in df.columns:
                series = df[col].dropna()
                if len(series) > 0:
                    quality['distribution_quality'][col] = {
                        'mean': float(series.mean()),
                        'std': float(series.std()),
                        'skewness': float(series.skew()),
                        'kurtosis': float(series.kurtosis()),
                        'zeros_percentage': float((series == 0).sum() / len(series) * 100)
                    }
    
    completeness_pct = quality['completeness']['completeness_rate'] * 100
    warnings_count = len(quality['ydata_warnings'])
    print(f"  📊 Qualité: {completeness_pct:.1f}% complétude, {warnings_count} warnings YData")
    
    return quality

def analyze_timeseries_patterns(df, temporal_columns, table_name):
    """Analyse des patterns temporels"""
    ts_analysis = {}
    
    for col_name, col_info in temporal_columns.items():
        if not col_info['is_temporal']:
            continue
            
        print(f"  📈 Analyse temporelle: {col_name}")
        
        # Conversion en datetime
        if col_info['type'] == 'parseable':
            time_series = pd.to_datetime(df[col_name], errors='coerce')
        else:
            time_series = df[col_name]
        
        # Analyse des patterns
        valid_dates = time_series.dropna()
        if len(valid_dates) > 0:
            time_range = (valid_dates.max() - valid_dates.min())
            
            analysis = {
                'range': [str(valid_dates.min()), str(valid_dates.max())],
                'span_days': int(time_range.days),
                'valid_dates_count': len(valid_dates),
                'frequency_analysis': {}
            }
            
            # Analyse de fréquence
            if len(valid_dates) > 1:
                sorted_dates = valid_dates.sort_values()
                time_diffs = sorted_dates.diff().dropna()
                
                if len(time_diffs) > 0:
                    median_interval_hours = time_diffs.median().total_seconds() / 3600
                    analysis['frequency_analysis'] = {
                        'median_interval_hours': float(median_interval_hours),
                        'min_interval_hours': float(time_diffs.min().total_seconds() / 3600),
                        'max_interval_hours': float(time_diffs.max().total_seconds() / 3600)
                    }
            
            ts_analysis[col_name] = analysis
    
    return ts_analysis

def prepare_for_timeseries_synthesis(df, temporal_columns, metadata, table_name):
    """Préparation pour TimeSeriesSynthesizer"""
    synthesis_info = {
        'ready_for_synthesis': False,
        'requirements_met': [],
        'requirements_missing': []
    }
    
    temporal_cols = [col for col, info in temporal_columns.items() if info['is_temporal']]
    
    if temporal_cols:
        synthesis_info['primary_time_column'] = temporal_cols[0]
        synthesis_info['requirements_met'].append(f'Colonnes temporelles: {len(temporal_cols)}')
        
        # Volume suffisant
        if len(df) >= 100:
            synthesis_info['requirements_met'].append(f'Volume suffisant: {len(df)} lignes')
        else:
            synthesis_info['requirements_missing'].append(f'Volume insuffisant: {len(df)} < 100')
        
        # Variables numériques pour les métriques
        if metadata.numerical_vars and len(metadata.numerical_vars) > 0:
            synthesis_info['requirements_met'].append(f'Variables numériques: {len(metadata.numerical_vars)}')
            synthesis_info['numeric_columns'] = list(metadata.numerical_vars)
        else:
            synthesis_info['requirements_missing'].append('Aucune variable numérique')
        
        # Prêt si toutes conditions remplies
        synthesis_info['ready_for_synthesis'] = len(synthesis_info['requirements_missing']) == 0
        
        status = "✅ PRÊT" if synthesis_info['ready_for_synthesis'] else "⚠️ MANQUE REQ"
        print(f"  🎯 TimeSeriesSynthesizer: {status}")
    
    return synthesis_info

def analyze_correlations_advanced(df, metadata, table_name):
    """Analyse des corrélations sur variables numériques"""
    numeric_cols = list(metadata.numerical_vars)
    numeric_df = df[numeric_cols].select_dtypes(include=[np.number])
    
    if len(numeric_df.columns) < 2:
        return {'note': 'Moins de 2 colonnes numériques'}
    
    # Matrice de corrélation Pearson
    corr_matrix = numeric_df.corr(method='pearson')
    
    # Corrélations fortes
    strong_correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if not pd.isna(corr_val) and abs(corr_val) > 0.5:
                strong_correlations.append({
                    'var1': corr_matrix.columns[i],
                    'var2': corr_matrix.columns[j], 
                    'correlation': float(corr_val),
                    'strength': 'forte' if abs(corr_val) > 0.7 else 'modérée'
                })
    
    analysis = {
        'matrix_shape': corr_matrix.shape,
        'strong_correlations': strong_correlations,
        'max_correlation': float(corr_matrix.abs().max().max()) if not corr_matrix.empty else 0
    }
    
    if strong_correlations:
        print(f"  🔗 {len(strong_correlations)} corrélations fortes détectées")
    
    return analysis

def detect_outliers_advanced(df, metadata, table_name):
    """Détection d'outliers sur variables numériques YData"""
    numeric_cols = list(metadata.numerical_vars)
    outlier_info = {}
    
    for col in numeric_cols:
        if col not in df.columns:
            continue
            
        series = df[col].dropna()
        if len(series) < 10:
            continue
            
        # Méthode IQR
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        if IQR == 0:  # Éviter division par zéro
            continue
            
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers_mask = (series < lower_bound) | (series > upper_bound)
        outlier_count = outliers_mask.sum()
        
        if outlier_count > 0:
            outlier_info[col] = {
                'count': int(outlier_count),
                'percentage': float(outlier_count / len(series) * 100),
                'bounds': [float(lower_bound), float(upper_bound)],
                'extreme_values': {
                    'min_outlier': float(series[outliers_mask].min()),
                    'max_outlier': float(series[outliers_mask].max())
                }
            }
    
    if outlier_info:
        total_outliers = sum([info['count'] for info in outlier_info.values()])
        print(f"  🎯 {total_outliers} outliers dans {len(outlier_info)} colonnes")
    
    return outlier_info

def analyze_cardinality(df, metadata, table_name):
    """Analyse de cardinalité des variables catégorielles"""
    categorical_cols = list(metadata.categorical_vars) if metadata.categorical_vars else []
    cardinality_info = {}
    
    for col in categorical_cols:
        if col not in df.columns:
            continue
            
        unique_count = df[col].nunique()
        total_count = len(df[col].dropna())
        
        if total_count > 0:
            cardinality_info[col] = {
                'unique_values': int(unique_count),
                'total_values': int(total_count),
                'cardinality_ratio': float(unique_count / total_count),
                'top_values': df[col].value_counts().head(5).to_dict()
            }
    
    if cardinality_info:
        high_card = [col for col, info in cardinality_info.items() if info['cardinality_ratio'] > 0.9]
        if high_card:
            print(f"  📊 Cardinalité élevée détectée: {high_card}")
    
    return cardinality_info

def save_analysis_results(results_list):
    """Sauvegarder résultats avec support JSON amélioré"""
    import json
    
    # JSON détaillé
    json_path = "ydata_analysis/ydata_sdk_complete_results.json"
    
    # Conversion pour JSON
    json_results = []
    for result in results_list:
        json_result = {}
        for key, value in result.items():
            try:
                json_result[key] = convert_for_json(value)
            except:
                json_result[key] = str(value)
        json_results.append(json_result)
    
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    
    print(f"📊 Résultats JSON: {json_path}")
    
    # Rapport HTML amélioré
    generate_enhanced_html_report(json_results)

def convert_for_json(obj):
    """Conversion robuste pour JSON"""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict()
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
        return list(obj)
    else:
        return obj

def generate_enhanced_html_report(results):
    """Rapport HTML enrichi avec analyses YData SDK"""
    
    # Calculer statistiques globales
    successful_results = [r for r in results if 'error' not in r.get('analyses', {})]
    total_rows = sum([r.get('rows', 0) for r in successful_results])
    total_columns = sum([r.get('columns', 0) for r in successful_results])
    
    # Tables temporelles
    temporal_tables = []
    synthesis_ready_tables = []
    
    for result in successful_results:
        temporal_cols = result.get('analyses', {}).get('temporal_columns', {})
        if temporal_cols and any(col.get('is_temporal', False) for col in temporal_cols.values()):
            temporal_tables.append(result['table_name'])
            
            synthesis_info = result.get('analyses', {}).get('synthesis_ready', {})
            if synthesis_info.get('ready_for_synthesis', False):
                synthesis_ready_tables.append(result['table_name'])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YData SDK 3.0+ - Analyse Complète</title>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; padding: 20px; 
                background: #f5f5f5; 
            }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; color: #2c3e50; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
            .metric-number {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
            .metric-label {{ font-size: 0.9em; opacity: 0.9; }}
            .table-container {{ overflow-x: auto; margin: 20px 0; }}
            .analysis-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .analysis-table th, .analysis-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            .analysis-table th {{ background: #34495e; color: white; font-weight: bold; }}
            .analysis-table tr:nth-child(even) {{ background: #f9f9f9; }}
            .status-good {{ color: #27ae60; font-weight: bold; }}
            .status-warning {{ color: #f39c12; font-weight: bold; }}
            .status-error {{ color: #e74c3c; font-weight: bold; }}
            .section {{ margin: 30px 0; }}
            .section h2 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            .recommendation {{ background: #e8f6f3; border-left: 4px solid #1abc9c; padding: 15px; margin: 15px 0; }}
            .temporal-ready {{ background: #d5f4e6; }}
            .synthesis-ready {{ background: #fef9e7; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔬 YData SDK 3.0+ - Analyse Complète</h1>
                <p><strong>Date d'analyse:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Résumé Global</h2>
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-number">{len(successful_results)}</div>
                        <div class="metric-label">Tables Analysées</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">{total_rows:,}</div>
                        <div class="metric-label">Lignes Totales</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">{total_columns}</div>
                        <div class="metric-label">Colonnes Totales</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">{len(temporal_tables)}</div>
                        <div class="metric-label">Tables Temporelles</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📋 Analyse Détaillée par Table</h2>
                <div class="table-container">
                    <table class="analysis-table">
                        <thead>
                            <tr>
                                <th>Table</th>
                                <th>Lignes</th>
                                <th>Colonnes</th>
                                <th>Variables Num.</th>
                                <th>Variables Cat.</th>
                                <th>Temporelles</th>
                                <th>Qualité</th>
                                <th>Synthèse</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for result in results:
        if 'error' in result.get('analyses', {}):
            continue
            
        table_name = result['table_name']
        rows = result.get('rows', 0)
        columns = result.get('columns', 0)
        
        # Extraire les infos YData metadata
        ydata_meta = result.get('analyses', {}).get('ydata_metadata', {})
        num_vars = len(ydata_meta.get('numerical_vars', []))
        cat_vars = len(ydata_meta.get('categorical_vars', []))
        
        # Info temporelles
        temporal_cols = result.get('analyses', {}).get('temporal_columns', {})
        temporal_count = len([k for k, v in temporal_cols.items() if v.get('is_temporal', False)])
        temporal_class = 'temporal-ready' if temporal_count > 0 else ''
        
        # Qualité
        quality_info = result.get('analyses', {}).get('data_quality', {})
        completeness = quality_info.get('completeness', {}).get('completeness_rate', 0)
        
        if completeness > 0.95:
            quality_status = f'<span class="status-good">{completeness:.1%}</span>'
        elif completeness > 0.8:
            quality_status = f'<span class="status-warning">{completeness:.1%}</span>'
        else:
            quality_status = f'<span class="status-error">{completeness:.1%}</span>'
        
        # Prêt pour synthèse
        synthesis_info = result.get('analyses', {}).get('synthesis_ready', {})
        synthesis_ready = synthesis_info.get('ready_for_synthesis', False)
        synthesis_class = 'synthesis-ready' if synthesis_ready else ''
        synthesis_status = '<span class="status-good">✅ Prêt</span>' if synthesis_ready else '<span class="status-warning">⚠️ Req. manquantes</span>'
        
        html_content += f"""
                            <tr class="{temporal_class} {synthesis_class}">
                                <td><strong>{table_name}</strong></td>
                                <td>{rows:,}</td>
                                <td>{columns}</td>
                                <td>{num_vars}</td>
                                <td>{cat_vars}</td>
                                <td>{temporal_count}</td>
                                <td>{quality_status}</td>
                                <td>{synthesis_status}</td>
                            </tr>
        """
    
    html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <h2>🎯 Recommandations YData SDK</h2>
                
                <div class="recommendation">
                    <h3>🕒 Time Series Synthesis</h3>
                    <p><strong>Tables prêtes:</strong> {len(synthesis_ready_tables)} sur {len(temporal_tables)} temporelles</p>
                    <p><strong>Candidats:</strong> {', '.join(synthesis_ready_tables) if synthesis_ready_tables else 'Aucun'}</p>
                    <p><strong>Action:</strong> Utiliser TimeSeriesSynthesizer pour générer des données synthétiques temporelles</p>
                </div>
                
                <div class="recommendation">
                    <h3>📊 Data Quality</h3>
                    <p><strong>Tables avec complétude < 90%:</strong> À investiguer pour améliorer la qualité</p>
                    <p><strong>Variables catégorielles:</strong> Analyser la cardinalité pour optimisation</p>
                </div>
                
                <div class="recommendation">
                    <h3>🔬 Analyses Avancées</h3>
                    <p><strong>Corrélations fortes:</strong> Utiliser pour feature engineering</p>
                    <p><strong>Outliers détectés:</strong> Nettoyer ou investiguer les valeurs aberrantes</p>
                    <p><strong>RegularSynthesizer:</strong> Générer des données synthétiques pour tables non-temporelles</p>
                </div>
            </div>
            
            <div class="section">
                <h2>🗂️ Fichiers Générés</h2>
                <ul>
                    <li><strong>ydata_sdk_complete_results.json</strong> - Données détaillées de l'analyse</li>
                    <li><strong>ydata_sdk_analysis_report.html</strong> - Ce rapport visuel</li>
                    <li><strong>*.csv</strong> - Export des données par table pour réutilisation</li>
                </ul>
            </div>
            
            <footer style="text-align: center; margin-top: 40px; padding: 20px; color: #7f8c8d;">
                <p><em>Généré par YData SDK 3.0+ - Analyse complète avec Metadata, Dataset et Synthesizers</em></p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    html_path = "ydata_analysis/ydata_sdk_analysis_report.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 Rapport HTML enrichi: {html_path}")

def main():
    """Analyse complète avec YData SDK 3.0+ API corrigée"""
    
    print("🚀 ANALYSE COMPLÈTE AVEC YDATA SDK 3.0+ (API CORRIGÉE)")
    print("=" * 80)
    
    # Configuration
    configure_ydata()
    
    # Import des composants
    sdk_components = import_ydata_sdk()
    if not sdk_components:
        print("❌ Impossible d'importer YData SDK")
        return
    
    # Connexion base
    conn = connect_to_duckdb()
    
    # Liste des tables
    tables = conn.execute('SHOW TABLES').fetchall()
    table_names = [table[0] for table in tables]
    
    print(f"\n📋 Analyse YData SDK 3.0+ de {len(table_names)} tables:")
    print("=" * 80)
    
    results_list = []
    
    for table_name in table_names:
        try:
            # Récupération données avec échantillonnage intelligent
            count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
            
            if count > 100000:
                df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 50000').df()
                print(f"\n🔄 {table_name}: Échantillon 50k/{count:,} lignes")
            else:
                df = conn.execute(f'SELECT * FROM {table_name}').df()
                print(f"\n🔄 {table_name}: {count:,} lignes complètes")
            
            # Analyse YData SDK complète
            result = analyze_table_with_ydata_sdk(table_name, df, sdk_components)
            results_list.append(result)
            
        except Exception as e:
            print(f"❌ Erreur {table_name}: {e}")
            results_list.append({
                'table_name': table_name,
                'analyses': {'error': str(e)}
            })
    
    # Sauvegarde résultats
    save_analysis_results(results_list)
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL - YDATA SDK 3.0+")
    print("=" * 80)
    
    successful_tables = [r for r in results_list if 'error' not in r.get('analyses', {})]
    total_rows = sum([r.get('rows', 0) for r in successful_tables])
    
    # Compter tables temporelles et prêtes pour synthèse
    temporal_tables = []
    synthesis_ready = []
    
    for result in successful_tables:
        temporal_cols = result.get('analyses', {}).get('temporal_columns', {})
        if temporal_cols and any(col.get('is_temporal', False) for col in temporal_cols.values()):
            temporal_tables.append(result['table_name'])
            
            synthesis_info = result.get('analyses', {}).get('synthesis_ready', {})
            if synthesis_info.get('ready_for_synthesis', False):
                synthesis_ready.append(result['table_name'])
    
    print(f"✅ Tables analysées avec succès: {len(successful_tables)}/{len(table_names)}")
    print(f"📊 Total lignes analysées: {total_rows:,}")
    print(f"🕒 Tables avec colonnes temporelles: {len(temporal_tables)}")
    print(f"   → {temporal_tables}")
    print(f"🎯 Tables prêtes pour TimeSeriesSynthesizer: {len(synthesis_ready)}")
    print(f"   → {synthesis_ready}")
    
    if synthesis_ready:
        print(f"\n🚀 PROCHAINE ÉTAPE RECOMMANDÉE:")
        print(f"   Utiliser TimeSeriesSynthesizer sur: {', '.join(synthesis_ready)}")
    
    print(f"\n📁 Fichiers générés dans ydata_analysis/:")
    print(f"  - ydata_sdk_complete_results.json (données brutes)")
    print(f"  - ydata_sdk_analysis_report.html (rapport visuel)")
    print(f"  - *.csv (exports par table)")
    
    conn.close()
    print(f"\n🎉 Analyse YData SDK 3.0+ terminée avec succès!")

if __name__ == "__main__":
    main()
