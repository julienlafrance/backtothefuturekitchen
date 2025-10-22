"""
🔍 Script de diagnostic S3 - Test complet de connexion
=====================================================

Ce script teste :
1. ✅ Lecture du fichier credentials
2. ✅ Connexion DuckDB avec httpfs
3. ✅ Test réseau vers l'endpoint S3
4. ✅ Authentification S3
5. ✅ Liste des fichiers dans le bucket
6. ✅ Lecture d'un fichier CSV depuis S3

Usage:
    python test_s3_connection.py
"""

import sys
from pathlib import Path
import duckdb
from configparser import ConfigParser
import socket
import urllib.request
import urllib.error
import json

# =============================================================================
# 🎨 HELPERS D'AFFICHAGE
# =============================================================================

def print_section(title: str):
    """Affiche un titre de section."""
    print(f"\n{'='*70}")
    print(f"🔍 {title}")
    print(f"{'='*70}")

def print_success(msg: str):
    """Affiche un message de succès."""
    print(f"✅ {msg}")

def print_error(msg: str):
    """Affiche un message d'erreur."""
    print(f"❌ {msg}")

def print_warning(msg: str):
    """Affiche un avertissement."""
    print(f"⚠️  {msg}")

def print_info(msg: str):
    """Affiche une information."""
    print(f"ℹ️  {msg}")

# =============================================================================
# 📂 TEST 1: LOCALISATION DES CREDENTIALS
# =============================================================================

def test_credentials_file():
    """Test 1: Vérifie que le fichier credentials existe."""
    print_section("TEST 1: Localisation du fichier credentials")
    
    # Recherche du fichier
    anchors = [Path.cwd().resolve(), *Path.cwd().resolve().parents]
    creds_path = None
    
    for anchor in anchors:
        candidate = anchor / "96_keys" / "credentials"
        print_info(f"Vérification: {candidate}")
        if candidate.exists():
            creds_path = candidate
            break
    
    if creds_path is None:
        print_error("Fichier credentials introuvable dans 96_keys/")
        print_info("Recherche effectuée depuis: " + str(Path.cwd()))
        return None
    
    print_success(f"Fichier trouvé: {creds_path}")
    
    # Lecture du contenu
    config = ConfigParser()
    config.read(creds_path)
    
    if 's3fast' not in config:
        print_error("Profil [s3fast] introuvable dans credentials")
        print_info(f"Profils disponibles: {list(config.sections())}")
        return None
    
    print_success("Profil [s3fast] trouvé")
    
    # Affichage des paramètres (masqués)
    s3_config = config['s3fast']
    print_info(f"Endpoint: {s3_config.get('endpoint_url', 'NON DÉFINI')}")
    print_info(f"Region: {s3_config.get('region', 'NON DÉFINI')}")
    print_info(f"Access Key: {s3_config.get('aws_access_key_id', 'NON DÉFINI')[:10]}...")
    print_info(f"Secret Key: {'*' * 20} (masqué)")
    
    return s3_config

# =============================================================================
# 🌐 TEST 2: TEST RÉSEAU
# =============================================================================

