import streamlit as st
import requests
import pandas as pd
import time
from sklearn.preprocessing import LabelEncoder
from translations import load_translations

def _load_data():
    """Charge les données nécessaires et prépare les mappings."""
    df = pd.read_csv("data_etl_output.csv")
    mspr_df = pd.read_csv("mspr2_dataset.csv")
    
    le = LabelEncoder()
    le.fit(df['Country'])
    country_to_code = {country: int(code) for country, code in zip(le.classes_, le.transform(le.classes_))}
    country_to_population = dict(zip(mspr_df['Country'], mspr_df['Population']))
    
    return country_to_code, country_to_population

def _render_v1_inputs(country_to_code, t):
    """Affiche les inputs pour la version 1 du modèle."""
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
    return country_display[1]

def _render_v2_inputs(country_to_code, t):
    """Affiche les inputs pour la version 2 du modèle."""
    def _render_month_inputs(month_prefix, month_label):
        st.markdown(f"**{month_label}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                t['input_labels'][f'{month_prefix}_cases'],
                min_value=0,
                max_value=1000000,
                value=0,
                key=f"{month_prefix}_cases"
            )
        with col2:
            st.number_input(
                t['input_labels'][f'{month_prefix}_deaths'],
                min_value=0,
                max_value=1000000,
                value=0,
                key=f"{month_prefix}_deaths"
            )
        with col3:
            st.number_input(
                t['input_labels'][f'{month_prefix}_recovered'],
                min_value=0,
                max_value=1000000,
                value=0,
                key=f"{month_prefix}_recovered"
            )

    _render_month_inputs("current", "Current Month")
    _render_month_inputs("month1", "Month-1")
    _render_month_inputs("month2", "Month-2")
    
    country_display = st.selectbox(
        t['input_labels']['country'],
        options=[(name, code) for name, code in country_to_code.items()],
        format_func=lambda x: x[0],
        index=0,
        key="country_v2",
        help=t['help_messages']['country_select']
    )
    return country_display[1], country_display[0]

def _make_prediction_request(model_version, selected_country_code, selected_country_name, country_to_population):
    """Effectue la requête de prédiction."""
    if model_version == 'v1':
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
    
    return requests.post(endpoint, json=request_data)

def _display_prediction_results(prediction, t):
    """Affiche les résultats de la prédiction."""
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

def predictions():
    # Initialisation
    lang = st.session_state['language']
    translations = load_translations(lang)
    t = translations['predictions']

    st.markdown(f"<h3 style='text-align: center;'>{t['title']}</h3>", unsafe_allow_html=True)

    if 'predicted' in st.session_state:
        st.session_state.pop("predicted")
        st.rerun()
        return

    # Configuration de base
    if 'model_version' not in st.session_state:
        st.session_state.model_version = 'v1'

    # Chargement des données
    country_to_code, country_to_population = _load_data()

    # Sélection du modèle
    model_version = st.radio(
        t['input_labels']['model_version'],
        options=['v1', 'v2'],
        horizontal=True,
        index=0 if st.session_state.model_version == 'v1' else 1,
        key="model_version_radio",
        on_change=lambda: setattr(st.session_state, 'model_version', st.session_state.model_version_radio)
    )
    st.session_state.model_version = model_version

    # Affichage des inputs
    if st.session_state.model_version == 'v1':
        selected_country_code = _render_v1_inputs(country_to_code, t)
        selected_country_name = None
    else:
        selected_country_code, selected_country_name = _render_v2_inputs(country_to_code, t)

    # Bouton de prédiction
    col_left, _ = st.columns([1, 4])
    with col_left:
        predict_clicked = st.button(
            t['predict_button'],
            use_container_width=True,
            help=t['help_messages']['predict_button']
        )

    # Traitement de la prédiction
    if predict_clicked:
        with st.spinner(t['progress_text']):
            progress = st.progress(0)
            for i in range(1, 101, 10):
                time.sleep(0.03)
                progress.progress(i)
            
            try:
                response = _make_prediction_request(
                    st.session_state.model_version,
                    selected_country_code,
                    selected_country_name,
                    country_to_population
                )
            except Exception as e:
                st.error(f"API Request Failed: {str(e)}")
                progress.empty()
                return

            progress.progress(100)
            progress.empty()

        if response.status_code == 200:
            _display_prediction_results(response.json().get("prediction", [[0, 0, 0]]), t)
        else:
            st.error(f"{t['error_prefix']} {response.json().get('message')}")