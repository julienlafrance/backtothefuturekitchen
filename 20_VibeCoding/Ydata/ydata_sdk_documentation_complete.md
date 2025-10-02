# Documentation Exhaustive YData SDK : Analyse de Données CSV/DuckDB et Time Series

## Table des Matières

1. [Introduction à YData SDK](#introduction)
2. [Installation et Configuration](#installation)
3. [Connexion aux Sources de Données](#connexions)
4. [Analyse et Profilage de Données](#profiling)
5. [Time Series : Analyse Avancée](#timeseries)
6. [Génération de Données Synthétiques](#synthetic)
7. [Intégration avec DuckDB](#duckdb)
8. [Cas d'Usage Avancés](#advanced)
9. [Bonnes Pratiques](#best-practices)

---

## 1. Introduction à YData SDK {#introduction}

YData SDK est le package Python leader pour l'IA et les données, fournissant un écosystème de méthodes qui permet aux professionnels des données d'adopter une approche de développement centrée sur les données, axée sur l'amélioration de la qualité des données.

### Composants Principaux

La bibliothèque comprend des composants intégrés pour :
- **Data Ingestion** : Connexion transparente à diverses sources de données
- **Data Quality Evaluation** : Métriques et évaluations standardisées
- **Data Improvement** : Outils pour améliorer la qualité des datasets
- **Synthetic Data Generation** : Création de datasets synthétiques de haute qualité

### Nouveautés Time Series et Texte

La dernière version introduit le support pour les données textuelles et non structurées, incluant :
- **QAGenerator** : Génération automatique de paires question-réponse de haute qualité à partir de documents
- **DocumentGenerator** : Génération de documents internes synthétiques (PDF, DOCX, HTML)
- **TextSynthesizer et QASynthesizer** : Génération de corpus de texte préservant la confidentialité

---

## 2. Installation et Configuration {#installation}

### Installation Basique

```bash
# Installation complète avec toutes les fonctionnalités
pip install ydata-sdk

# Installation avec options spécifiques
pip install ydata-sdk[notebook,time-series,synthetic]

# Pour les gros datasets avec Spark
pip install ydata-sdk[pyspark]
```

### Configuration de la Licence

```python
import os

# Configuration de la clé de licence
os.environ['YDATA_LICENSE_KEY'] = 'votre-cle-de-licence'

# Alternative : configuration dans le code
from ydata import configure
configure(license_key='votre-cle-de-licence')
```

### Imports Essentiels

```python
# Imports de base
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

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
```

---

## 3. Connexion aux Sources de Données {#connexions}

### 3.1 Connexion Fichiers Locaux

YData SDK permet aux utilisateurs de consommer des ressources de données à partir de stockages distants via des Connecteurs.

#### Exemple Basique CSV

```python
from ydata.connectors.storages.local_connector import LocalConnector
from ydata.connectors.filetype import FileType

# Initialisation du connecteur local
connector = LocalConnector()

# Lister les fichiers dans un répertoire
files_dirs = connector.list(path="./data")
print("Fichiers disponibles:", files_dirs)

# Lecture d'un fichier CSV spécifique
data = connector.read_file("./data/sales_data.csv", file_type=FileType.CSV)
print(f"Dataset shape: {data.shape}")
print(data.head())

# Lecture de tous les CSV d'un dossier
all_csv_data = connector.read_file("./data", file_type=FileType.CSV)

# Lecture d'un échantillon pour les gros fichiers
sample = connector.read_sample("./data/large_dataset.csv", 
                              file_type=FileType.CSV, 
                              n_rows=1000)
```

#### Gestion de Fichiers CSV Complexes

```python
# Lecture avec paramètres personnalisés
import pandas as pd

# Pour des CSV avec séparateurs spéciaux
connector = LocalConnector()
data = connector.read_file("./data/european_data.csv", 
                          file_type=FileType.CSV,
                          sep=';',
                          encoding='utf-8',
                          decimal=',')

# Gestion des dates dans les CSV
date_columns = ['date_creation', 'date_modification']
data = connector.read_file("./data/timestamped_data.csv",
                          file_type=FileType.CSV,
                          parse_dates=date_columns,
                          date_parser=pd.to_datetime)
```

### 3.2 Connexion DuckDB

Bien que YData SDK n'ait pas de connecteur DuckDB natif intégré, voici comment combiner DuckDB avec YData :

```python
import duckdb
import pandas as pd
from ydata.dataset import Dataset

def load_from_duckdb(query, db_path=None):
    """
    Charge des données depuis DuckDB vers YData SDK
    
    Args:
        query (str): Requête SQL
        db_path (str): Chemin vers la base DuckDB (None pour en mémoire)
    
    Returns:
        Dataset: Dataset YData prêt pour l'analyse
    """
    # Connexion à DuckDB
    if db_path:
        conn = duckdb.connect(db_path)
    else:
        conn = duckdb.connect()
    
    # Exécution de la requête
    df = conn.execute(query).fetchdf()
    conn.close()
    
    # Conversion en Dataset YData
    return Dataset(df)

# Exemple d'utilisation
# Lecture d'un CSV via DuckDB
data = load_from_duckdb("""
    SELECT * FROM 'data/sales_timeseries.csv'
    WHERE date >= '2023-01-01'
    ORDER BY date
""")

# Requête complexe avec agrégations
monthly_sales = load_from_duckdb("""
    SELECT 
        date_trunc('month', date) as month,
        region,
        SUM(amount) as total_sales,
        COUNT(*) as transactions,
        AVG(amount) as avg_transaction
    FROM 'data/sales_data.csv'
    GROUP BY month, region
    ORDER BY month, region
""")
```

### 3.3 Connecteurs Avancés

#### Connexion Base de Données

```python
# Exemple pour PostgreSQL/MySQL (concept)
from ydata.connectors.storages.sql_connector import SQLConnector

# Configuration de connexion
config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'analytics',
    'username': 'user',
    'password': 'password'
}

sql_connector = SQLConnector(config)

# Lecture avec requête SQL
time_series_data = sql_connector.read_query("""
    SELECT 
        timestamp,
        sensor_id,
        temperature,
        humidity,
        pressure
    FROM sensor_data 
    WHERE timestamp >= '2024-01-01'
    ORDER BY timestamp
""")
```

---

## 4. Analyse et Profilage de Données {#profiling}

### 4.1 Profilage Basique

Le profilage offre des insights complets sur divers types de données, incluant les données tabulaires, les time-series et les données textuelles.

```python
from ydata.profiling import ProfileReport

# Chargement des données
df = pd.read_csv('data/customer_data.csv')

# Génération du rapport de profilage basique
profile = ProfileReport(df, title="Analyse Customer Data")

# Affichage dans Jupyter
profile.to_notebook_iframe()

# Sauvegarde en HTML
profile.to_file("reports/customer_analysis.html")

# Export en JSON pour intégration
profile.to_file("reports/customer_analysis.json")
```

### 4.2 Configuration Avancée du Profilage

```python
# Configuration personnalisée
from ydata.profiling import ProfileReport

# Configuration détaillée
config = {
    'samples': {
        'head': 10,
        'tail': 10,
        'random': 10
    },
    'correlations': {
        'pearson': {'calculate': True, 'warn_high_correlations': True},
        'spearman': {'calculate': True},
        'kendall': {'calculate': False},
        'phi_k': {'calculate': True},
        'cramers': {'calculate': True}
    },
    'missing_diagrams': {
        'matrix': True,
        'bar': True,
        'heatmap': True,
        'dendrogram': True
    },
    'duplicates': {
        'head': 10,
        'key': '_row'
    },
    'interactions': {
        'continuous': True,
        'targets': []
    }
}

# Application de la configuration
profile = ProfileReport(df, 
                       title="Analyse Avancée", 
                       config=config,
                       explorative=True)
```

### 4.3 Analyse des Variables Spécifiques

Pour les données tabulaires, le profilage fournit des statistiques précieuses sur la distribution des données, les tendances centrales et les fréquences des variables catégorielles.

```python
# Analyse spécifique des outliers
def analyze_outliers(df, column):
    """
    Analyse détaillée des outliers pour une colonne
    """
    from ydata.profiling import ProfileReport
    
    # Profilage avec focus sur les outliers
    profile = ProfileReport(df[[column]], 
                          title=f"Analyse Outliers - {column}",
                          vars={
                              'num': {
                                  'low_categorical_threshold': 5,
                                  'chi_squared_threshold': 0.95
                              }
                          })
    
    return profile

# Exemple d'utilisation
outlier_analysis = analyze_outliers(df, 'transaction_amount')
outlier_analysis.to_file("reports/outliers_transaction_amount.html")

# Analyse des corrélations personnalisée
def correlation_analysis(df, target_column):
    """
    Analyse des corrélations avec une variable cible
    """
    profile = ProfileReport(df,
                          title=f"Corrélations avec {target_column}",
                          interactions={
                              'targets': [target_column],
                              'continuous': True
                          })
    return profile
```

### 4.4 Comparaison de Datasets

```python
# Comparaison avant/après traitement
df_before = pd.read_csv('data/raw_data.csv')
df_after = pd.read_csv('data/processed_data.csv')

# Génération des profils individuels
profile_before = ProfileReport(df_before, title="Données Brutes")
profile_after = ProfileReport(df_after, title="Données Traitées")

# Comparaison
comparison_report = profile_before.compare(profile_after)
comparison_report.to_file("reports/comparison_before_after.html")

# Comparaison train/test
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    df.drop('target', axis=1), df['target'], 
    test_size=0.3, random_state=42
)

train_profile = ProfileReport(X_train, title="Training Set")
test_profile = ProfileReport(X_test, title="Test Set")

train_test_comparison = train_profile.compare(test_profile)
train_test_comparison.to_file("reports/train_test_comparison.html")
```

---

## 5. Time Series : Analyse Avancée {#timeseries}

### 5.1 Configuration Time Series

ydata-profiling peut être utilisé pour une analyse exploratoire rapide des données time-series. Ceci est utile pour une compréhension rapide du comportement des variables dépendantes du temps concernant les comportements tels que les graphiques temporels, la saisonnalité, les tendances, la stationnarité et les écarts de données.

```python
# Préparation des données time series
def prepare_timeseries_data(csv_path):
    """
    Prépare les données time series pour l'analyse YData
    """
    df = pd.read_csv(csv_path)
    
    # Conversion de la colonne date
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Tri par timestamp
    df = df.sort_values('timestamp')
    
    # Définition de l'index temporel
    df.set_index('timestamp', inplace=True)
    
    return df

# Chargement des données
ts_data = prepare_timeseries_data('data/sensor_readings.csv')

# Profilage time series
ts_profile = ProfileReport(ts_data,
                          tsmode=True,  # Active le mode time series
                          sortby='timestamp',  # Colonne de tri temporel
                          title="Analyse Time Series - Capteurs")

ts_profile.to_file("reports/timeseries_analysis.html")
```

### 5.2 Détection de Saisonnalité et Tendances

Spécifiquement pour l'analyse de time-series, 2 nouveaux avertissements ont été ajoutés à la famille d'avertissements de ydata-profiling : NON_STATIONARY et SEASONAL.

```python
# Configuration avancée pour time series
ts_config = {
    'timeseries': {
        'autocorrelation': 0.7,  # Seuil de détection d'autocorrélation
        'lags': 40,  # Nombre de lags pour ACF/PACF
        'pacf_acf_lag': 40,
        'active': True
    },
    'vars': {
        'timeseries': {
            'autocorrelation_threshold': 0.7,
            'pacf_acf_lag': 40
        }
    }
}

# Application de la configuration
profile_ts_advanced = ProfileReport(ts_data,
                                   tsmode=True,
                                   config=ts_config,
                                   title="Analyse Time Series Avancée")

# Analyse spécifique de la stationnarité
def stationarity_analysis(ts_data, column):
    """
    Analyse détaillée de la stationnarité
    """
    from statsmodels.tsa.stattools import adfuller
    
    # Test ADF
    result = adfuller(ts_data[column].dropna())
    
    analysis = {
        'adf_statistic': result[0],
        'p_value': result[1],
        'critical_values': result[4],
        'is_stationary': result[1] < 0.05
    }
    
    return analysis

# Exemple d'utilisation
stationarity_result = stationarity_analysis(ts_data, 'temperature')
print(f"Série stationnaire: {stationarity_result['is_stationary']}")
```

### 5.3 Détection de Gaps et Anomalies

L'identification automatique de ydata-profiling des lacunes potentielles dans les time-series est basée sur l'analyse des intervalles de temps. En analysant les intervalles de temps entre les points de données, les lacunes sont supposées être reflétées comme des intervalles plus grands dans la distribution.

```python
# Configuration pour détection de gaps
gap_config = {
    'timeseries': {
        'active': True,
        'autocorrelation': 0.7,
        'lags': 40,
        'pacf_acf_lag': 40,
        'gaps': {
            'threshold': 24,  # Seuil en heures
            'active': True
        }
    }
}

# Analyse avec détection de gaps
profile_with_gaps = ProfileReport(ts_data,
                                 tsmode=True,
                                 config=gap_config,
                                 title="Détection de Gaps Time Series")

# Fonction personnalisée pour analyser les gaps
def analyze_time_gaps(df, timestamp_col='timestamp'):
    """
    Analyse détaillée des gaps temporels
    """
    df_sorted = df.sort_values(timestamp_col)
    
    # Calcul des différences temporelles
    time_diffs = df_sorted[timestamp_col].diff()
    
    # Statistiques des gaps
    gap_stats = {
        'median_interval': time_diffs.median(),
        'mean_interval': time_diffs.mean(),
        'max_gap': time_diffs.max(),
        'min_gap': time_diffs.min(),
        'total_gaps': time_diffs.isna().sum(),
        'gaps_over_threshold': (time_diffs > pd.Timedelta(hours=24)).sum()
    }
    
    return gap_stats, time_diffs

# Exemple d'analyse des gaps
gap_stats, time_diffs = analyze_time_gaps(ts_data.reset_index())
print("Statistiques des gaps:", gap_stats)
```

### 5.4 Analyse Multi-variables Time Series

```python
# Données multi-capteurs
def create_multisensor_analysis(csv_path):
    """
    Analyse time series multi-variables (plusieurs capteurs)
    """
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Pivot pour avoir une colonne par capteur
    df_pivot = df.pivot_table(
        index='timestamp',
        columns='sensor_id',
        values=['temperature', 'humidity', 'pressure'],
        aggfunc='mean'
    )
    
    # Aplatissement des colonnes multi-niveau
    df_pivot.columns = [f"{val}_{sensor}" for val, sensor in df_pivot.columns]
    
    return df_pivot

# Analyse multi-capteurs
multi_sensor_data = create_multisensor_analysis('data/multi_sensor_data.csv')

# Profilage avec corrélations croisées
cross_correlation_config = {
    'correlations': {
        'pearson': {'calculate': True},
        'spearman': {'calculate': True},
        'phi_k': {'calculate': True}
    },
    'timeseries': {
        'active': True,
        'autocorrelation': 0.7
    }
}

profile_multi = ProfileReport(multi_sensor_data,
                             tsmode=True,
                             config=cross_correlation_config,
                             title="Analyse Multi-Capteurs")
```

### 5.5 Time Series avec Entités Multiples

```python
# Analyse time series avec entités multiples (ex: multiple stores)
def prepare_multi_entity_timeseries(csv_path):
    """
    Prépare des données time series avec multiples entités
    """
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Tri par entité puis par date
    df = df.sort_values(['store_id', 'date'])
    
    return df

# Données multi-entités
multi_entity_data = prepare_multi_entity_timeseries('data/multi_store_sales.csv')

# Analyse par entité
def analyze_by_entity(df, entity_col, date_col):
    """
    Analyse time series groupée par entité
    """
    results = {}
    
    for entity in df[entity_col].unique():
        entity_data = df[df[entity_col] == entity].copy()
        entity_data = entity_data.set_index(date_col)
        
        # Profilage pour cette entité
        profile = ProfileReport(entity_data,
                               tsmode=True,
                               title=f"Time Series - {entity}")
        
        results[entity] = profile
    
    return results

# Analyse par store
store_analyses = analyze_by_entity(multi_entity_data, 'store_id', 'date')

# Sauvegarde des rapports
for store_id, profile in store_analyses.items():
    profile.to_file(f"reports/timeseries_store_{store_id}.html")
```

### 5.6 Analyse de Fréquence et Resampling

```python
# Analyse de fréquence des données
def frequency_analysis(df, timestamp_col='timestamp'):
    """
    Analyse la fréquence des données time series
    """
    df_sorted = df.sort_values(timestamp_col)
    
    # Inférence de la fréquence
    freq_inferred = pd.infer_freq(df_sorted[timestamp_col])
    
    # Statistiques de fréquence
    time_diffs = df_sorted[timestamp_col].diff().dropna()
    
    freq_stats = {
        'inferred_frequency': freq_inferred,
        'modal_interval': time_diffs.mode().iloc[0] if len(time_diffs.mode()) > 0 else None,
        'regular_intervals': len(time_diffs.unique()) <= 5,  # Heuristique
        'total_timespan': df_sorted[timestamp_col].max() - df_sorted[timestamp_col].min(),
        'expected_points': None,
        'actual_points': len(df_sorted),
        'completeness_ratio': None
    }
    
    # Calcul du ratio de complétude
    if freq_inferred:
        expected_range = pd.date_range(
            start=df_sorted[timestamp_col].min(),
            end=df_sorted[timestamp_col].max(),
            freq=freq_inferred
        )
        freq_stats['expected_points'] = len(expected_range)
        freq_stats['completeness_ratio'] = len(df_sorted) / len(expected_range)
    
    return freq_stats

# Resampling pour régulariser les données
def resample_and_analyze(df, timestamp_col='timestamp', target_freq='1H'):
    """
    Resample les données et analyse la régularité
    """
    df_copy = df.copy()
    df_copy = df_copy.set_index(timestamp_col)
    
    # Resampling avec différentes méthodes d'agrégation
    resampled_data = {
        'mean': df_copy.resample(target_freq).mean(),
        'median': df_copy.resample(target_freq).median(),
        'sum': df_copy.resample(target_freq).sum(),
        'count': df_copy.resample(target_freq).count()
    }
    
    # Profilage des données resampleées
    profiles = {}
    for method, data in resampled_data.items():
        if not data.empty:
            profile = ProfileReport(data,
                                   tsmode=True,
                                   title=f"Time Series Resampled - {method}")
            profiles[method] = profile
    
    return resampled_data, profiles

# Exemple d'utilisation
freq_stats = frequency_analysis(ts_data.reset_index())
print("Analyse de fréquence:", freq_stats)

resampled_data, resampled_profiles = resample_and_analyze(
    ts_data.reset_index(), 
    target_freq='1H'
)
```

---

## 6. Génération de Données Synthétiques {#synthetic}

### 6.1 Données Tabulaires Synthétiques

La RegularSynthesizer est parfaite pour la synthèse de données hautement dimensionnelles et indépendantes du temps avec des résultats de qualité exceptionnelle.

```python
from ydata.synthesizers.regular.model import RegularSynthesizer
from ydata.metadata import Metadata

# Préparation des données pour la synthèse
df = pd.read_csv('data/customer_data.csv')

# Création des métadonnées
metadata = Metadata(df)

# Initialisation du synthesizer
synthesizer = RegularSynthesizer(
    name='Customer_Synthesizer',
    metadata=metadata
)

# Entraînement du modèle
synthesizer.fit(df, 
               n_epochs=100,
               batch_size=500)

# Génération de données synthétiques
synthetic_data = synthesizer.sample(n_samples=1000)

print(f"Données originales: {df.shape}")
print(f"Données synthétiques: {synthetic_data.shape}")

# Sauvegarde du modèle
synthesizer.save('models/customer_synthesizer.pkl')
```

### 6.2 Time Series Synthétiques

La TimeSeriesSynthesizer gère à la fois les données de time-series régulières et irrégulières, des capteurs intelligents aux données de marché financier, incluant le support pour les données transactionnelles avec des intervalles irréguliers.

```python
from ydata.synthesizers.timeseries.model import TimeSeriesSynthesizer

# Préparation des données time series
ts_df = pd.read_csv('data/stock_prices.csv')
ts_df['date'] = pd.to_datetime(ts_df['date'])
ts_df = ts_df.sort_values('date')

# Configuration du synthesizer time series
ts_synthesizer = TimeSeriesSynthesizer(
    name='Stock_TimeSeries_Synthesizer'
)

# Entraînement avec spécification de la clé temporelle
ts_synthesizer.fit(ts_df, 
                   sortbykey='date',  # Colonne de tri temporel
                   entities=None,     # Pas d'entités multiples
                   sequence_length=30) # Longueur de séquence

# Génération de time series synthétiques
synthetic_ts = ts_synthesizer.sample(n_samples=1000,
                                    sequence_length=30)

print(f"Time series synthétiques générées: {synthetic_ts.shape}")
```

### 6.3 Time Series Multi-entités

```python
# Time series avec entités multiples (ex: multiple stocks)
multi_entity_df = pd.read_csv('data/multi_stock_data.csv')
multi_entity_df['date'] = pd.to_datetime(multi_entity_df['date'])

# Synthesizer pour entités multiples
multi_ts_synthesizer = TimeSeriesSynthesizer(
    name='Multi_Stock_Synthesizer'
)

# Entraînement avec entités
multi_ts_synthesizer.fit(multi_entity_df,
                        sortbykey='date',
                        entities='stock_symbol',  # Colonne des entités
                        sequence_length=50)

# Génération avec entités spécifiques
synthetic_multi_ts = multi_ts_synthesizer.sample(
    n_samples=500,
    entities=['AAPL', 'GOOGL', 'MSFT']  # Entités spécifiques
)
```

### 6.4 Anonymisation et Règles Métier

```python
# Configuration d'anonymisation
anonymizer_config = {
    'customer_id': {'type': 'regex', 'regex': r'CUST_[0-9]{6}'},
    'phone': {'type': 'regex', 'regex': r'[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}'},
    'email': {'type': 'categorical'},  # Anonymisation catégorielle
    'salary': {'type': 'numerical', 'noise_level': 0.1}  # Ajout de bruit
}

# Règles métier pour préserver la cohérence
def salary_education_rule(education_level: pd.Series) -> pd.Series:
    """
    Règle métier : corrélation entre niveau d'éducation et salaire
    """
    education_mapping = {
        'High School': 30000,
        'Bachelor': 50000,
        'Master': 70000,
        'PhD': 90000
    }
    
    base_salary = education_level.map(education_mapping)
    # Ajout de variabilité
    noise = np.random.normal(0, 0.2, len(base_salary))
    return base_salary * (1 + noise)

# Synthesizer avec règles métier
class CustomRegularSynthesizer(RegularSynthesizer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business_rules = {}
    
    def add_business_rule(self, target_column, rule_function, dependencies):
        """
        Ajoute une règle métier au synthesizer
        """
        self.business_rules[target_column] = {
            'function': rule_function,
            'dependencies': dependencies
        }
    
    def apply_business_rules(self, data):
        """
        Applique les règles métier aux données synthétiques
        """
        for target_col, rule in self.business_rules.items():
            if target_col in data.columns:
                # Application de la règle
                dependencies_data = data[rule['dependencies']]
                data[target_col] = rule['function'](dependencies_data)
        
        return data

# Utilisation du synthesizer avec règles
custom_synthesizer = CustomRegularSynthesizer(
    name='Custom_Business_Rules_Synthesizer',
    metadata=metadata
)

# Ajout de règles métier
custom_synthesizer.add_business_rule(
    target_column='salary',
    rule_function=salary_education_rule,
    dependencies=['education_level']
)

# Entraînement et génération
custom_synthesizer.fit(df)
synthetic_with_rules = custom_synthesizer.sample(n_samples=1000)

# Application des règles post-génération
synthetic_with_rules = custom_synthesizer.apply_business_rules(synthetic_with_rules)
```

### 6.5 Évaluation de la Qualité des Données Synthétiques

Un rapport étendu de qualité des données synthétiques qui mesure 3 dimensions : la confidentialité, l'utilité et la fidélité des données générées.

```python
from ydata.report import SyntheticDataProfile

# Évaluation de la qualité
quality_report = SyntheticDataProfile(
    original_data=df,
    synthetic_data=synthetic_data,
    title="Évaluation Qualité - Customer Data"
)

# Génération du rapport
quality_report.to_file("reports/synthetic_quality_assessment.html")

# Export JSON pour intégration
quality_report.to_file("reports/synthetic_quality_assessment.json")

# Métriques personnalisées
def calculate_privacy_metrics(original, synthetic):
    """
    Calcule des métriques de confidentialité personnalisées
    """
    from sklearn.metrics import accuracy_score
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # Préparation pour attaque d'inférence d'appartenance
    X_orig = original.select_dtypes(include=[np.number])
    X_synth = synthetic.select_dtypes(include=[np.number])
    
    # Labels : 1 pour original, 0 pour synthétique
    X_combined = pd.concat([X_orig, X_synth])
    y_combined = np.concatenate([np.ones(len(X_orig)), np.zeros(len(X_synth))])
    
    # Division train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X_combined, y_combined, test_size=0.3, random_state=42
    )
    
    # Entraînement d'un classificateur
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_train, y_train)
    
    # Prédiction
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Score de confidentialité (plus proche de 0.5 = mieux)
    privacy_score = abs(accuracy - 0.5) * 2
    
    return {
        'membership_inference_accuracy': accuracy,
        'privacy_score': privacy_score,  # 0 = parfait, 1 = aucune confidentialité
        'privacy_level': 'High' if privacy_score < 0.1 else 'Medium' if privacy_score < 0.3 else 'Low'
    }

# Calcul des métriques de confidentialité
privacy_metrics = calculate_privacy_metrics(df, synthetic_data)
print("Métriques de confidentialité:", privacy_metrics)
```

---

## 7. Intégration avec DuckDB {#duckdb}

### 7.1 Pipeline DuckDB + YData SDK

```python
import duckdb
from ydata.dataset import Dataset
from ydata.profiling import ProfileReport

class DuckDBYDataPipeline:
    """
    Pipeline intégré DuckDB + YData SDK pour l'analyse de données
    """
    
    def __init__(self, db_path=None):
        """
        Initialise le pipeline
        
        Args:
            db_path (str): Chemin vers la base DuckDB (None pour en mémoire)
        """
        self.conn = duckdb.connect(db_path) if db_path else duckdb.connect()
        self.datasets = {}
        self.profiles = {}
    
    def load_csv_to_duckdb(self, csv_path, table_name):
        """
        Charge un CSV dans DuckDB
        """
        query = f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM '{csv_path}'
        """
        self.conn.execute(query)
        print(f"Table {table_name} créée depuis {csv_path}")
    
    def query_to_dataset(self, query, dataset_name):
        """
        Exécute une requête DuckDB et crée un Dataset YData
        """
        df = self.conn.execute(query).fetchdf()
        dataset = Dataset(df)
        self.datasets[dataset_name] = dataset
        return dataset
    
    def profile_dataset(self, dataset_name, **profile_kwargs):
        """
        Génère un profil YData pour un dataset
        """
        if dataset_name not in self.datasets:
            raise ValueError(f"Dataset {dataset_name} non trouvé")
        
        df = self.datasets[dataset_name].data
        profile = ProfileReport(df, title=f"Profile - {dataset_name}", **profile_kwargs)
        self.profiles[dataset_name] = profile
        return profile
    
    def analyze_timeseries_with_duckdb(self, table_name, timestamp_col, value_cols):
        """
        Analyse time series combinant DuckDB et YData
        """
        # Requêtes DuckDB pour préparer les données
        
        # 1. Détection de gaps
        gap_query = f"""
        WITH time_diffs AS (
            SELECT 
                {timestamp_col},
                {timestamp_col} - LAG({timestamp_col}) OVER (ORDER BY {timestamp_col}) as time_diff
            FROM {table_name}
            ORDER BY {timestamp_col}
        )
        SELECT 
            COUNT(*) as total_records,
            COUNT(time_diff) as time_diffs,
            AVG(EXTRACT(EPOCH FROM time_diff)) as avg_interval_seconds,
            MAX(EXTRACT(EPOCH FROM time_diff)) as max_gap_seconds,
            MIN(EXTRACT(EPOCH FROM time_diff)) as min_gap_seconds
        FROM time_diffs
        """
        
        gap_analysis = self.conn.execute(gap_query).fetchdf()
        
        # 2. Agrégations temporelles
        aggregated_query = f"""
        SELECT 
            date_trunc('hour', {timestamp_col}) as hour,
            {', '.join([f'AVG({col}) as avg_{col}' for col in value_cols])},
            {', '.join([f'COUNT({col}) as count_{col}' for col in value_cols])},
            {', '.join([f'STDDEV({col}) as std_{col}' for col in value_cols])}
        FROM {table_name}
        GROUP BY hour
        ORDER BY hour
        """
        
        hourly_data = self.query_to_dataset(aggregated_query, f"{table_name}_hourly")
        
        # 3. Profilage YData des données agrégées
        hourly_profile = self.profile_dataset(f"{table_name}_hourly", tsmode=True)
        
        return {
            'gap_analysis': gap_analysis,
            'hourly_dataset': hourly_data,
            'hourly_profile': hourly_profile
        }
    
    def close(self):
        """
        Ferme la connexion DuckDB
        """
        self.conn.close()

# Exemple d'utilisation
pipeline = DuckDBYDataPipeline()

# Chargement de données CSV
pipeline.load_csv_to_duckdb('data/sensor_data.csv', 'sensors')

# Requête complexe avec fenêtres temporelles
complex_query = """
SELECT 
    timestamp,
    sensor_id,
    temperature,
    humidity,
    -- Moyennes mobiles
    AVG(temperature) OVER (
        PARTITION BY sensor_id 
        ORDER BY timestamp 
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) as temp_ma_6,
    
    -- Détection d'anomalies basique
    CASE 
        WHEN ABS(temperature - AVG(temperature) OVER (PARTITION BY sensor_id)) > 
             2 * STDDEV(temperature) OVER (PARTITION BY sensor_id)
        THEN 1 ELSE 0
    END as is_anomaly,
    
    -- Lag features
    LAG(temperature, 1) OVER (PARTITION BY sensor_id ORDER BY timestamp) as temp_lag1,
    LAG(temperature, 24) OVER (PARTITION BY sensor_id ORDER BY timestamp) as temp_lag24

FROM sensors
ORDER BY sensor_id, timestamp
"""

# Création du dataset avec features engineering
engineered_dataset = pipeline.query_to_dataset(complex_query, 'sensors_engineered')

# Analyse time series complète
ts_analysis = pipeline.analyze_timeseries_with_duckdb(
    'sensors', 
    'timestamp', 
    ['temperature', 'humidity']
)

# Profilage du dataset avec features
engineered_profile = pipeline.profile_dataset('sensors_engineered', tsmode=True)
engineered_profile.to_file('reports/sensors_engineered_profile.html')

pipeline.close()
```

### 7.2 Optimisations DuckDB pour Time Series

DuckDB peut effectuer des analyses temporelles en utilisant des fenêtres avec différentes sémantiques (par exemple, fenêtres tumbling, hopping et sliding).

```python
def create_optimized_timeseries_tables(conn, source_table):
    """
    Crée des tables optimisées pour l'analyse time series
    """
    
    # Table avec partitioning temporel
    conn.execute(f"""
    CREATE TABLE {source_table}_daily AS
    SELECT 
        date_trunc('day', timestamp) as date,
        sensor_id,
        COUNT(*) as record_count,
        AVG(temperature) as avg_temp,
        MIN(temperature) as min_temp,
        MAX(temperature) as max_temp,
        STDDEV(temperature) as std_temp,
        AVG(humidity) as avg_humidity,
        MIN(humidity) as min_humidity,
        MAX(humidity) as max_humidity,
        STDDEV(humidity) as std_humidity
    FROM {source_table}
    GROUP BY date, sensor_id
    ORDER BY date, sensor_id
    """)
    
    # Table avec fenêtres glissantes
    conn.execute(f"""
    CREATE TABLE {source_table}_sliding_windows AS
    SELECT 
        timestamp,
        sensor_id,
        temperature,
        humidity,
        
        -- Fenêtres de 1 heure
        AVG(temperature) OVER (
            PARTITION BY sensor_id 
            ORDER BY timestamp 
            RANGE BETWEEN INTERVAL 1 HOUR PRECEDING AND CURRENT ROW
        ) as temp_1h_avg,
        
        -- Fenêtres de 24 heures
        AVG(temperature) OVER (
            PARTITION BY sensor_id 
            ORDER BY timestamp 
            RANGE BETWEEN INTERVAL 24 HOUR PRECEDING AND CURRENT ROW
        ) as temp_24h_avg,
        
        -- Détection de changements
        temperature - LAG(temperature) OVER (
            PARTITION BY sensor_id ORDER BY timestamp
        ) as temp_change,
        
        -- Percentiles mobiles
        PERCENT_RANK() OVER (
            PARTITION BY sensor_id 
            ORDER BY temperature
        ) as temp_percentile_rank
        
    FROM {source_table}
    ORDER BY sensor_id, timestamp
    """)

# Exemple d'utilisation
conn = duckdb.connect()
conn.execute("CREATE TABLE sensors AS SELECT * FROM 'data/sensor_data.csv'")
create_optimized_timeseries_tables(conn, 'sensors')

# Chargement et analyse des tables optimisées
daily_data = conn.execute("SELECT * FROM sensors_daily").fetchdf()
sliding_data = conn.execute("SELECT * FROM sensors_sliding_windows").fetchdf()

# Profilage des données agrégées
daily_profile = ProfileReport(daily_data, 
                             tsmode=True, 
                             title="Données Agrégées Quotidiennes")

sliding_profile = ProfileReport(sliding_data, 
                               tsmode=True, 
                               title="Fenêtres Glissantes")

conn.close()
```

---

## 8. Cas d'Usage Avancés {#advanced}

### 8.1 Pipeline Complet d'Analyse

```python
class AdvancedTimeSeriesAnalysisPipeline:
    """
    Pipeline complet pour l'analyse avancée de time series
    """
    
    def __init__(self, config=None):
        self.config = config or self._default_config()
        self.results = {}
    
    def _default_config(self):
        return {
            'outlier_detection': {
                'method': 'iqr',
                'threshold': 1.5
            },
            'seasonality_detection': {
                'max_period': 365,
                'min_period': 7
            },
            'trend_analysis': {
                'window_size': 30
            },
            'synthetic_generation': {
                'n_samples': 1000,
                'sequence_length': 50
            }
        }
    
    def load_and_prepare_data(self, data_source, timestamp_col='timestamp'):
        """
        Charge et prépare les données time series
        """
        if isinstance(data_source, str):
            # Chargement depuis CSV
            df = pd.read_csv(data_source)
        else:
            df = data_source.copy()
        
        # Conversion timestamp
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        df = df.sort_values(timestamp_col)
        
        # Détection de la fréquence
        freq = pd.infer_freq(df[timestamp_col])
        
        self.results['raw_data'] = df
        self.results['frequency'] = freq
        
        return df
    
    def detect_outliers(self, df, value_columns):
        """
        Détection d'outliers multi-méthodes
        """
        outliers_info = {}
        
        for col in value_columns:
            if col in df.columns:
                data = df[col].dropna()
                
                # Méthode IQR
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                iqr_outliers = (data < lower_bound) | (data > upper_bound)
                
                # Méthode Z-score
                z_scores = np.abs((data - data.mean()) / data.std())
                zscore_outliers = z_scores > 3
                
                outliers_info[col] = {
                    'iqr_outliers': iqr_outliers.sum(),
                    'iqr_percentage': (iqr_outliers.sum() / len(data)) * 100,
                    'zscore_outliers': zscore_outliers.sum(),
                    'zscore_percentage': (zscore_outliers.sum() / len(data)) * 100,
                    'bounds': {'lower': lower_bound, 'upper': upper_bound}
                }
        
        self.results['outliers'] = outliers_info
        return outliers_info
    
    def analyze_seasonality(self, df, timestamp_col, value_columns):
        """
        Analyse de saisonnalité avancée
        """
        from scipy import signal
        from scipy.fft import fft, fftfreq
        
        seasonality_results = {}
        
        for col in value_columns:
            if col in df.columns:
                # Préparation des données
                ts_data = df.set_index(timestamp_col)[col].dropna()
                
                # FFT pour détection de périodes
                fft_values = fft(ts_data.values)
                fft_freq = fftfreq(len(ts_data.values))
                
                # Recherche des pics de fréquence
                power_spectrum = np.abs(fft_values) ** 2
                peaks, _ = signal.find_peaks(power_spectrum[1:len(power_spectrum)//2], 
                                           height=np.max(power_spectrum) * 0.1)
                
                # Conversion en périodes
                significant_periods = []
                for peak in peaks:
                    if fft_freq[peak + 1] != 0:
                        period = 1 / abs(fft_freq[peak + 1])
                        significant_periods.append(period)
                
                seasonality_results[col] = {
                    'significant_periods': sorted(significant_periods),
                    'dominant_period': min(significant_periods) if significant_periods else None,
                    'power_spectrum_peaks': len(peaks)
                }
        
        self.results['seasonality'] = seasonality_results
        return seasonality_results
    
    def generate_comprehensive_profile(self, df, timestamp_col):
        """
        Génère un profil complet avec toutes les analyses
        """
        # Configuration avancée pour le profilage
        advanced_config = {
            'timeseries': {
                'active': True,
                'autocorrelation': 0.7,
                'lags': 50,
                'pacf_acf_lag': 50
            },
            'correlations': {
                'pearson': {'calculate': True},
                'spearman': {'calculate': True},
                'phi_k': {'calculate': True}
            },
            'missing_diagrams': {
                'matrix': True,
                'bar': True,
                'heatmap': True
            },
            'interactions': {
                'continuous': True
            }
        }
        
        # Génération du profil
        profile = ProfileReport(df,
                               tsmode=True,
                               sortby=timestamp_col,
                               config=advanced_config,
                               title="Analyse Time Series Complète")
        
        self.results['comprehensive_profile'] = profile
        return profile
    
    def generate_synthetic_data(self, df, timestamp_col, entity_col=None):
        """
        Génération de données synthétiques time series
        """
        # Préparation pour le synthesizer
        synth_df = df.copy()
        
        if entity_col:
            # Multi-entités
            synthesizer = TimeSeriesSynthesizer(name='Advanced_TS_Synthesizer')
            synthesizer.fit(synth_df,
                           sortbykey=timestamp_col,
                           entities=entity_col,
                           sequence_length=self.config['synthetic_generation']['sequence_length'])
        else:
            # Single entité
            synthesizer = TimeSeriesSynthesizer(name='Advanced_TS_Synthesizer')
            synthesizer.fit(synth_df,
                           sortbykey=timestamp_col,
                           sequence_length=self.config['synthetic_generation']['sequence_length'])
        
        # Génération
        synthetic_data = synthesizer.sample(
            n_samples=self.config['synthetic_generation']['n_samples']
        )
        
        self.results['synthetic_data'] = synthetic_data
        self.results['synthesizer'] = synthesizer
        
        return synthetic_data
    
    def run_complete_analysis(self, data_source, timestamp_col='timestamp', 
                            value_columns=None, entity_col=None):
        """
        Exécute l'analyse complète
        """
        print("🚀 Démarrage de l'analyse complète...")
        
        # 1. Chargement et préparation
        print("📊 Chargement des données...")
        df = self.load_and_prepare_data(data_source, timestamp_col)
        
        if value_columns is None:
            value_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 2. Détection d'outliers
        print("🔍 Détection d'outliers...")
        outliers = self.detect_outliers(df, value_columns)
        
        # 3. Analyse de saisonnalité
        print("📈 Analyse de saisonnalité...")
        seasonality = self.analyze_seasonality(df, timestamp_col, value_columns)
        
        # 4. Profilage complet
        print("📋 Génération du profil complet...")
        profile = self.generate_comprehensive_profile(df, timestamp_col)
        
        # 5. Génération de données synthétiques
        print("🎭 Génération de données synthétiques...")
        synthetic_data = self.generate_synthetic_data(df, timestamp_col, entity_col)
        
        # 6. Évaluation de qualité synthétique
        print("✅ Évaluation de la qualité...")
        quality_report = SyntheticDataProfile(
            original_data=df,
            synthetic_data=synthetic_data,
            title="Évaluation Qualité Time Series"
        )
        
        self.results['quality_report'] = quality_report
        
        print("✨ Analyse complète terminée!")
        return self.results
    
    def export_results(self, output_dir='reports'):
        """
        Exporte tous les résultats
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Export du profil principal
        if 'comprehensive_profile' in self.results:
            self.results['comprehensive_profile'].to_file(
                f"{output_dir}/comprehensive_profile.html"
            )
        
        # Export du rapport de qualité
        if 'quality_report' in self.results:
            self.results['quality_report'].to_file(
                f"{output_dir}/quality_assessment.html"
            )
        
        # Export des données synthétiques
        if 'synthetic_data' in self.results:
            self.results['synthetic_data'].to_csv(
                f"{output_dir}/synthetic_data.csv", index=False
            )
        
        # Export des analyses JSON
        import json
        analysis_summary = {
            'outliers': self.results.get('outliers', {}),
            'seasonality': self.results.get('seasonality', {}),
            'frequency': self.results.get('frequency', None)
        }
        
        with open(f"{output_dir}/analysis_summary.json", 'w') as f:
            json.dump(analysis_summary, f, indent=2, default=str)

# Exemple d'utilisation complète
pipeline = AdvancedTimeSeriesAnalysisPipeline()

# Configuration personnalisée
custom_config = {
    'synthetic_generation': {
        'n_samples': 2000,
        'sequence_length': 100
    }
}
pipeline.config.update(custom_config)

# Exécution de l'analyse complète
results = pipeline.run_complete_analysis(
    data_source='data/complex_timeseries.csv',
    timestamp_col='timestamp',
    value_columns=['temperature', 'humidity', 'pressure'],
    entity_col='sensor_id'
)

# Export des résultats
pipeline.export_results('reports/advanced_analysis')
```

### 8.2 Détection d'Anomalies Avancée

```python
class TimeSeriesAnomalyDetector:
    """
    Détecteur d'anomalies spécialisé pour time series
    """
    
    def __init__(self):
        self.models = {}
        self.thresholds = {}
    
    def isolation_forest_anomalies(self, df, value_columns):
        """
        Détection d'anomalies avec Isolation Forest
        """
        from sklearn.ensemble import IsolationForest
        
        anomalies = {}
        
        for col in value_columns:
            if col in df.columns:
                # Préparation des features
                data = df[col].dropna().values.reshape(-1, 1)
                
                # Entraînement Isolation Forest
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_labels = iso_forest.fit_predict(data)
                
                # -1 pour anomalie, 1 pour normal
                anomaly_indices = np.where(anomaly_labels == -1)[0]
                
                anomalies[col] = {
                    'model': iso_forest,
                    'anomaly_indices': anomaly_indices,
                    'anomaly_count': len(anomaly_indices),
                    'anomaly_percentage': (len(anomaly_indices) / len(data)) * 100
                }
        
        return anomalies
    
    def statistical_anomalies(self, df, timestamp_col, value_columns, window_size=50):
        """
        Détection d'anomalies basée sur les statistiques mobiles
        """
        anomalies = {}
        
        for col in value_columns:
            if col in df.columns:
                # Calcul des statistiques mobiles
                rolling_mean = df[col].rolling(window=window_size).mean()
                rolling_std = df[col].rolling(window=window_size).std()
                
                # Détection d'anomalies (> 3 sigma)
                upper_bound = rolling_mean + 3 * rolling_std
                lower_bound = rolling_mean - 3 * rolling_std
                
                anomaly_mask = (df[col] > upper_bound) | (df[col] < lower_bound)
                anomaly_indices = df[anomaly_mask].index.tolist()
                
                anomalies[col] = {
                    'anomaly_indices': anomaly_indices,
                    'anomaly_count': len(anomaly_indices),
                    'upper_bound': upper_bound,
                    'lower_bound': lower_bound,
                    'rolling_mean': rolling_mean,
                    'rolling_std': rolling_std
                }
        
        return anomalies
    
    def generate_anomaly_report(self, df, timestamp_col, anomalies_dict):
        """
        Génère un rapport d'anomalies avec YData Profiling
        """
        # Ajout des colonnes d'anomalies au DataFrame
        df_with_anomalies = df.copy()
        
        for col, anomaly_info in anomalies_dict.items():
            anomaly_col = f"{col}_anomaly"
            df_with_anomalies[anomaly_col] = False
            df_with_anomalies.loc[anomaly_info['anomaly_indices'], anomaly_col] = True
        
        # Profilage avec les colonnes d'anomalies
        profile = ProfileReport(df_with_anomalies,
                               tsmode=True,
                               sortby=timestamp_col,
                               title="Rapport de Détection d'Anomalies")
        
        return profile

# Utilisation du détecteur d'anomalies
detector = TimeSeriesAnomalyDetector()

# Chargement des données
df = pd.read_csv('data/sensor_readings.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Détection avec Isolation Forest
iso_anomalies = detector.isolation_forest_anomalies(df, ['temperature', 'humidity'])

# Détection statistique
stat_anomalies = detector.statistical_anomalies(df, 'timestamp', ['temperature', 'humidity'])

# Génération du rapport
anomaly_report = detector.generate_anomaly_report(df, 'timestamp', stat_anomalies)
anomaly_report.to_file('reports/anomaly_detection_report.html')
```

---

## 9. Bonnes Pratiques {#best-practices}

### 9.1 Optimisation des Performances

```python
# Configuration optimisée pour gros datasets
def optimize_for_large_datasets():
    """
    Configuration optimisée pour les gros datasets
    """
    optimized_config = {
        'samples': {
            'head': 5,
            'tail': 5,
            'random': 10
        },
        'correlations': {
            'pearson': {'calculate': True, 'warn_high_correlations': False},
            'spearman': {'calculate': False},  # Désactivé pour performance
            'kendall': {'calculate': False},
            'phi_k': {'calculate': False},  # Coûteux en calcul
            'cramers': {'calculate': True}
        },
        'missing_diagrams': {
            'matrix': False,  # Coûteux pour gros datasets
            'bar': True,
            'heatmap': False,
            'dendrogram': False
        },
        'duplicates': {
            'head': 5,
            'key': '_row'
        },
        'interactions': {
            'continuous': False  # Très coûteux
        },
        'html': {
            'minify_html': True,
            'use_local_assets': True
        }
    }
    
    return optimized_config

# Exemple d'utilisation pour gros dataset
large_df = pd.read_csv('data/very_large_dataset.csv')
optimized_config = optimize_for_large_datasets()

profile_large = ProfileReport(large_df,
                             config=optimized_config,
                             title="Analyse Optimisée - Gros Dataset")
```

### 9.2 Gestion de la Mémoire

```python
def memory_efficient_analysis(csv_path, chunk_size=10000):
    """
    Analyse efficace en mémoire pour très gros fichiers
    """
    # Lecture par chunks
    chunk_profiles = []
    
    for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size)):
        # Profilage simplifié pour chaque chunk
        chunk_profile = ProfileReport(chunk,
                                     minimal=True,
                                     title=f"Chunk {i+1}")
        chunk_profiles.append(chunk_profile)
        
        # Optionnel : sauvegarde immédiate
        chunk_profile.to_file(f"reports/chunk_{i+1}_profile.html")
    
    return chunk_profiles

# Analyse par échantillonnage stratifié
def stratified_sampling_analysis(df, strata_column, sample_size=1000):
    """
    Analyse par échantillonnage stratifié
    """
    stratified_samples = []
    
    for stratum in df[strata_column].unique():
        stratum_data = df[df[strata_column] == stratum]
        
        # Échantillonnage proportionnel
        n_samples = min(sample_size, len(stratum_data))
        sample = stratum_data.sample(n=n_samples, random_state=42)
        
        stratified_samples.append(sample)
    
    # Combinaison des échantillons
    combined_sample = pd.concat(stratified_samples, ignore_index=True)
    
    # Profilage de l'échantillon représentatif
    profile = ProfileReport(combined_sample,
                           title="Analyse par Échantillonnage Stratifié")
    
    return profile, combined_sample
```

### 9.3 Validation et Tests

```python
def validate_synthetic_data_quality(original_df, synthetic_df, threshold_dict=None):
    """
    Validation complète de la qualité des données synthétiques
    """
    if threshold_dict is None:
        threshold_dict = {
            'correlation_similarity': 0.9,
            'distribution_similarity': 0.8,
            'privacy_score': 0.3
        }
    
    validation_results = {}
    
    # 1. Comparaison des corrélations
    orig_corr = original_df.select_dtypes(include=[np.number]).corr()
    synth_corr = synthetic_df.select_dtypes(include=[np.number]).corr()
    
    # Similarité des matrices de corrélation
    correlation_diff = np.abs(orig_corr - synth_corr).mean().mean()
    correlation_similarity = 1 - correlation_diff
    
    validation_results['correlation_similarity'] = {
        'score': correlation_similarity,
        'threshold': threshold_dict['correlation_similarity'],
        'passed': correlation_similarity >= threshold_dict['correlation_similarity']
    }
    
    # 2. Test Kolmogorov-Smirnov pour les distributions
    from scipy.stats import ks_2samp
    
    ks_results = {}
    for col in original_df.select_dtypes(include=[np.number]).columns:
        if col in synthetic_df.columns:
            ks_stat, p_value = ks_2samp(original_df[col].dropna(), 
                                       synthetic_df[col].dropna())
            ks_results[col] = {
                'ks_statistic': ks_stat,
                'p_value': p_value,
                'distributions_similar': p_value > 0.05
            }
    
    validation_results['distribution_tests'] = ks_results
    
    # 3. Score de confidentialité
    privacy_score = calculate_privacy_metrics(original_df, synthetic_df)
    validation_results['privacy'] = {
        'score': privacy_score['privacy_score'],
        'threshold': threshold_dict['privacy_score'],
        'passed': privacy_score['privacy_score'] <= threshold_dict['privacy_score']
    }
    
    # 4. Score global
    passed_tests = sum([
        validation_results['correlation_similarity']['passed'],
        sum([test['distributions_similar'] for test in ks_results.values()]) / len(ks_results),
        validation_results['privacy']['passed']
    ])
    
    validation_results['overall_score'] = passed_tests / 3
    validation_results['quality_level'] = (
        'Excellent' if validation_results['overall_score'] > 0.8 
        else 'Good' if validation_results['overall_score'] > 0.6 
        else 'Acceptable' if validation_results['overall_score'] > 0.4 
        else 'Poor'
    )
    
    return validation_results

# Tests automatisés
def run_automated_tests(data_path):
    """
    Suite de tests automatisés pour validation des pipelines
    """
    test_results = {}
    
    try:
        # Test 1: Chargement des données
        df = pd.read_csv(data_path)
        test_results['data_loading'] = {'passed': True, 'message': 'OK'}
    except Exception as e:
        test_results['data_loading'] = {'passed': False, 'message': str(e)}
        return test_results
    
    try:
        # Test 2: Profilage basique
        profile = ProfileReport(df.head(1000), minimal=True)
        test_results['basic_profiling'] = {'passed': True, 'message': 'OK'}
    except Exception as e:
        test_results['basic_profiling'] = {'passed': False, 'message': str(e)}
    
    try:
        # Test 3: Génération synthétique (si applicable)
        if len(df) > 100:
            metadata = Metadata(df.head(1000))
            synthesizer = RegularSynthesizer(metadata=metadata)
            synthesizer.fit(df.head(1000), n_epochs=5)  # Test rapide
            synthetic_sample = synthesizer.sample(n_samples=100)
            test_results['synthetic_generation'] = {'passed': True, 'message': 'OK'}
    except Exception as e:
        test_results['synthetic_generation'] = {'passed': False, 'message': str(e)}
    
    # Résumé des tests
    passed_tests = sum([test['passed'] for test in test_results.values()])
    total_tests = len(test_results)
    
    test_results['summary'] = {
        'passed': passed_tests,
        'total': total_tests,
        'success_rate': passed_tests / total_tests
    }
    
    return test_results
```

### 9.4 Configuration par Environnement

```python
# Configurations par environnement
ENVIRONMENT_CONFIGS = {
    'development': {
        'profiling': {
            'samples': {'head': 5, 'tail': 5, 'random': 5},
            'correlations': {'pearson': {'calculate': True}, 'spearman': {'calculate': False}},
            'interactions': {'continuous': False}
        },
        'synthetic': {
            'n_epochs': 10,
            'batch_size': 100
        }
    },
    'testing': {
        'profiling': {
            'samples': {'head': 10, 'tail': 10, 'random': 10},
            'correlations': {'pearson': {'calculate': True}, 'spearman': {'calculate': True}},
            'interactions': {'continuous': True}
        },
        'synthetic': {
            'n_epochs': 50,
            'batch_size': 500
        }
    },
    'production': {
        'profiling': {
            'samples': {'head': 20, 'tail': 20, 'random': 20},
            'correlations': {'pearson': {'calculate': True}, 'spearman': {'calculate': True}, 'phi_k': {'calculate': True}},
            'interactions': {'continuous': True}
        },
        'synthetic': {
            'n_epochs': 200,
            'batch_size': 1000
        }
    }
}

def get_environment_config(env='development'):
    """
    Récupère la configuration pour un environnement donné
    """
    return ENVIRONMENT_CONFIGS.get(env, ENVIRONMENT_CONFIGS['development'])

# Utilisation
config = get_environment_config('production')
profile = ProfileReport(df, config=config['profiling'])
```

---

## Conclusion

Cette documentation exhaustive couvre l'ensemble des fonctionnalités de YData SDK pour l'analyse de données CSV et DuckDB, avec un focus particulier sur les time series. YData SDK est un écosystème complet qui permet aux professionnels des données d'adopter une approche centrée sur les données pour améliorer la qualité des datasets, offrant des outils puissants pour :

- **Profilage avancé** : Analyse comprehensive des données tabulaires, time-series et textuelles
- **Détection d'anomalies** : Identification automatique des problèmes de stationnarité et de saisonnalité
- **Génération synthétique** : Création de datasets synthétiques de haute qualité préservant les propriétés statistiques
- **Intégration flexible** : Compatible avec les workflows existants et les bases de données modernes

Les exemples et techniques présentés dans cette documentation permettent de tirer parti de la puissance combinée de YData SDK et des outils modernes d'analyse de données pour créer des pipelines robustes et efficaces.
