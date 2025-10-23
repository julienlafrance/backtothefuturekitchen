# 🧪 Tests d'Infrastructure - 50_test/

## Vue d'ensemble

Le répertoire `50_test/` contient des **tests d'infrastructure** pour valider la configuration S3, DuckDB et les requêtes SQL du projet. Contrairement aux tests unitaires classiques, ces tests vérifient l'**intégration avec les services externes** (S3, DuckDB).

## Pourquoi pas de coverage ici ?

Les tests d'infrastructure **ne nécessitent pas de coverage** car :

1. **Pas de code métier** - Ce sont des tests de validation, pas du code de production
2. **Tests d'intégration** - Vérifient les connexions S3, DuckDB, Docker
3. **Automatisation de validation** - Scannent automatiquement le code pour trouver les fichiers parquet et requêtes SQL

**Le coverage est pertinent pour** : 10_preprod, 20_prod, 00_eda (code métier)
**Le coverage n'est PAS pertinent pour** : 50_test (tests d'infrastructure)

---

## Architecture des tests

```
50_test/
├── S3_duckdb_test.py           # Tests S3 + DuckDB (14 tests)
├── test_s3_parquet_files.py    # Validation parquet files (5 tests)
├── test_sql_queries.py         # Validation requêtes SQL (16 tests)
├── pyproject.toml              # Configuration pytest (sans coverage)
└── README_TESTS.md             # Ce fichier
```

---

## 1. S3_duckdb_test.py (14 tests)

### Objectif
Tests complets de l'infrastructure S3 + DuckDB avec connexion au bucket Garage.

### Tests effectués

#### 📦 Environnement (4 tests)
- `test_environment_hostname` - Vérifie le hostname
- `test_environment_ip` - Détecte l'IP et le réseau local
- `test_credentials_file_exists` - Vérifie `96_keys/credentials`
- `test_duckdb_file_exists` - Vérifie `96_keys/garage_s3.duckdb`

#### 🔌 Connexion S3 (2 tests)
- `test_s3_client_creation` - Crée le client boto3
- `test_s3_bucket_accessible` - Liste les objets du bucket
- `test_s3_list_all_objects` - Statistiques complètes du bucket

#### ⚡ Performance (1 test)
- `test_s3_download_performance` - Télécharge un fichier et mesure la vitesse
  - **Objectif**: > 5 MB/s
  - **Résultat typique**: ~8.8 MB/s

#### 🗄️ DuckDB + S3 (3 tests)
- `test_duckdb_s3_count_recipes` - `COUNT(*)` sur CSV S3
- `test_duckdb_s3_group_by` - `GROUP BY` sur CSV S3
- `test_duckdb_s3_parquet_file` - Lecture fichier parquet S3

#### 🐳 Docker (4 tests - optionnels)
- `test_docker_containers_running` - Liste les containers actifs
- `test_docker_s3_in_containers` - Teste boto3 dans mange_preprod et mange_prod

**Note**: Les tests Docker sont **skip automatiquement** si Docker n'est pas disponible.

### Configuration S3

```python
# Lecture depuis 96_keys/credentials
[s3fast]
aws_access_key_id = GK...
aws_secret_access_key = 50e...
endpoint_url = http://s3fast.lafrance.io
region = garage-fast
```

### Fixtures pytest

```python
@pytest.fixture(scope="module")
def s3_config(credentials_file):
    """Charge la config S3 depuis credentials"""

@pytest.fixture(scope="module")
def s3_client(s3_config):
    """Crée le client boto3 S3"""

@pytest.fixture(scope="module")
def duckdb_connection(s3_config):
    """Connexion DuckDB avec secret S3"""
```

### Commandes

```bash
# Tous les tests
pytest S3_duckdb_test.py -v

# Avec output détaillé
pytest S3_duckdb_test.py -v -s

# Tests spécifiques
pytest S3_duckdb_test.py::test_s3_bucket_accessible -v
pytest S3_duckdb_test.py::test_duckdb_s3_count_recipes -v
```

---

## 2. test_s3_parquet_files.py (5 tests)

### Objectif
**Scanne automatiquement** tous les fichiers `.py` et `.ipynb` du projet pour trouver les références aux fichiers parquet, puis vérifie leur accessibilité sur S3.

### Logique de détection

```python
def extract_parquet_files_from_code() -> Dict[str, List[str]]:
    """
    Scanne 00_eda, 10_preprod, 20_prod

    Returns:
        {
            'interactions_sample.parquet': [
                '00_eda/notebook.ipynb',
                '10_preprod/src/module.py'
            ]
        }
    """
```

**Patterns détectés:**
- `s3://mangetamain/file.parquet`
- `'file.parquet'` ou `"file.parquet"`
- `FROM 'file.parquet'` (dans SQL)

### Tests effectués

