import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.dialects.postgresql import UUID # Ensure this is here
from dotenv import load_dotenv
from typing import List, Dict, Any
import uuid

# Load environment variables
load_dotenv()

# --- Declarative Base for ORM Models ---
Base = declarative_base()

# --- Import ORM Models ---
# All your SQLAlchemy ORM models must be imported here.
from models.user_model import User
from models.research_session_model import ResearchSession
from models.research_query_model import ResearchQuery
from models.research_output_model import ResearchOutput
from models.tool_execution_model import ToolExecution
from models.document_model import Document
from models.document_chunk_model import DocumentChunk

# --- Database Connection Configuration ---
db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("POSTGRESQL_PASSWORD")
db_name = os.getenv("DB_NAME", "smartresearchagent")
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", 5432))

if not db_password:
    raise ValueError("POSTGRESQL_PASSWORD environment variable not set.")

db_url = URL.create(
    drivername="postgresql",
    username=db_user,
    password=db_password,
    database=db_name,
    host=db_host,
    port=db_port
)

engine = create_engine(db_url, pool_pre_ping=True)

# --- Session Management for FastAPI ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Database Initialization Function ---
def create_db_tables():
    print("Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully (or already existed).")
    except Exception as e:
        print(f"ERROR: Failed to create database tables: {e}")
        print("Please check your PostgreSQL connection, credentials, and database permissions.")
        print("Ensure 'gen_random_uuid()' is available (pgcrypto extension might be needed).")
        raise

# --- New Helper Functions for DB Interactions ---

# Helper to create a new research session for a user
def create_new_research_session(db: Session, user_id: uuid.UUID, title: str) -> ResearchSession:
    session = ResearchSession(user_id=user_id, session_title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

# Helper to create a research query entry
def create_research_query(
    db: Session,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    query_text: str,
    llm_model_used: str = None
) -> ResearchQuery:
    query_entry = ResearchQuery(
        user_id=user_id,
        session_id=session_id,
        query_text=query_text,
        llm_model_used=llm_model_used
    )
    db.add(query_entry)
    db.commit()
    db.refresh(query_entry)
    return query_entry

# Helper to update research query with token usage/cost
def update_research_query_metrics(
    db: Session,
    query_id: uuid.UUID,
    input_tokens: int,
    output_tokens: int,
    total_cost: float
):
    query_entry = db.query(ResearchQuery).filter(ResearchQuery.query_id == query_id).first()
    if query_entry:
        query_entry.input_tokens = input_tokens
        query_entry.output_tokens = output_tokens
        query_entry.total_cost = total_cost
        db.add(query_entry)
        db.commit()

# Helper to create a research output entry
def create_research_output(
    db: Session,
    query_id: uuid.UUID,
    topic: str,
    summary: str,
    sources: List[str],
    tools_used_reported: List[str],
    parsing_successful: bool,
    raw_llm_output: str
) -> ResearchOutput:
    output_entry = ResearchOutput(
        query_id=query_id,
        topic=topic,
        summary=summary,
        sources=sources, # SQLAlchemy's JSONB type handles list/dict directly
        tools_used_reported=tools_used_reported,
        parsing_successful=parsing_successful,
        raw_llm_output=raw_llm_output
    )
    db.add(output_entry)
    db.commit()
    db.refresh(output_entry)
    return output_entry

# Helper to create a tool execution entry
def create_tool_execution(
    db: Session,
    query_id: uuid.UUID,
    tool_name: str,
    tool_input: str,
    tool_output: str,
    status: str,
    error_message: str = None
) -> ToolExecution:
    execution_entry = ToolExecution(
        query_id=query_id,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_output=tool_output,
        status=status,
        error_message=error_message
    )
    db.add(execution_entry)
    db.commit() # Commit each tool execution as it happens, or batch
    db.refresh(execution_entry)
    return execution_entry


# --- Example Usage (for testing table creation directly) ---
if __name__ == "__main__":
    print("Running database.py directly to create tables.")
    create_db_tables()
    print("Direct database setup process initiated. Check your PostgreSQL logs for table creation details.")

