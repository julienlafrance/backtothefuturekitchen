# 📦 Utilisation S3 - Guide pratique

## 🎯 Endpoint unique

Partout (hôte, Docker, Python, CLI) :
```
http://s3fast.lafrance.io
```

Pas besoin de spécifier le port `:80` !

---

## 💻 AWS CLI

```bash
# Liste fichiers
aws s3 ls s3://mangetamain/ \
  --endpoint-url http://s3fast.lafrance.io \
  --region garage-fast

# Download
aws s3 cp s3://mangetamain/PP_recipes.csv /tmp/recipes.csv \
  --endpoint-url http://s3fast.lafrance.io \
  --region garage-fast

# Upload
aws s3 cp /tmp/results.csv s3://mangetamain/results/ \
  --endpoint-url http://s3fast.lafrance.io \
  --region garage-fast
```

---

## 🐍 Python avec boto3

```python
import boto3
from configparser import ConfigParser

# Charger credentials depuis 96_keys/
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
for obj in response.get('Contents', []):
    print(f"{obj['Key']} - {obj['Size']/1e6:.1f} MB")

# Download
s3.download_file('mangetamain', 'PP_recipes.csv', '/tmp/recipes.csv')

# Upload
s3.upload_file('/tmp/results.csv', 'mangetamain', 'results/analysis.csv')
```

---

## 🦆 DuckDB (requêtes SQL sur S3)

### En CLI

```bash
# Requête simple
duckdb ~/mangetamain/96_keys/garage_s3.duckdb \
  -c "SELECT COUNT(*) FROM 's3://mangetamain/PP_recipes.csv'"

# Analyse
duckdb ~/mangetamain/96_keys/garage_s3.duckdb -c "
SELECT calorie_level, COUNT(*) as total 
FROM 's3://mangetamain/PP_recipes.csv' 
GROUP BY calorie_level
ORDER BY total DESC
"
```

### En Python

```python
import duckdb
from pathlib import Path

# Connexion à la base avec secret S3
db_path = Path.home() / 'mangetamain' / '96_keys' / 'garage_s3.duckdb'
conn = duckdb.connect(str(db_path))

# Query directe sur S3 (pas de téléchargement!)
df = conn.sql("""
    SELECT * 
    FROM 's3://mangetamain/PP_recipes.csv' 
    LIMIT 10
""").df()

print(df)

# Analyse complexe
query = """
SELECT 
    calorie_level,
    COUNT(*) as nb_recipes,
    AVG(minutes) as avg_time
FROM 's3://mangetamain/PP_recipes.csv'
GROUP BY calorie_level
"""
df_stats = conn.sql(query).df()
```

---

## 🐳 Docker

### Depuis un conteneur

```bash
# Exec dans le conteneur
docker exec mange_preprod python3 -c "
import boto3
from configparser import ConfigParser

config = ConfigParser()
config.read('../96_keys/credentials')

s3 = boto3.client(
    's3',
    endpoint_url=config['s3fast']['endpoint_url'],
    aws_access_key_id=config['s3fast']['aws_access_key_id'],
    aws_secret_access_key=config['s3fast']['aws_secret_access_key'],
    region_name=config['s3fast']['region']
)

response = s3.list_objects_v2(Bucket='mangetamain', MaxKeys=5)
print('✅ Fichiers:', [obj['Key'] for obj in response['Contents']])
"
```

---

## 🔍 Dépannage

### Test connexion

```bash
# Test DNS
getent hosts s3fast.lafrance.io

# Test iptables
sudo iptables -t nat -L OUTPUT -n -v | grep 3910

# Test S3
aws s3 ls s3://mangetamain/ \
  --endpoint-url http://s3fast.lafrance.io \
  --region garage-fast
```

### Vérifier credentials

```bash
cat ~/mangetamain/96_keys/credentials
# Doit contenir le profil [s3fast]
```

### Performance lente ?

```bash
# Vérifier que le bypass DNAT est actif
sudo iptables -t nat -L OUTPUT -n -v | grep 3910
# Doit afficher des paquets traités (colonne pkts > 0)
```

---

## 📊 Exemples avancés

### Copier tous les CSV

```bash
aws s3 sync s3://mangetamain/ /tmp/backup/ \
  --endpoint-url http://s3fast.lafrance.io \
  --region garage-fast \
  --exclude "*" --include "*.csv"
```

### Analyse DuckDB multi-fichiers

```python
import duckdb
from pathlib import Path

db_path = Path.home() / 'mangetamain' / '96_keys' / 'garage_s3.duckdb'
conn = duckdb.connect(str(db_path))

# JOIN entre plusieurs fichiers S3
query = """
SELECT 
    r.name,
    COUNT(i.user_id) as nb_interactions
FROM 's3://mangetamain/PP_recipes.csv' r
LEFT JOIN 's3://mangetamain/interactions_train.csv' i 
    ON r.id = i.recipe_id
GROUP BY r.name
ORDER BY nb_interactions DESC
LIMIT 10
"""

df = conn.sql(query).df()
print("Top 10 recettes les plus populaires:")
print(df)
```

---

## 🎯 Points clés

1. **Un seul endpoint** : `http://s3fast.lafrance.io`
2. **Credentials** : Dans `96_keys/credentials`
3. **DuckDB** : Requêtes SQL directes sur S3
4. **Performance** : 534-917 MB/s
5. **Code identique** : Hôte et Docker

---

**Bucket** : `mangetamain`  
**Région** : `garage-fast`  
**Performance** : 534 MB/s (hôte) | 917 MB/s (Docker)
