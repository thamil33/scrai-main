import pytest
from uuid import uuid4
from unittest.mock import patch, MagicMock, AsyncMock
from scrai_core.agents.models import Agent, EpisodicMemory
from scrai_core.core.persistence import get_session
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import ActionEvent, WorldStateCommittedEvent
from scrai_core.agents.memory_consolidator import MemoryConsolidator

@pytest.fixture(scope="function")
def test_agent():
    """Fixture to create a test agent and clean up after."""
    session = next(get_session())
    try:
        agent = Agent(name="TestAgent", position="0,0")
        session.add(agent)
        session.commit()
        session.refresh(agent)
        yield agent
    finally:
        session.delete(agent)
        session.commit()
        session.close()

@patch("scrai_core.agents.memory_consolidator.SentenceTransformer")
def test_memory_consolidation(mock_sentence_transformer, test_agent):
    """
    Tests that the MemoryConsolidator correctly processes events and
    creates memories in the database.
    """
    # Mock the embedding model to avoid actual embedding computation
    mock_model = MagicMock()
    mock_model.encode.return_value = [0.1] * 384  # Mock embedding vector
    mock_sentence_transformer.return_value = mock_model

    event_bus = EventBus()
    consolidator = MemoryConsolidator(event_bus=event_bus, buffer_threshold=5)

    # 1. Publish enough events to trigger consolidation
    for i in range(5):
        action_event = ActionEvent(
            entity_id=test_agent.id,
            sequence=i,
            action_type="move",
            payload={"new_position": f"1,{i}"}
        )
        world_state_event = WorldStateCommittedEvent(
            event_id=str(uuid4()),
            sequence=i,
            entity_id=test_agent.id,
            schema_version="1.0",
            action_event=action_event,
            previous_state={"position": f"0,{i}"},
            new_state={"position": f"1,{i}"}
        )
        consolidator.event_buffer.append(world_state_event)

    # 2. Manually trigger the consolidator's processing logic for the test

    # Process the buffer directly
    consolidator._process_buffer()

    # 3. Verify that memories were created
    session = next(get_session())
    try:
        memories = session.query(EpisodicMemory).filter(EpisodicMemory.agent_id == test_agent.id).all()
    finally:
        session.close()
        assert len(memories) == 5
        for memory in memories:
            assert "Agent moved from" in memory.content
