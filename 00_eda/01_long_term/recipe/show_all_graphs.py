#!/usr/bin/env python3
"""
Script pour afficher tous les graphiques des analyses de tendances
"""

import sys
sys.path.append('../../')

from recipe_analysis_trendline_clean import (
    analyse_trendline_1,
    analyse_trendline_2, 
    analyse_trendline_3,
    analyse_trendline_4,
    analyse_trendline_5,
    analyse_trendline_6
)

def main():
    """
    Fonction principale pour exécuter toutes les analyses et afficher tous les graphiques.
    """
    
    print("🚀 Démarrage de toutes les analyses...\n")
    
    print("📊 Analyse 1: Évolution du nombre de recettes")
    analyse_trendline_1()
    
    print("\n⏱️ Analyse 2: Évolution de la durée de préparation")
    analyse_trendline_2()
    
    print("\n🔧 Analyse 3: Évolution de la complexité")
    analyse_trendline_3()
    
    print("\n🥗 Analyse 4: Évolution nutritionnelle")
    analyse_trendline_4()
    
    print("\n🧄 Analyse 5: Évolution des ingrédients")
    analyse_trendline_5()
    
    print("\n🏷️ Analyse 6: Évolution des tags")
    analyse_trendline_6()
    
    print("\n✅ Toutes les analyses terminées avec succès !")

if __name__ == "__main__":
    main()