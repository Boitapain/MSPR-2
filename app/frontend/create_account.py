import streamlit as st
import requests
import re

def validate_password(password):
    """Validate password strength requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[^a-zA-Z0-9]", password):
        return False, "Password must contain at least one special character"
    return True, ""

def validate_form_fields(name, email, password, confirm_password):
    """Validate all form fields and return validation result."""
    if not all([name, email, password, confirm_password]):
        return False, "All fields are required"
    
    if password != confirm_password:
        return False, "Passwords do not match"
    
    is_valid, message = validate_password(password)
    if not is_valid:
        return False, message
    
    return True, ""

def register_user(name, email, password, country):
    """Handle user registration API call."""
    try:
        response = requests.post(f"{st.session_state['API_URL']}/register", json={
            "name": name,
            "email": email,
            "password": password,
            "country": country,
        })
        
        if response.status_code == 201:
            st.success("Account created successfully!")
            st.session_state['new_user'] = True
            st.session_state['page'] = 'login'
            st.rerun()
        else:
            error_message = response.json().get("message", "Unknown error")
            st.error(f"Failed to create account: {error_message}")
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")

def create_account():
    st.markdown("<h1 style='text-align: center;'>Disease track</h1>", unsafe_allow_html=True)
    st.subheader("Create Account")
    
    name = st.text_input("Name", help="Enter your full name")
    email = st.text_input("Email", help="Enter your email address")
    country = st.selectbox("Country", ["USA", "France", "Suisse"], help="Select your country of residence")
    password = st.text_input("Password", type="password", help="Enter a secure password")
    confirm_password = st.text_input("Confirm Password", type="password", help="Re-enter your password for confirmation")
    
    col1, col2, _, _ = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("Cancel", help="Go back to login", icon=":material/close:", on_click=lambda: st.session_state.update({"page": "login"})):
            st.session_state['page'] = 'login'
            st.rerun()
    
    with col2:
        if st.button("Register", help="Create your account",type="primary", icon=":material/assignment_turned_in:"):
            is_valid, error_message = validate_form_fields(name, email, password, confirm_password)
            
            if not is_valid:
                st.error(error_message)
                return
                
            register_user(name, email, password, country)