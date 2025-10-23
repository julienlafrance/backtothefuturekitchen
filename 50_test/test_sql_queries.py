#!/usr/bin/env python3
"""
Test pytest pour vérifier toutes les requêtes SQL du projet

Ce script:
1. Scanne automatiquement tous les fichiers Python et notebooks
2. Extrait toutes les requêtes SQL (DuckDB, S3, tables locales)
3. Teste leur validité et exécution

Usage:
    pytest test_sql_queries.py -v
    pytest test_sql_queries.py -v -s  # avec output détaillé
"""

import pytest
import duckdb
import re
from pathlib import Path
from configparser import ConfigParser
from typing import Dict, List, Tuple


def clean_sql_query(query: str, context: str = "") -> tuple[str, bool]:
    """
    Nettoie et valide une requête SQL extraite.

    Returns:
        (cleaned_query, is_valid)
    """
    # Supprimer le code Python après la requête
    # Chercher des patterns Python communs
    python_patterns = [
        r'\)\s*#',  # Commentaire Python
        r'\)\s*def\s+',  # Définition de fonction
        r'\)\s*return\s+',  # Return statement
        r'\)\s*with\s+',  # With statement
        r'\)\s*if\s+',  # If statement
        r'"\s*if\s+',  # Fin de string avec if
    ]

    for pattern in python_patterns:
        match = re.search(pattern, query)
        if match:
            query = query[:match.start()].strip()
            break

    # Vérifier si la requête contient des templates non résolus
    has_templates = bool(re.search(r'\{[^}]+\}', query))

    # Vérifier si c'est une vraie requête SQL complète
    has_select = 'SELECT' in query.upper()
    has_from = 'FROM' in query.upper()
    is_complete = has_select and has_from and not has_templates

    # Nettoyer les espaces multiples
    query = re.sub(r'\s+', ' ', query).strip()

    return query, is_complete


