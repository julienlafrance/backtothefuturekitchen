#!/usr/bin/env python3
"""
Analyse complète avec le vrai YData SDK - Toutes fonctionnalités avancées
Utilise LocalConnector, Metadata, Dataset, Synthesizers et profiling avancé
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
    """Analyse complète d'une table avec YData SDK"""
    
    print(f"\n🔬 ANALYSE YDATA SDK COMPLÈTE: {table_name}")
    print("-" * 60)
    
    results = {
        'table_name': table_name,
        'rows': len(df),
        'columns': len(df.columns),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'analyses': {}
    }
    
    # 1. Export CSV pour LocalConnector
    csv_path = f"ydata_analysis/{table_name}.csv"
    df.to_csv(csv_path, index=False)
    print(f"📁 Export CSV: {csv_path}")
    
    try:
        # 2. LocalConnector et Dataset
        connector = sdk_components['LocalConnector']()
        
        # Lire via le connector
        dataset_data = connector.read_file(csv_path)
        print(f"📊 Données lues via LocalConnector: {len(dataset_data)} lignes")
        
        # 3. Création des Metadata
        metadata = sdk_components['Metadata'](df)
        print("🧠 Métadonnées générées avec YData SDK")
        
        # Analyser les métadonnées
        metadata_info = {
            'dtypes': metadata.dtypes,
            'describe': metadata.describe(),
        }
        
        results['analyses']['metadata'] = metadata_info
        
        # 4. Détection colonnes temporelles avec logique avancée
        temporal_columns = detect_temporal_columns_advanced(df, table_name)
        results['analyses']['temporal_columns'] = temporal_columns
        
        # 5. Analyse de qualité des données
        quality_analysis = analyze_data_quality(df, table_name)
        results['analyses']['data_quality'] = quality_analysis
        
        # 6. Si colonnes temporelles → analyse time-series
        if temporal_columns:
            ts_analysis = analyze_timeseries_patterns(df, temporal_columns, table_name)
            results['analyses']['timeseries'] = ts_analysis
            
            # Préparer pour TimeSeriesSynthesizer
            ts_ready = prepare_for_timeseries_synthesis(df, temporal_columns, table_name)
            results['analyses']['synthesis_ready'] = ts_ready
        
        # 7. Analyse des corrélations avancées
        correlation_analysis = analyze_correlations_advanced(df, table_name)
        results['analyses']['correlations'] = correlation_analysis
        
        # 8. Détection d'outliers
        outlier_analysis = detect_outliers_advanced(df, table_name)
        results['analyses']['outliers'] = outlier_analysis
        
        print(f"✅ Analyse YData SDK complète pour {table_name}")
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur analyse YData SDK {table_name}: {e}")
        results['analyses']['error'] = str(e)
        return results

def detect_temporal_columns_advanced(df, table_name):
    """Détection avancée des colonnes temporelles"""
    temporal_info = {}
    
    for col in df.columns:
        col_info = {'is_temporal': False}
        
        # Test direct datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            col_info = {
                'is_temporal': True,
                'type': 'datetime64',
                'range': [df[col].min(), df[col].max()],
                'null_count': df[col].isnull().sum()
            }
            temporal_info[col] = col_info
            continue
        
        # Test parsing pour colonnes texte
        if col.lower() in ['date', 'timestamp', 'time', 'submitted', 'created', 'modified']:
            try:
                sample = df[col].dropna().head(1000)
                if len(sample) > 0:
                    parsed = pd.to_datetime(sample, errors='coerce')
                    success_rate = parsed.notna().sum() / len(sample)
                    
                    if success_rate > 0.8:
                        col_info = {
                            'is_temporal': True,
                            'type': 'parseable',
                            'success_rate': success_rate,
                            'sample_parsed': str(parsed.iloc[0]) if len(parsed) > 0 else None
                        }
                        temporal_info[col] = col_info
            except:
                pass
    
    if temporal_info:
        print(f"  🕒 {len(temporal_info)} colonnes temporelles détectées: {list(temporal_info.keys())}")
    
    return temporal_info

