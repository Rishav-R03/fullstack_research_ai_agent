from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("research_sessions.session_id"), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50))
    upload_timestamp = Column(DateTime(timezone=True), default=func.now())
    is_indexed = Column(Boolean, default=False) 
    embedding_model_used = Column(String(100))
    
    user = relationship("User", back_populates="documents")
    session = relationship("ResearchSession", back_populates="documents")

    document_chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_order"
    )

    def __repr__(self):
        return f"<Document(id={self.document_id}, filename='{self.file_name}', user_id={self.user_id})>"
