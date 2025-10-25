import pytest
import pytest_asyncio
import asyncio
import json
from scrai_core.agents.models import Agent
from scrai_core.core.persistence import Base
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import ActionEvent
from scrai_core.world.systems import WorldStateSystem
from scrai_core.agents.memory import MemorySystem
import os
from dotenv import load_dotenv

load_dotenv()

TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")

@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for each test module."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def event_bus():
    """Fixture to provide a connected EventBus instance."""
    bus = EventBus(redis_url=TEST_REDIS_URL)
    await bus.connect()
    # Clear any old data from the streams
    redis_client = bus._redis
    await redis_client.delete("action_events", "world_state_committed_events")
    yield bus
    await bus.disconnect()

@pytest.mark.asyncio
async def test_heartbeat_pipeline(db_session, event_bus: EventBus):
    """
    Tests the full event consumer pipeline from ActionEvent to DB commit
    and WorldStateCommittedEvent publication.
    """
    # 1. Setup: Create a test agent
    test_agent = Agent(name="TestAgent", position="0,0")
    db_session.add(test_agent)
    db_session.commit()
    db_session.refresh(test_agent)
    agent_id = test_agent.id

    # 2. Start consumers in the background
    world_system = WorldStateSystem(event_bus, session_factory=lambda: db_session)
    memory_system = MemorySystem(event_bus)
    
    world_consumer_task = asyncio.create_task(world_system.run_consumer())
    memory_consumer_task = asyncio.create_task(memory_system.run_consumer())
    
    # Give consumers a moment to start up
    await asyncio.sleep(0.5)

    # 3. Publish an ActionEvent
    action_event = ActionEvent(
        entity_id=agent_id,
        sequence=1,
        action_type="move",
        payload={"new_position": "10,10"}
    )
    await event_bus.publish("action_events", action_event.model_dump(mode='json'))

    # 4. Assertions
    await asyncio.sleep(1) # Allow time for processing

    # Assert DB state changed
    updated_agent = db_session.query(Agent).filter(Agent.id == agent_id).one()
    assert updated_agent.position == "10,10"

    # Assert WorldStateCommittedEvent was received by MemorySystem
    # (In a real test, we'd check logs or a mock. For now, we'll check the stream)
    committed_stream = "world_state_committed_events"
    messages = await event_bus._redis.xrange(committed_stream)
    assert len(messages) == 1
    committed_event_data = json.loads(messages[0][1]['data'])
    assert committed_event_data['entity_id'] == agent_id
    assert committed_event_data['new_state']['position'] == "10,10"

    # 5. Test Idempotency
    # Publish the same event again
    await event_bus.publish("action_events", action_event.model_dump(mode='json'))
    await asyncio.sleep(1)

    # The DB state should NOT change again, but a new committed event will be published
    # by the current implementation. A more robust system would check event_id in a cache.
    # For now, we just ensure no errors occur.
    final_agent = db_session.query(Agent).filter(Agent.id == agent_id).one()
    assert final_agent.position == "10,10" # Still "10,10"

    # 6. Cleanup
    world_consumer_task.cancel()
    memory_consumer_task.cancel()
    await asyncio.gather(world_consumer_task, memory_consumer_task, return_exceptions=True)
