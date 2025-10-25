import streamlit as st
from streamlit_extras.switch_page_button import switch_page_button

# Test simple
st.write("Test streamlit-extras")

# Voir ce qui est disponible
try:
    from streamlit_extras import button_selector
    st.write("✅ button_selector disponible")
    st.write(dir(button_selector))
except Exception as e:
    st.write(f"❌ button_selector: {e}")

try:
    from streamlit_extras.switch_page_button import switch_page_button
    st.write("✅ switch_page_button disponible")
except Exception as e:
    st.write(f"❌ switch_page_button: {e}")
