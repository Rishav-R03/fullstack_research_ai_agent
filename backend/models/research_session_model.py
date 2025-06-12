from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base # Import Base from your database.py

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    session_title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    last_updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_archived = Column(Boolean, default=False)

    # Define relationship to User
    user = relationship("User", back_populates="research_sessions")

    # Define relationship to ResearchQuery (one-to-many)
    research_queries = relationship(
        "ResearchQuery",
        back_populates="session",
        cascade="all, delete-orphan", # Deletes queries if session is deleted
        order_by="ResearchQuery.query_timestamp.desc()" # Order queries by most recent
    )

    # Define relationship to Document (one-to-many, optional)
    documents = relationship(
        "Document",
        back_populates="session",
        cascade="all, delete-orphan" # Deletes documents if session is deleted
    )

    def __repr__(self):
        return f"<ResearchSession(id={self.session_id}, title='{self.session_title}', user_id={self.user_id})>"
