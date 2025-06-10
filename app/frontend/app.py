import streamlit as st
from login import login
from create_account import create_account
from dashboard import dashboard
import os

def navigate_to_create_account():
    st.session_state["page"] = "create_account"

def main():
    if os.getenv('RENDER'):
        # Production (Render) environment
        API_URL = 'https://backend-l0n0.onrender.com'
    else:
        # Local development with docker-compose
        API_URL = 'http://api:5000'
    st.session_state['API_URL'] = API_URL

    # Initialize session state variables if they don't exist
    if 'new_user' not in st.session_state:
        st.session_state['new_user'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Set the page configuration
    st.set_page_config(
        page_title="Disease Track",
        page_icon="https://open.gitbook.com/~gitbook/image?url=https%3A%2F%2F4141789323-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Forganizations%252Fu9WT6puw9kHCPITtWSCY%252Fsites%252Fsite_dWsRi%252Ficon%252FbWVB6Yfwt8HDjQZq3ceg%252FChanger%2520Couleurs%2520PNG.png%3Falt%3Dmedia%26token%3D1b09cb73-feab-4508-9750-82cc96920a70&width=48&height=48&sign=d8eb1004&sv=2",
        layout="centered",
        initial_sidebar_state="auto",
    )

    # Navigate to the appropriate page based on session state
    if st.session_state['logged_in'] or st.session_state.get("page") == "dashboard":
        # If the user is logged in or the page is set to "dashboard", show the dashboard
        dashboard(st.session_state['user'])
    elif st.session_state.get("page") == "create_account":
        # If the page is set to "create_account", show the create account page
        create_account()
        if st.session_state['new_user']:
            # Reset the page state after account creation
            st.session_state['page'] = None
    else:
        # Otherwise, show the login page
        login()

if __name__ == "__main__":
    main()
