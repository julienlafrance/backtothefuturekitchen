"""Language selector widget for Streamlit bilingual support."""

import streamlit as st
from typing import Literal

Language = Literal["en", "fr"]


def init_language() -> Language:
    """Initialize language in session state.

    Checks URL query parameters for ?lang=en or ?lang=fr
    If no parameter is provided, defaults to English.

    Returns:
        Current language (defaults to English)
    """
    if "language" not in st.session_state:
        # Check for language query parameter
        try:
            query_params = st.query_params
            lang_param = query_params.get("lang", "en")
            # Validate parameter
            if lang_param in ["en", "fr"]:
                st.session_state.language = lang_param
            else:
                st.session_state.language = "en"
        except Exception:
            # Fallback if query_params not available
            st.session_state.language = "en"
    return st.session_state.language


def render_language_selector() -> None:
    """Render language selector widget in sidebar.

    Displays a selectbox allowing users to switch between French and English.
    When language changes, triggers a rerun to update the entire interface.
    """
    # Custom CSS to ensure selectbox options have correct background color
    st.markdown(
        """
        <style>
        /* Force selectbox dropdown background to match theme */
        [data-baseweb="select"] > div {
            background-color: #333333 !important;
        }
        [data-baseweb="popover"] {
            background-color: #333333 !important;
        }
        /* Selectbox options */
        [data-baseweb="menu"] {
            background-color: #333333 !important;
        }
        [role="option"] {
            background-color: #333333 !important;
        }
        [role="option"]:hover {
            background-color: #444444 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    languages = {
        "🇫🇷 Français": "fr",
        "🇬🇧 English": "en",
    }

    current_lang = st.session_state.get("language", "en")

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
    return st.session_state.get("language", "en")
