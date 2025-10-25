from sqlalchemy.orm import Session
from ..agents.models import Agent
import logging

logger = logging.getLogger(__name__)

def create_agent(db: Session, name: str, position: str) -> Agent:
    """
    Creates a new agent and saves it to the database.
    This is a simple utility for setting up test scenarios.
    """
    try:
        new_agent = Agent(name=name, position=position)
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        logger.info(f"Created agent '{name}' with ID {new_agent.id} at position {position}.")
        return new_agent
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create agent '{name}': {e}")
        raise
