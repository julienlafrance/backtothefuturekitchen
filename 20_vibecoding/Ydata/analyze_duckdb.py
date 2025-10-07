#!/usr/bin/env python3
"""
Script d'analyse des données DuckDB avec YData Profiling
"""

import duckdb
import pandas as pd
from ydata_profiling import ProfileReport
import os
from pathlib import Path

# Configuration
DB_PATH = "/home/dataia25/mangetamain/00_preprod/data/mangetamain.duckdb"
OUTPUT_DIR = "reports"

def connect_to_duckdb(db_path):
    """Se connecter à la base DuckDB"""
    try:
        conn = duckdb.connect(db_path)
        print(f"✅ Connexion réussie à {db_path}")
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def list_tables(conn):
    """Lister toutes les tables de la base"""
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        table_names = [table[0] for table in tables]
        print(f"📋 Tables trouvées: {table_names}")
        return table_names
    except Exception as e:
        print(f"❌ Erreur lors de la liste des tables: {e}")
        return []

def get_table_info(conn, table_name):
    """Obtenir des informations sur une table"""
    try:
        # Compter les lignes
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        
        # Obtenir le schéma
        schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
        
        print(f"📊 Table '{table_name}': {count:,} lignes")
        print("   Colonnes:")
        for col in schema:
            print(f"     - {col[0]} ({col[1]})")
        
        return count, schema
    except Exception as e:
        print(f"❌ Erreur pour la table {table_name}: {e}")
        return 0, []

def load_table_to_dataframe(conn, table_name, sample_size=None):
    """Charger une table dans un DataFrame pandas"""
    try:
        if sample_size:
            query = f"SELECT * FROM {table_name} LIMIT {sample_size}"
            print(f"📥 Chargement d'un échantillon de {sample_size} lignes de '{table_name}'...")
        else:
            query = f"SELECT * FROM {table_name}"
            print(f"📥 Chargement complet de la table '{table_name}'...")
        
        df = conn.execute(query).df()
        print(f"✅ DataFrame créé: {df.shape[0]} lignes, {df.shape[1]} colonnes")
        return df
    except Exception as e:
        print(f"❌ Erreur lors du chargement: {e}")
        return None

def generate_profile_report(df, table_name, output_dir):
    """Générer un rapport de profilage avec YData Profiling"""
    try:
        print(f"🔍 Génération du rapport de profilage pour '{table_name}'...")
        
        # Configuration du rapport
        profile = ProfileReport(
            df,
            title=f"Analyse des données - {table_name}",
            dataset={
                "description": f"Rapport de profilage automatique pour la table {table_name}",
                "copyright_holder": "Analyse des données",
                "copyright_year": "2024",
            },
            variables={
                "descriptions": {}
            },
            # Configuration pour optimiser les performances
            minimal=False,
            explorative=True,
        )
        
        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Sauvegarder le rapport
        output_file = os.path.join(output_dir, f"{table_name}_profile_report.html")
        profile.to_file(output_file)
        
        print(f"✅ Rapport sauvegardé: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport: {e}")
        return None

def main():
    """Fonction principale"""
    print("🚀 Début de l'analyse des données DuckDB avec YData Profiling")
    print("=" * 60)
    
    # Vérifier que le fichier DB existe
    if not os.path.exists(DB_PATH):
        print(f"❌ Le fichier DB n'existe pas: {DB_PATH}")
        return
    
    # Se connecter à la base
    conn = connect_to_duckdb(DB_PATH)
    if not conn:
        return
    
    try:
        # Lister les tables
        tables = list_tables(conn)
        if not tables:
            print("❌ Aucune table trouvée")
            return
        
        print("\n" + "=" * 60)
        
        # Analyser chaque table
        for table_name in tables:
            print(f"\n📋 Analyse de la table: {table_name}")
            print("-" * 40)
            
            # Obtenir les informations de la table
            count, schema = get_table_info(conn, table_name)
            
            if count == 0:
                print(f"⚠️  Table '{table_name}' vide, passage à la suivante")
                continue
            
            # Décider de la taille de l'échantillon
            sample_size = None
            if count > 100000:
                sample_size = 50000  # Échantillonner les grandes tables
                print(f"🎯 Table volumineuse ({count:,} lignes), échantillonnage à {sample_size} lignes")
            
            # Charger les données
            df = load_table_to_dataframe(conn, table_name, sample_size)
            if df is None or df.empty:
                print(f"⚠️  Impossible de charger la table '{table_name}'")
                continue
            
            # Générer le rapport
            report_file = generate_profile_report(df, table_name, OUTPUT_DIR)
            if report_file:
                print(f"📊 Rapport disponible: {report_file}")
            
            print("-" * 40)
    
    finally:
        # Fermer la connexion
        conn.close()
        print(f"\n✅ Analyse terminée. Rapports dans le dossier: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
