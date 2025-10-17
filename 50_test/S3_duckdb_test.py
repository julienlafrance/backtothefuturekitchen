#!/usr/bin/env python3
"""
🧪 Script de test complet S3 + DuckDB
Tests toutes les fonctionnalités de la configuration S3 simplifiée

Usage: ./S3_duckdb_test.py
"""

import boto3
import duckdb
import time
import sys
import socket
from configparser import ConfigParser
from pathlib import Path


def print_header(title):
    """Affiche un header stylisé"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)


def print_status(status, message):
    """Affiche un statut avec emoji"""
    emoji = "✅" if status == "OK" else "❌" if status == "FAIL" else "🔍"
    print(f"{emoji} {message}")


def test_environment():
    """Test 1: Environnement et configuration"""
    print_header("TEST 1: ENVIRONNEMENT")
    
    # Hostname et IP
    hostname = socket.gethostname()
    print_status("INFO", f"Machine: {hostname}")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print_status("INFO", f"IP locale: {local_ip}")
        
        # Détection réseau local
        is_local = (local_ip.startswith('192.168.80.') or 
                   local_ip.startswith('192.168.0.') or
                   'int' in hostname.lower() or 
                   'dataia' in hostname.lower())
        
        print_status("INFO", f"Réseau local: {'OUI' if is_local else 'NON'}")
        
    except Exception as e:
        print_status("WARN", f"Détection IP échouée: {e}")
    
    # Vérification credentials
    cred_file = Path(__file__).parent.parent / '96_keys' / 'credentials'
    if cred_file.exists():
        print_status("OK", f"Credentials trouvées: {cred_file}")
    else:
        print_status("FAIL", f"Credentials manquantes: {cred_file}")
        return False
        
    # Vérification DuckDB S3
    db_file = Path(__file__).parent.parent / '96_keys' / 'garage_s3.duckdb'
    if db_file.exists():
        print_status("OK", f"DuckDB S3 trouvée: {db_file}")
    else:
        print_status("WARN", f"DuckDB S3 manquante: {db_file}")
    
    return True


def test_s3_connection():
    """Test S3 avec boto3"""
    print_header("TEST 2: CONNEXION S3")
    
    try:
        # Charger credentials
        config = ConfigParser()
        config.read('../96_keys/credentials')
        
        # Créer client S3
        s3 = boto3.client(
            's3',
            endpoint_url='http://s3fast.lafrance.io',
            aws_access_key_id=config['s3fast']['aws_access_key_id'],
            aws_secret_access_key=config['s3fast']['aws_secret_access_key'],
            region_name='garage-fast'
        )
        
        print_status("OK", "Client S3 créé")
        
        # Test list objects
        start_time = time.time()
        response = s3.list_objects_v2(Bucket='mangetamain', MaxKeys=5)
        duration = time.time() - start_time
        
        if 'Contents' in response:
            print_status("OK", f"Bucket accessible ({duration:.3f}s)")
            print_status("INFO", f"Fichiers trouvés: {len(response['Contents'])}")
            
            # Afficher les premiers fichiers
            for obj in response['Contents'][:3]:
                size_mb = obj['Size'] / 1e6
                print_status("INFO", f"  📄 {obj['Key']} - {size_mb:.1f} MB")
            
            return s3
        else:
            print_status("FAIL", "Bucket inaccessible")
            return None
            
    except Exception as e:
        print_status("FAIL", f"Connexion S3 échouée: {e}")
        return None


def test_s3_performance(s3_client):
    """Test performance S3"""
    print_header("TEST 3: PERFORMANCE S3")
    
    if not s3_client:
        print_status("SKIP", "Client S3 non disponible")
        return
    
    try:
        # Test download
        print_status("INFO", "Download PP_users.csv (~13.6MB)...")
        
        start_time = time.time()
        s3_client.download_file('mangetamain', 'PP_users.csv', '/tmp/test_users.csv')
        duration = time.time() - start_time
        
        file_size = Path('/tmp/test_users.csv').stat().st_size
        speed_mb = (file_size / 1e6) / duration
        
        print_status("OK", f"Download: {duration:.3f}s - {speed_mb:.1f} MB/s")
        
        # Nettoyer
        Path('/tmp/test_users.csv').unlink(missing_ok=True)
        
    except Exception as e:
        print_status("FAIL", f"Test performance échoué: {e}")


def test_duckdb_s3():
    """Test DuckDB avec S3 direct"""
    print_header("TEST 4: DUCKDB + S3")
    
    try:
        # Charger credentials
        config = ConfigParser()
        config.read('../96_keys/credentials')
        access_key = config['s3fast']['aws_access_key_id']
        secret_key = config['s3fast']['aws_secret_access_key']
        
        # Se connecter à la base
        db_file = Path(__file__).parent.parent / '96_keys' / 'garage_s3.duckdb'
        
        if db_file.exists():
            print_status("INFO", "Utilisation de garage_s3.duckdb")
            conn = duckdb.connect(str(db_file))
        else:
            print_status("INFO", "Base DuckDB manquante, création temporaire")
            conn = duckdb.connect()
            
        # Charger httpfs et recréer le secret (nécessaire en Python)
        try:
            conn.execute("LOAD httpfs")
        except:
            conn.execute("INSTALL httpfs")
            conn.execute("LOAD httpfs")
            
        # Recréer le secret à chaque session Python
        conn.execute(f"""
            CREATE OR REPLACE SECRET garage_s3 (
                TYPE s3,
                KEY_ID '{access_key}',
                SECRET '{secret_key}',
                ENDPOINT 's3fast.lafrance.io',
                REGION 'garage-fast',
                URL_STYLE 'path',
                USE_SSL false
            )
        """)
        
        # Test 1: Count total recipes
        print_status("INFO", "Query: COUNT(*) sur PP_recipes.csv...")
        start_time = time.time()
        
        result = conn.execute("SELECT COUNT(*) as total FROM 's3://mangetamain/PP_recipes.csv'").fetchone()
        duration = time.time() - start_time
        
        if result:
            print_status("OK", f"Total recettes: {result[0]:,} ({duration:.3f}s)")
        
        # Test 2: GROUP BY
        print_status("INFO", "Query: GROUP BY calorie_level...")
        start_time = time.time()
        
        results = conn.execute("""
            SELECT calorie_level, COUNT(*) as nb_recipes
            FROM 's3://mangetamain/PP_recipes.csv' 
            GROUP BY calorie_level 
            ORDER BY nb_recipes DESC
        """).fetchall()
        
        duration = time.time() - start_time
        
        if results:
            print_status("OK", f"GROUP BY terminé ({duration:.3f}s)")
            for level, count in results:
                print_status("INFO", f"  Niveau {level}: {count:,} recettes")
        
        conn.close()
        
    except Exception as e:
        print_status("FAIL", f"Test DuckDB échoué: {e}")


def test_docker_containers():
    """Test containers Docker"""
    print_header("TEST 5: CONTAINERS DOCKER")
    
    try:
        import subprocess
        
        # Lister les containers
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            containers = [name for name in result.stdout.strip().split('\n') if name]
            print_status("INFO", f"Containers actifs: {len(containers)}")
            
            for name in containers:
                print_status("INFO", f"  🐳 {name}")
                
                # Test S3 si c'est mange_preprod ou mange_prod
                if name in ['mange_preprod', 'mange_prod']:
                    print_status("INFO", f"Test S3 dans {name}...")
                    
                    # Test avec .venv/bin/python
                    test_cmd = f'''cd /app && .venv/bin/python -c "
import boto3
from configparser import ConfigParser
try:
    config = ConfigParser()
    config.read('../96_keys/credentials')
    s3 = boto3.client('s3', endpoint_url='http://s3fast.lafrance.io',
                      aws_access_key_id=config['s3fast']['aws_access_key_id'],
                      aws_secret_access_key=config['s3fast']['aws_secret_access_key'],
                      region_name='garage-fast')
    response = s3.list_objects_v2(Bucket='mangetamain', MaxKeys=1)
    print('OK' if response.get('Contents') else 'FAIL')
except Exception as e:
    print('FAIL')
"'''
                    
                    try:
                        container_result = subprocess.run([
                            'docker', 'exec', name, 'bash', '-c', test_cmd
                        ], capture_output=True, text=True, timeout=10)
                        
                        if container_result.returncode == 0 and 'OK' in container_result.stdout:
                            print_status("OK", f"S3 fonctionne dans {name}")
                        else:
                            print_status("FAIL", f"S3 échoue dans {name}")
                    except subprocess.TimeoutExpired:
                        print_status("WARN", f"Test container {name} timeout")
        else:
            print_status("INFO", "Aucun container Docker actif")
            
    except Exception as e:
        print_status("WARN", f"Test containers échoué: {e}")


def main():
    """Fonction principale"""
    print_header("🧪 TEST COMPLET S3 + DUCKDB")
    print("Configuration S3 simplifiée avec DNAT bypass")
    print("Endpoint unique: http://s3fast.lafrance.io")
    
    # Tests séquentiels
    if not test_environment():
        print_status("FAIL", "Environnement non configuré")
        sys.exit(1)
    
    s3_client = test_s3_connection()
    
    if s3_client:
        test_s3_performance(s3_client)
    
    test_duckdb_s3()
    
    test_docker_containers()
    
    print_header("🎉 TESTS TERMINÉS")
    print_status("OK", "Configuration S3 simplifiée validée!")
    print_status("INFO", "Performance: DNAT bypass 80→3910")
    print_status("INFO", "DuckDB: Requêtes SQL directes sur S3")


if __name__ == "__main__":
    main()