def test_network_connectivity(endpoint_url: str):
    """Test 2: Vérifie la connectivité réseau vers l'endpoint S3."""
    print_section("TEST 2: Connectivité réseau")
    
    # Extraire le hostname
    hostname = endpoint_url.replace('http://', '').replace('https://', '').split(':')[0]
    print_info(f"Hostname: {hostname}")
    
    # Test DNS
    try:
        ip_address = socket.gethostbyname(hostname)
        print_success(f"Résolution DNS: {hostname} → {ip_address}")
    except socket.gaierror as e:
        print_error(f"Échec résolution DNS: {e}")
        return False
    
    # Test ping TCP (port 80 ou 443)
    port = 443 if 'https' in endpoint_url else 80
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print_success(f"Port {port} accessible sur {hostname}")
        else:
            print_error(f"Port {port} inaccessible (code: {result})")
            return False
    except Exception as e:
        print_error(f"Erreur connexion socket: {e}")
        return False
    
    # Test HTTP simple
    try:
        test_url = f"{endpoint_url}/"
        print_info(f"Test HTTP GET: {test_url}")
        req = urllib.request.Request(test_url, method='GET')
        with urllib.request.urlopen(req, timeout=10) as response:
            print_success(f"HTTP GET réussi (Status: {response.status})")
    except urllib.error.HTTPError as e:
        # Un 403/404 est OK, ça veut dire que le serveur répond
        if e.code in [403, 404]:
            print_success(f"Serveur répond (HTTP {e.code})")
        else:
            print_warning(f"HTTP Error: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        print_error(f"Erreur URL: {e.reason}")
        return False
    except Exception as e:
        print_error(f"Erreur HTTP: {e}")
        return False
    
    return True

# =============================================================================
# 🦆 TEST 3: CONNEXION DUCKDB
# =============================================================================

def test_duckdb_connection(s3_config: dict):
    """Test 3: Crée une connexion DuckDB et configure S3."""
    print_section("TEST 3: Connexion DuckDB avec httpfs")
    
    endpoint_url = s3_config.get('endpoint_url', 'http://s3fast.lafrance.io')
    access_key = s3_config.get('aws_access_key_id')
    secret_key = s3_config.get('aws_secret_access_key')
    region = s3_config.get('region', 'garage-fast')
    
    try:
        # Créer connexion
        conn = duckdb.connect(database=':memory:')
        print_success("Connexion DuckDB créée")
        
        # Installer httpfs
        conn.execute("INSTALL httpfs;")
        print_success("Extension httpfs installée")
        
        # Charger httpfs
        conn.execute("LOAD httpfs;")
        print_success("Extension httpfs chargée")
        
        # Configurer le secret S3
        endpoint_clean = endpoint_url.replace('http://', '').replace('https://', '')
        use_ssl = 'https' in endpoint_url
        
        secret_sql = f"""
            CREATE SECRET s3fast (
                TYPE s3,
                KEY_ID '{access_key}',
                SECRET '{secret_key}',
                ENDPOINT '{endpoint_clean}',
                REGION '{region}',
                URL_STYLE 'path',
                USE_SSL {str(use_ssl).lower()}
            );
        """
        
        conn.execute(secret_sql)
        print_success("Secret S3 configuré")
        
        # Vérifier la configuration
        result = conn.execute("SELECT * FROM duckdb_secrets();").fetchall()
        print_info(f"Secrets configurés: {len(result)}")
        for secret in result:
            print_info(f"  • Secret: {secret[0]} (Type: {secret[1]})")
        
        return conn
        
    except Exception as e:
        print_error(f"Erreur DuckDB: {e}")
        return None

# =============================================================================
# 📁 TEST 4: LISTE DES FICHIERS S3
# =============================================================================

def test_list_s3_files(conn, bucket: str = "mangetamain"):
    """Test 4: Liste les fichiers dans le bucket S3."""
    print_section(f"TEST 4: Liste des fichiers dans s3://{bucket}/")
    
    if conn is None:
        print_error("Connexion DuckDB non disponible")
        return []
    
    try:
        # Essayer de lister les fichiers (glob pattern)
        sql = f"SELECT * FROM glob('s3://{bucket}/*');"
        print_info(f"SQL: {sql}")
        
        result = conn.execute(sql).fetchall()
        
        if len(result) == 0:
            print_warning(f"Aucun fichier trouvé dans s3://{bucket}/")
        else:
            print_success(f"{len(result)} fichier(s) trouvé(s):")
            for file in result[:10]:  # Limiter à 10
                print_info(f"  • {file[0]}")
            if len(result) > 10:
                print_info(f"  ... et {len(result) - 10} autres")
        
        return [f[0] for f in result]
        
    except Exception as e:
        print_error(f"Erreur lors du listing: {e}")
        
        # Essayer une approche alternative (lecture directe)
        print_info("Tentative de lecture directe d'un fichier spécifique...")
        return []

# =============================================================================
# 📄 TEST 5: LECTURE D'UN FICHIER CSV
# =============================================================================

def test_read_csv(conn, file_path: str = "s3://mangetamain/PP_recipes.csv"):
    """Test 5: Tente de lire un fichier CSV depuis S3."""
    print_section(f"TEST 5: Lecture du fichier {file_path}")
    
    if conn is None:
        print_error("Connexion DuckDB non disponible")
        return False
    
    try:
        # Test 1: COUNT(*)
        sql_count = f"SELECT COUNT(*) as total FROM '{file_path}' LIMIT 1;"
        print_info(f"SQL: {sql_count}")
        
        result = conn.execute(sql_count).fetchone()
        total_rows = result[0] if result else 0
        print_success(f"Nombre de lignes: {total_rows:,}")
        
        # Test 2: Lecture de 5 lignes
        sql_sample = f"SELECT * FROM '{file_path}' LIMIT 5;"
        print_info(f"SQL: {sql_sample}")
        
        df = conn.execute(sql_sample).pl()
        print_success(f"DataFrame lu: {df.shape[0]} lignes × {df.shape[1]} colonnes")
        print_info(f"Colonnes: {', '.join(df.columns[:5])}...")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur lors de la lecture: {e}")
        print_info(f"Type d'erreur: {type(e).__name__}")
        
        # Suggestions de diagnostic
        print_warning("\n🔧 Suggestions de diagnostic:")
        print_info("1. Vérifier que le fichier existe bien à cet emplacement")
        print_info("2. Vérifier les permissions d'accès au bucket")
        print_info("3. Tester avec un autre fichier (ex: .parquet)")
        print_info("4. Vérifier les credentials AWS (Access Key / Secret Key)")
        
        return False

# =============================================================================
# 🧪 TEST 6: TEST AVEC DIFFÉRENTS FORMATS
# =============================================================================

def test_different_formats(conn, bucket: str = "mangetamain"):
    """Test 6: Teste la lecture de différents formats de fichiers."""
    print_section("TEST 6: Test de différents formats")
    
    if conn is None:
        print_error("Connexion DuckDB non disponible")
        return
    
    test_files = [
        (f"s3://{bucket}/PP_recipes.csv", "CSV"),
        (f"s3://{bucket}/PP_recipes.parquet", "Parquet"),
        (f"s3://{bucket}/PP_interactions.csv", "CSV (interactions)"),
    ]
    
    for file_path, format_name in test_files:
        try:
            print_info(f"\nTest: {file_path} ({format_name})")
            result = conn.execute(f"SELECT COUNT(*) FROM '{file_path}' LIMIT 1;").fetchone()
            count = result[0] if result else 0
            print_success(f"{format_name}: {count:,} lignes")
        except Exception as e:
            print_error(f"{format_name}: Échec - {str(e)[:100]}")

# =============================================================================
# 🚀 MAIN - EXÉCUTION DES TESTS
# =============================================================================

def main():
    """Exécute tous les tests de diagnostic."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║         🔍 DIAGNOSTIC S3 - Back to the Future Kitchen            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Credentials
    s3_config = test_credentials_file()
    if s3_config is None:
        print_error("\n❌ ARRÊT: Impossible de charger les credentials")
        return
    
    # Test 2: Réseau
    endpoint_url = s3_config.get('endpoint_url', 'http://s3fast.lafrance.io')
    network_ok = test_network_connectivity(endpoint_url)
    if not network_ok:
        print_error("\n❌ ARRÊT: Problème de connectivité réseau")
        return
    
    # Test 3: DuckDB
    conn = test_duckdb_connection(s3_config)
    if conn is None:
        print_error("\n❌ ARRÊT: Impossible de créer la connexion DuckDB")
        return
    
    # Test 4: Listing
    files = test_list_s3_files(conn, bucket="mangetamain")
    
    # Test 5: Lecture CSV
    csv_ok = test_read_csv(conn, file_path="s3://mangetamain/PP_recipes.csv")
    
    # Test 6: Différents formats
    test_different_formats(conn, bucket="mangetamain")
    
    # Fermeture
    conn.close()
    
    # Résumé final
    print_section("RÉSUMÉ")
    print_success("Tests terminés !" if csv_ok else "Tests terminés avec erreurs")
    
    if not csv_ok:
        print_warning("\n💡 Prochaines étapes:")
        print_info("1. Vérifier l'accès au bucket S3 via l'interface web")
        print_info("2. Tester avec curl: curl http://s3fast.lafrance.io/mangetamain/")
        print_info("3. Vérifier les credentials AWS dans 96_keys/credentials")
        print_info("4. Contacter l'administrateur S3 si le problème persiste")

if __name__ == "__main__":
    main()
