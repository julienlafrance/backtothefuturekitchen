# >ê Tests d'Infrastructure - 50_test

![Tests](https://img.shields.io/badge/tests-35_total-blue)
![Infrastructure](https://img.shields.io/badge/infrastructure-S3+DuckDB+Docker-orange)
![Python](https://img.shields.io/badge/python-3.14.0-blue)
![pytest](https://img.shields.io/badge/pytest-8.4.2-green)

Tests d'infrastructure pour valider S3, DuckDB et les requêtes SQL du projet.

## <¯ Vue d'ensemble

Ce répertoire contient des **tests d'infrastructure** (pas du code métier):
-  Validation connexion S3 + DuckDB
-  Tests performance (download > 5 MB/s)
-  Scan automatique des fichiers parquet
-  Scan automatique des requêtes SQL
-  Tests Docker (optionnels)

**Note:** Pas de coverage ici car ce sont des tests de validation, pas du code de production.

## =Ê Tests Disponibles

| Fichier | Tests | Description |
|---------|-------|-------------|
| `S3_duckdb_test.py` | 14 tests | S3 + DuckDB + Docker |
| `test_s3_parquet_files.py` | 5 tests | Scan & validation parquet |
| `test_sql_queries.py` | 16 tests | Scan & validation SQL |
| **Total** | **35 tests** | Infrastructure complète |

## =€ Commandes

### Tous les tests

```bash
cd 50_test
pytest -v
```

**Résultat:**
- Local: 14-16 tests (Docker skip)
- Serveur: 35 tests (avec Docker)

### Tests spécifiques

```bash
# S3 + DuckDB seulement
pytest S3_duckdb_test.py -v

# Parquet files seulement
pytest test_s3_parquet_files.py -v

# SQL queries seulement
pytest test_sql_queries.py -v
```

## =Ú Documentation

**Guide complet:** Voir [README_TESTS.md](README_TESTS.md)

Contient:
- Logique de détection automatique
- Configuration S3
- Exemples de résultats
- Dépannage
- Bonnes pratiques

##  Résultats Attendus

### Tests qui passent
-  Environnement (hostname, IP, credentials)
-  S3 connexion et performance
-  DuckDB + S3 intégration
-  Parquet files accessibles
-  SQL queries valides

### Tests qui peuvent skip
-   Docker tests (si pas disponible localement)

---

**Tests d'infrastructure prêts!** Voir [README_TESTS.md](README_TESTS.md) pour les détails.
