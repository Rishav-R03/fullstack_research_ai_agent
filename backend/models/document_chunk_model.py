from sqlalchemy import Column,Text, Integer, ForeignKey, func, text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Text) 
    chunk_order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now()) 
    document = relationship("Document", back_populates="document_chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.chunk_id}, doc_id={self.document_id}, order={self.chunk_order})>"
