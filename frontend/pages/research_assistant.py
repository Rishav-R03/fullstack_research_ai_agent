# frontend/pages/research_assistant.py

import streamlit as st
import requests
import json
from config import FASTAPI_BASE_URL # Import the base URL

def logout():
    """Logs out the user by clearing session state."""
    st.session_state.logged_in = False
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.info("You have been logged out.")
    st.rerun() # Rerun to display login page

def display_research_assistant_page():
    """Displays the main research assistant UI."""
    st.title("📚 Gemini Research Assistant")

    # Display user info and logout button if logged in
    if st.session_state.logged_in and st.session_state.user_info:
        st.write(f"Logged in as: **{st.session_state.user_info['username']}** (ID: `{st.session_state.user_info['user_id']}`)")
        st.button("Logout", on_click=logout)
    else:
        st.warning("Please login to use the Research Assistant.")
        return # Stop execution if not logged in

    st.markdown("Enter a query below and let the AI assistant research it for you!")

    user_query = st.text_input("Enter your research query here:", placeholder="e.g., 'Latest advancements in quantum computing'")

    if st.button("Start Research"):
        if not user_query:
            st.warning("Please enter a research query.")
        else:
            st.info(f"Researching: '{user_query}'...")
            with st.spinner("Processing your request... This might take a moment as the AI agent works..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                    response = requests.post(f"{FASTAPI_BASE_URL}/research", json={"query": user_query}, headers=headers)
                    response.raise_for_status()

                    research_data = response.json()

                    st.success("Research Complete!")
                    st.subheader("Research Summary")
                    st.write(f"**Topic:** {research_data.get('topic', 'N/A')}")
                    st.write(f"**Summary:**")
                    st.markdown(research_data.get('summary', 'N/A'))

                    st.subheader("Sources")
                    sources = research_data.get('sources', [])
                    if sources:
                        for source in sources:
                            st.markdown(f"- {source}")
                    else:
                        st.write("No specific sources provided.")

                    st.subheader("Tools Used")
                    tools_used = research_data.get('tools_used', [])
                    if tools_used:
                        st.write(", ".join(tools_used))
                    else:
                        st.write("No tools explicitly reported by the agent.")

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        st.error("Authentication required. Your session might have expired. Please log in again.")
                        logout() # Force logout if token expired/invalid
                    else:
                        st.error(f"Research failed: {e.response.json().get('detail', 'Server error')}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Could not connect to the FastAPI server at {FASTAPI_BASE_URL}. Please ensure the server is running.")
                except json.JSONDecodeError:
                    st.error("Failed to decode JSON response from the server. Unexpected server response.")
                except Exception as e:
                    st.error(f"An unexpected error occurred during research: {e}")

    st.markdown("---")
    st.caption("Powered by Google Gemini and LangChain")
