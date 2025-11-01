"""Language selector widget for Streamlit bilingual support."""

import streamlit as st
from typing import Literal

Language = Literal["en", "fr"]


def init_language() -> Language:
    """Initialize language in session state.

    Checks URL query parameters for ?lang=en or ?lang=fr
    If no parameter is provided, defaults to French.

    Returns:
        Current language (defaults to French)
    """
    if "language" not in st.session_state:
        # Check for language query parameter
        try:
            query_params = st.query_params
            lang_param = query_params.get("lang", "fr")
            # Validate parameter
            if lang_param in ["en", "fr"]:
                st.session_state.language = lang_param
            else:
                st.session_state.language = "fr"
        except Exception:
            # Fallback if query_params not available
            st.session_state.language = "fr"
    return st.session_state.language


def render_language_selector() -> None:
    """Render language selector widget in sidebar.

    Displays a selectbox allowing users to switch between French and English.
    When language changes, triggers a rerun to update the entire interface.
    """
    languages = {
        "🇫🇷 Français": "fr",
        "🇬🇧 English": "en",
    }

    current_lang = st.session_state.get("language", "fr")
    current_display = "🇫🇷 Français" if current_lang == "fr" else "🇬🇧 English"

    selected = st.sidebar.selectbox(
        "Language / Langue",
        options=list(languages.keys()),
        index=list(languages.values()).index(current_lang),
        key="lang_selector",
        label_visibility="collapsed",
    )

    new_lang = languages[selected]
    if new_lang != current_lang:
        st.session_state.language = new_lang
        st.rerun()


def get_current_language() -> Language:
    """Get current language from session state.

    Returns:
        Current language code ('fr' or 'en')
    """
    return st.session_state.get("language", "fr")
