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

Le module `utils/utils_s3.py` détecte automatiquement votre environnement :

- **Réseau local** (`192.168.80.x` ou `192.168.0.x`) → Utilise l'IP directe (ultra-rapide ⚡)
- **Réseau externe** → Utilise le reverse proxy HTTPS (sécurisé 🔒)

## 🚀 Démarrage rapide

### Import du module

Le module `utils/` est présent dans chaque sous-projet (00_eda, 10_preprod, 20_prod) :

```python
# Import direct depuis le même dossier
from utils.utils_s3 import get_s3_client, get_duckdb_s3_connection
```

### 1. Connexion S3 classique

```python
from utils.utils_s3 import get_s3_client

# Connexion automatique
client, bucket = get_s3_client()

# Lister les fichiers
response = client.list_objects_v2(Bucket=bucket)
for obj in response.get('Contents', []):
    print(f"📄 {obj['Key']} - {obj['Size']} bytes")
```

### 2. Télécharger un fichier

```python
# Télécharger un fichier spécifique
client.download_file(
    Bucket=bucket,
    Key='mangetamain.duckdb',
    Filename='data/mangetamain.duckdb'
)
```

### 3. Uploader un fichier

```python
# Uploader un fichier
client.upload_file(
    Filename='data/results.csv',
    Bucket=bucket,
    Key='results/analysis_results.csv'
)
```

## 🦆 DuckDB avec S3 (Recommandé)

### Connexion directe (sans téléchargement !)

```python
from utils.utils_s3 import get_duckdb_s3_connection

# Connexion DuckDB avec S3 configuré automatiquement
con, bucket = get_duckdb_s3_connection()
```

### Query directe sur fichier CSV S3

```python
# Lire directement depuis S3 - AUCUN téléchargement !
df = con.execute(f"SELECT * FROM 's3://{bucket}/PP_recipes.csv' LIMIT 5").df()
print(df)
```

### Agrégations SQL complexes

```python
# Analyse directe sur S3 sans téléchargement
query = f"""
SELECT 
    calorie_level,
    COUNT(*) as nb_recipes,
    COUNT(DISTINCT id) as unique_recipes
FROM 's3://{bucket}/PP_recipes.csv'
GROUP BY calorie_level
ORDER BY calorie_level
"""

df = con.execute(query).df()
print(df)
```

**Résultat :**
```
 calorie_level  nb_recipes  unique_recipes
             0       69699           69699
             1       63255           63255
             2       45311           45311
```

## 🐳 Utilisation dans Docker

Les containers Docker accèdent aux credentials via un **volume read-only** :

```yaml
volumes:
  - ../96_keys:/app/../96_keys:ro       # Credentials (read-only)
  - ../10_preprod/utils:/app/utils:ro   # Module utils_s3
```

### Test dans un container

```bash
# Tester S3 dans preprod
docker exec -w /app mange_preprod uv run python -c "
from utils.utils_s3 import get_s3_client
client, bucket = get_s3_client(verbose=True)
print(f'✅ {bucket}')
"

# Tester DuckDB dans prod
docker exec -w /app mange_prod uv run python -c "
from utils.utils_s3 import get_duckdb_s3_connection
con, bucket = get_duckdb_s3_connection()
df = con.execute(f'SELECT COUNT(*) as total FROM s3://{bucket}/PP_recipes.csv').df()
print(df)
"
```

### Démarrage des containers

```bash
cd 30_docker

# Preprod (port 8500)
docker-compose -p mangetamain-preprod -f docker-compose-preprod.yml up -d

# Prod (port 8501)
docker-compose -p mangetamain-prod -f docker-compose-prod.yml up -d
```

Voir [README_DOCKER_S3.md](README_DOCKER_S3.md) pour plus de détails sur Docker.

## ⚙️ Options avancées

### Mode verbose

Pour voir les informations de connexion :

```python
client, bucket = get_s3_client(verbose=True)
# 📁 Credentials chargés depuis fichier local
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
| **Docker** | HTTPS externe | ~13s | ~107 MB/s |

💡 **Astuce** : La détection automatique utilise toujours le mode le plus rapide disponible !

## 🔒 Sécurité

### Credentials

Les credentials sont stockés dans `96_keys/credentials` (ignoré par git).

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

Le dossier `96_keys/` doit être dans `.gitignore` :

```bash
# Dans /home/dataia25/mangetamain/.gitignore
96_keys/
```

### Chargement des credentials

Le module `utils_s3.py` charge les credentials dans cet ordre :

1. **Variables d'environnement** (prioritaire, pour production distante)
   - `S3_ACCESS_KEY_ID`
   - `S3_SECRET_ACCESS_KEY`
   - `S3_BUCKET`
   - `S3_REGION` (optionnel)
   - `S3_ENDPOINT_URL` (optionnel)

2. **Fichier credentials** (pour développement local et Docker)
   - Chemin : `../96_keys/credentials`
   - Format : INI avec section `[s3fast]`

## 🛠️ Dépannage

### Problème de connexion

```python
# Tester la connexion
from utils.utils_s3 import get_s3_client