1. **test_parquet_files_discovered** - Vérifie qu'au moins 1 fichier est trouvé
2. **test_parquet_accessible** - Teste `COUNT(*)` sur chaque parquet (parametrized)
3. **test_parquet_schema** - Lit le schéma (colonnes) de chaque parquet
4. **test_parquet_sample_data** - Lit 5 lignes de chaque parquet
5. **test_all_parquet_files_summary** - Résumé global avec statistiques

### Exemple de résultat

```
📋 Fichiers parquet découverts: 1
   • interactions_sample.parquet
     └─ 00_eda/09_test/analyse_ratings_simple_clean.py
     └─ 10_preprod/src/mangetamain_analytics/visualization/analyse_ratings_simple.py

✅ interactions_sample.parquet
   ├─ 50,000 lignes × 6 colonnes
   └─ Utilisé par 2 fichier(s)
```

### Commandes

```bash
# Tous les tests
pytest test_s3_parquet_files.py -v -s

# Découverte seulement
pytest test_s3_parquet_files.py::test_parquet_files_discovered -v

# Scan manuel (sans tests)
python test_s3_parquet_files.py
```

---

## 3. test_sql_queries.py (16 tests)

### Objectif
**Scanne automatiquement** tous les fichiers `.py` et `.ipynb` pour extraire les requêtes SQL, puis teste leur syntaxe et exécutabilité.

### Logique de détection

```python
def extract_sql_queries_from_code() -> Dict[str, List[Dict]]:
    """
    Trouve toutes les requêtes SQL dans le projet

    Returns:
        {
            'file.py': [
                {
                    'query': 'SELECT * FROM table',
                    'line': 42,
                    'is_complete': True
                }
            ]
        }
    """
```

**Patterns détectés:**
- `conn.execute("""SELECT...""")`
- `sql = """SELECT..."""`
- `QUERY = f"""SELECT..."""`
- Fonctionne avec triple quotes et f-strings

### Nettoyage et validation

```python
def clean_sql_query(query: str) -> tuple[str, bool]:
    """
    Nettoie une requête et vérifie si elle est testable

    Returns:
        (cleaned_query, is_complete)

    is_complete = True si:
    - Contient SELECT et FROM
    - Pas de templates {variable}
    - Pas de code Python mélangé
    """
```

**Exemples de requêtes filtrées:**
- ❌ `SELECT * FROM {table_name}` - Template non résolu
- ❌ `SELECT * FROM iris` - Exemple générique
- ✅ `SELECT * FROM 's3://mangetamain/file.csv'` - Requête complète

### Tests effectués

1. **test_sql_queries_discovered** - Affiche les statistiques de découverte
2. **test_sql_query_valid_syntax** - Teste `EXPLAIN query` (parametrized)
3. **test_sql_query_executable** - Exécute `query LIMIT 1` (parametrized)
4. **test_sql_queries_summary** - Résumé global avec catégorisation

### Exemple de résultat

```
📋 Requêtes SQL découvertes:
   • Total: 27
   • Complètes (testables): 7
   • Incomplètes (templates): 20

📄 Requêtes testables par fichier:

   10_preprod/src/mangetamain_analytics/visualization/analyse_ratings_simple.py
      └─ ligne 51: SELECT rating, COUNT(*) as count FROM 's3://...

   00_eda/09_test/test_module.py
      └─ ligne 33: SELECT * FROM RAW_interactions WHERE rating...

🔍 Types de requêtes:
   • Requêtes S3: 3
   • Requêtes sur tables DuckDB: 4
```

### Commandes

```bash
# Tous les tests
pytest test_sql_queries.py -v -s

# Découverte seulement
pytest test_sql_queries.py::test_sql_queries_discovered -v

# Test syntaxe seulement
pytest test_sql_queries.py -k "valid_syntax" -v

# Scan manuel
python test_sql_queries.py
```

---

## Configuration pytest

### pyproject.toml

```toml
[project]
dependencies = [
    "boto3>=1.40.48",
    "duckdb>=1.4.1",
    "pytest>=8.0.0",
    "pytest-cov>=6.0.0",
    "pandas>=2.0.0",
]

[tool.pytest.ini_options]
testpaths = ["."]
python_files = ["test_*.py", "S3_duckdb_test.py"]
addopts = ["-v"]  # Pas de coverage pour les tests d'infrastructure
```

**Note importante:** Pas de `--cov` dans `addopts` car ce sont des tests d'infrastructure.

---

## Exécution des tests

### Sur machine locale

```bash
cd 50_test

# Tous les tests (sauf Docker)
pytest -v

# Tests S3 + DuckDB seulement
pytest S3_duckdb_test.py -v

# Tests parquet seulement
pytest test_s3_parquet_files.py -v

# Tests SQL seulement
pytest test_sql_queries.py -v
```

**Résultat local:** 14-16 tests passent (Docker skip)

### Sur serveur (dataia)

```bash
ssh dataia
cd mangetamain/000_dev/50_test

# Installer les dépendances
uv sync

# Lancer tous les tests
uv run pytest -v
```

**Résultat serveur:** 35 tests passent (Docker disponible)

---

## Résultats attendus

