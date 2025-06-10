import streamlit as st
from translations import load_translations

def home(user):
    lang = st.session_state.get('language', 'en')
    translations = load_translations(lang)
    t = translations['home']

    # Welcome message with user's name
    st.markdown(
        f"<h3 style='text-align: center;'>{t['welcome'].format(name=user['name'])}</h3>",
        unsafe_allow_html=True
    )
    # Dashboard introduction
    st.markdown(
        f"""
        <p style='text-align: center; font-size: 18px;'>
        <b>{t['intro']['title']}</b><br>
        {t['intro']['description']}
        <hr>
        <h4 style='text-align: center;'>{t['actions']['title']}</h4>
        <ul style='font-size: 16px;'>
            <li>{t['actions']['statistics']}</li>
            <li>{t['actions']['manage_data']}</li>
            <li>{t['actions']['analyze']}</li>
        </ul>
        <p style='text-align: center; font-size: 16px;'>
        {t['navigation_tip']}
        </p>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    st.session_state['language'] = 'en'  # Default language
    home({"name": "Test User"})