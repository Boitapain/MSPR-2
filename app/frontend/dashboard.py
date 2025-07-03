import streamlit as st
from dashboard_pages.home import home
from dashboard_pages.csv_import import csv_import
from dashboard_pages.db_viz import db_viz
from dashboard_pages.stats import stats
from dashboard_pages.profile import profile
from dashboard_pages.predictions import predictions
from dashboard_pages.manage_users import manage_users
import os

from translations import load_translations

# Constants
MARGIN_TOP_DIV = "<div style='margin-top: 10px;'></div>"

def switch_language(country):
    """Switch the language based on the user's country."""
    if not st.session_state.get('update_language', False):
        if country == "USA":
            st.session_state['language'] = 'en'
        elif country == "France":
            st.session_state['language'] = 'fr'
        elif country == "Suisse":
            st.session_state['language'] = 'fr'
        else:
            st.session_state['language'] = 'en' # Default to English if country is not recognized

def get_api_url():
    """Get the appropriate API URL based on environment."""
    if os.getenv("RENDER"):
        return st.session_state["API_URL"]
    else:
        return "http://localhost:5001"

def render_navigation_buttons(user, t):
    """Render navigation buttons in the sidebar."""
    # Home button
    st.button(t["navigation"]["home"], type="tertiary", help=t["navigation"]["home_help"], icon=":material/home:", on_click=lambda: st.session_state.update({"dashboard_page": "home"}))
    st.markdown(MARGIN_TOP_DIV, unsafe_allow_html=True)
    
    if user["country"] == "USA":
        url = get_api_url()
        st.link_button(t["navigation"]["api_docs"], help=t["navigation"]["api_docs_help"], url=f"{url}/swagger", type="tertiary", icon=":material/article:")

def render_data_management_section(user, t):
    """Render data management section for USA users."""
    if user["country"] == "USA":
        st.header(t["sections"]["data_management"])
        if user["isAdmin"]:
            st.button(t["buttons"]["csv_import"], help=t["buttons"]["csv_import_help"], type="tertiary", icon=":material/download:", on_click=lambda: st.session_state.update({"dashboard_page": "csv_import"}))
        st.button(t["buttons"]["database"], help=t["buttons"]["database_help"], type="tertiary", icon=":material/database:", on_click=lambda: st.session_state.update({"dashboard_page": "database"}))
        st.markdown(MARGIN_TOP_DIV, unsafe_allow_html=True)

def render_data_visualization_section(user, t):
    """Render data visualization section."""
    st.header(t["sections"]["data_visualization"])
    
    if user["country"] != "Suisse":
        st.button(t["buttons"]["statistics"], help=t["buttons"]["statistics_help"], type="tertiary", icon=":material/monitoring:", on_click=lambda: st.session_state.update({"dashboard_page": "statistics"}))
    st.button(t["buttons"]["predictions"], help=t["buttons"]["predictions_help"], type="tertiary", icon=":material/rocket_launch:", on_click=lambda: st.session_state.update({"dashboard_page": "predictions"}))
    st.markdown(MARGIN_TOP_DIV, unsafe_allow_html=True)

def render_settings_section(user, t):
    """Render settings section."""
    st.header(t["sections"]["settings"])
    if user["isAdmin"]:
        st.button(t["buttons"]["manage_users"], help=t["buttons"]["manage_users_help"], type="tertiary", icon=":material/group:", on_click=lambda: st.session_state.update({"dashboard_page": "manage_users"}))
    st.button(t["buttons"]["profile"], help=t["buttons"]["profile_help"], type="tertiary", icon=":material/person:", on_click=lambda: st.session_state.update({"dashboard_page": "profile"}))

def dashboard(user):
    # Initialize session state for dashboard page if it doesn't exist
    if 'dashboard_page' not in st.session_state:
        st.session_state['dashboard_page'] = 'home'
        
    switch_language(user["country"])
    lang = st.session_state['language']
    translations = load_translations(lang)
    t = translations['dashboard']

    st.markdown(
    """
    <style>
    /* Customize the sidebar container */
    [data-testid="stSidebar"] {
        background-color: #D1D5DB !important;
        width: fit-content !important; /* Use a fixed width for consistency */
    }

    /* Customize text inside the sidebar */
    [data-testid="stSidebar"] span {
        font-weight: bold; /* Optional: Make the text bold */
    }               

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
    )
    
    # Sidebar with navigation buttons
    with st.sidebar:
        st.markdown("""
        <h1 style="margin-top:0;padding: 0rem 0rem 1rem;">Disease Track<img style="width:40px;" src='https://mspr-team.gitbook.io/~gitbook/image?url=https%3A%2F%2F4141789323-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Forganizations%252Fu9WT6puw9kHCPITtWSCY%252Fsites%252Fsite_dWsRi%252Ficon%252FngObCdhfrJl7KEq70xGH%252FChanger%2520couleurs%2520PNG%2520%281%29.png%3Falt%3Dmedia%26token%3D83947e0c-3451-4fcd-96bb-44a7447036d0&width=32&dpr=2&quality=100&sign=67c622a5&sv=2'/></h1>
        """,unsafe_allow_html=True)
        
        render_navigation_buttons(user, t)
        render_data_management_section(user, t)
        render_data_visualization_section(user, t)
        render_settings_section(user, t)
    
    # Display the appropriate page based on session state
    if st.session_state['dashboard_page'] == 'home':
        home(user)
    elif st.session_state['dashboard_page'] == 'csv_import':
        csv_import()
    elif st.session_state['dashboard_page'] == 'database':
        db_viz(user)
    elif st.session_state['dashboard_page'] == 'statistics':
        stats(user)
    elif st.session_state['dashboard_page'] == 'profile':
        profile(user)
    elif st.session_state['dashboard_page'] == 'predictions':
        predictions()
    elif st.session_state['dashboard_page'] == 'manage_users':
        manage_users(user)
if __name__ == "__main__":
    dashboard("User")