try:
    client, bucket = get_s3_client(verbose=True)
    print(f"✅ Connexion réussie au bucket: {bucket}")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

### Vérifier le réseau

```python
from utils.utils_s3 import is_on_local_network

if is_on_local_network():
    print("📍 Vous êtes sur le réseau local")
else:
    print("🌐 Vous êtes sur un réseau externe")
```

### Credentials introuvables

Si vous voyez l'erreur `Credentials introuvable`, vérifiez :

```bash
# Le fichier doit exister ici :
ls -la 96_keys/credentials

# Si absent, contactez l'administrateur
```

### Test complet dans uv

```bash
cd 10_preprod
uv run python -c "
from utils.utils_s3 import get_s3_client, get_duckdb_s3_connection

# Test S3
client, bucket = get_s3_client(verbose=True)
print(f'✅ S3 : {bucket}')

# Test DuckDB
con, bucket = get_duckdb_s3_connection()
df = con.execute(f'SELECT COUNT(*) FROM s3://{bucket}/PP_recipes.csv').df()
print(f'✅ DuckDB : {df.iloc[0,0]} recettes')
"
```

## 📚 Exemples complets

### Exemple 1 : Analyse DuckDB sur CSV S3

```python
from utils.utils_s3 import get_duckdb_s3_connection

# Connexion directe S3
con, bucket = get_duckdb_s3_connection()

# Analyse directe sans téléchargement
query = f"""
SELECT 
    calorie_level,
    COUNT(*) as recipes_count,
    COUNT(DISTINCT id) as unique_recipes
FROM 's3://{bucket}/PP_recipes.csv'
GROUP BY calorie_level
ORDER BY recipes_count DESC
"""

df = con.execute(query).df()
print("📊 Analyse des recettes par niveau calorique:")
print(df)
```

### Exemple 2 : Comparaison de fichiers S3

```python
# Comparer deux datasets directement sur S3
query = f"""
SELECT 
    'recipes' as source,
    COUNT(*) as count
FROM 's3://{bucket}/PP_recipes.csv'

UNION ALL

SELECT 
    'interactions' as source,
    COUNT(*) as count
FROM 's3://{bucket}/PP_user_interactions.csv'
"""

df = con.execute(query).df()
print("📈 Comparaison des datasets:")
print(df)
```

### Exemple 3 : Export de résultats vers S3

```python
from utils.utils_s3 import get_s3_client, get_duckdb_s3_connection
import pandas as pd

# Analyse avec DuckDB
con, bucket = get_duckdb_s3_connection()
df_results = con.execute(f"SELECT * FROM 's3://{bucket}/PP_recipes.csv' LIMIT 100").df()

# Sauvegarder localement
df_results.to_csv('analysis_results.csv', index=False)

# Upload vers S3
client, bucket = get_s3_client()
client.upload_file('analysis_results.csv', bucket, 'results/analysis_results.csv')
print("✅ Résultats uploadés sur S3")
```

## 📦 Structure du projet

```
mangetamain/
├── 96_keys/                    ← Credentials (ignoré par git)
│   └── credentials
├── utils/                      ← Module partagé (référence)
│   ├── __init__.py
│   └── utils_s3.py
├── 00_eda/
│   └── utils/                  ← Copie locale
├── 10_preprod/
│   └── utils/                  ← Copie locale
├── 20_prod/
│   └── utils/                  ← Copie locale
└── 30_docker/
    ├── docker-compose-preprod.yml
    └── docker-compose-prod.yml
```

**Note** : Le dossier `utils/` est copié dans chaque sous-projet pour faciliter le déploiement Docker.

## 📞 Support

Pour toute question ou problème :
- Vérifiez d'abord ce README
- Testez avec `verbose=True` pour plus d'informations
- Consultez [README_DOCKER_S3.md](README_DOCKER_S3.md) pour Docker
- Contactez l'équipe infrastructure pour les problèmes de credentials

---

**Dernière mise à jour** : 2025-10-08  
**Responsable** : Infrastructure Team  
**Tests** : ✅ Validé sur preprod et prod Docker
