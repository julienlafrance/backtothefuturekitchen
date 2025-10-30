# 🦆 Guide DuckDB + S3 Garage - Configuration complète

## 📋 Vue d'ensemble

Ce guide décrit la configuration optimale pour utiliser DuckDB avec votre stockage S3 Garage, avec deux approches :
1. **Bases DuckDB avec secrets** (pour requêtes SQL)
2. **Profils AWS boto3** (pour gestion fichiers)

---

## 🏗️ Architecture S3

### Endpoints disponibles

| Type | URL | Protocole | Performance | Usage |
|------|-----|-----------|-------------|-------|
| **Local** | `192.168.80.202:3910` | HTTP | 991 MB/s ⚡ | Réseau LAN |
| **Externe** | `s3fast.lafrance.io` | HTTPS | 111 MB/s | Internet |

**Bucket** : `mangetamain` (1.4 GB, 10 fichiers)

### Credentials

```
Access Key: GK4febbfbbce789dbbe85f1bad
Secret Key: 50e63b5146a4298f2f79a7e0fe5d5b602b4ef26434c6c5c72d017b85d2d61321
Région: garage-fast
```

---

## 🎯 Solution 1 : Bases DuckDB avec secrets (Recommandé)

### Installation (une seule fois)

```bash
cd ~/mangetamain/96_keys

# Base locale (réseau LAN)
duckdb garage_local.duckdb
```

Puis dans DuckDB :
```sql
INSTALL httpfs;
LOAD httpfs;
CREATE SECRET garage_s3 (
    TYPE s3,
    KEY_ID 'GK4febbfbbce789dbbe85f1bad',
    SECRET '50e63b5146a4298f2f79a7e0fe5d5b602b4ef26434c6c5c72d017b85d2d61321',
    ENDPOINT '192.168.80.202:3910',
    REGION 'garage',
    URL_STYLE 'path',
    USE_SSL false
);
.quit
```

Faire de même pour `garage_external.duckdb` avec `ENDPOINT 's3fast.lafrance.io'` et `USE_SSL true`.

### Utilisation CLI

```bash
# Local (réseau LAN - ultra rapide)
duckdb ~/mangetamain/96_keys/garage_local.duckdb -c "SELECT COUNT(*) FROM 's3://mangetamain/PP_recipes.csv'"

# Externe (internet)
duckdb ~/mangetamain/96_keys/garage_external.duckdb -c "SELECT * FROM 's3://mangetamain/PP_recipes.csv' LIMIT 5"
```

### Utilisation Python

```python
import duckdb
from pathlib import Path

# Chemin vers la base avec secret
keys_dir = Path(__file__).parent.parent / '96_keys'
db_file = keys_dir / 'garage_local.duckdb'

# Connexion
conn = duckdb.connect(str(db_file))

# Requête directe sur S3
df = conn.sql("SELECT * FROM 's3://mangetamain/PP_recipes.csv' LIMIT 10").df()
print(df)
```

---

## 📊 Performances mesurées

### Download 195 MB (PP_recipes.csv)

| Endpoint | Temps | Vitesse | Ratio |
|----------|-------|---------|-------|
| Local HTTP | **0.20s** | 991 MB/s ⚡ | 1x |
| Reverse proxy HTTPS | 1.86s | 105 MB/s | 9.4x plus lent |

### Download 581 MB (mangetamain.duckdb)

| Endpoint | Temps | Vitesse | Ratio |
|----------|-------|---------|-------|
| Local HTTP | **0.90s** | 646 MB/s ⚡ | 1x |
| Reverse proxy HTTPS | 5.25s | 111 MB/s | 5.8x plus lent |

### Conclusion

**Le reverse proxy fonctionne** mais l'overhead HTTPS ralentit significativement :
- HTTPS : ~110 MB/s (acceptable)
- HTTP local : ~650-990 MB/s (optimal)

💡 **Recommandation** : Gardez la détection réseau pour profiter des performances locales !

---

## 🔄 Helper Python avec détection automatique

Créer `utils/garage_helper.py` :

```python
import socket
import duckdb
import boto3
from pathlib import Path

def is_local_network():
    """Détecte si on est sur le réseau local"""
    try:
        socket.create_connection(('192.168.80.202', 3910), timeout=0.5)
        return True
    except:
        return False

def get_duckdb():
    """Connexion DuckDB avec détection auto"""
    keys_dir = Path(__file__).parent.parent / '96_keys'
    db = 'garage_local.duckdb' if is_local_network() else 'garage_external.duckdb'
    return duckdb.connect(str(keys_dir / db))

def get_s3():
    """Client boto3 avec détection auto"""
    keys_dir = Path(__file__).parent.parent / '96_keys'
    profile = 'garage-local' if is_local_network() else 'garage-external'
    
    session = boto3.Session(
        profile_name=profile,
        aws_credentials_file=str(keys_dir / 'aws_credentials'),
        aws_config_file=str(keys_dir / 'aws_config')
    )
    return session.client('s3')
```

### Utilisation

```python
from utils.garage_helper import get_duckdb, get_s3

# DuckDB - requêtes SQL
conn = get_duckdb()
df = conn.sql("SELECT * FROM 's3://mangetamain/PP_recipes.csv' LIMIT 5").df()

# boto3 - gestion fichiers
s3 = get_s3()
s3.download_file('mangetamain', 'file.pkl', '/tmp/file.pkl')
```

---

## 🔧 Optimisation reverse proxy

Pour améliorer les performances HTTPS, configurez nginx :

```nginx
server {
    listen 443 ssl http2;
    server_name s3fast.lafrance.io;
    
    ssl_protocols TLSv1.3;
    ssl_session_cache shared:SSL:10m;
    
    location / {
        proxy_pass http://192.168.80.202:3910;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_http_version 1.1;
    }
}
```

Option HTTP (port 80) pour performances maximales :

```nginx
server {
    listen 80;
    server_name s3fast.lafrance.io;
    
    location / {
        proxy_pass http://192.168.80.202:3910;
        proxy_buffering off;
    }
}
```

---

## 🎯 Résumé des bonnes pratiques

1. ✅ **DuckDB** : Utilisez les bases avec secrets (zéro config après setup)
2. ✅ **boto3** : Utilisez les profils AWS (standard, portable)
3. ✅ **Détection réseau** : Helper de 10 lignes pour auto-switch
4. ✅ **Docker** : Mêmes chemins relatifs → code identique hôte/Docker
5. ✅ **Performance** : Détection réseau = 5-10x plus rapide en local
6. ✅ **Sécurité** : Tout dans `96_keys/` ignoré par git

---

**Dernière mise à jour** : 2025-10-09  
**Responsable** : Julien Lafrance  
**Performance validée** : ✅ Local 991 MB/s | Externe 111 MB/s
