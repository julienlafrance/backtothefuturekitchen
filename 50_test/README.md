# >� Tests d'Infrastructure - 50_test

![Tests](https://img.shields.io/badge/tests-35_total-blue)
![Infrastructure](https://img.shields.io/badge/infrastructure-S3+DuckDB+Docker-orange)
![Python](https://img.shields.io/badge/python-3.14.0-blue)
![pytest](https://img.shields.io/badge/pytest-8.4.2-green)

Tests d'infrastructure pour valider S3, DuckDB et les requ�tes SQL du projet.

## <� Vue d'ensemble

Ce r�pertoire contient des **tests d'infrastructure** (pas du code m�tier):
-  Validation connexion S3 + DuckDB
-  Tests performance (download > 5 MB/s)
-  Scan automatique des fichiers parquet
-  Scan automatique des requ�tes SQL
-  Tests Docker (optionnels)

**Note:** Pas de coverage ici car ce sont des tests de validation, pas du code de production.

## =� Tests Disponibles

| Fichier | Tests | Description |
|---------|-------|-------------|
| `S3_duckdb_test.py` | 14 tests | S3 + DuckDB + Docker |
| `test_s3_parquet_files.py` | 5 tests | Scan & validation parquet |
| `test_sql_queries.py` | 16 tests | Scan & validation SQL |
| **Total** | **35 tests** | Infrastructure compl�te |

## =� Commandes

### Tous les tests

```bash
cd 50_test
pytest -v
```

**R�sultat:**
- Local: 14-16 tests (Docker skip)
- Serveur: 35 tests (avec Docker)

### Tests sp�cifiques

```bash
# S3 + DuckDB seulement
pytest S3_duckdb_test.py -v

# Parquet files seulement
pytest test_s3_parquet_files.py -v

# SQL queries seulement
pytest test_sql_queries.py -v
```

## =� Documentation

**Guide complet:** Voir [README_TESTS.md](README_TESTS.md)

Contient:
- Logique de d�tection automatique
- Configuration S3
- Exemples de r�sultats
- D�pannage
- Bonnes pratiques

##  R�sultats Attendus

### Tests qui passent
-  Environnement (hostname, IP, credentials)
-  S3 connexion et performance
-  DuckDB + S3 int�gration
-  Parquet files accessibles
-  SQL queries valides

### Tests qui peuvent skip
- � Docker tests (si pas disponible localement)

---

**Tests d'infrastructure pr�ts!** Voir [README_TESTS.md](README_TESTS.md) pour les d�tails.
