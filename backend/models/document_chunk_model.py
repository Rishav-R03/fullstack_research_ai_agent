from sqlalchemy import Column,Text, Integer, ForeignKey, func, text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base # Import Base from your database.py

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.document_id"), nullable=False, index=True)
    chunk_text = Column(Text, nullable=False)
    # For embedding, you'd typically use `VECTOR` type if `pgvector` extension is installed.
    # Otherwise, you might store a string representation (e.g., JSON string) and parse in app.
    # Placeholder: if using pgvector, change to `VECTOR(embedding_dimension)`
    embedding = Column(Text) # Placeholder for vector embedding (e.g., JSON string of float array)
    chunk_order = Column(Integer, nullable=False) # Order of chunk within the document
    created_at = Column(DateTime(timezone=True), default=func.now()) # When the chunk was created

    # Define relationship back to Document
    document = relationship("Document", back_populates="document_chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.chunk_id}, doc_id={self.document_id}, order={self.chunk_order})>"
