import asyncio
import structlog
from typing import List
from scrai_core.core.persistence import get_session
from scrai_core.agents.models import EpisodicMemory
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import WorldStateCommittedEvent

logger = structlog.get_logger(__name__)

class MemorySystem:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.consumer_group = "memory_system_group"
        self.consumer_name = "memory_system_consumer_1"
        self.committed_event_stream = "world_state_committed_events"

    async def process_event(self, event_data: dict):
        """
        Processes a WorldStateCommittedEvent and logs it.
        """
        try:
            event = WorldStateCommittedEvent.model_validate(event_data)
            logger.info(
                "MemorySystem received WorldStateCommittedEvent",
                event_id=event.event_id,
                entity_id=event.entity_id,
            )
            # In a real implementation, this is where the event would be
            # processed and stored as a long-term memory for the agent.
        except Exception as e:
            logger.error(
                "Error processing WorldStateCommittedEvent in MemorySystem",
                error=e,
                event_data=event_data,
            )

    async def run_consumer(self):
        """
        Continuously listens for WorldStateCommittedEvents and processes them.
        """
        logger.info("MemorySystem consumer starting...")
        await self.event_bus.connect()
        try:
            async for event_data in self.event_bus.subscribe(
                self.committed_event_stream,
                self.consumer_group,
                self.consumer_name,
            ):
                await self.process_event(event_data)
        except asyncio.CancelledError:
            logger.info("MemorySystem consumer stopped.")
        finally:
            await self.event_bus.disconnect()

def get_memories_for_agent(agent_id: str, limit: int = 50) -> List[EpisodicMemory]:
    """
    Retrieves the most recent memories for a given agent.

    :param agent_id: The ID of the agent whose memories to retrieve.
    :param limit: The maximum number of memories to return.
    :return: A list of EpisodicMemory objects.
    """
    session = next(get_session())
    try:
        return (
            session.query(EpisodicMemory)
            .filter(EpisodicMemory.agent_id == agent_id)
            .order_by(EpisodicMemory.timestamp.desc())
            .limit(limit)
            .all()
        )
    finally:
        session.close()

def get_relevant_memories(agent_id: str, query_embedding, k: int = 10) -> List[EpisodicMemory]:
    """
    Retrieves the most relevant memories for a given agent using vector similarity search.

    :param agent_id: The ID of the agent.
    :param query_embedding: The embedding of the query.
    :param k: The number of memories to retrieve.
    :return: A list of the most relevant EpisodicMemory objects.
    """
    session = next(get_session())
    try:
        # The <=> operator is the cosine distance operator in pgvector
        return session.query(EpisodicMemory).filter(EpisodicMemory.agent_id == agent_id).order_by(EpisodicMemory.embedding.cosine_distance(query_embedding)).limit(k).all()
    finally:
        session.close()
