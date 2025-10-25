from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import JSONB
from scrai_core.core.persistence import Base
from uuid import uuid4

class WorldObject(Base):
    __tablename__ = "world_objects"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    object_type = Column(String, nullable=False)
    position = Column(String, nullable=False)
    properties = Column(JSONB, nullable=True)

    def __repr__(self):
        return f"<WorldObject(id='{self.id}', type='{self.object_type}', position='{self.position}')>"
