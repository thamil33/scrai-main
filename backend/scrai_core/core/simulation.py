import asyncio
from sqlalchemy.orm import Session
from scrai_core.core.persistence import get_session
from scrai_core.events.bus import EventBus
from scrai_core.agents.models import Agent
from scrai_core.agents.cognition import CognitiveAgent
import logging

logger = logging.getLogger(__name__)

class Simulation:
    def __init__(self, event_bus: EventBus, db_session: Session):
        self.event_bus = event_bus
        self.db_session = db_session
        self.agents = []

    def load_agents(self):
        """Loads all agents from the database and creates cognitive agent instances."""
        try:
            all_agents = self.db_session.query(Agent).all()
            self.agents = [CognitiveAgent(agent, self.event_bus) for agent in all_agents]
            logger.info(f"Loaded {len(self.agents)} cognitive agents for simulation.")
        except Exception as e:
            logger.error(f"Failed to load agents: {e}")
            raise

    async def tick(self):
        """
        Executes one tick of the simulation, where each agent publishes an action.
        """
        if not self.agents:
            logger.warning("No agents loaded, simulation tick has no effect.")
            return
        
        logger.info(f"--- Simulation Tick Start ---")
        tasks = [agent.tick() for agent in self.agents]
        await asyncio.gather(*tasks)
        logger.info(f"--- Simulation Tick End ---")

async def main():
    # Example usage
    from scrai_core.scenarios.loader import create_agent
    
    # Setup
    event_bus = EventBus()
    await event_bus.connect()
    
    # Create a sample agent for the simulation
    db = next(get_session())
    create_agent(db, name="SimAgent1", position="0,0")
    create_agent(db, name="SimAgent2", position="5,5")
    db.close()

    # Run simulation
    sim = Simulation(event_bus, db)
    sim.load_agents()
    
    try:
        for i in range(3): # Run 3 ticks
            await sim.tick()
            await asyncio.sleep(1)
    finally:
        await event_bus.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
