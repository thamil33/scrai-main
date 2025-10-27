import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from scrai_core.agents.cognition import CognitiveAgent
from scrai_core.agents.models import Agent
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import ActionEvent

@pytest.fixture
def test_agent_model():
    """Fixture for a test Agent model."""
    return Agent(id="test_agent_id", name="TestAgent", latitude=10.0, longitude=10.0)

@pytest.fixture
def mock_event_bus():
    """Fixture for a mocked EventBus."""
    return MagicMock(spec=EventBus)

@pytest.mark.asyncio
@patch("scrai_core.agents.cognition.get_session")
@patch("scrai_core.agents.cognition.get_relevant_memories")
@patch("scrai_core.agents.cognition.get_chat_model_from_env")
async def test_cognitive_agent_tick(mock_get_chat_model, mock_get_relevant_memories, mock_get_session, test_agent_model, mock_event_bus, db_session):
    """
    Tests a single tick of the CognitiveAgent, ensuring the full
    perceive-reason-act loop completes and an action is published.
    """
    # Arrange
    # Mock database and memory retrieval
    mock_get_session.return_value.query.return_value.filter.return_value.one.return_value = test_agent_model
    mock_get_relevant_memories.return_value = []

    # Create LLM stub that returns a fixed response instead of making actual API calls
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content='{"action_type": "move", "payload": {"new_position": "11,11"}}'))
    mock_get_chat_model.return_value = mock_llm

    # Make the mocked event bus's publish method awaitable
    mock_event_bus.publish = AsyncMock(return_value=None)

    # Initialize the agent
    agent = CognitiveAgent(agent_model=test_agent_model, event_bus=mock_event_bus)

    # Act
    await agent.tick()

    # Assert
    # Ensure the perception step fetched data
    mock_get_session.assert_called_once()
    mock_get_relevant_memories.assert_called_once()

    # Ensure the reasoning step called the LLM
    mock_llm.ainvoke.assert_called_once()

    # Ensure the action step published an event
    mock_event_bus.publish.assert_called_once()

    # Verify the content of the published event
    published_args = mock_event_bus.publish.call_args[0]
    assert published_args[0] == "action_events"

    # The event data is the second argument
    event_data = published_args[1]
    assert event_data['action_type'] == "move"
    assert event_data['payload']['new_position'] == "11,11"
