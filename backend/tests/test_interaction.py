import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from scrai_core.agents.cognition import CognitiveAgent
from scrai_core.agents.models import Agent
from scrai_core.world.models import WorldObject
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import ActionEvent
from scrai_core.world.systems import WorldStateSystem
from scrai_core.core.persistence import get_session

@pytest.fixture
def test_agent_model():
    return Agent(id="test_agent_id", name="TestAgent", position="10,10")

@pytest.fixture
def test_world_object():
    return WorldObject(id="test_object_id", object_type="resource", position="11,11", properties={"resource_level": 5})

@pytest.fixture
def mock_event_bus():
    return MagicMock(spec=EventBus)

@pytest.mark.asyncio
@patch("scrai_core.agents.cognition.get_session")
@patch("scrai_core.agents.cognition.get_memories_for_agent")
@patch("scrai_core.agents.cognition.get_chat_model_from_env")
async def test_agent_interacts_with_object(mock_get_chat_model, mock_get_memories, mock_get_session, test_agent_model, test_world_object, mock_event_bus):
    # Arrange
    mock_get_session.return_value.query.return_value.filter.return_value.one.return_value = test_agent_model
    mock_get_session.return_value.query.return_value.all.return_value = [test_world_object]
    mock_get_memories.return_value = []

    # Mock the LLM response from the factory
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content='{"action_type": "interact_with_object", "payload": {"object_id": "test_object_id"}}'))
    mock_get_chat_model.return_value = mock_llm
    
    # Make the mocked event bus's publish method awaitable
    mock_event_bus.publish = AsyncMock(return_value=None)

    agent = CognitiveAgent(agent_model=test_agent_model, event_bus=mock_event_bus)

    # Act
    await agent.tick()

    # Assert
    mock_event_bus.publish.assert_called_once()
    
    # Verify the content of the published event
    published_args = mock_event_bus.publish.call_args[0]
    assert published_args[0] == "action_events"
    
    # The event data is the second argument
    event_data = published_args[1]
    assert event_data['action_type'] == "interact_with_object"
    assert event_data['payload']['object_id'] == "test_object_id"
