from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base # Import Base from your database.py

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("research_sessions.session_id"), nullable=True) # Optional: associate with a specific session
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False) # Path to stored file (e.g., S3 URL, local path)
    file_type = Column(String(50)) # e.g., 'pdf', 'docx', 'txt', 'csv'
    upload_timestamp = Column(DateTime(timezone=True), default=func.now())
    is_indexed = Column(Boolean, default=False) # True if chunks/embeddings are generated
    embedding_model_used = Column(String(100)) # e.g., 'text-embedding-001'
    
    # Define relationship to User
    user = relationship("User", back_populates="documents")

    # Define relationship to ResearchSession
    session = relationship("ResearchSession", back_populates="documents")

    # Define relationship to DocumentChunk (one-to-many)
    document_chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan", # Deletes chunks if document is deleted
        order_by="DocumentChunk.chunk_order"
    )

    def __repr__(self):
        return f"<Document(id={self.document_id}, filename='{self.file_name}', user_id={self.user_id})>"
