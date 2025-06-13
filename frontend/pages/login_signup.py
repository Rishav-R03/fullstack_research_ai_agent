# frontend/pages/login_signup.py

import streamlit as st
import requests
import json
from config import FASTAPI_BASE_URL # Import the base URL

# --- Session State Management (for this module's scope, but Home.py will manage central state) ---
# Note: Streamlit's session_state is global across the app once set, so these checks
# are good for robustness, but usually set up in the main app file (home.py).

def login_user(username, password):
    """Attempts to log in the user and update session state."""
    try:
        # Define headers for the request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(
            f"{FASTAPI_BASE_URL}/token",
            data={"username": username, "password": password},
            headers=headers # <-- Explicitly add the headers here
        )
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        token_data = response.json()
        st.session_state.access_token = token_data.get("access_token")
        st.session_state.logged_in = True

        # Immediately fetch user info to display
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        user_response = requests.get(f"{FASTAPI_BASE_URL}/users/me/", headers=headers)
        user_response.raise_for_status()
        st.session_state.user_info = user_response.json()

        st.success(f"Welcome, {st.session_state.user_info['username']}! You are logged in.")
        st.rerun()

    except requests.exceptions.HTTPError as e:
        # Now, check if the response actually has JSON content before trying to parse
        try:
            error_detail = e.response.json().get('detail', 'Invalid credentials or server error')
        except json.JSONDecodeError:
            # If it's not JSON, show the raw text response for debugging
            error_detail = f"Server returned non-JSON error: {e.response.text}"
        st.error(f"Login failed: {error_detail}")
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the FastAPI server at {FASTAPI_BASE_URL}. Please ensure the server is running.")
    except Exception as e:
        st.error(f"An unexpected error occurred during login: {e}")

def signup_user(username, email, password):
    """Attempts to sign up a new user."""
    try:
        response = requests.post(
            f"{FASTAPI_BASE_URL}/users/",
            json={"username": username, "email": email, "password": password}
        )
        response.raise_for_status()

        st.success("Account created successfully! Please login.")
        return True

    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get('detail', 'Unknown error during signup')
        st.error(f"Signup failed: {error_detail}")
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the FastAPI server at {FASTAPI_BASE_URL}. Please ensure the server is running.")
    except Exception as e:
        st.error(f"An unexpected error occurred during signup: {e}")
    return False


def display_login_form():
    """Displays the login form in Streamlit."""
    st.subheader("Login to Your Account")
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_username_form") # Unique key
        login_password = st.text_input("Password", type="password", key="login_password_form") # Unique key
        login_submitted = st.form_submit_button("Login")

        if login_submitted:
            if not login_username or not login_password:
                st.error("Please enter both username and password.")
            else:
                login_user(login_username, login_password)


def display_signup_form():
    """Displays the signup form in Streamlit."""
    st.subheader("Create a New Account")
    with st.form("signup_form"):
        signup_username = st.text_input("Choose Username", key="signup_username_form") # Unique key
        signup_email = st.text_input("Enter Email", key="signup_email_form") # Unique key
        signup_password = st.text_input("Choose Password", type="password", key="signup_password_form") # Unique key
        signup_submitted = st.form_submit_button("Sign Up")

        if signup_submitted:
            if not signup_username or not signup_email or not signup_password:
                st.error("All fields are required.")
            else:
                signup_user(signup_username, signup_email, signup_password)

