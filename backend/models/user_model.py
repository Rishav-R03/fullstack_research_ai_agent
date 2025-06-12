from sqlalchemy import Column, String, DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship # Import relationship

from database import Base # Import Base from your database.py

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    # settings = Column(JSONB, default={})

    # Define relationships to other models that link back to User
    research_sessions = relationship("ResearchSession", back_populates="user", cascade="all, delete-orphan")
    research_queries = relationship("ResearchQuery", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}')>"
