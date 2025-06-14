AI-Powered Research Assistant
Welcome to Your Smart Research Companion!
The AI-Powered Research Assistant is an intelligent full-stack web application designed to revolutionize your research workflow. This personal AI assistant can dynamically gather, synthesize, and structure information from the web based on your natural language queries, saving you valuable time and delivering precise insights.

Beyond basic search, this application handles user authentication, maintains a comprehensive history of all your inquiries, and provides the foundation for integrating your own documents into a personalized knowledge base.

Features You'll Love
Intelligent Research Agent:

Powered by LangChain and Google Gemini 1.5 Flash.
Dynamically selects and orchestrates specialized tools (Web Search, Wikipedia) to answer complex research questions.
Delivers comprehensive, summarized answers.
Secure User Authentication:

Full user registration and login system with secure password hashing (bcrypt).
JWT (JSON Web Token)-based authentication for secure API access, ensuring your research is private.
Structured & Actionable Output:

Utilizes Pydantic for rigorous data validation, ensuring all research results (topic, summary, sources, tools used) are consistently structured for clarity and easy processing.
Persistent & Organized Research History:

All your research queries, generated outputs, and every step the AI agent takes (tool calls, LLM usage) are meticulously logged and stored in a robust PostgreSQL database.
Future-proofed with dedicated tables for research sessions, queries, outputs, and granular tool executions.
Custom Knowledge Base (RAG Foundation):

Document Upload: Easily upload your own files (PDFs, TXTs, DOCXs).
Metadata Storage: Stores detailed information about your uploaded documents in the database, laying the groundwork for powerful Retrieval Augmented Generation (RAG) features to allow the AI to answer questions from your documents.
High-Performance Backend:

Built with FastAPI, a modern, asynchronous Python web framework known for its speed and developer-friendliness.
Seamlessly connects to PostgreSQL using SQLAlchemy ORM for efficient and reliable database operations.
Intuitive Web Interface:

A clean, responsive, and real-time frontend developed with Streamlit for easy query input, interactive results display, and seamless navigation.
# Technologies Under the Hood
This project demonstrates a robust full-stack architecture using a modern tech stack:

Backend:

Python: The core programming language.
FastAPI: High-performance web framework.
PostgreSQL: Robust relational database.
SQLAlchemy: Python SQL Toolkit and Object-Relational Mapper (ORM).
python-dotenv: Environment variable management.
passlib: Secure password hashing.
python-jose: JSON Web Token (JWT) implementation for authentication.
python-multipart: For handling file uploads.
AI/LLM:

LangChain: Framework for building LLM-powered applications and agent orchestration.
Google Gemini API: State-of-the-art Large Language Model (specifically Gemini 1.5 Flash).
langchain-google-genai: LangChain integration for Google Gemini.
langchain-community: Provides common LangChain integrations (e.g., DuckDuckGo Search, Wikipedia).
Pydantic: Data validation and structured output.
Frontend:

Streamlit: For creating the interactive web user interface.
requests: Python HTTP library for communicating with the FastAPI backend.
# Get Started in Minutes!
Follow these simple steps to set up and run the AI-Powered Research Assistant on your local machine.

Prerequisites
Before you begin, ensure you have:

Python 3.9+ installed.
A PostgreSQL database server running locally or accessible.
Create a database (e.g., smartresearchagent) and a user with access (e.g., postgres with password root123 or your own credentials).
If using psql, you can create the database with: CREATE DATABASE smartresearchagent;
An API key from Google AI Studio for Gemini model access.
A secret key for JWT authentication (you can generate one with openssl rand -hex 32 in your terminal).
Installation
Clone the repository:

Bash

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/Rishav-R03/fullstack_research_ai_agent)
cd your-repo-name

Create and Activate a Virtual Environment (Highly Recommended):

```python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```
Install Dependencies:
First, create a requirements.txt file in your project's root directory with the following contents:
```
fastapi==0.111.0 # Or compatible version you are using
uvicorn[standard]==0.29.0 # Or compatible version
streamlit==1.36.0 # Or compatible version
requests==2.32.3 # Or compatible version
python-dotenv==1.0.1 # Or compatible version
pydantic==2.7.4 # Or compatible version
sqlalchemy==2.0.30 # Or compatible version
greenlet==3.0.3 # Often needed for SQLAlchemy
psycopg2-binary==2.9.9 # PostgreSQL adapter
passlib[bcrypt]==1.7.4 # Password hashing
python-jose[cryptography]==3.3.0 # JWT
python-multipart==0.0.9 # For file uploads
```
# LangChain specific packages
```
langchain-google-genai==1.0.5 # Or compatible version
langchain-community==0.2.7 # Or compatible version
langchain-core==0.2.14 # Or compatible version (ensure this is the right one for your setup)
langchain==0.2.7 # Or compatible version (usually pulls others)
```
Then, install them:

