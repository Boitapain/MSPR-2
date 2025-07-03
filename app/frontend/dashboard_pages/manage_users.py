import streamlit as st
import pandas as pd
import requests
import time
from translations import load_translations

def manage_users(user):
    lang = st.session_state.get('language', 'en')
    translations = load_translations(lang)
    t = translations['manage_users']

    st.markdown(f"<h3 style='text-align: center;'>{t['title']}</h3>", unsafe_allow_html=True)

    if 'users_updated' in st.session_state:
        st.session_state.pop("users_updated")
        st.rerun()

    try:
        response = requests.get(f"{st.session_state['API_URL']}/users")
        response.raise_for_status()
        data = response.json().get("users")
        users = pd.DataFrame(data, columns=[
            "id", "name", "email", "country", "isAdmin"
        ])

        if user["isAdmin"]:
            cols = st.columns([1, 4, 1])
            with cols[1]:
                users_edited = st.data_editor(
                    users,
                    column_config={
                        "id": st.column_config.NumberColumn(),
                        "name": st.column_config.TextColumn(),
                        "email": st.column_config.TextColumn(),
                        "country": st.column_config.TextColumn(
                            default="USA"
                        ),
                        "isAdmin": st.column_config.CheckboxColumn(
                            default=False
                        )
                    },
                    num_rows="dynamic"
                )
                if st.button(
                    t['update_button'],
                    help=t['help_messages']['update_button']
                ):
                    users_edited["country"] = users_edited["country"].fillna("USA")
                    if users_edited.isnull().values.any():
                        st.error(t['empty_fields_error'])
                    else:
                        data_json = users_edited.to_json(orient="records")
                        response = requests.put(
                            f"{st.session_state['API_URL']}/update_users",
                            json={"users": data_json},
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            my_bar = st.progress(0, text=t['update_progress'].format(percent=0))
                            my_bar.help(t['help_messages']['progress_bar'])

                            for percent_complete in range(100):
                                time.sleep(0.01)
                                my_bar.progress(
                                    percent_complete + 1,
                                    text=t['update_progress'].format(percent=percent_complete + 1)
                                )
                            time.sleep(1)
                            my_bar.empty()
                            st.session_state["users_updated"] = True
                            st.rerun()
                        else:
                            st.error(t['update_error'])
        else:
            cols = st.columns([1, 2, 1])
            with cols[1]:
                st.dataframe(users, help=t['help_messages']['readonly_view'])
    except requests.exceptions.RequestException:
        st.error(t['no_data_error'])