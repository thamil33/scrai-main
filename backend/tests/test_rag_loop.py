import pytest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock, AsyncMock
from scrai_core.core.persistence import get_engine, Base
from scrai_core.agents.models import Agent, EpisodicMemory
from scrai_core.world.models import WorldObject
from scrai_core.events.bus import EventBus
from scrai_core.agents.cognition import CognitiveAgent
from sentence_transformers import SentenceTransformer
import asyncio

@pytest.fixture(scope="module")
def setup_database():
    engine = get_engine()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.mark.asyncio
@patch("scrai_core.agents.cognition.get_chat_model_from_env")
async def test_rag_loop(mock_get_chat_model, setup_database):
    session = setup_database
    event_bus = EventBus()
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # Create LLM stub that returns a fixed response instead of making actual API calls
    class LLMStub:
        def __init__(self, response_content):
            self.response_content = response_content

        async def ainvoke(self, prompt):
            # Return a stub response instead of making actual API call
            return MagicMock(content=self.response_content)

    # Use stub instead of mock to avoid actual API calls
    llm_stub = LLMStub('{"action_type": "move", "payload": {"new_latitude": 10.0, "new_longitude": 10.0}}')
    mock_get_chat_model.return_value = llm_stub

    # 1. Create an agent and a memory
    agent = Agent(name="TestAgent", latitude=0.0, longitude=0.0)
    session.add(agent)
    session.commit()

    memory_content = "A critical piece of information is stored at location 10,10."
    memory_embedding = embedding_model.encode(memory_content)
    memory = EpisodicMemory(
        agent_id=agent.id,
        content=memory_content,
        embedding=memory_embedding,
        event_type="information"
    )
    session.add(memory)
    session.commit()

    # 2. Create a cognitive agent
    cognitive_agent = CognitiveAgent(agent, event_bus)

    # 3. Tick the agent's cognitive loop
    # In a real scenario, the agent would perceive the need to find the information.
    # For this test, we'll simulate this by crafting a perception that should trigger the memory.

    # We'll manually set the state to simulate the agent being near the location
    # This is a simplified way to test the RAG loop
    initial_state = {
        "agent_model": agent,
        "memories": [],
        "relevant_memories": [],
        "nearby_objects": [],
        "nearby_agents": [],
        "environmental_context": f"Agent is at latitude {agent.latitude}, longitude {agent.longitude}. There are 0 objects and 0 other agents in the environment.",
        "next_action": None
    }

    # Manually invoke the recall and reason steps to check the output
    recalled_state = await cognitive_agent._recall(initial_state)
    assert any(memory_content in mem for mem in recalled_state["relevant_memories"])

    reasoned_state = await cognitive_agent._reason(recalled_state)
    # Check that an action was decided (the specific action may vary based on LLM response)
    assert reasoned_state["next_action"] is not None
    assert reasoned_state["next_action"].action_type in ["move", "interact_with_object", "communicate"]
    # Check that the payload contains the expected structure
    assert "payload" in reasoned_state["next_action"].model_dump()