### ✅ Tests qui doivent passer

- **Environnement** - Hostname, IP, credentials
- **S3 connexion** - Client boto3, bucket accessible
- **S3 performance** - Download > 5 MB/s
- **DuckDB + S3** - COUNT, GROUP BY, lecture parquet
- **Parquet files** - Tous les fichiers référencés sont accessibles
- **SQL queries** - Syntaxe valide et exécutable

### ⚠️ Tests qui peuvent skip

- **Docker tests** - Si Docker n'est pas disponible localement
- **Fichiers parquet** - Si aucun parquet référencé dans le code

### ❌ Tests qui indiquent un problème

- **S3 non accessible** - Vérifier credentials ou réseau
- **DuckDB erreur** - Vérifier installation DuckDB
- **Parquet introuvable** - Fichier manquant sur S3
- **SQL échoue** - Table manquante ou syntaxe incorrecte

---

## Dépannage

### Erreur: "Credentials file not found"

```bash
# Vérifier l'existence du fichier
ls -la ../96_keys/credentials

# Le fichier doit contenir:
[s3fast]
aws_access_key_id = ...
aws_secret_access_key = ...
```

### Erreur: "No data was collected" (coverage)

C'est normal! Les tests d'infrastructure n'ont pas besoin de coverage.

### Erreur: "Bucket not accessible"

```bash
# Tester la connexion manuellement
python -c "
import boto3
from configparser import ConfigParser

config = ConfigParser()
config.read('../96_keys/credentials')

s3 = boto3.client(
    's3',
    endpoint_url='http://s3fast.lafrance.io',
    aws_access_key_id=config['s3fast']['aws_access_key_id'],
    aws_secret_access_key=config['s3fast']['aws_secret_access_key']
)

print(s3.list_objects_v2(Bucket='mangetamain', MaxKeys=5))
"
```

### Tests Docker skip

Normal sur machine locale. Les tests Docker ne s'exécutent que sur le serveur.

---

## Bonnes pratiques

### ✅ À faire

1. **Lancer les tests avant commit** - Valide que tout fonctionne
2. **Vérifier les nouveaux parquets** - Ajouter au S3 avant de les référencer
3. **Tester les nouvelles requêtes SQL** - S'assurer qu'elles sont complètes
4. **Mettre à jour les credentials** - Si changement de clés S3

### ❌ À éviter

1. **Ne pas ajouter de coverage** - Pas pertinent pour tests d'infrastructure
2. **Ne pas commit les credentials** - Toujours dans 96_keys/ (gitignore)
3. **Ne pas tester en production** - Tests safe mais utiliser preprod quand possible
4. **Ne pas ignorer les warnings** - Peuvent indiquer des problèmes

---

## Ajout de nouveaux tests

### 1. Ajouter un nouveau fichier parquet

Le test le détectera automatiquement! Il suffit de:

```python
# Dans votre code
df = conn.execute("SELECT * FROM 's3://mangetamain/nouveau_fichier.parquet'").df()
```

Au prochain `pytest test_s3_parquet_files.py`, il sera testé.

### 2. Ajouter une nouvelle requête SQL

Le test la détectera automatiquement! Il suffit de:

```python
# Dans votre code
result = conn.execute("""
    SELECT column1, COUNT(*) as count
    FROM ma_table
    GROUP BY column1
""").fetchdf()
```

Au prochain `pytest test_sql_queries.py`, elle sera testée.

### 3. Ajouter un test d'infrastructure

Créer un nouveau fichier `test_nouvelle_feature.py`:

```python
import pytest

def test_ma_nouvelle_infrastructure():
    """Test de validation de nouvelle infrastructure"""
    # Setup
    connexion = create_connection()

    # Test
    result = connexion.test_feature()

    # Validation
    assert result is not None
    assert result.status == "OK"
```

---

## Intégration CI/CD

Ces tests sont idéaux pour CI/CD car ils valident l'infrastructure complète:

```yaml
# .github/workflows/test-infrastructure.yml
name: Infrastructure Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          cd 50_test
          uv sync

      - name: Run infrastructure tests
        run: |
          cd 50_test
          uv run pytest -v --junit-xml=test-results.xml
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

---

## Résumé

**50_test/** contient des **tests d'infrastructure** qui:

1. ✅ Valident S3 + DuckDB + Docker
2. 🔍 Scannent automatiquement le code pour trouver parquets et SQL
3. ⚡ Testent performance et accessibilité
4. 🚫 Ne nécessitent PAS de coverage (pas du code métier)

**Commande principale:**
```bash
cd 50_test
pytest -v
```

**Résultat attendu:**
- Local: 14-16 tests (Docker skip)
- Serveur: 35 tests (avec Docker)

---

**📚 Pour plus d'infos sur le coverage du code métier:**
- `10_preprod/` → Voir tests unitaires avec 96% coverage
- `20_prod/` → Voir tests unitaires avec 100% coverage
- `README_COVERAGE.md` → Guide complet du coverage
