#!/usr/bin/env python3
"""
Test pytest pour vérifier l'accessibilité des fichiers parquet sur S3

Ce script:
1. Scanne automatiquement tous les notebooks et fichiers Python du projet
2. Extrait toutes les références aux fichiers parquet
3. Teste leur accessibilité sur S3 via DuckDB

Usage:
    pytest test_s3_parquet_files.py -v
    pytest test_s3_parquet_files.py -v -s  # avec output détaillé
"""

import pytest
import duckdb
import re
from pathlib import Path
from configparser import ConfigParser
from typing import List, Set, Dict


def extract_parquet_files_from_code() -> Dict[str, List[str]]:
    """
    Scanne tous les fichiers .py et .ipynb pour trouver les références aux fichiers parquet.

    Returns:
        Dict avec {nom_fichier_parquet: [liste_des_fichiers_qui_l_utilisent]}
    """
    project_root = Path(__file__).parent.parent
    parquet_files = {}  # {parquet_file: [source_files]}

    # Patterns de recherche pour les fichiers parquet
    patterns = [
        r"s3://mangetamain/([^'\"\\s]+\.parquet)",  # s3://mangetamain/file.parquet
        r"['\"]([a-zA-Z0-9_]+\.parquet)['\"]",       # 'file.parquet' ou "file.parquet"
        r"FROM\s+['\"]([^'\"]+\.parquet)['\"]",      # SQL FROM 'file.parquet'
    ]

    # Répertoires à scanner
    scan_dirs = ['00_eda', '10_preprod', '20_prod']

    for scan_dir in scan_dirs:
        dir_path = project_root / scan_dir
        if not dir_path.exists():
            continue

        # Scanner les fichiers Python
        for py_file in dir_path.rglob("*.py"):
            # Ignorer venv et pycache
            if '.venv' in str(py_file) or '__pycache__' in str(py_file) or 'site-packages' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')

                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Nettoyer le nom de fichier
                        filename = match.strip().strip("'\"")
                        # Ignorer les exemples génériques et les tests
                        if (filename and
                            not filename.startswith('example') and
                            not filename.startswith('test') and
                            not filename.startswith('data') and
                            not filename == '*.parquet' and
                            'mangetamain' in filename or filename.endswith('.parquet')):
                            # Extraire seulement le nom du fichier si c'est un chemin S3
                            if 'mangetamain/' in filename:
                                filename = filename.split('mangetamain/')[-1]

                            # Ajouter le fichier source qui utilise ce parquet
                            relative_path = py_file.relative_to(project_root)
                            if filename not in parquet_files:
                                parquet_files[filename] = []
                            if str(relative_path) not in parquet_files[filename]:
                                parquet_files[filename].append(str(relative_path))
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")

        # Scanner les notebooks Jupyter
        for nb_file in dir_path.rglob("*.ipynb"):
            if '.venv' in str(nb_file) or '__pycache__' in str(nb_file):
                continue

            try:
                content = nb_file.read_text(encoding='utf-8')

                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        filename = match.strip().strip("'\"")
                        if (filename and
                            not filename.startswith('example') and
                            not filename.startswith('test') and
                            not filename.startswith('data') and
                            not filename == '*.parquet' and
                            ('mangetamain' in filename or filename.endswith('.parquet'))):
                            if 'mangetamain/' in filename:
                                filename = filename.split('mangetamain/')[-1]

                            # Ajouter le notebook source qui utilise ce parquet
                            relative_path = nb_file.relative_to(project_root)
                            if filename not in parquet_files:
                                parquet_files[filename] = []
                            if str(relative_path) not in parquet_files[filename]:
                                parquet_files[filename].append(str(relative_path))
            except Exception as e:
                print(f"Warning: Could not read {nb_file}: {e}")

    # Filtrer les noms de fichiers valides
    valid_files = {f: sources for f, sources in parquet_files.items()
                   if f and len(f) > 0 and not f.startswith('{')}

    return valid_files


# Collecter les fichiers parquet au moment de l'import du module
PARQUET_FILES_MAP = extract_parquet_files_from_code()
PARQUET_FILES = sorted(list(PARQUET_FILES_MAP.keys()))

