"""Module pour charger les données avec cache Streamlit.

Ce module wrapper les fonctions de chargement depuis mangetamain_data_utils
avec le décorateur @st.cache_data pour améliorer les performances.
"""

import streamlit as st
from mangetamain_data_utils.data_utils_recipes import load_recipes_clean
from mangetamain_data_utils.data_utils_interactions import (
    load_interactions_sample,
    load_ratings_for_longterm_analysis,
)


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des recettes depuis S3...")
def get_recipes_clean():
    """Charge les recettes depuis S3 avec cache (1h)."""
    return load_recipes_clean()


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des interactions depuis S3...")
def get_interactions_sample():
    """Charge les interactions échantillonnées depuis S3 avec cache (1h)."""
    return load_interactions_sample()


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des ratings depuis S3...")
def get_ratings_longterm():
    """Charge les ratings pour analyse long-terme depuis S3 avec cache (1h)."""
    return load_ratings_for_longterm_analysis()
