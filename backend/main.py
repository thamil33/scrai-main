import sys
import os
import asyncio
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from prometheus_client import Counter
from typing import List
from pydantic import BaseModel
from scrai_core.core.logging_config import setup_logging
from scrai_core.core.persistence import get_session
from scrai_core.core.db_init import init_db
from scrai_core.agents.models import Agent, EpisodicMemory
from scrai_core.world.models import WorldObject
from scrai_core.agents.schemas import Agent as AgentSchema, EpisodicMemory as EpisodicMemorySchema
from scrai_core.events.bus import EventBus
from scrai_core.world.systems import WorldStateSystem
from scrai_core.agents.memory_consolidator import MemoryConsolidator
from scrai_core.core.simulation import Simulation


logger = structlog.get_logger(__name__)

# --- Simulation State ---
SIMULATION_PAUSED = asyncio.Event()
SIMULATION_PAUSED.set() # Start in a running state
MANUAL_TICK = asyncio.Event()
SIMULATION_INSTANCE = None

# --- Prometheus Metrics ---
EVENTS_PROCESSED = Counter("events_processed_total", "Total number of events processed by the WorldStateSystem")

# --- FastAPI App ---
app = FastAPI(title="ScrAI Simulation")

# --- Background Tasks ---
async def run_simulation_loop():
    """The main loop for the simulation ticks."""
    while True:
        await SIMULATION_PAUSED.wait()
        
        if MANUAL_TICK.is_set():
            if SIMULATION_INSTANCE:
                await SIMULATION_INSTANCE.tick()
            MANUAL_TICK.clear()
        else:
            # Automatic tick every 2 seconds if not paused and not manually ticked
            if SIMULATION_INSTANCE:
                await SIMULATION_INSTANCE.tick()
        
        await asyncio.sleep(2)

async def run_systems():
    """Runs the core systems of the simulation."""
    global SIMULATION_INSTANCE
    setup_logging()
    event_bus = EventBus()
    db_session = next(get_session())
    
    # Initialize and load the simulation
    SIMULATION_INSTANCE = Simulation(event_bus, db_session)
    SIMULATION_INSTANCE.load_agents()

    world_system = WorldStateSystem(event_bus, session_factory=get_session)
    memory_consolidator = MemoryConsolidator(event_bus)

    # Instrument the process_action_event method
    original_process_action = world_system.process_action_event
    async def instrumented_process_action(event_data: dict):
        await original_process_action(event_data)
        EVENTS_PROCESSED.inc()
    world_system.process_action_event = instrumented_process_action

    # Start consumers and simulation loop
    world_task = asyncio.create_task(world_system.run_consumer())
    memory_task = asyncio.create_task(memory_consolidator.run())
    simulation_task = asyncio.create_task(run_simulation_loop())
    
    await asyncio.gather(world_task, memory_task, simulation_task)

@app.on_event("startup")
async def startup_event():
    """Initialize DB and start the background simulation systems."""
    init_db()
    asyncio.create_task(run_systems())

# --- API Models ---
class DashboardData(BaseModel):
    agents: List[AgentSchema]
    memories: List[EpisodicMemorySchema]

class CreateAgentRequest(BaseModel):
    name: str
    latitude: float
    longitude: float

# --- Routes ---
@app.get("/api/dashboard", response_model=DashboardData)
def get_dashboard_data():
    session = next(get_session())
    try:
        agents = session.query(Agent).all()
        memories = session.query(EpisodicMemory).order_by(EpisodicMemory.timestamp.desc()).limit(20).all()
        return {"agents": agents, "memories": memories}
    finally:
        session.close()

@app.post("/api/agents", response_model=AgentSchema, status_code=201)
def create_agent(agent_data: CreateAgentRequest):
    """Creates a new agent and adds it to the simulation."""
    session = next(get_session())
    try:
        new_agent = Agent(
            name=agent_data.name,
            latitude=agent_data.latitude,
            longitude=agent_data.longitude
        )
        session.add(new_agent)
        session.commit()
        session.refresh(new_agent)
        
        logger.info("Created new agent", agent_name=new_agent.name, agent_id=new_agent.id)
        
        # Reload agents in the running simulation instance
        if SIMULATION_INSTANCE:
            SIMULATION_INSTANCE.load_agents()
            logger.info("Reloaded simulation agents.")
        
        return new_agent
    except Exception as e:
        session.rollback()
        logger.error("Failed to create agent", error=e)
        raise HTTPException(status_code=500, detail="Failed to create agent in the database.")
    finally:
        session.close()

# --- Simulation Control ---
@app.post("/api/simulation/pause")
async def pause_simulation():
    SIMULATION_PAUSED.clear()
    logger.info("Simulation paused.")
    return {"status": "paused"}

@app.post("/api/simulation/resume")
async def resume_simulation():
    SIMULATION_PAUSED.set()
    logger.info("Simulation resumed.")
    return {"status": "running"}

@app.post("/api/simulation/tick")
async def tick_simulation():
    logger.info("Manual simulation tick requested.")
    MANUAL_TICK.set()
    return {"status": "tick requested"}

@app.post("/api/simulation/reset")
async def reset_simulation():
    """Resets the simulation state by clearing all agents, memories, and objects."""
    global SIMULATION_INSTANCE
    logger.info("Resetting simulation state...")
    
    session = next(get_session())
    try:
        # Clear all state-related tables
        session.query(EpisodicMemory).delete()
        session.query(Agent).delete()
        session.query(WorldObject).delete()
        session.commit()
        logger.info("Cleared database tables.")
        
        # Re-initialize the simulation
        if SIMULATION_INSTANCE:
            SIMULATION_INSTANCE.load_agents()
            logger.info("Reloaded agents and scenarios.")
        
        return {"status": "reset"}
    except Exception as e:
        session.rollback()
        logger.error("Failed to reset simulation", error=e)
        raise HTTPException(status_code=500, detail="Failed to reset the simulation.")
    finally:
        session.close()

# Add Prometheus metrics endpoint
metrics_app = PrometheusFastApiInstrumentator().instrument(app).expose(app)
