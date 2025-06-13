# frontend/home.py

import streamlit as st
# Import functions from your new page modules
from pages.login_signup import display_login_form, display_signup_form
from pages.research_assistant import display_research_assistant_page, logout
from pages.document_upload import display_document_upload_page # <-- NEW IMPORT
# --- Initialize Session State ---
# This ensures that these state variables persist across reruns
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

st.set_page_config(page_title="Smart Research Assistant", layout="wide")

st.sidebar.title("Navigation")
# Control navigation based on login status
if st.session_state.logged_in:
    page = st.sidebar.radio("Go to", ["Research Assistant", "Login/Signup"])
elif st.session_state.logged_in:
    page = st.sidebar.radio("Go to", ["Upload document", "Login/Signup"])
else:
    page = st.sidebar.radio("Go to", ["Login/Signup", "Research Assistant"]) # Force login first

# Display main title
st.title("Smart Research Assistant")
st.write("Welcome to our application!")

# --- Conditional Page Display ---
if page == "Login/Signup":
    # If not logged in, always show login/signup
    if not st.session_state.logged_in:
        col1, col2 = st.columns(2)
        with col1:
            display_login_form()
        with col2:
            display_signup_form()
    else:
        st.info(f"You are already logged in as **{st.session_state.user_info['username']}**.")
        st.button("Logout", on_click=logout) # Allow logout from here too
        st.markdown("Go to the 'Research Assistant' page in the sidebar to start researching.")

elif page == "Research Assistant":
    # The research assistant page itself handles the "Please login" message
    display_research_assistant_page()

elif page == "Upload Documents": # <-- NEW PAGE HANDLING
    display_document_upload_page()


