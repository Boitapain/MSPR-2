import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from translations import load_translations

from translations import load_translations

def stats():
    lang = st.session_state['language']
    translations = load_translations(lang)
    t = translations['stats']
    
    st.markdown(f"<h1 id='main-title' style='text-align: center;'>{t['title']}</h1>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{st.session_state['API_URL']}/diseases")
        response.raise_for_status()
        data = response.json().get("diseases")
        
        if not data:
            st.warning(t['data_fetch']['no_data'])
            return
            
        df = pd.DataFrame(data, columns=[
            "Id", "Name", "Date", "Country", "Confirmed", "Deaths", "Recovered", 
            "New_cases", "New_deaths", "New_recovered"
        ])
        
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
            df["YearMonth"] = df["Date"].dt.to_period("M")
            months = sorted(df["YearMonth"].unique())
            month_pairs = [(months[i], months[i + 1]) for i in range(len(months) - 1)]

            # UI with help tooltips
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"#### {t['filters']['month_range']['title']}")
                selected_pair = st.selectbox(
                    t['filters']['month_range']['label'],
                    options=month_pairs,
                    format_func=lambda x: t['filters']['month_range']['format'].format(start=x[0], end=x[1]),
                    
                )
            with col2:
                st.markdown(f"#### {t['filters']['statistic']['title']}")
                selected_stat = st.selectbox(
                    t['filters']['statistic']['label'], 
                    options=["Confirmed", "Deaths", "Recovered", "New_cases", "New_deaths", "New_recovered"])
            
            start_month, end_month = selected_pair
            df = df[(df["YearMonth"] >= start_month) & (df["YearMonth"] <= end_month)]
            
            disease_options = [t['filters']['disease']['all_option']] + df["Name"].unique().tolist()
            selected_disease = st.selectbox(
                t['filters']['disease']['label'], 
                disease_options,
            )
            
            if selected_disease != t['filters']['disease']['all_option']:
                df = df[df["Name"] == selected_disease]
            
            # Visualizations with help tooltips
            st.markdown(f"### {t['visualizations']['map_title'].format(stat=selected_stat)}")
            fig = px.choropleth(
                df,
                locations="Country",
                locationmode="country names",
                color=selected_stat,
                color_continuous_scale=[[0, "#FFFFFF"], [1, "#4169E1"]],
                hover_name="Country",
                hover_data=[selected_stat]
            )
            st.plotly_chart(fig)
            
            st.markdown(f"### {t['visualizations']['table_title']}")
            st.dataframe(df)  # Using dataframe instead of table for better display
            
    except requests.exceptions.RequestException as e:
        st.error(t['data_fetch']['api_error'].format(error=e))
    except Exception as e:
        st.error(t['data_fetch']['general_error'].format(error=e))

if __name__ == "__main__":
    stats()