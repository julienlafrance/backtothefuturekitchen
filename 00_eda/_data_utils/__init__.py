# =============================================================================
# _data_utils/__init__.py
# Point d’entrée du module (BACKWARD COMPATIBLE)
# =============================================================================
"""
🎯 Module unifié data_utils
Permet d'importer toutes les fonctions communes, recettes et interactions
avec un simple :
    from data_utils import *
"""

# _data_utils/__init__.py
from .data_utils_common import *
from .data_utils_ratings import *
from .data_utils_recipes import *

print("✅ _data_utils module chargé (common + ratings + recipes)")
