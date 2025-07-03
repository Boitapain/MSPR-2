import streamlit as st
import pandas as pd
import requests
import time
from translations import load_translations

def db_viz(user):
    lang = st.session_state.get('language', 'en')
    translations = load_translations(lang)
    t = translations['db_viz']

    st.markdown(f"<h3 style='text-align: center;'>{t['title']}</h3>", unsafe_allow_html=True)
    
    if 'updated' in st.session_state:
        st.session_state.pop("updated")
        st.rerun()
    
    try:
        response = requests.get(f"{st.session_state['API_URL']}/diseases")
        response.raise_for_status()  
        # Get data from the response or session state
        data = response.json().get("diseases")
        diseases = pd.DataFrame(data, columns=[
            "Id", "Nom", "Month", "Country_Region", "Confirmed", "Deaths", "Recovered", 
            "New_cases", "New_deaths", "New_recovered"
        ])
        # Display data editor if user is admin, otherwise display the dataframe
        if user["isAdmin"] and user["country"] == "USA":
            diseases_edited = st.data_editor(
                diseases, 
                column_config={
                    "Id": st.column_config.NumberColumn(
                        default=0,
                    ),
                }, 
                num_rows="dynamic"
            )
            if st.button(
                t["admin_section"]["update_button"],
                help=t["help_messages"]["update_button"]
            ):
                data_json = diseases_edited.to_json(orient="records")
                response = requests.put(f"{st.session_state['API_URL']}/update_diseases_route", json={"diseases": data_json}, headers={"Content-Type": "application/json"})
                if response.status_code == 200:
                    my_bar = st.progress(0, text=t["admin_section"]["progress_text"].format(percent=0))
                    my_bar.help(t["help_messages"]["progress_bar"])

                    for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=t["admin_section"]["progress_text"].format(percent=percent_complete + 1))
                    time.sleep(1)
                    my_bar.empty()
                    st.session_state.update({"df": diseases_edited})
                    st.session_state["updated"] = True
                    st.rerun()
                else:
                    st.error(t["admin_section"]["error_message"])

        else:
            st.dataframe(diseases)
    except requests.exceptions.RequestException:
        st.error(t["error_message"])