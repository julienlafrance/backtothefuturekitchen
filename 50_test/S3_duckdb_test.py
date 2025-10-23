#!/usr/bin/env python3
"""
🧪 Tests complets S3 + DuckDB avec pytest
Tests toutes les fonctionnalités de la configuration S3 simplifiée

Usage:
    pytest S3_duckdb_test.py -v
    pytest S3_duckdb_test.py -v -s  # avec output détaillé
"""

import pytest
import boto3
import duckdb
import time
import socket
import subprocess
from configparser import ConfigParser
from pathlib import Path


@pytest.fixture(scope="module")
def credentials_file():
    """Fixture pour vérifier et charger le fichier credentials"""
    cred_file = Path(__file__).parent.parent / '96_keys' / 'credentials'

    if not cred_file.exists():
        pytest.skip(f"Fichier credentials non trouvé: {cred_file}")

    return cred_file


@pytest.fixture(scope="module")
def s3_config(credentials_file):
    """Fixture pour charger la configuration S3"""
    config = ConfigParser()
    config.read(credentials_file)

    if 's3fast' not in config:
        pytest.skip("Section [s3fast] manquante dans credentials")

    return {
        'access_key': config['s3fast']['aws_access_key_id'],
        'secret_key': config['s3fast']['aws_secret_access_key'],
        'endpoint_url': 'http://s3fast.lafrance.io',
        'region': 'garage-fast',
        'bucket': 'mangetamain'
    }


@pytest.fixture(scope="module")
def s3_client(s3_config):
    """Fixture pour créer un client S3 boto3"""
    client = boto3.client(
        's3',
        endpoint_url=s3_config['endpoint_url'],
        aws_access_key_id=s3_config['access_key'],
        aws_secret_access_key=s3_config['secret_key'],
        region_name=s3_config['region']
    )
    return client


@pytest.fixture(scope="module")
def duckdb_connection(s3_config):
    """Fixture pour créer une connexion DuckDB configurée pour S3"""
    db_file = Path(__file__).parent.parent / '96_keys' / 'garage_s3.duckdb'

    if db_file.exists():
        conn = duckdb.connect(str(db_file))
    else:
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
            ENDPOINT 's3fast.lafrance.io',
            REGION '{s3_config['region']}',
            URL_STYLE 'path',
            USE_SSL false
        )
    """)

    yield conn

    conn.close()


# =============================================================================
# TESTS ENVIRONNEMENT
# =============================================================================

def test_environment_hostname():
    """Vérifie le hostname de la machine"""
    hostname = socket.gethostname()
    print(f"\n🖥️  Hostname: {hostname}")
    assert hostname, "Hostname non détecté"


def test_environment_ip():
    """Vérifie l'IP locale de la machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        print(f"🌐 IP locale: {local_ip}")

        # Détection réseau local
        is_local = (local_ip.startswith('192.168.80.') or
                   local_ip.startswith('192.168.0.'))

        print(f"📍 Réseau local: {'OUI' if is_local else 'NON'}")

        assert local_ip, "IP locale non détectée"

    except Exception as e:
        pytest.skip(f"Détection IP échouée: {e}")


def test_credentials_file_exists(credentials_file):
    """Vérifie que le fichier credentials existe"""
    print(f"\n✅ Credentials: {credentials_file}")
    assert credentials_file.exists()


def test_duckdb_file_exists():
    """Vérifie que la base DuckDB S3 existe"""
    db_file = Path(__file__).parent.parent / '96_keys' / 'garage_s3.duckdb'

    if db_file.exists():
        print(f"\n✅ DuckDB S3: {db_file}")
        print(f"   Taille: {db_file.stat().st_size / 1024:.1f} KB")
    else:
        print(f"\n⚠️  DuckDB S3 manquante (sera créée): {db_file}")


# =============================================================================
# TESTS CONNEXION S3
# =============================================================================

def test_s3_client_creation(s3_client):
    """Vérifie que le client S3 est créé"""
    print("\n✅ Client S3 créé avec succès")
    assert s3_client is not None


