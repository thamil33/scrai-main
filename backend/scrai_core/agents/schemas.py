from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Agent(BaseModel):
    id: str
    name: str
    position: str

    class Config:
        from_attributes = True

class EpisodicMemory(BaseModel):
    id: str
    agent_id: str
    timestamp: datetime
    content: str
    event_type: Optional[str] = None
    salience_score: Optional[float] = None

    class Config:
        from_attributes = True
