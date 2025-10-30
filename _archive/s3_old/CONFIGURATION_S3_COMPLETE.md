# 🚀 Configuration S3 Complète - Garage avec Bypass DNAT

## 📋 Vue d'ensemble

Configuration unifiée pour accès S3 Garage avec performances maximales grâce au bypass du reverse proxy.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│  Endpoint unifié: http://s3fast.lafrance.io         │
│  (sans spécifier le port :80)                       │
├─────────────────────────────────────────────────────┤
│  DNS local: s3fast.lafrance.io → 192.168.80.202    │
│  iptables DNAT: port 80 → port 3910                │
│  Résultat: Accès direct à Garage S3                │
└─────────────────────────────────────────────────────┘
```

**Bucket** : `mangetamain`  
**Région** : `garage-fast`

---

## 📊 Performances

| Source | Vitesse | vs Baseline HTTPS |
|--------|---------|-------------------|
| **Hôte** | **534 MB/s** | **+381%** 🚀 |
| **Docker** | **917 MB/s** | **+726%** ⚡ |

---

## 🔧 Configuration dans 96_keys/

### 1. Fichier `credentials`

```ini
[s3fast]
aws_access_key_id = GK4feb...
aws_secret_access_key = 50e63b...
endpoint_url = http://s3fast.lafrance.io
region = garage-fast
bucket = mangetamain
```

### 2. Fichier `aws_config`

```ini
[profile s3fast]
region = garage-fast
s3 =
    endpoint_url = http://s3fast.lafrance.io
```

### 3. Base DuckDB `garage_s3.duckdb`

Créée avec secret S3 intégré :

```sql
INSTALL httpfs;
LOAD httpfs;

CREATE SECRET s3fast (
    TYPE s3,
    KEY_ID 'votre_access_key',
    SECRET 'votre_secret_key',
    ENDPOINT 's3fast.lafrance.io',
    REGION 'garage-fast',
    URL_STYLE 'path',
    USE_SSL false
);
```

---

## 💻 Utilisation

### AWS CLI

```bash
export AWS_SHARED_CREDENTIALS_FILE=~/mangetamain/96_keys/credentials

aws s3 ls s3://mangetamain/ \
  --endpoint-url http://s3fast.lafrance.io \
  --region garage-fast
```

### Python avec boto3

```python
import boto3
from configparser import ConfigParser

# Charger credentials
config = ConfigParser()
config.read('../96_keys/credentials')

s3 = boto3.client(
    's3',
    endpoint_url=config['s3fast']['endpoint_url'],
    aws_access_key_id=config['s3fast']['aws_access_key_id'],
    aws_secret_access_key=config['s3fast']['aws_secret_access_key'],
    region_name=config['s3fast']['region']
)

# Liste fichiers
response = s3.list_objects_v2(Bucket='mangetamain')
```

### DuckDB

```python
import duckdb
from pathlib import Path

# Connexion à la base avec secret
db_path = Path.home() / 'mangetamain' / '96_keys' / 'garage_s3.duckdb'
conn = duckdb.connect(str(db_path))

# Query directe sur S3
df = conn.sql("SELECT * FROM 's3://mangetamain/PP_recipes.csv' LIMIT 10").df()
```

---

## 🐳 Docker

Les conteneurs sont auto-configurés avec :
- `extra_hosts` : DNS local pour s3fast.lafrance.io
- `cap_add: NET_ADMIN` : Permission iptables
- Règle DNAT créée au démarrage

**Aucun changement de code nécessaire !**

---

## 🔒 Sécurité

- ✅ Dossier `96_keys/` dans `.gitignore`
- ✅ Credentials jamais dans le code
- ✅ Volume Docker en read-only (`:ro`)
- ✅ Accès local uniquement (pas exposé sur internet)

---

## 📝 Fichiers de configuration

```
96_keys/
├── credentials          # AWS credentials (profil s3fast)
├── aws_config          # AWS config (profil s3fast)
├── garage_s3.duckdb    # Base DuckDB avec secret S3
└── load_credentials.py # Helper Python (legacy)
```

---

## 🎯 Résumé

1. **Un seul endpoint** : `http://s3fast.lafrance.io`
2. **Un seul profil** : `s3fast`
3. **Une seule base DuckDB** : `garage_s3.duckdb`
4. **Code identique** partout (hôte, Docker)
5. **Performance maximale** : 534-917 MB/s

---

**Dernière mise à jour** : 2025-10-09  
**Configuration** : Bypass DNAT actif et permanent
