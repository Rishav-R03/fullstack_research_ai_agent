from sqlalchemy import Column, String, Text, Boolean, ForeignKey, func, text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB 
from sqlalchemy.orm import relationship

from database import Base 
class ResearchOutput(Base):
    __tablename__ = "research_outputs"

    output_id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    query_id = Column(UUID(as_uuid=True), ForeignKey("research_queries.query_id"), unique=True, nullable=False, index=True)
    topic = Column(String(255))
    summary = Column(Text)
    sources = Column(JSONB) 
    tools_used_reported = Column(JSONB)
    parsing_successful = Column(Boolean, default=True)
    raw_llm_output = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now()) 
    research_query = relationship("ResearchQuery", back_populates="research_output")

    def __repr__(self):
        return f"<ResearchOutput(id={self.output_id}, query_id={self.query_id}, topic='{self.topic[:30]}...')>"
