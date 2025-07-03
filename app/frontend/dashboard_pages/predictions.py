import streamlit as st
import requests
import pandas as pd
import time
from sklearn.preprocessing import LabelEncoder
from translations import load_translations

def predictions():
    lang = st.session_state['language']
    translations = load_translations(lang)
    t = translations['predictions']

    st.markdown(f"<h3 style='text-align: center;'>{t['title']}</h3>", unsafe_allow_html=True)

    if 'predicted' in st.session_state:
        st.session_state.pop("predicted")
        st.rerun()
    
    # Initialize model version in session state if not exists
    if 'model_version' not in st.session_state:
        st.session_state.model_version = 'v1'
    
    # Load necessary data
    df = pd.read_csv("data_etl_output.csv")
    mspr_df = pd.read_csv("mspr2_dataset.csv")  # For population data
    
    # Prepare country encoder
    le = LabelEncoder()
    le.fit(df['Country'])
    country_to_code = {country: int(code) for country, code in zip(le.classes_, le.transform(le.classes_))}
    
    # Get population mapping
    country_to_population = dict(zip(mspr_df['Country'], mspr_df['Population']))

    # Model selection - updates session state when changed
    model_version = st.radio(
        t['input_labels']['model_version'],
        options=['v1', 'v2'],
        horizontal=True,
        index=0 if st.session_state.model_version == 'v1' else 1,
        key="model_version_radio",
        on_change=lambda: setattr(st.session_state, 'model_version', st.session_state.model_version_radio)
    )

    # Update session state model version
    st.session_state.model_version = model_version

    if st.session_state.model_version == 'v1':
        # Original v1 inputs
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
                key="country_v1",
                help=t['help_messages']['country_select']
            )
            selected_country_code = country_display[1]
    else:
        # v2 inputs - 3 months of data
        st.markdown("**Current Month**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                t['input_labels']['current_cases'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="current_cases"
            )
        with col2:
            st.number_input(
                t['input_labels']['current_deaths'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="current_deaths"
            )
        with col3:
            st.number_input(
                t['input_labels']['current_recovered'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="current_recovered"
            )
        
        st.markdown("**Month-1**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                t['input_labels']['month1_cases'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="month1_cases"
            )
        with col2:
            st.number_input(
                t['input_labels']['month1_deaths'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="month1_deaths"
            )
        with col3:
            st.number_input(
                t['input_labels']['month1_recovered'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="month1_recovered"
            )
        
        st.markdown("**Month-2**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                t['input_labels']['month2_cases'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="month2_cases"
            )
        with col2:
            st.number_input(
                t['input_labels']['month2_deaths'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="month2_deaths"
            )
        with col3:
            st.number_input(
                t['input_labels']['month2_recovered'],
                min_value=0,
                max_value=1000000,
                value=0,
                key="month2_recovered"
            )
        
        country_display = st.selectbox(
            t['input_labels']['country'],
            options=[(name, code) for name, code in country_to_code.items()],
            format_func=lambda x: x[0],
            index=0,
            key="country_v2",
            help=t['help_messages']['country_select']
        )
        selected_country_code = country_display[1]
        selected_country_name = country_display[0]

    # Predict button
    col_left, _ = st.columns([1, 4])  # Variable inutilisée remplacée par _
    with col_left:
        predict_clicked = st.button(
            t['predict_button'],
            use_container_width=True,
            help=t['help_messages']['predict_button']
        )

    if predict_clicked:
        with st.spinner(t['progress_text']):
            progress = st.progress(0)
            
            for i in range(1, 101, 10):
                time.sleep(0.03)
                progress.progress(i)
            
            # Prepare the request data with logging
            if st.session_state.model_version == 'v1':
                request_data = {
                    "cases": st.session_state.cases,
                    "deaths": st.session_state.deaths,
                    "recovered": st.session_state.recovered,
                    "country": selected_country_code
                }
                endpoint = f"{st.session_state['API_URL']}/predict"
            else:
                request_data = {
                    "cases_lag1": st.session_state.current_cases,
                    "deaths_lag1": st.session_state.current_deaths,
                    "recovered_lag1": st.session_state.current_recovered,
                    "cases_lag2": st.session_state.month1_cases,
                    "deaths_lag2": st.session_state.month1_deaths,
                    "recovered_lag2": st.session_state.month1_recovered,
                    "cases_lag3": st.session_state.month2_cases,
                    "deaths_lag3": st.session_state.month2_deaths,
                    "recovered_lag3": st.session_state.month2_recovered,
                    "country": selected_country_code,
                    "population": country_to_population.get(selected_country_name, 1000000)
                }
                endpoint = f"{st.session_state['API_URL']}/predict_v2"
            
            try:
                response = requests.post(endpoint, json=request_data)
                
            except Exception as e:
                st.error(f"API Request Failed: {str(e)}")
                return
            
            progress.progress(100)
            progress.empty()
            
        if response.status_code == 200:
            prediction = response.json().get("prediction", [[0, 0, 0]])  # Default fallback
            
            # Safely convert predictions to integers with fallback to 0
            confirmed = int(prediction[0][0]) if prediction and prediction[0] and prediction[0][0] is not None else 0
            deaths = int(prediction[0][1]) if prediction and prediction[0] and len(prediction[0]) > 1 and prediction[0][1] is not None else 0
            recovered = int(prediction[0][2]) if prediction and prediction[0] and len(prediction[0]) > 2 and prediction[0][2] is not None else 0
            
            st.session_state.predicted = prediction
            st.markdown(
                f"""
                <div style="border-radius: 10px; border: 1px solid #e6e6e6; padding: 2rem; margin-top: 2rem; background: #fafbfc;">
                    <h4 style="text-align:center; color:#222;">{t.get('results_title', 'Prediction Results')}</h4>
                    <div style="font-size: 1.2rem; text-align:center;">
                        <b>{t.get('results_labels', {}).get('confirmed', 'Confirmed')}</b> {confirmed:,}<br>
                        <b>{t.get('results_labels', {}).get('deaths', 'Deaths')}</b> {deaths:,}<br>
                        <b>{t.get('results_labels', {}).get('recovered', 'Recovered')}</b> {recovered:,}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error(f"{t['error_prefix']} {response.json().get('message')}")