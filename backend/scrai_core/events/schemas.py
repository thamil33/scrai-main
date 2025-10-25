from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Dict, Any

class ActionEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    sequence: int
    entity_id: str
    schema_version: str = "1.0"
    action_type: str
    payload: Dict[str, Any]

from typing import Literal

class WorldStateCommittedEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    sequence: int
    entity_id: str
    schema_version: str = "1.0"
    action_event: ActionEvent
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]

ActionType = Literal["move", "interact_with_object"]

def create_action_event(agent_id: str, action_type: ActionType, payload: Dict[str, Any], sequence: int) -> ActionEvent:
    return ActionEvent(
        entity_id=agent_id,
        action_type=action_type,
        payload=payload,
        sequence=sequence
    )
