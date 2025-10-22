#!/usr/bin/env python3
"""
Test script pour vérifier le chargement des données depuis S3.
"""

import sys
from pathlib import Path

# Ajouter le répertoire _data_utils au path
sys.path.insert(0, str(Path(__file__).parent / "_data_utils"))

from data_utils_ratings import load_interactions_raw, load_enriched_interactions
from data_utils_recipes import load_recipes_raw

def test_s3_loading():
    """Test complet du chargement S3."""
    print("=" * 80)
    print("🧪 Test du chargement des données depuis S3")
    print("=" * 80)
    
    try:
        # Test 1: Charger les recettes
        print("\n📦 Test 1: Chargement des recettes depuis S3...")
        df_recipes = load_recipes_raw(use_s3=True, limit=10)
        print(f"✅ Succès! Shape: {df_recipes.shape}")
        print(f"   Colonnes: {df_recipes.columns[:5]}...")
        
        # Test 2: Charger les interactions
        print("\n📦 Test 2: Chargement des interactions depuis S3...")
        df_interactions = load_interactions_raw(use_s3=True)
        print(f"✅ Succès! Shape: {df_interactions.shape}")
        print(f"   Colonnes: {df_interactions.columns}")
        
        # Test 3: Charger les interactions enrichies
        print("\n📦 Test 3: Chargement des interactions enrichies depuis S3...")
        df_enriched = load_enriched_interactions(use_s3=True)
        print(f"✅ Succès! Shape: {df_enriched.shape}")
        print(f"   Colonnes: {df_enriched.columns}")
        
        # Afficher un aperçu
        print("\n" + "=" * 80)
        print("📊 Aperçu des données (5 premières lignes des interactions enrichies)")
        print("=" * 80)
        print(df_enriched.head(5))
        
        print("\n" + "=" * 80)
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_s3_loading()
    sys.exit(0 if success else 1)
