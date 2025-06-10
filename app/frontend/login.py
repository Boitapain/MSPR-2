import streamlit as st
import requests
import os

api_url = os.getenv('API_URL', 'http://127.0.0.1:5000') 

def login():
    st.markdown("<h1 style='text-align: center;'>Disease track <img style='width:40px;' src='https://open.gitbook.com/~gitbook/image?url=https%3A%2F%2F4141789323-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Forganizations%252Fu9WT6puw9kHCPITtWSCY%252Fsites%252Fsite_dWsRi%252Ficon%252FbWVB6Yfwt8HDjQZq3ceg%252FChanger%2520Couleurs%2520PNG.png%3Falt%3Dmedia%26token%3D1b09cb73-feab-4508-9750-82cc96920a70&width=48&height=48&sign=d8eb1004&sv=2'/></h1>", unsafe_allow_html=True)
    st.subheader("Login")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Login", help="Connect to your account", key="login_button", type="primary", icon=":material/login:"):
            response = requests.post(f"{st.session_state['API_URL']}/login", json={"email": email, "password": password}, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                user = response.json().get("user")
                st.session_state['user'] = user
                st.session_state['page'] = 'dashboard'
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Invalid email or password")
    
    with col2:
        st.button("Create Account", help="Create your new account", type="primary", icon=":material/person_add:", on_click=lambda: st.session_state.update({"page": "create_account"}), key="create_account_button")

if __name__ == "__main__":
    login()