def extract_sql_queries_from_code() -> Dict[str, List[Dict]]:
    """
    Scanne tous les fichiers .py et .ipynb pour trouver les requêtes SQL.

    Returns:
        Dict avec {fichier_source: [{"query": sql, "line": num, "context": str, "is_complete": bool}]}
    """
    project_root = Path(__file__).parent.parent
    sql_queries = {}

    # Patterns améliorés pour détecter UNIQUEMENT les requêtes SQL complètes
    patterns = [
        # Requêtes SQL dans conn.execute() avec triple quotes (plus précis)
        (r'conn\.execute\(\s*f?"""[\s]*(SELECT[\s\S]+?FROM[\s\S]+?)[\s]*"""\s*\)', "conn.execute triple quotes"),
        (r'conn\.execute\(\s*f?\'\'\'[\s]*(SELECT[\s\S]+?FROM[\s\S]+?)[\s]*\'\'\'\s*\)', "conn.execute triple quotes"),

        # Variables SQL avec triple quotes
        (r'(?:sql|query|QUERY)\s*=\s*f?"""[\s]*(SELECT[\s\S]+?FROM[\s\S]+?)[\s]*"""', "variable triple quotes"),
        (r'(?:sql|query|QUERY)\s*=\s*f?\'\'\'[\s]*(SELECT[\s\S]+?FROM[\s\S]+?)[\s]*\'\'\'', "variable triple quotes"),

        # Requêtes SQL sur une seule ligne
        (r'conn\.execute\(\s*f?["\']+(SELECT\s+.+?\s+FROM\s+.+?)["\']', "conn.execute single line"),
        (r'(?:sql|query|QUERY)\s*=\s*f?["\']+(SELECT\s+.+?\s+FROM\s+.+?)["\']', "variable single line"),
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
                lines = content.split('\n')
                relative_path = str(py_file.relative_to(project_root))

                for pattern, pattern_type in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                    for match in matches:
                        raw_query = match.group(1).strip()

                        # Trouver le numéro de ligne
                        line_num = content[:match.start()].count('\n') + 1

                        # Contexte: quelques lignes avant
                        context_start = max(0, line_num - 3)
                        context = '\n'.join(lines[context_start:line_num])

                        # Nettoyer et valider la requête
                        cleaned_query, is_complete = clean_sql_query(raw_query, context)

                        # Ignorer les exemples/tests génériques
                        if ('iris' in cleaned_query.lower() or
                            'example' in cleaned_query.lower() or
                            ('test' in cleaned_query.lower() and 'interactions_test' not in cleaned_query.lower())):
                            continue

                        # Ignorer les requêtes trop courtes (probablement mal extraites)
                        if len(cleaned_query) < 20:
                            continue

                        if relative_path not in sql_queries:
                            sql_queries[relative_path] = []

                        sql_queries[relative_path].append({
                            'query': cleaned_query,
                            'line': line_num,
                            'type': pattern_type,
                            'context': context[-150:] if len(context) > 150 else context,
                            'is_complete': is_complete,
                            'raw_query': raw_query[:100]  # Pour debug
                        })

            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")

        # Scanner les notebooks Jupyter
        for nb_file in dir_path.rglob("*.ipynb"):
            if '.venv' in str(nb_file) or '__pycache__' in str(nb_file):
                continue

            try:
                content = nb_file.read_text(encoding='utf-8')
                relative_path = str(nb_file.relative_to(project_root))

                # Pour les notebooks, on cherche dans le JSON
                for pattern, pattern_type in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                    for match in matches:
                        raw_query = match.group(1).strip()
                        cleaned_query, is_complete = clean_sql_query(raw_query)

                        if ('iris' in cleaned_query.lower() or
                            'example' in cleaned_query.lower() or
                            ('test' in cleaned_query.lower() and 'interactions_test' not in cleaned_query.lower())):
                            continue

                        if len(cleaned_query) < 20:
                            continue

                        if relative_path not in sql_queries:
                            sql_queries[relative_path] = []

                        sql_queries[relative_path].append({
                            'query': cleaned_query,
                            'line': -1,  # Difficile de déterminer dans un notebook
                            'type': f"notebook {pattern_type}",
                            'context': '',
                            'is_complete': is_complete,
                            'raw_query': raw_query[:100]
                        })

            except Exception as e:
                print(f"Warning: Could not read {nb_file}: {e}")

    return sql_queries


# Collecter les requêtes SQL au moment de l'import
SQL_QUERIES_MAP = extract_sql_queries_from_code()

# Créer une liste plate pour pytest.parametrize - SEULEMENT les requêtes complètes
SQL_QUERIES_LIST = []
SQL_QUERIES_ALL = []  # Toutes les requêtes (pour statistiques)

for source_file, queries in SQL_QUERIES_MAP.items():
    for idx, query_info in enumerate(queries):
        query_dict = {
            'id': f"{source_file}:{query_info['line']}:query{idx}",
            'source': source_file,
            'line': query_info['line'],
            'query': query_info['query'],
            'type': query_info['type'],
            'is_complete': query_info.get('is_complete', False)
        }

        SQL_QUERIES_ALL.append(query_dict)

        # Ajouter uniquement les requêtes complètes pour les tests
        if query_info.get('is_complete', False):
            SQL_QUERIES_LIST.append(query_dict)

if not SQL_QUERIES_LIST:
    print("⚠️  Aucune requête SQL trouvée dans le code")


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
    """Crée une connexion DuckDB configurée pour S3 et la base locale"""
    # Connexion à la base locale si elle existe
    db_path = Path(__file__).parent.parent / "10_preprod" / "data" / "mangetamain.duckdb"

    if db_path.exists():
        conn = duckdb.connect(str(db_path), read_only=True)
    else:
        conn = duckdb.connect()

    # Charger httpfs pour S3
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


def test_sql_queries_discovered():
    """Vérifie qu'au moins une requête SQL a été trouvée"""
    total_all = len(SQL_QUERIES_ALL)
    total_complete = len(SQL_QUERIES_LIST)
    total_incomplete = total_all - total_complete

    print(f"\n📋 Requêtes SQL découvertes:")
    print(f"   • Total: {total_all}")
    print(f"   • Complètes (testables): {total_complete}")
    print(f"   • Incomplètes (templates): {total_incomplete}")

    # Grouper par fichier source (seulement complètes)
    by_source = {}
    for q in SQL_QUERIES_LIST:
        source = q['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(q)

    print(f"\n📄 Requêtes testables par fichier:")
    for source, queries in sorted(by_source.items()):
        print(f"\n   {source}")
        for q in queries:
            line_info = f"ligne {q['line']}" if q['line'] > 0 else "notebook"
            query_preview = q['query'][:80] + "..." if len(q['query']) > 80 else q['query']
            print(f"      └─ {line_info}: {query_preview}")

    assert len(SQL_QUERIES_LIST) > 0, "Aucune requête SQL testable trouvée dans le code"


@pytest.mark.parametrize("query_info", SQL_QUERIES_LIST, ids=lambda q: q['id'])
def test_sql_query_valid_syntax(duckdb_connection, query_info):
    """Vérifie que la syntaxe SQL est valide (EXPLAIN)"""
    query = query_info['query']
    source = query_info['source']
    line = query_info['line']

    try:
        # Utiliser EXPLAIN pour vérifier la syntaxe sans exécuter
        duckdb_connection.execute(f"EXPLAIN {query}")

        print(f"\n✅ Syntaxe SQL valide")
        print(f"   Source: {source}:{line}")
        print(f"   Query: {query[:100]}...")

    except Exception as e:
        error_msg = str(e)[:200]
        pytest.fail(f"❌ Syntaxe SQL invalide dans {source}:{line}\n   Query: {query}\n   Erreur: {error_msg}")


@pytest.mark.parametrize("query_info", SQL_QUERIES_LIST, ids=lambda q: q['id'])
def test_sql_query_executable(duckdb_connection, query_info):
    """Vérifie que la requête SQL peut s'exécuter (avec LIMIT 1)"""
    query = query_info['query']
    source = query_info['source']
    line = query_info['line']

    # Ajouter LIMIT 1 si pas déjà présent pour accélérer les tests
    if 'LIMIT' not in query.upper():
        # LIMIT doit être APRÈS ORDER BY
        test_query = f"{query} LIMIT 1"
    else:
        test_query = query

    try:
        result = duckdb_connection.execute(test_query).fetchall()

        print(f"\n✅ Requête exécutée avec succès")
        print(f"   Source: {source}:{line}")
        print(f"   Résultat: {len(result)} ligne(s)")

    except Exception as e:
        error_msg = str(e)[:300]
        pytest.fail(f"❌ Erreur d'exécution dans {source}:{line}\n   Query: {query}\n   Erreur: {error_msg}")


def test_sql_queries_summary(duckdb_connection):
    """Résumé de toutes les requêtes SQL testées"""
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DES REQUÊTES SQL")
    print("="*70)

    # Grouper par fichier
    by_source = {}
    for q in SQL_QUERIES_LIST:
        source = q['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(q)

    total_queries = len(SQL_QUERIES_LIST)
    total_files = len(by_source)

    print(f"\n📈 Statistiques:")
    print(f"   • Total de requêtes: {total_queries}")
    print(f"   • Fichiers avec SQL: {total_files}")
    print(f"   • Moyenne par fichier: {total_queries/total_files:.1f}")

    print(f"\n📄 Détail par fichier:")
    for source, queries in sorted(by_source.items()):
        print(f"   • {source}: {len(queries)} requête(s)")

    # Analyser les types de requêtes
    s3_queries = sum(1 for q in SQL_QUERIES_LIST if 's3://' in q['query'])
    table_queries = sum(1 for q in SQL_QUERIES_LIST
                       if 'FROM RAW_' in q['query'] or 'FROM PP_' in q['query'] or 'FROM interactions_' in q['query'])

    print(f"\n🔍 Types de requêtes:")
    print(f"   • Requêtes S3: {s3_queries}")
    print(f"   • Requêtes sur tables DuckDB: {table_queries}")
    print(f"   • Autres: {total_queries - s3_queries - table_queries}")

    print("="*70 + "\n")


if __name__ == "__main__":
    # Test manuel: afficher les requêtes découvertes
    print("="*70)
    print("🔍 SCAN DU PROJET POUR REQUÊTES SQL")
    print("="*70)

    queries_map = extract_sql_queries_from_code()

    if queries_map:
        total = sum(len(qs) for qs in queries_map.values())
        print(f"\n✅ {total} requête(s) SQL trouvée(s) dans {len(queries_map)} fichier(s):")

        for source, queries in sorted(queries_map.items()):
            print(f"\n   📄 {source}")
            for i, q in enumerate(queries, 1):
                line_info = f"ligne {q['line']}" if q['line'] > 0 else "notebook"
                print(f"      {i}. [{line_info}] Type: {q['type']}")
                query_lines = q['query'][:150].replace('\n', ' ')
                print(f"         {query_lines}...")
    else:
        print("\n⚠️  Aucune requête SQL trouvée dans le code")

    print("\n" + "="*70)
    print("Pour tester les requêtes SQL, exécuter:")
    print("   pytest test_sql_queries.py -v -s")
    print("="*70 + "\n")
