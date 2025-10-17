# 🐳 Configuration S3 pour Docker

## 📋 Résumé

Les containers Docker accèdent aux credentials S3 via un **volume read-only** qui monte le dossier `96_keys/`.

## ✅ Avantages de cette approche

1. **Sécurisé** : Le dossier `96_keys/` reste sur l'hôte, pas dans l'image Docker
2. **Read-only** : Les containers ne peuvent PAS modifier les credentials
3. **Simple** : Pas de gestion de variables d'environnement
4. **Unifié** : Même méthode en dev et en production

## 🔧 Configuration dans docker-compose

Les deux fichiers sont déjà configurés :
- `30_docker/docker-compose-preprod.yml`
- `30_docker/docker-compose-prod.yml`

Ligne ajoutée dans les volumes :
```yaml
volumes:
  - ../96_keys:/app/../96_keys:ro  # Monter les credentials en READ-ONLY
  - ../10_preprod/utils:/app/utils:ro  # Module utils avec get_s3_client()
```

## 📦 Structure dans le container

```
/app/                           ← working_dir
├── src/                        ← Code de l'application
├── utils/                      ← Module utils_s3.py
│   ├── __init__.py
│   └── utils_s3.py
└── ../96_keys/                 ← Credentials (montés en read-only)
    └── credentials
```

## 🚀 Utilisation dans le code

Dans vos scripts Python (Streamlit, etc.) :

```python
from utils.utils_s3 import get_s3_client, get_duckdb_s3_connection

# Connexion S3
client, bucket = get_s3_client()

# Ou connexion DuckDB avec S3
con, bucket = get_duckdb_s3_connection()
df = con.execute(f"SELECT * FROM 's3://{bucket}/PP_recipes.csv' LIMIT 5").df()
```

Le module `utils_s3.py` :
1. ✅ Cherche d'abord les variables d'environnement (si vous décidez de les utiliser plus tard)
2. ✅ Sinon charge depuis `../96_keys/credentials` (fonctionne en dev ET en Docker)

## 🔒 Sécurité

- ✅ `96_keys/` ignoré par git (`.gitignore`)
- ✅ Monté en read-only dans Docker (`:ro`)
- ✅ Accessible uniquement depuis l'hôte
- ✅ Pas de credentials dans le code source
- ✅ Pas de credentials dans les variables d'environnement visibles

## 🧪 Test

Pour vérifier que le module utils fonctionne dans Docker :

```bash
# Démarrer le container
cd 30_docker
docker-compose -f docker-compose-preprod.yml up -d

# Vérifier les logs
docker logs mange_preprod

# Tester l'accès S3 depuis le container
docker exec mange_preprod python3 -c "
from utils.utils_s3 import get_s3_client
client, bucket = get_s3_client(verbose=True)
print(f'✅ Connexion S3 OK : {bucket}')
"
```

## 🔄 Redémarrage des containers

Si les containers tournent déjà, redémarrez-les pour prendre en compte les nouveaux volumes :

```bash
cd 30_docker

# Preprod
docker-compose -f docker-compose-preprod.yml down
docker-compose -f docker-compose-preprod.yml up -d

# Prod
docker-compose -f docker-compose-prod.yml down
docker-compose -f docker-compose-prod.yml up -d
```

---

**Dernière mise à jour** : 2025-10-08