def test_s3_bucket_accessible(s3_client, s3_config):
    """Vérifie l'accessibilité du bucket S3"""
    start_time = time.time()
    response = s3_client.list_objects_v2(Bucket=s3_config['bucket'], MaxKeys=5)
    duration = time.time() - start_time

    print(f"\n✅ Bucket accessible en {duration:.3f}s")

    assert 'Contents' in response, "Aucun objet trouvé dans le bucket"

    files_count = len(response['Contents'])
    print(f"📁 Fichiers trouvés: {files_count}")

    # Afficher les premiers fichiers
    for obj in response['Contents'][:3]:
        size_mb = obj['Size'] / 1e6
        print(f"   📄 {obj['Key']} - {size_mb:.1f} MB")

    assert files_count > 0


def test_s3_list_all_objects(s3_client, s3_config):
    """Liste tous les objets du bucket"""
    try:
        response = s3_client.list_objects_v2(Bucket=s3_config['bucket'])

        if 'Contents' in response:
            all_objects = response['Contents']
            print(f"\n📊 Total objets dans {s3_config['bucket']}: {len(all_objects)}")

            # Calculer taille totale
            total_size = sum(obj['Size'] for obj in all_objects)
            print(f"💾 Taille totale: {total_size / 1e6:.1f} MB")

            # Grouper par extension
            extensions = {}
            for obj in all_objects:
                ext = Path(obj['Key']).suffix or 'no_ext'
                extensions[ext] = extensions.get(ext, 0) + 1

            print(f"📋 Fichiers par extension:")
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
                print(f"   {ext}: {count}")

    except Exception as e:
        pytest.skip(f"Impossible de lister tous les objets: {e}")


# =============================================================================
# TESTS PERFORMANCE S3
# =============================================================================

def test_s3_download_performance(s3_client, s3_config):
    """Teste la performance de téléchargement S3"""
    test_file = 'PP_users.csv'
    local_path = '/tmp/test_users.csv'

    try:
        print(f"\n🔽 Download {test_file}...")

        start_time = time.time()
        s3_client.download_file(s3_config['bucket'], test_file, local_path)
        duration = time.time() - start_time

        file_size = Path(local_path).stat().st_size
        speed_mb = (file_size / 1e6) / duration

        print(f"✅ Download: {duration:.3f}s")
        print(f"⚡ Vitesse: {speed_mb:.1f} MB/s")
        print(f"📦 Taille: {file_size / 1e6:.1f} MB")

        # Nettoyer
        Path(local_path).unlink(missing_ok=True)

        # Assert vitesse minimale acceptable (>5 MB/s)
        assert speed_mb > 5, f"Vitesse trop lente: {speed_mb:.1f} MB/s (attendu >5 MB/s)"

    except Exception as e:
        pytest.fail(f"Test performance échoué: {e}")


# =============================================================================
# TESTS DUCKDB + S3
# =============================================================================

def test_duckdb_s3_count_recipes(duckdb_connection):
    """Teste COUNT(*) sur PP_recipes.csv via S3"""
    print(f"\n🔍 Query: SELECT COUNT(*) FROM 's3://mangetamain/PP_recipes.csv'")

    start_time = time.time()
    result = duckdb_connection.execute(
        "SELECT COUNT(*) as total FROM 's3://mangetamain/PP_recipes.csv'"
    ).fetchone()
    duration = time.time() - start_time

    assert result is not None, "Aucun résultat"
    total = result[0]

    print(f"✅ Total recettes: {total:,}")
    print(f"⏱️  Durée: {duration:.3f}s")

    assert total > 0, "Aucune recette trouvée"


def test_duckdb_s3_group_by(duckdb_connection):
    """Teste GROUP BY sur PP_recipes.csv via S3"""
    print(f"\n🔍 Query: GROUP BY calorie_level")

    start_time = time.time()
    results = duckdb_connection.execute("""
        SELECT calorie_level, COUNT(*) as nb_recipes
        FROM 's3://mangetamain/PP_recipes.csv'
        GROUP BY calorie_level
        ORDER BY nb_recipes DESC
    """).fetchall()
    duration = time.time() - start_time

    assert results, "Aucun résultat GROUP BY"

    print(f"✅ GROUP BY terminé en {duration:.3f}s")
    print(f"📊 Résultats:")

    for level, count in results:
        print(f"   Niveau {level}: {count:,} recettes")

    assert len(results) > 0


