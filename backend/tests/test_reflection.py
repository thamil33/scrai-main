import pytest
from sqlalchemy.orm import sessionmaker
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
async def test_reflection(setup_database):
    session = setup_database
    event_bus = EventBus()
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # 1. Create an agent and some memories
    agent = Agent(name="TestAgent", position="0,0")
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
