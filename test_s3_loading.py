#!/usr/bin/env python3
"""Test du chargement des données depuis S3 avec DuckDB."""

import sys
import time
from pathlib import Path
import pandas as pd
import duckdb

# Ajouter le chemin vers 96_keys
sys.path.append(str(Path(__file__).parent / '96_keys'))

print("=" * 60)
print("TEST CHARGEMENT DEPUIS S3")
print("=" * 60)

# Charger les credentials
from load_credentials import load_s3_credentials

print("\n1. Chargement des credentials...")
creds = load_s3_credentials()
print(f"   ✅ Endpoint: {creds['endpoint_url']}")
print(f"   ✅ Bucket: {creds['bucket']}")

# Connexion DuckDB
print("\n2. Connexion DuckDB...")
conn = duckdb.connect()
conn.execute("INSTALL httpfs")
conn.execute("LOAD httpfs")

# Créer le secret S3
print("\n3. Configuration secret S3...")
conn.execute(f"""
    CREATE SECRET s3_secret (
        TYPE S3,
        KEY_ID '{creds['aws_access_key_id']}',
        SECRET '{creds['aws_secret_access_key']}',
        ENDPOINT '{creds['endpoint_url'].replace('http://', '')}',
        REGION '{creds['region_name']}',
        URL_STYLE 'path',
        USE_SSL false
    )
""")
print("   ✅ Secret configuré")

# Test 1: Compter les lignes
print("\n4. Test COUNT(*) sur les interactions...")
start = time.time()
try:
    count = conn.execute("""
        SELECT COUNT(*) as total
        FROM 's3://mangetamain/*.parquet'
    """).fetchone()[0]
    elapsed = time.time() - start
    print(f"   ✅ {count:,} lignes trouvées en {elapsed:.2f}s")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 2: Lire un échantillon
print("\n5. Test lecture échantillon (100 lignes)...")
start = time.time()
try:
    sample = conn.execute("""
        SELECT *
        FROM 's3://mangetamain/*.parquet'
        LIMIT 100
    """).fetchdf()
    elapsed = time.time() - start
    print(f"   ✅ {len(sample)} lignes lues en {elapsed:.2f}s")
    print(f"   ✅ Colonnes: {list(sample.columns)}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 3: Agrégation par recette (petit échantillon)
print("\n6. Test agrégation ratings par recette (top 1000)...")
start = time.time()
try:
    ratings_agg = conn.execute("""
        WITH top_recipes AS (
            SELECT recipe_id, COUNT(*) as cnt
            FROM 's3://mangetamain/*.parquet'
            GROUP BY recipe_id
            ORDER BY cnt DESC
            LIMIT 1000
        )
        SELECT
            r.recipe_id as id,
            AVG(r.rating) as rating,
            COUNT(*) as n_ratings,
            COUNT(DISTINCT r.user_id) as n_users
        FROM 's3://mangetamain/*.parquet' r
        WHERE r.recipe_id IN (SELECT recipe_id FROM top_recipes)
        GROUP BY r.recipe_id
    """).fetchdf()
    elapsed = time.time() - start
    print(f"   ✅ {len(ratings_agg)} recettes agrégées en {elapsed:.2f}s")
    print(f"   ✅ Exemple:")
    print(ratings_agg.head(3))
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 4: Agrégation complète (si rapide)
print("\n7. Test agrégation COMPLETE des ratings...")
start = time.time()
try:
    ratings_full = conn.execute("""
        SELECT
            recipe_id as id,
            AVG(rating) as rating,
            COUNT(*) as n_ratings,
            COUNT(DISTINCT user_id) as n_users
        FROM 's3://mangetamain/*.parquet'
        GROUP BY recipe_id
        LIMIT 10
    """).fetchdf()
    elapsed = time.time() - start
    print(f"   ✅ Agrégation de {len(ratings_full)} recettes en {elapsed:.2f}s")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

conn.close()
print("\n" + "=" * 60)
print("TEST TERMINÉ")
print("=" * 60)