from sqlalchemy import Column, String, Text, DateTime, Integer, DECIMAL, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

class ResearchQuery(Base):
    __tablename__ = "research_queries"

    query_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("research_sessions.session_id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, index=True) # Redundant but useful for direct access
    query_text = Column(Text, nullable=False)
    query_timestamp = Column(DateTime(timezone=True), default=func.now())
    llm_model_used = Column(String(100)) 
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_cost = Column(DECIMAL(10, 6))

    session = relationship("ResearchSession", back_populates="research_queries")
    user = relationship("User", back_populates="research_queries")
    research_output = relationship(
        "ResearchOutput",
        back_populates="research_query",
        uselist=False,
        cascade="all, delete-orphan"
    )
    tool_executions = relationship(
        "ToolExecution",
        back_populates="research_query",
        cascade="all, delete-orphan",
        order_by="ToolExecution.execution_timestamp"
    )

    def __repr__(self):
        return f"<ResearchQuery(id={self.query_id}, session_id={self.session_id}, text='{self.query_text[:50]}...')>"
