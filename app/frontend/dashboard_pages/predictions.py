import streamlit as st
import requests
import pandas as pd
import time
from sklearn.preprocessing import LabelEncoder
from translations import load_translations

from sklearn.preprocessing import LabelEncoder
from translations import load_translations

def predictions(user):
    lang = st.session_state['language']
    translations = load_translations(lang)
    t = translations['predictions']  # Note: Fixed typo from 'predictions'

    st.markdown(f"<h3 style='text-align: center;'>{t['title']}</h3>", unsafe_allow_html=True)

    if 'predicted' in st.session_state:
        st.session_state.pop("predicted")
        st.rerun()
    
    df = pd.read_csv("data_etl_output.csv")
    countries = sorted(df['Country'].unique())
    le = LabelEncoder()
    le.fit(df['Country'])
    country_to_code = {country: int(code) for country, code in zip(le.classes_, le.transform(le.classes_))}

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.number_input(
            t['input_labels']['cases'],
            min_value=0,
            max_value=1000000,
            value=0,
            key="cases",
            help=t['help_messages']['cases_input']
        )
    with col2:
        st.number_input(
            t['input_labels']['deaths'],
            min_value=0,
            max_value=1000000,
            value=0,
            key="deaths",
            help=t['help_messages']['deaths_input']
        )
    with col3:
        st.number_input(
            t['input_labels']['recovered'],
            min_value=0,
            max_value=1000000,
            value=0,
            key="recovered",
            help=t['help_messages']['recovered_input']
        )
    with col4:
        country_display = st.selectbox(
            t['input_labels']['country'],
            options=[(name, code) for name, code in country_to_code.items()],
            format_func=lambda x: x[0],
            index=0,
            key="country",
            help=t['help_messages']['country_select']
        )
        selected_country_code = country_display[1]

    # Center the button using columns
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        predict_clicked = st.button(
            t['predict_button'],
            use_container_width=True,
            help=t['help_messages']['predict_button']
        )

    if predict_clicked:
        with st.spinner(t['progress_text']):
            progress = st.progress(0)
            progress.help(t['help_messages']['progress_bar'])
            
            # Simulate progress
            for i in range(1, 101, 10):
                time.sleep(0.03)
                progress.progress(i)
                
            response = requests.post(f"{st.session_state['API_URL']}/predict", json={
                "cases": st.session_state.cases,
                "deaths": st.session_state.deaths,
                "recovered": st.session_state.recovered,
                "country": selected_country_code
            })
            progress.progress(100)
            progress.empty()
            
        if response.status_code == 200:
            prediction = response.json().get("prediction")
            st.session_state.predicted = prediction
            st.markdown(
                f"""
                <div style="border-radius: 10px; border: 1px solid #e6e6e6; padding: 2rem; margin-top: 2rem; background: #fafbfc;">
                    <h4 style="text-align:center; color:#222;">{t['results_title']}</h4>
                    <p style="text-align:center; font-size: 0.8rem; color: #666;"></p>
                    <div style="font-size: 1.2rem; text-align:center;">
                        <b>{t['results_labels']['confirmed']}</b> {int(prediction[0][0]):,}<br>
                        <b>{t['results_labels']['deaths']}</b> {int(prediction[0][1]):,}<br>
                        <b>{t['results_labels']['recovered']}</b> {int(prediction[0][2]):,}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='color: #b00020; text-align:center; font-weight:bold;'>{t['error_prefix']} {response.json().get('message')}</div>",
                unsafe_allow_html=True
            )