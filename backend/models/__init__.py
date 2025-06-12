# backend/models/__init__.py

# Import all your ORM models here so they are discoverable by Base.metadata.create_all()
from models.user_model import User
from models.research_session_model import ResearchSession
from models.research_query_model import ResearchQuery
from models.research_output_model import ResearchOutput
from models.tool_execution_model import ToolExecution
from models.document_model import Document
from models.document_chunk_model import DocumentChunk

# You can also define __all__ if you want to explicitly control what's imported
# when someone does `from backend.models import *`
__all__ = [
    "User",
    "ResearchSession",
    "ResearchQuery",
    "ResearchOutput",
    "ToolExecution",
    "Document",
    "DocumentChunk",
]
