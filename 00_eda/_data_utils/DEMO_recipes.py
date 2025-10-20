"""
🎯 DÉMONSTRATION du module data_utils_recipes_recipes.py

Ce script montre comment utiliser les 4 fonctions principales du module.
"""

import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent))

from data_utils_recipes_recipes import *

# =============================================================================
# 💡 EXEMPLE D'USAGE RECOMMANDÉ
# =============================================================================

print("="*70)
print("🚀 DÉMONSTRATION - Module data_utils_recipes")
print("="*70)
print()

# ----------------------------------------------------------------------------
# Méthode 1 : Pipeline complet en une seule commande (RECOMMANDÉ)
# ----------------------------------------------------------------------------
print("📌 Méthode 1 : Pipeline complet (load_clean_recipes)")
print("-" * 70)

df = load_clean_recipes()
print(f"\n✅ DataFrame prêt : {df.shape[0]:,} lignes × {df.shape[1]} colonnes\n")

# Afficher un échantillon
show_recipes_sample(df, n=3)

# Rapport de qualité
report = analyze_recipe_quality(df)

# ----------------------------------------------------------------------------
# Méthode 2 : Pipeline étape par étape (POUR CONTRÔLE FIN)
# ----------------------------------------------------------------------------
print("\n\n📌 Méthode 2 : Pipeline étape par étape")
print("-" * 70)

# Étape 1 : Chargement
df_raw = load_recipes_raw(limit=10000)  # Limiter pour la démo

# Étape 2 : Nettoyage
df_clean = clean_recipes(df_raw)

# Étape 3 : Enrichissement
df_enriched = enrich_recipes(df_clean)

# Étape 4 : Analyse qualité
report = analyze_recipe_quality(df_enriched)

print("\n✅ Pipeline terminé avec succès!")
print()

# ----------------------------------------------------------------------------
# Exemples d'analyses rapides
# ----------------------------------------------------------------------------
print("\n\n📊 EXEMPLES D'ANALYSES")
print("-" * 70)

# Top 5 années avec le plus de recettes
if "year" in df.columns:
    top_years = (
        df.group_by("year")
        .agg(pl.len().alias("n_recipes"))
        .sort("n_recipes", descending=True)
        .head(5)
    )
    print("\n🏆 Top 5 années les plus productives :")
    print(top_years)

# Complexité moyenne par saison
if "season" in df.columns and "complexity_score" in df.columns:
    complexity_season = (
        df.group_by("season")
        .agg(pl.mean("complexity_score").alias("avg_complexity"))
        .sort("avg_complexity", descending=True)
    )
    print("\n🎯 Complexité moyenne par saison :")
    print(complexity_season)

# Calories moyennes par année
if "year" in df.columns and "calories" in df.columns:
    calories_year = (
        df.group_by("year")
        .agg(pl.mean("calories").alias("avg_calories"))
        .sort("year")
        .tail(5)
    )
    print("\n🔥 Calories moyennes (5 dernières années) :")
    print(calories_year)

print("\n" + "="*70)
print("✅ Démonstration terminée !")
print("="*70)
