import pytest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock, AsyncMock
from scrai_core.core.persistence import get_engine, Base
from scrai_core.agents.models import Agent, EpisodicMemory
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
async def test_reflection(mock_get_chat_model, setup_database):
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
    llm_stub = LLMStub('- I have been moving around a lot lately.\n- I interacted with object A.')
    mock_get_chat_model.return_value = llm_stub

    # 1. Create an agent and some memories
    agent = Agent(name="TestAgent", latitude=0.0, longitude=0.0)
    session.add(agent)
    session.commit()

    memories_content = [
        "Agent moved from 0,0 to 1,1.",
        "Agent moved from 1,1 to 2,2.",
        "Agent interacted with object A.",
        "Agent moved from 2,2 to 3,3.",
    ]

    for content in memories_content:
        embedding = embedding_model.encode(content)
        memory = EpisodicMemory(
            agent_id=agent.id,
            content=content,
            embedding=embedding,
            event_type="move" if "moved" in content else "interact"
        )
        session.add(memory)
    session.commit()

    # 2. Create a cognitive agent
    cognitive_agent = CognitiveAgent(agent, event_bus)

    # 3. Manually invoke the reflection step
    initial_state = {
        "agent_model": agent,
        "memories": [],
        "relevant_memories": [],
        "nearby_objects": [],
        "next_action": None
    }

    await cognitive_agent._reflect(initial_state)

    # 4. Verify that new reflection memories were created
    reflections = session.query(EpisodicMemory).filter(
        EpisodicMemory.agent_id == agent.id,
        EpisodicMemory.event_type == 'reflection'
    ).all()

    assert len(reflections) > 0
    assert "moving" in reflections[0].content.lower() or "interacted" in reflections[0].content.lower()
