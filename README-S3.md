# 📦 Guide d'utilisation du S3 Storage

## 🎯 Vue d'ensemble

Ce projet utilise **Garage S3** pour le stockage des données. Le système détecte automatiquement votre environnement réseau pour optimiser les performances.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  S3 Fast (NVMe) - Stockage haute performance   │
├─────────────────────────────────────────────────┤
│  Endpoint local:  http://192.168.80.202:3910   │
│  Endpoint externe: https://s3fast.lafrance.io   │
│  Région: garage-fast                            │
│  Bucket: mangetamain                            │
└─────────────────────────────────────────────────┘
```

### 📍 Détection automatique du réseau

Le module `utils_s3.py` détecte automatiquement votre environnement :

- **Réseau local** (`192.168.80.x` ou `192.168.0.x`) → Utilise l'IP directe (ultra-rapide ⚡)
- **Réseau externe** → Utilise le reverse proxy HTTPS (sécurisé 🔒)

## 🚀 Démarrage rapide

### 1. Import simple

```python
from utils_s3 import get_s3_client

# Connexion automatique
client, bucket = get_s3_client()
```

### 2. Lister les fichiers

```python
response = client.list_objects_v2(Bucket=bucket)

for obj in response.get('Contents', []):
    print(f"📄 {obj['Key']} - {obj['Size']} bytes")
```

### 3. Télécharger un fichier

```python
# Télécharger un fichier spécifique
client.download_file(
    Bucket=bucket,
    Key='mangetamain.duckdb',
    Filename='data/mangetamain.duckdb'
)
```

### 4. Uploader un fichier

```python
# Uploader un fichier
client.upload_file(
    Filename='data/results.csv',
    Bucket=bucket,
    Key='results.csv'
)
```

### 5. Télécharger un dossier complet

```python
import os

# Télécharger tous les fichiers du bucket
response = client.list_objects_v2(Bucket=bucket)

for obj in response.get('Contents', []):
    local_path = f"data/{obj['Key']}"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    client.download_file(
        Bucket=bucket,
        Key=obj['Key'],
        Filename=local_path
    )
    print(f"✅ Téléchargé: {obj['Key']}")
```

## ⚙️ Options avancées

### Mode verbose

Pour voir les informations de connexion :

```python
client, bucket = get_s3_client(verbose=True)
# 🔗 S3 Endpoint: local (direct)
```

### Forcer l'endpoint externe

Utile pour tester ou contourner des problèmes réseau :

```python
client, bucket = get_s3_client(force_external=True)
```

### Utiliser un profil différent

Si vous avez plusieurs profils S3 configurés :

```python
client, bucket = get_s3_client(profile='autre_profil')
```

## 📊 Performances

| Environnement | Endpoint | Temps (1.4GB) | Débit |
|---------------|----------|---------------|-------|
| **VM locale** | Direct (3910) | ~2.7s | ~523 MB/s ⚡ |
| **VM via HTTPS** | Reverse proxy | ~13s | ~107 MB/s |
| **Hôte ixia** | Localhost | ~1.9s | ~718 MB/s 🚀 |

💡 **Astuce** : La détection automatique utilise toujours le mode le plus rapide disponible !

## 🔒 Sécurité

### Credentials

Les credentials sont stockés dans `../96_keys/credentials` (ignoré par git).

**Structure du fichier :**

```ini
[s3fast]
aws_access_key_id = GK4feb...
aws_secret_access_key = 50e63b...
endpoint_url = https://s3fast.lafrance.io
region = garage-fast
bucket = mangetamain
```

⚠️ **IMPORTANT** : Ne JAMAIS commit les credentials dans git !

### Vérifier le .gitignore

Le dossier `96_keys/` doit être dans `.gitignore` au niveau parent :

```bash
# Dans /home/dataia25/mangetamain/.gitignore
96_keys/
```

## 🛠️ Dépannage

### Problème de connexion

```python
# Tester la connexion
from utils_s3 import get_s3_client

try:
    client, bucket = get_s3_client(verbose=True)
    print(f"✅ Connexion réussie au bucket: {bucket}")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

### Vérifier le réseau

```python
from utils_s3 import is_on_local_network

if is_on_local_network():
    print("📍 Vous êtes sur le réseau local")
else:
    print("🌐 Vous êtes sur un réseau externe")
```

### Credentials introuvables

Si vous voyez l'erreur `Credentials introuvable`, vérifiez :

```bash
# Le fichier doit exister ici :
ls -la ../96_keys/credentials

# Si absent, contactez l'administrateur
```

## 📚 Exemples complets

### Exemple 1 : Charger la base DuckDB depuis S3

```python
from utils_s3 import get_s3_client
import duckdb

# Télécharger la base
client, bucket = get_s3_client()
client.download_file(bucket, 'mangetamain.duckdb', 'data/local.duckdb')

# Utiliser avec DuckDB
con = duckdb.connect('data/local.duckdb')
df = con.execute("SELECT * FROM recipes LIMIT 5").df()
print(df)
```

### Exemple 2 : Uploader les résultats d'une analyse

```python
from utils_s3 import get_s3_client
import pandas as pd

# Créer des résultats
results = pd.DataFrame({'metric': ['accuracy', 'f1'], 'value': [0.95, 0.89]})
results.to_csv('results.csv', index=False)

# Uploader sur S3
client, bucket = get_s3_client()
client.upload_file('results.csv', bucket, 'analysis/results.csv')
print("✅ Résultats uploadés sur S3")
```

### Exemple 3 : Synchroniser un dossier complet

```python
from utils_s3 import get_s3_client
import os
from pathlib import Path

client, bucket = get_s3_client(verbose=True)

# Créer le dossier local
local_dir = Path('data/s3_sync')
local_dir.mkdir(parents=True, exist_ok=True)

# Télécharger tous les fichiers
response = client.list_objects_v2(Bucket=bucket)

for obj in response.get('Contents', []):
    local_file = local_dir / obj['Key']
    local_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"⬇️  {obj['Key']}", end=' ... ')
    client.download_file(bucket, obj['Key'], str(local_file))
    print("✅")

print(f"\n🎉 {len(response.get('Contents', []))} fichiers synchronisés !")
```

## 📞 Support

Pour toute question ou problème :
- Vérifiez d'abord ce README
- Testez avec `verbose=True` pour plus d'informations
- Contactez l'équipe infrastructure pour les problèmes de credentials

---

**Dernière mise à jour** : 2025-10-08  
**Responsable** : Julien Lafrance
