"""Module pour charger les données avec cache Streamlit.

Ce module wrapper les fonctions de chargement depuis mangetamain_data_utils
avec le décorateur @st.cache_data pour améliorer les performances.

Note: Les imports sont faits dans les fonctions pour éviter les erreurs
quand mangetamain_data_utils n'est pas disponible (ex: tests locaux).
"""

import streamlit as st


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des recettes depuis S3...")
def get_recipes_clean():
    """Charge les recettes depuis S3 avec cache (1h)."""
    from mangetamain_data_utils.data_utils_recipes import load_recipes_clean

    return load_recipes_clean()


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des interactions depuis S3...")
def get_interactions_sample():
    """Charge les interactions échantillonnées depuis S3 avec cache (1h)."""
    from mangetamain_data_utils.data_utils_interactions import (
        load_interactions_sample,
    )

    return load_interactions_sample()


@st.cache_data(ttl=3600, show_spinner="🔄 Chargement des ratings depuis S3...")
def get_ratings_longterm():
    """Charge les ratings pour analyse long-terme depuis S3 avec cache (1h)."""
    from mangetamain_data_utils.data_utils_ratings import (
        load_ratings_for_longterm_analysis,
    )

    return load_ratings_for_longterm_analysis()