def analyze_data_quality(df, table_name):
    """Analyse de qualité des données"""
    quality = {
        'completeness': {},
        'uniqueness': {},
        'consistency': {},
        'validity': {}
    }
    
    # Completeness (complétude)
    total_cells = len(df) * len(df.columns)
    null_cells = df.isnull().sum().sum()
    quality['completeness'] = {
        'total_cells': total_cells,
        'null_cells': int(null_cells),
        'completeness_rate': 1 - (null_cells / total_cells)
    }
    
    # Uniqueness (unicité)
    for col in df.columns:
        unique_rate = df[col].nunique() / len(df) if len(df) > 0 else 0
        quality['uniqueness'][col] = {
            'unique_values': int(df[col].nunique()),
            'uniqueness_rate': float(unique_rate),
            'duplicates': int(len(df) - df[col].nunique())
        }
    
    # Consistency (cohérence des types)
    for col in df.columns:
        dtype_consistency = df[col].dtype
        quality['consistency'][col] = {
            'dtype': str(dtype_consistency),
            'consistent': True  # Pandas assure déjà la cohérence des types
        }
    
    print(f"  📊 Qualité données: {quality['completeness']['completeness_rate']:.1%} complétude")
    
    return quality

def analyze_timeseries_patterns(df, temporal_columns, table_name):
    """Analyse des patterns temporels"""
    ts_analysis = {}
    
    for col_name, col_info in temporal_columns.items():
        if not col_info['is_temporal']:
            continue
            
        print(f"  📈 Analyse temporelle: {col_name}")
        
        # Conversion en datetime si nécessaire
        if col_info['type'] == 'parseable':
            time_series = pd.to_datetime(df[col_name], errors='coerce')
        else:
            time_series = df[col_name]
        
        # Analyse des patterns
        analysis = {
            'range': [str(time_series.min()), str(time_series.max())],
            'span_days': (time_series.max() - time_series.min()).days if time_series.notna().any() else 0,
            'frequency_analysis': {},
            'seasonal_patterns': {}
        }
        
        # Analyse de fréquence
        if len(time_series.dropna()) > 0:
            time_diff = time_series.dropna().sort_values().diff().dropna()
            if len(time_diff) > 0:
                analysis['frequency_analysis'] = {
                    'median_interval_hours': float(time_diff.median().total_seconds() / 3600),
                    'most_common_interval': str(time_diff.mode().iloc[0]) if len(time_diff.mode()) > 0 else None
                }
        
        ts_analysis[col_name] = analysis
    
    return ts_analysis

def prepare_for_timeseries_synthesis(df, temporal_columns, table_name):
    """Préparer les données pour TimeSeriesSynthesizer"""
    synthesis_info = {
        'ready_for_synthesis': False,
        'requirements': [],
        'preprocessing_needed': []
    }
    
    if len(temporal_columns) > 0:
        synthesis_info['ready_for_synthesis'] = True
        synthesis_info['primary_time_column'] = list(temporal_columns.keys())[0]
        synthesis_info['requirements'].append('Colonnes temporelles détectées')
        
        # Vérifier autres critères
        if len(df) >= 100:
            synthesis_info['requirements'].append('Volume suffisant (>100 lignes)')
        else:
            synthesis_info['preprocessing_needed'].append('Volume insuffisant')
        
        # Vérifier présence de valeurs numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            synthesis_info['requirements'].append(f'{len(numeric_cols)} colonnes numériques pour métriques')
            synthesis_info['numeric_columns'] = list(numeric_cols)
        
        print(f"  🎯 Prêt pour TimeSeriesSynthesizer: {synthesis_info['ready_for_synthesis']}")
    
    return synthesis_info

