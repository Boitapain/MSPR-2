import streamlit as st
import requests
import re

def create_account():
    st.markdown("<h1 style='text-align: center;'>Disease track</h1>", unsafe_allow_html=True)
    st.subheader("Create Account")
    
    name = st.text_input("Name", help="Enter your full name")
    email = st.text_input("Email", help="Enter your email address")
    country = st.selectbox("Country", ["USA", "France", "Suisse"], help="Select your country of residence")
    password = st.text_input("Password", type="password", help="Enter a secure password")
    confirm_password = st.text_input("Confirm Password", type="password", help="Re-enter your password for confirmation")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("Cancel", help="Go back to login", icon=":material/close:", on_click=lambda: st.session_state.update({"page": "login"})):
            st.session_state['page'] = 'login'
            st.rerun()
    
    with col2:
        if st.button("Register", help="Create your account",type="primary", icon=":material/assignment_turned_in:"):
            if name == "" or email == "" or password == "" or confirm_password == "":
                st.error("All fields are required")
            else:
                if password == confirm_password:
                    if (
                        len(password) < 8
                        or not re.search(r"[a-z]", password)
                        or not re.search(r"[A-Z]", password)
                        or not re.search(r"[^a-zA-Z0-9]", password)
                    ):
                        st.error("Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one special character.")
                        return
                    response = requests.post(f"{st.session_state['API_URL']}/register", json={
                        "name": name,
                        "email": email,
                        "password": password,
                        "country": country,  # Default country, can be changed later
                    })
                    if response.status_code == 201:
                        st.success("Account created successfully!")
                        st.session_state['new_user'] = True
                        st.session_state['page'] = 'login'
                        st.rerun()
                    else:
                        st.error("Failed to create account: " + response.json().get("message", "Unknown error"))
                else:
                    st.error("Passwords do not match")