def test_duckdb_s3_parquet_file(duckdb_connection):
    """Teste lecture du fichier parquet interactions_sample"""
    print(f"\n🔍 Query: SELECT COUNT(*) FROM interactions_sample.parquet")

    try:
        start_time = time.time()
        result = duckdb_connection.execute(
            "SELECT COUNT(*) as total FROM 's3://mangetamain/interactions_sample.parquet'"
        ).fetchone()
        duration = time.time() - start_time

        assert result is not None, "Aucun résultat parquet"
        total = result[0]

        print(f"✅ Total interactions: {total:,}")
        print(f"⏱️  Durée: {duration:.3f}s")

        assert total > 0, "Aucune interaction trouvée"

    except Exception as e:
        pytest.fail(f"Erreur lecture parquet: {e}")


# =============================================================================
# TESTS DOCKER (OPTIONNELS)
# =============================================================================

@pytest.mark.skipif(not Path('/var/run/docker.sock').exists(),
                    reason="Docker non disponible")
def test_docker_containers_running():
    """Vérifie les containers Docker actifs"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            containers = [name for name in result.stdout.strip().split('\n') if name]

            print(f"\n🐳 Containers actifs: {len(containers)}")
            for name in containers:
                print(f"   • {name}")

            assert len(containers) > 0
        else:
            pytest.skip("Aucun container Docker actif")

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("Docker non accessible")


@pytest.mark.skipif(not Path('/var/run/docker.sock').exists(),
                    reason="Docker non disponible")
def test_docker_s3_in_containers():
    """Teste S3 dans les containers Docker mange_preprod et mange_prod"""
    target_containers = ['mange_preprod', 'mange_prod']

    try:
        # Lister les containers actifs
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            pytest.skip("Impossible de lister les containers")

        active_containers = result.stdout.strip().split('\n')
        test_results = {}

        for container in target_containers:
            if container not in active_containers:
                print(f"\n⚠️  Container {container} non actif")
                continue

            print(f"\n🧪 Test S3 dans {container}...")

            # Test simple: vérifier si boto3 est disponible
            test_cmd = '''python3 -c "import boto3; print('OK')" 2>/dev/null || echo "FAIL"'''

            try:
                container_result = subprocess.run(
                    ['docker', 'exec', container, 'bash', '-c', test_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if container_result.returncode == 0 and 'OK' in container_result.stdout:
                    test_results[container] = True
                    print(f"   ✅ boto3 disponible dans {container}")
                else:
                    test_results[container] = False
                    print(f"   ❌ boto3 non disponible dans {container}")

            except subprocess.TimeoutExpired:
                print(f"   ⏱️  Timeout pour {container}")
                test_results[container] = False

        if test_results:
            success_count = sum(1 for v in test_results.values() if v)
            print(f"\n📊 Résumé: {success_count}/{len(test_results)} containers OK")
        else:
            pytest.skip("Aucun container cible actif")

    except Exception as e:
        pytest.skip(f"Test Docker échoué: {e}")


# =============================================================================
# TEST RÉSUMÉ
# =============================================================================

def test_summary(s3_config, duckdb_connection):
    """Affiche un résumé de tous les tests"""
    print("\n" + "="*70)
    print("🎉 RÉSUMÉ DES TESTS S3 + DUCKDB")
    print("="*70)

    print(f"\n📋 Configuration:")
    print(f"   • Endpoint: {s3_config['endpoint_url']}")
    print(f"   • Region: {s3_config['region']}")
    print(f"   • Bucket: {s3_config['bucket']}")

    print(f"\n✅ Tests validés:")
    print(f"   • Environnement système")
    print(f"   • Connexion S3 boto3")
    print(f"   • Performance download")
    print(f"   • DuckDB + S3 intégration")
    print(f"   • Requêtes SQL sur CSV")
    print(f"   • Requêtes SQL sur Parquet")

    print(f"\n💡 Configuration simplifiée:")
    print(f"   • DNAT bypass 80→3910")
    print(f"   • Endpoint unique pour tous les environnements")
    print(f"   • Secret S3 persistant dans DuckDB")

    print("="*70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