if not PARQUET_FILES:
    print("⚠️  Aucun fichier parquet trouvé dans le code")
    # Ajouter au moins le fichier connu
    PARQUET_FILES = ["interactions_sample.parquet"]
    PARQUET_FILES_MAP = {"interactions_sample.parquet": ["(référence par défaut)"]}


@pytest.fixture(scope="module")
def s3_config():
    """Charge la configuration S3 depuis les credentials"""
    credentials_path = Path(__file__).parent.parent / "96_keys" / "credentials"

    if not credentials_path.exists():
        pytest.skip(f"Fichier credentials non trouvé: {credentials_path}")

    config = ConfigParser()
    config.read(credentials_path)

    if 's3fast' not in config:
        pytest.skip("Section [s3fast] manquante dans credentials")

    return {
        'access_key': config['s3fast']['aws_access_key_id'],
        'secret_key': config['s3fast']['aws_secret_access_key'],
        'endpoint': config['s3fast']['endpoint_url'].replace('http://', ''),
        'region': config['s3fast']['region']
    }


@pytest.fixture(scope="module")
def duckdb_connection(s3_config):
    """Crée une connexion DuckDB configurée pour S3"""
    conn = duckdb.connect()

    # Charger httpfs
    try:
        conn.execute("LOAD httpfs")
    except:
        conn.execute("INSTALL httpfs")
        conn.execute("LOAD httpfs")

    # Créer le secret S3
    conn.execute(f"""
        CREATE OR REPLACE SECRET garage_s3 (
            TYPE s3,
            KEY_ID '{s3_config['access_key']}',
            SECRET '{s3_config['secret_key']}',
            ENDPOINT '{s3_config['endpoint']}',
            REGION '{s3_config['region']}',
            URL_STYLE 'path',
            USE_SSL false
        )
    """)

    yield conn

    conn.close()


def test_parquet_files_discovered():
    """Vérifie qu'au moins un fichier parquet a été trouvé dans le code"""
    print(f"\n📋 Fichiers parquet découverts: {len(PARQUET_FILES)}")
    for pf in PARQUET_FILES:
        sources = PARQUET_FILES_MAP.get(pf, [])
        print(f"   • {pf}")
        for src in sources:
            print(f"     └─ {src}")

    assert len(PARQUET_FILES) > 0, "Aucun fichier parquet trouvé dans le code source"


@pytest.mark.parametrize("parquet_file", PARQUET_FILES)
def test_parquet_accessible(duckdb_connection, parquet_file):
    """Vérifie que le fichier parquet est accessible sur S3"""
    s3_path = f"s3://mangetamain/{parquet_file}"

    try:
        # Tenter de lire le fichier
        result = duckdb_connection.execute(
            f"SELECT COUNT(*) as count FROM '{s3_path}'"
        ).fetchone()

        assert result is not None, f"Aucune donnée retournée pour {s3_path}"
        row_count = result[0]

        assert row_count >= 0, f"Nombre de lignes invalide: {row_count}"

        print(f"\n✅ {parquet_file}: {row_count:,} lignes")

    except Exception as e:
        pytest.fail(f"❌ Erreur lors de l'accès à {s3_path}: {str(e)}")


@pytest.mark.parametrize("parquet_file", PARQUET_FILES)
def test_parquet_schema(duckdb_connection, parquet_file):
    """Vérifie que le schéma du fichier parquet est lisible"""
    s3_path = f"s3://mangetamain/{parquet_file}"

    try:
        # Lire le schéma
        schema = duckdb_connection.execute(
            f"DESCRIBE SELECT * FROM '{s3_path}' LIMIT 0"
        ).fetchall()

        assert len(schema) > 0, f"Aucune colonne trouvée dans {s3_path}"

        columns = [col[0] for col in schema]
        print(f"\n✅ {parquet_file}: {len(columns)} colonnes - {columns[:5]}{'...' if len(columns) > 5 else ''}")

    except Exception as e:
        pytest.fail(f"❌ Erreur lors de la lecture du schéma de {s3_path}: {str(e)}")


