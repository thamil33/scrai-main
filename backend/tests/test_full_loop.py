import pytest
import pytest_asyncio
import asyncio
from unittest.mock import patch
from scrai_core.agents.models import Agent
from scrai_core.core.persistence import Base
from scrai_core.events.bus import EventBus
from scrai_core.core.simulation import Simulation
from scrai_core.scenarios.loader import create_agent
from scrai_core.world.systems import WorldStateSystem
import os
from dotenv import load_dotenv

load_dotenv()

TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def event_bus():
    bus = EventBus(redis_url=TEST_REDIS_URL)
    await bus.connect()
    redis_client = bus._redis
    await redis_client.delete("action_events", "world_state_committed_events")
    yield bus
    await bus.disconnect()

@pytest.mark.asyncio
@patch("scrai_core.agents.cognition.get_session")
async def test_full_simulation_loop(mock_get_session, db_session, event_bus: EventBus):
    """
    Tests the full end-to-end loop from agent action publication
    to world state change.
    """
    # Make the patched get_session return the test's db_session
    mock_get_session.return_value = iter([db_session])

    # 1. Setup: Create a test agent using the scenario loader
    test_agent = create_agent(db_session, name="FullLoopAgent", position="start")
    agent_id = test_agent.id

    # 2. Start the WorldStateSystem consumer
    world_system = WorldStateSystem(event_bus, session_factory=lambda: db_session)
    consumer_task = asyncio.create_task(world_system.run_consumer())
    await asyncio.sleep(0.5)

    # 3. Initialize and run one tick of the simulation
    simulation = Simulation(event_bus, db_session)
    simulation.load_agents() # Loads the agent we just created
    await simulation.tick()

    # 4. Assertions
    await asyncio.sleep(1) # Allow time for event processing

    # Assert the agent's state has changed in the database
    updated_agent = db_session.query(Agent).filter(Agent.id == agent_id).one()
    # Note: The exact position will depend on the LLM's response,
    # so we just check that it's not the starting position.
    assert updated_agent.position != "start"

    # 5. Cleanup
    consumer_task.cancel()
    await asyncio.gather(consumer_task, return_exceptions=True)