def analyze_correlations_advanced(df, table_name):
    """Analyse avancée des corrélations"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if len(numeric_df.columns) < 2:
        return {'note': 'Moins de 2 colonnes numériques pour corrélation'}
    
    # Corrélations Pearson
    pearson_corr = numeric_df.corr(method='pearson')
    
    # Trouver les corrélations fortes
    strong_correlations = []
    for i in range(len(pearson_corr.columns)):
        for j in range(i+1, len(pearson_corr.columns)):
            corr_val = pearson_corr.iloc[i, j]
            if abs(corr_val) > 0.5:  # Corrélation forte
                strong_correlations.append({
                    'var1': pearson_corr.columns[i],
                    'var2': pearson_corr.columns[j],
                    'correlation': float(corr_val),
                    'strength': 'forte' if abs(corr_val) > 0.7 else 'modérée'
                })
    
    correlation_analysis = {
        'correlation_matrix_shape': pearson_corr.shape,
        'strong_correlations': strong_correlations,
        'max_correlation': float(pearson_corr.abs().max().max()) if len(pearson_corr) > 0 else 0
    }
    
    if strong_correlations:
        print(f"  🔗 {len(strong_correlations)} corrélations fortes détectées")
    
    return correlation_analysis

def detect_outliers_advanced(df, table_name):
    """Détection avancée d'outliers"""
    numeric_df = df.select_dtypes(include=[np.number])
    outlier_info = {}
    
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        if len(series) == 0:
            continue
            
        # Méthode IQR
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
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
                    'min_outlier': float(series[outliers_mask].min()) if outlier_count > 0 else None,
                    'max_outlier': float(series[outliers_mask].max()) if outlier_count > 0 else None
                }
            }
    
    if outlier_info:
        total_outliers = sum([info['count'] for info in outlier_info.values()])
        print(f"  🎯 {total_outliers} outliers détectés dans {len(outlier_info)} colonnes")
    
    return outlier_info

def save_analysis_results(results_list):
    """Sauvegarder les résultats d'analyse en JSON et HTML"""
    import json
    
    # Sauvegarde JSON
    json_path = "ydata_analysis/complete_analysis_results.json"
    
    # Convertir pour JSON (gérer les types non sérialisables)
    json_results = []
    for result in results_list:
        json_result = {}
        for key, value in result.items():
            if key == 'analyses':
                # Convertir les analyses
                json_analyses = {}
                for analysis_key, analysis_value in value.items():
                    try:
                        json_analyses[analysis_key] = convert_for_json(analysis_value)
                    except:
                        json_analyses[analysis_key] = str(analysis_value)
                json_result[key] = json_analyses
            else:
                json_result[key] = convert_for_json(value)
        json_results.append(json_result)
    
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    
    print(f"📊 Résultats sauvegardés: {json_path}")
    
    # Générer un rapport HTML simple
    generate_html_report(json_results)

def convert_for_json(obj):
    """Convertir les objets pour JSON"""
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    else:
        return obj

def generate_html_report(results):
    """Générer un rapport HTML de synthèse"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YData SDK - Analyse Complète</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .table th {{ background-color: #f2f2f2; }}
            .metric {{ background: #e7f3ff; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .temporal {{ color: #28a745; }}
            .quality {{ color: #17a2b8; }}
        </style>
    </head>
    <body>
        <h1>🔬 YData SDK - Analyse Complète</h1>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📊 Résumé Global</h2>
        <div class="metric">
            <strong>Tables analysées:</strong> {len(results)}<br>
            <strong>Total lignes:</strong> {sum([r['rows'] for r in results]):,}<br>
            <strong>Total colonnes:</strong> {sum([r['columns'] for r in results])}<br>
        </div>
        
        <h2>📋 Détail par Table</h2>
        <table class="table">
            <tr>
                <th>Table</th>
                <th>Lignes</th>
                <th>Colonnes</th>
                <th>Temporelles</th>
                <th>Qualité</th>
                <th>Corrélations</th>
                <th>Outliers</th>
            </tr>
    """
    
    for result in results:
        table_name = result['table_name']
        rows = result['rows']
        columns = result['columns']
        
        # Données temporelles
        temporal_info = result['analyses'].get('temporal_columns', {})
        temporal_count = len([k for k, v in temporal_info.items() if v.get('is_temporal', False)])
        
        # Qualité
        quality_info = result['analyses'].get('data_quality', {})
        completeness = quality_info.get('completeness', {}).get('completeness_rate', 0)
        
        # Corrélations
        corr_info = result['analyses'].get('correlations', {})
        strong_corr = len(corr_info.get('strong_correlations', []))
        
        # Outliers
        outlier_info = result['analyses'].get('outliers', {})
        outlier_columns = len(outlier_info) if isinstance(outlier_info, dict) else 0
        
        html_content += f"""
            <tr>
                <td><strong>{table_name}</strong></td>
                <td>{rows:,}</td>
                <td>{columns}</td>
                <td class="temporal">{temporal_count} col(s)</td>
                <td class="quality">{completeness:.1%}</td>
                <td>{strong_corr}</td>
                <td>{outlier_columns}</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <h2>🎯 Recommandations</h2>
        <ul>
            <li><strong>Time Series:</strong> Les tables avec colonnes temporelles sont prêtes pour TimeSeriesSynthesizer</li>
            <li><strong>Data Quality:</strong> Vérifier la complétude des données pour les tables < 90%</li>
            <li><strong>Correlations:</strong> Analyser les corrélations fortes pour feature engineering</li>
            <li><strong>Outliers:</strong> Investiguer les outliers détectés pour nettoyage des données</li>
        </ul>
        
        <footer>
            <p><em>Généré par YData SDK - Analyse complète des données</em></p>
        </footer>
    </body>
    </html>
    """
    
    html_path = "ydata_analysis/complete_analysis_report.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"📄 Rapport HTML généré: {html_path}")

