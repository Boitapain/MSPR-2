import streamlit as st
import requests
import re
from translations import load_translations

def profile(user):
    lang = st.session_state['language']
    translations = load_translations(lang)
    t = translations['profile']
    
    st.markdown(f"<h1 style='text-align: center;'>{t['title']}</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    # Display country information
    with col1:
        st.markdown(
            f"<p style='font-size:1.5rem;'>{t['user_info']['user']} <b>{user['name']}</b></p>", 
            unsafe_allow_html=True,
        )
    # Display language selection only if the user is from Switzerland
    with col2: 
        st.markdown(
            f"<p style='font-size:1.5rem;'> <span>{user['email']}</span></p>", 
            unsafe_allow_html=True
        )    
    
    st.markdown(
        f"<p style='font-size:1.5rem;'>{t['user_info']['country']} <span>{user['country']}</span></p>", 
        unsafe_allow_html=True
    )

    # Display language selection only if the user is from Switzerland
    if user["country"] == "Suisse":
        # Mapping between display names and language codes
        lang_map = {
            'Italiano': 'it',
            'Français': 'fr',
            'Deutsch': 'de'
        }

        # Reverse mapping for default index
        lang_display = list(lang_map.keys())
        lang_codes = list(lang_map.values())

        # Get default index
        default_index = lang_codes.index(lang) if lang in lang_codes else 0

        # Display selectbox
        selected_display = st.selectbox(
            t['language_selection'],
            options=lang_display,
            index=default_index,
            key="language_selector",
            help=t['help_messages']['language_selector']
        )

        # Get corresponding language code
        new_lang = lang_map[selected_display]

        # Update session state if language changed
        if new_lang != lang:
            st.session_state['update_language'] = True
            st.session_state['language'] = new_lang
            st.rerun()  # Rerun the app to apply the new language
    
    st.markdown(
        f"<p style='font-size:1.5rem;'>{t['user_info']['isAdmin']} <b>{True if user['isAdmin'] == 1 else False}</b></h3>", 
        unsafe_allow_html=True
    )

    st.markdown("---")
    
    # Toggle visibility of the password form
    if 'show_password_form' not in st.session_state:
        st.session_state['show_password_form'] = False

    # Clickable text to show/hide
    if st.button(
        t['password_section']['title'], 
        use_container_width=True,
        help=t['help_messages']['password_toggle']
    ):
        st.session_state['show_password_form'] = not st.session_state['show_password_form']

    if st.session_state['show_password_form']:
        with st.form("update_password_form"):
            old_password = st.text_input(
                t['password_section']['current_password'], 
                type="password"
                )
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
            submitted = st.form_submit_button(
                t['password_section']['update_button'], 
                use_container_width=True,
                help=t['help_messages']['password_update']
            )
            if submitted:
                if not old_password or not new_password or not confirm_password:
                    st.error(t['password_section']['errors']['required'])
                elif new_password != confirm_password:
                    st.error(t['password_section']['errors']['mismatch'])
                else:
                    if (
                        len(new_password) < 8
                        or not re.search(r"[a-z]", new_password)
                        or not re.search(r"[A-Z]", new_password)
                        or not re.search(r"[^a-zA-Z0-9]", new_password)
                    ):
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


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(
            t['logout_button'], 
            icon=":material/logout:",
            help=t['help_messages']['logout']
        ):
            st.session_state.clear()
            st.rerun()
