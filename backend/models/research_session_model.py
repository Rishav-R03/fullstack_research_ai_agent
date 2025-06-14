from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True)
    session_title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    last_updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_archived = Column(Boolean, default=False)
    user = relationship("User", back_populates="research_sessions")
    research_queries = relationship(
        "ResearchQuery",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ResearchQuery.query_timestamp.desc()"
    )
    documents = relationship(
        "Document",
        back_populates="session",
        cascade="all, delete-orphan" 
    )

    def __repr__(self):
        return f"<ResearchSession(id={self.session_id}, title='{self.session_title}', user_id={self.user_id})>"
