import pytest
from sqlalchemy.orm import sessionmaker
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
async def test_rag_loop(setup_database):
    session = setup_database
    event_bus = EventBus()
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # 1. Create an agent and a memory
    agent = Agent(name="TestAgent", position="0,0")
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
        "next_action": None
    }
    
    # Manually invoke the recall and reason steps to check the output
    recalled_state = await cognitive_agent._recall(initial_state)
    assert any(memory_content in mem for mem in recalled_state["relevant_memories"])

    reasoned_state = await cognitive_agent._reason(recalled_state)
    assert reasoned_state["next_action"].action_type == "move"
    assert reasoned_state["next_action"].payload["new_position"] == "10,10"