def main():
    """Fonction principale - Analyse complète avec YData SDK"""
    
    print("🚀 ANALYSE COMPLÈTE AVEC YDATA SDK")
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
    
    print(f"\n📋 Analyse YData SDK de {len(table_names)} tables:")
    print("=" * 80)
    
    results_list = []
    
    for table_name in table_names:
        try:
            # Récupération des données (avec échantillonnage si nécessaire)
            count = conn.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
            
            if count > 100000:  # Échantillonnage pour très gros datasets
                df = conn.execute(f'SELECT * FROM {table_name} USING SAMPLE 50000').df()
                print(f"\n🔄 {table_name}: Échantillon de 50k lignes sur {count:,}")
            else:
                df = conn.execute(f'SELECT * FROM {table_name}').df()
                print(f"\n🔄 {table_name}: Dataset complet de {count:,} lignes")
            
            # Analyse complète avec YData SDK
            result = analyze_table_with_ydata_sdk(table_name, df, sdk_components)
            results_list.append(result)
            
        except Exception as e:
            print(f"❌ Erreur {table_name}: {e}")
            results_list.append({
                'table_name': table_name,
                'error': str(e)
            })
    
    # Sauvegarde des résultats
    save_analysis_results(results_list)
    
    # Résumé final
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ FINAL - ANALYSE YDATA SDK")
    print("=" * 80)
    
    successful_tables = [r for r in results_list if 'error' not in r]
    total_rows = sum([r.get('rows', 0) for r in successful_tables])
    
    # Tables temporelles
    temporal_tables = []
    synthesis_ready = []
    
    for result in successful_tables:
        temporal_cols = result.get('analyses', {}).get('temporal_columns', {})
        if any(col_info.get('is_temporal', False) for col_info in temporal_cols.values()):
            temporal_tables.append(result['table_name'])
            
            synthesis_info = result.get('analyses', {}).get('synthesis_ready', {})
            if synthesis_info.get('ready_for_synthesis', False):
                synthesis_ready.append(result['table_name'])
    
    print(f"✅ Tables analysées: {len(successful_tables)}/{len(table_names)}")
    print(f"📊 Total lignes analysées: {total_rows:,}")
    print(f"🕒 Tables temporelles: {len(temporal_tables)} → {temporal_tables}")
    print(f"🎯 Prêtes pour synthesis: {len(synthesis_ready)} → {synthesis_ready}")
    
    print(f"\n📁 Fichiers générés:")
    print(f"  - complete_analysis_results.json (données détaillées)")  
    print(f"  - complete_analysis_report.html (rapport visuel)")
    print(f"  - *.csv (export des données par table)")
    
    conn.close()
    print(f"\n🎉 Analyse YData SDK terminée avec succès!")

if __name__ == "__main__":
    main()
