DIFFÉRENTIEL LOGURU - Correction Streamlit
Problème résolu
Les logs Loguru ne s'écrivaient pas avec Streamlit à cause du cache des modules.
Solution appliquée
Configuration corrigée
pythonimport sys
from loguru import logger

# Créer dossier logs
Path("logs").mkdir(exist_ok=True)

# Configuration protégée contre duplication
if not any("logs/mangetamain" in str(handler) for handler in logger._core.handlers.values()):
    logger.remove()
    logger.add("logs/mangetamain_app.log", rotation="1 MB", level="INFO")
    logger.add("logs/mangetamain_errors.log", rotation="1 MB", level="ERROR") 
    logger.add(sys.stderr, level="DEBUG")  # Console
Logs déplacés dans main()
pythondef main():
    # Logs s'exécutent à chaque visite maintenant
    logger.info("🚀 Streamlit application starting")
    logger.info("🏠 Main application function started")
    
    conn = get_db_connection()
    # ... reste du code
Logs dans les fonctions
pythondef get_db_connection():
    try:
        conn = duckdb.connect(db_path)
        logger.info(f"✅ DuckDB connected - {file_size:.1f} MB")
        logger.info(f"📊 Tables: {[t[0] for t in tables]}")
        return conn
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return None

def create_rating_distribution_chart(conn):
    logger.info("📊 Creating rating chart")
    # ... analyse ...
    logger.info(f"📈 Generated {total_ratings:,} ratings, most common: {rating}")
Fichiers générés
logs/
├── mangetamain_app.log     # Tous événements
└── mangetamain_errors.log  # Erreurs uniquement
Surveillance
bash# Monitoring temps réel
tail -f logs/mangetamain_app.log

# Recherche erreurs
grep "ERROR" logs/mangetamain_app.log

# Stats DB
grep "DuckDB\|Table" logs/mangetamain_app.log
Déploiement
bashcd ~/mangetamain/00_preprod
cp main_real.py src/mangetamain_analytics/main.py
docker restart [container]
Résultat
Logs fonctionnels qui s'écrivent à chaque visite utilisateur avec traçabilité complète des opérations et erreurs.
