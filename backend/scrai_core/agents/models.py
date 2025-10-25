from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import VECTOR
from scrai_core.core.persistence import Base
from uuid import uuid4
from datetime import datetime

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    position = Column(String, nullable=False) # This could be a more complex type later

    episodic_memories = relationship("EpisodicMemory", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent(id='{self.id}', name='{self.name}', position='{self.position}')>"

class EpisodicMemory(Base):
    __tablename__ = "episodic_memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    content = Column(Text, nullable=False)
    event_type = Column(String, nullable=True)
    salience_score = Column(Float, nullable=True)
    embedding = Column(VECTOR(384), nullable=False)

    agent = relationship("Agent", back_populates="episodic_memories")

    def __repr__(self):
        return f"<EpisodicMemory(id='{self.id}', agent_id='{self.agent_id}', timestamp='{self.timestamp}')>"
