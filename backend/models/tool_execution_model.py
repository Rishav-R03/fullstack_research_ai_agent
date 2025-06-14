from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

class ToolExecution(Base):
    __tablename__ = "tool_executions"

    execution_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    query_id = Column(UUID(as_uuid=True), ForeignKey("research_queries.query_id"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False) 
    tool_input = Column(Text)
    tool_output = Column(Text)
    execution_timestamp = Column(DateTime(timezone=True), default=func.now())
    status = Column(String(50), nullable=False) 
    error_message = Column(Text, nullable=True) 
    research_query = relationship("ResearchQuery", back_populates="tool_executions")

    def __repr__(self):
        return f"<ToolExecution(id={self.execution_id}, query_id={self.query_id}, tool='{self.tool_name}', status='{self.status}')>"