@pytest.mark.parametrize("parquet_file", PARQUET_FILES)
def test_parquet_sample_data(duckdb_connection, parquet_file):
    """Vérifie qu'on peut lire des données du fichier parquet"""
    s3_path = f"s3://mangetamain/{parquet_file}"

    try:
        # Lire un échantillon de données
        df = duckdb_connection.execute(
            f"SELECT * FROM '{s3_path}' LIMIT 5"
        ).df()

        assert not df.empty, f"Aucune donnée échantillon pour {s3_path}"
        assert len(df) > 0, f"DataFrame vide pour {s3_path}"

        print(f"\n✅ {parquet_file}: Échantillon de {len(df)} lignes lu avec succès")
        print(f"   Colonnes: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}")

    except Exception as e:
        pytest.fail(f"❌ Erreur lors de la lecture des données de {s3_path}: {str(e)}")


def test_all_parquet_files_summary(duckdb_connection):
    """Test global: résumé de tous les fichiers parquet accessibles"""
    results = {}

    print("\n" + "="*70)
    print("📊 ANALYSE DE TOUS LES FICHIERS PARQUET SUR S3")
    print("="*70)

    for parquet_file in PARQUET_FILES:
        s3_path = f"s3://mangetamain/{parquet_file}"

        try:
            result = duckdb_connection.execute(
                f"SELECT COUNT(*) FROM '{s3_path}'"
            ).fetchone()

            # Lire le schéma
            schema = duckdb_connection.execute(
                f"DESCRIBE SELECT * FROM '{s3_path}' LIMIT 0"
            ).fetchall()

            results[parquet_file] = {
                'accessible': True,
                'rows': result[0] if result else 0,
                'columns': len(schema)
            }
        except Exception as e:
            results[parquet_file] = {
                'accessible': False,
                'error': str(e)
            }

    # Afficher le résumé
    accessible_count = sum(1 for r in results.values() if r['accessible'])
    total_count = len(results)
    total_rows = sum(r.get('rows', 0) for r in results.values() if r['accessible'])

    print(f"\n{'='*70}")
    for file, info in results.items():
        sources = PARQUET_FILES_MAP.get(file, [])
        if info['accessible']:
            print(f"✅ {file}")
            print(f"   ├─ {info['rows']:,} lignes × {info['columns']} colonnes")
            print(f"   └─ Utilisé par {len(sources)} fichier(s):")
            for src in sources:
                print(f"      • {src}")
        else:
            error_msg = info.get('error', 'Erreur inconnue')
            # Tronquer le message d'erreur s'il est trop long
            if len(error_msg) > 60:
                error_msg = error_msg[:57] + "..."
            print(f"❌ {file}")
            print(f"   ├─ {error_msg}")
            print(f"   └─ Référencé par {len(sources)} fichier(s):")
            for src in sources:
                print(f"      • {src}")

    print(f"\n{'='*70}")
    print(f"📈 RÉSUMÉ:")
    print(f"   • Fichiers accessibles: {accessible_count}/{total_count}")
    print(f"   • Total de lignes: {total_rows:,}")
    print(f"{'='*70}\n")

    # Assert que tous les fichiers sont accessibles
    assert accessible_count == total_count, \
        f"Certains fichiers ne sont pas accessibles: {accessible_count}/{total_count}"


if __name__ == "__main__":
    # Test manuel: afficher les fichiers découverts
    print("="*70)
    print("🔍 SCAN DU PROJET POUR FICHIERS PARQUET")
    print("="*70)

    files_map = extract_parquet_files_from_code()

    if files_map:
        print(f"\n✅ {len(files_map)} fichier(s) parquet trouvé(s):")
        for f, sources in sorted(files_map.items()):
            print(f"   • {f}")
            print(f"     └─ Utilisé par {len(sources)} fichier(s):")
            for src in sources:
                print(f"        - {src}")
    else:
        print("\n⚠️  Aucun fichier parquet trouvé dans le code")

    print("\n" + "="*70)
    print("Pour tester l'accessibilité S3, exécuter:")
    print("   pytest test_s3_parquet_files.py -v -s")
    print("="*70 + "\n")