pip install -r requirements.txt
(Note: The exact versions above are suggestions. If you already have working versions, stick to those. langchain-core versions can be tricky, as we experienced!)

Configuration
Create a .env file: In the root directory of your project (where venv/ is), create a file named .env and add the following:
Code snippet
```
GOOGLE_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
SECRET_KEY="YOUR_GENERATED_JWT_SECRET_KEY"
```
# PostgreSQL Database Credentials
```
DB_USER="postgres"
DB_PASSWORD="root123" # Replace with your actual PostgreSQL password
DB_NAME="smartresearchagent"
DB_HOST="localhost"
DB_PORT=5432
```
Remember to replace the placeholder values with your actual keys and database credentials.
Running the Application
Your project consists of two main parts: the FastAPI Backend (API Server) and the Streamlit Frontend (Web UI). You need to run both concurrently.

Start the FastAPI Backend:
Open your first terminal window, navigate to your project's root, activate your virtual environment, and run:

```
uvicorn backend.server:app --reload --port 8000
```
You should see messages indicating the server starting and database tables being created/checked. Keep this terminal open.

Start the Streamlit Frontend:
Open a second terminal window, navigate to your project's root, activate your virtual environment, and run:
```
streamlit run frontend/home.py
```
This command will automatically open the Streamlit application in your default web browser (usually http://localhost:8501).

# How to Use
Once both the backend and frontend are running:

Login/Signup:

Navigate to the "Login/Signup" page in the Streamlit sidebar.
Sign Up: Create a new account using the "Create a New Account" form.
Login: Use your newly created (or existing) credentials to log in via the "Login to Your Account" form. You'll be redirected to the Research Assistant page upon successful login.
Upload Documents (Foundation for RAG):

Go to the "Upload Documents" page in the sidebar.
Choose a .pdf, .txt, or .docx file from your computer and click "Upload Document".
The file will be saved on the server (uploads/ directory), and its metadata stored in your PostgreSQL database.
Perform Research:

Navigate to the "Research Assistant" page.
Enter your research query (e.g., "What are the latest breakthroughs in AI ethics?") in the text box.
Click "Start Research".
The AI agent will process your request, use tools, and display a structured summary and sources directly in the UI. All this activity will be logged in your database.
# Visuals & Screenshots
1. Login & Signup Interface
![image](https://github.com/user-attachments/assets/a5292ae2-769b-49d5-a1ce-fa85cf538d0a)

2. Research Query & Results Display
![image](https://github.com/user-attachments/assets/4126b801-580d-441e-82dc-87b7655f178c)

4. ERD of Database Records
![image](https://github.com/user-attachments/assets/c8d855e0-c7fd-4a97-a91b-2354889e3ad1)

# Video Demonstration
See the AI-Powered Research Assistant in action!

[Youtube Link](https://youtu.be/xs0J-HnFero) 

Future Enhancements & Next Steps
This project is a strong foundation with many exciting possibilities for expansion:

Full RAG Implementation:
Process uploaded documents: Extract text, chunk, and generate vector embeddings.
Integrate a vector store (e.g., pgvector extension for PostgreSQL, or dedicated vector DB).
Enhance the agent to retrieve relevant chunks from your custom documents and use them for answering queries.
Research History View: Create a dedicated Streamlit page to browse, search, and filter your past research queries and outputs stored in the database.
Research Session Management UI: Allow users to create, select, and manage different "research projects" or "sessions."
Advanced Tooling: Integrate with more specialized APIs (e.g., Google Search API, ArXiv, PubMed, financial data).
Real-time Agent Trace: Stream the agent's "thoughts" and tool calls to the frontend in real-time for better user visibility and debugging.
User Profiles & Settings: Allow users to manage their profiles and customize agent behavior (e.g., preferred LLM model, default tools).
Scalability & Deployment: Containerize with Docker, set up CI/CD pipelines, and deploy to a cloud platform (AWS, GCP, Azure).

# Contributing
Contributions are highly appreciated! If you have suggestions for improvements, new features, or bug fixes, please open an issue or submit a pull request.

# License
This project is licensed under the MIT License - see the LICENSE file for details. (Remember to include an actual LICENSE file in your repository.)

# Contact
Rishav [Linkedin](https://www.linkedin.com/in/rishav-raj-15b077249/) - rishav042023@gmail.com
Project Link: [GitHub](https://github.com/Rishav-R03/fullstack_research_ai_agent)
