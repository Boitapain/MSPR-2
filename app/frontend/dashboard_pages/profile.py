import streamlit as st
import requests
import re
from translations import load_translations

def _display_user_info(user, t):
    """Affiche les informations de l'utilisateur"""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<p style='font-size:1.5rem;'>{t['user_info']['user']} <b>{user['name']}</b></p>", 
            unsafe_allow_html=True,
        )
    with col2: 
        st.markdown(
            f"<p style='font-size:1.5rem;'> <span>{user['email']}</span></p>", 
            unsafe_allow_html=True
        )    
    
    st.markdown(
        f"<p style='font-size:1.5rem;'>{t['user_info']['country']} <span>{user['country']}</span></p>", 
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='font-size:1.5rem;'>{t['user_info']['isAdmin']} <b>{bool(user['isAdmin'])}</b></h3>", 
        unsafe_allow_html=True
    )
    st.markdown("---")

def _handle_language_selection(user, lang, t):
    """Gère la sélection de langue pour les utilisateurs suisses"""
    if user["country"] != "Suisse":
        return
    
    lang_map = {'Italiano': 'it', 'Français': 'fr', 'Deutsch': 'de'}
    lang_display = list(lang_map.keys())
    lang_codes = list(lang_map.values())
    default_index = lang_codes.index(lang) if lang in lang_codes else 0

    selected_display = st.selectbox(
        t['language_selection'],
        options=lang_display,
        index=default_index,
        key="language_selector",
        help=t['help_messages']['language_selector']
    )

    new_lang = lang_map[selected_display]
    if new_lang != lang:
        st.session_state['update_language'] = True
        st.session_state['language'] = new_lang
        st.rerun()

def _validate_password(new_password):
    """Valide les critères du mot de passe"""
    return (
        len(new_password) >= 8 and
        re.search(r"[a-z]", new_password) and
        re.search(r"[A-Z]", new_password) and
        re.search(r"[^a-zA-Z0-9]", new_password)
    )

def _handle_password_update(user, t):
    """Gère la mise à jour du mot de passe"""
    if 'show_password_form' not in st.session_state:
        st.session_state['show_password_form'] = False

    if st.button(
        t['password_section']['title'], 
        use_container_width=True,
        help=t['help_messages']['password_toggle']
    ):
        st.session_state['show_password_form'] = not st.session_state['show_password_form']

    if not st.session_state['show_password_form']:
        return

    with st.form("update_password_form"):
        old_password = st.text_input(t['password_section']['current_password'], type="password")
        new_password = st.text_input(
            t['password_section']['new_password'], 
            type="password",
            help=t['help_messages']['new_password']
        )
        confirm_password = st.text_input(
            t['password_section']['confirm_password'], 
            type="password",
            help=t['help_messages']['confirm_password']
        )
        
        if not st.form_submit_button(
            t['password_section']['update_button'], 
            use_container_width=True,
            help=t['help_messages']['password_update']
        ):
            return

        if not old_password or not new_password or not confirm_password:
            st.error(t['password_section']['errors']['required'])
            return
        if new_password != confirm_password:
            st.error(t['password_section']['errors']['mismatch'])
            return
        if not _validate_password(new_password):
            st.error(t['password_section']['errors']['criteria'])
            return

        response = requests.put(
            f"{st.session_state['API_URL']}/update_password",
            json={
                "email": user["email"],
                "old_password": old_password,
                "new_password": new_password,
                "confirm_password": confirm_password
            }
        )
        if response.status_code == 200:
            st.success(t['password_section']['success'])
        else:
            st.error(response.json().get("message", t['password_section']['api_error']))

def profile(user):
    lang = st.session_state['language']
    translations = load_translations(lang)
    t = translations['profile']
    
    st.markdown(f"<h1 style='text-align: center;'>{t['title']}</h1>", unsafe_allow_html=True)

    _display_user_info(user, t)
    _handle_language_selection(user, lang, t)
    _handle_password_update(user, t)

    col1, _, _, _ = st.columns(4)
    with col1:
        if st.button(
            t['logout_button'], 
            icon=":material/logout:",
            help=t['help_messages']['logout']
        ):
            st.session_state.clear()
            st.rerun()