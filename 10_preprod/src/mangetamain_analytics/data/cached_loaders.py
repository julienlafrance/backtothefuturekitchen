"""Module pour charger les données avec cache Streamlit.

Ce module wrapper les fonctions de chargement avec le décorateur @st.cache_data
pour améliorer les performances. La logique de chargement et de gestion
d'erreurs est déléguée à la classe DataLoader.
"""

import streamlit as st
from .loaders import DataLoader


# Instance globale du loader
_loader = DataLoader()


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des recettes depuis S3...")
def get_recipes_clean():
    """Charge les recettes depuis S3 avec cache (1h)."""
    return _loader.load_recipes()


# @st.cache_data(ttl=3600, show_spinner="🔄 Chargement des interactions depuis S3...")
# def get_interactions_sample():
#     """Charge les interactions échantillonnées depuis S3 avec cache (1h)."""
#     from mangetamain_data_utils.data_utils_interactions import (
#         load_interactions_sample,
#     )
#
#     return load_interactions_sample()
# NOTE: Fonction commentée - module data_utils_interactions non disponible


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des ratings depuis S3...")
def get_ratings_longterm(min_interactions=100, return_metadata=False, verbose=False):
    """Charge les ratings pour analyse long-terme depuis S3 avec cache (1h)."""
    return _loader.load_ratings(min_interactions, return_metadata, verbose)
