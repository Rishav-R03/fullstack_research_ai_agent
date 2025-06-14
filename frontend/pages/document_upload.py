import streamlit as st
import requests
from config import FASTAPI_BASE_URL

def display_document_upload_page():
    """Displays the document upload interface."""
    st.title("📂 Upload Your Documents")
    st.markdown("Upload documents (e.g., PDFs, text files) to build your custom knowledge base.")

    if not st.session_state.logged_in:
        st.warning("Please login to upload documents.")
        return

    st.write(f"Logged in as: **{st.session_state.user_info['username']}**")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"], accept_multiple_files=False)

    if uploaded_file is not None:
        if st.button("Upload Document"):
            with st.spinner("Uploading document..."):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                    response = requests.post(
                        f"{FASTAPI_BASE_URL}/documents/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        headers=headers
                    )
                    response.raise_for_status()

                    upload_result = response.json()
                    st.success(f"Document '{upload_result['file_name']}' uploaded successfully!")
                    st.json(upload_result)

                except requests.exceptions.HTTPError as e:
                    st.error(f"Upload failed: {e.response.json().get('detail', 'Server error during upload.')}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Could not connect to the FastAPI server at {FASTAPI_BASE_URL}. Please ensure the server is running.")
                except Exception as e:
                    st.error(f"An unexpected error occurred during upload: {e}")