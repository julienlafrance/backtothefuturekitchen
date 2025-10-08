"""
Module pour la connexion S3 via boto3 avec détection automatique du réseau
Les credentials sont dans ../96_keys/ (ignoré par git)
"""
import boto3
import socket
from configparser import ConfigParser
from pathlib import Path

def is_on_local_network():
    """Détecte si on est sur le réseau local (192.168.80.x ou 192.168.0.x)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return (local_ip.startswith('192.168.80.') or local_ip.startswith('192.168.0.'))
    except:
        try:
            hostname = socket.gethostname()
            return 'int' in hostname.lower() or 'dataia' in hostname.lower()
        except:
            return False

def get_s3_client(profile='s3fast', force_external=False, verbose=False):
    """
    Crée et retourne un client S3 configuré avec détection automatique du réseau
    
    Args:
        profile: Le profil à charger depuis ../96_keys/credentials
        force_external: Force l'utilisation de l'endpoint externe (HTTPS)
        verbose: Affiche les informations de connexion
    
    Returns:
        tuple: (boto3.client, bucket_name)
    """
    cred_file = Path(__file__).parent.parent / '96_keys' / 'credentials'
    
    if not cred_file.exists():
        raise FileNotFoundError(f"Credentials introuvable: {cred_file}")
    
    config = ConfigParser()
    config.read(cred_file)
    
    # Déterminer l'endpoint
    if force_external or not is_on_local_network():
        endpoint_url = config[profile]['endpoint_url']
        endpoint_type = "externe (HTTPS)"
    else:
        endpoint_url = "http://192.168.80.202:3910"
        endpoint_type = "local (direct)"
    
    if verbose:
        print(f"🔗 S3 Endpoint: {endpoint_type}")
    
    # Créer le client S3
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=config[profile]['aws_access_key_id'],
        aws_secret_access_key=config[profile]['aws_secret_access_key'],
        region_name=config[profile]['region']
    )
    
    return s3_client, config[profile]['bucket']

# Test
if __name__ == "__main__":
    client, bucket = get_s3_client(verbose=True)
    print(f"✅ Connecté au bucket: {bucket}")
    
    response = client.list_objects_v2(Bucket=bucket, MaxKeys=3)
    print(f"📄 {len(response.get('Contents', []))} fichiers listés")


def get_duckdb_s3_connection():
    """
    Configure et retourne une connexion DuckDB avec accès S3 automatique
    
    Returns:
        tuple: (duckdb.Connection, bucket_name)
    
    Usage:
        con, bucket = get_duckdb_s3_connection()
        df = con.execute(f"SELECT * FROM 's3://{bucket}/PP_recipes.csv' LIMIT 5").df()
    """
    import duckdb
    
    # Charger les credentials
    cred_file = Path(__file__).parent.parent / '96_keys' / 'credentials'
    config = ConfigParser()
    config.read(cred_file)
    
    # Créer la connexion DuckDB
    con = duckdb.connect()
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")
    
    # Déterminer l'endpoint selon le réseau
    if is_on_local_network():
        endpoint = '192.168.80.202:3910'
        use_ssl = 'false'
    else:
        endpoint = 's3fast.lafrance.io'
        use_ssl = 'true'
    
    # Configurer S3 dans DuckDB
    con.execute(f"""
        SET s3_endpoint = '{endpoint}';
        SET s3_use_ssl = {use_ssl};
        SET s3_url_style = 'path';
        SET s3_region = '{config['s3fast']['region']}';
        SET s3_access_key_id = '{config['s3fast']['aws_access_key_id']}';
        SET s3_secret_access_key = '{config['s3fast']['aws_secret_access_key']}';
    """)
    
    return con, config['s3fast']['bucket']
