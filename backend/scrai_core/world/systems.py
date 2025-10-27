import asyncio
from sqlalchemy.orm import Session
from scrai_core.core.persistence import get_session
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import ActionEvent, WorldStateCommittedEvent
from scrai_core.agents.models import Agent
from scrai_core.world.models import WorldObject
from sqlalchemy.exc import SQLAlchemyError
import structlog

logger = structlog.get_logger(__name__)

from typing import Callable

class WorldStateSystem:
    def __init__(self, event_bus: EventBus, session_factory: Callable[[], Session]):
        self.event_bus = event_bus
        self.session_factory = session_factory
        self.consumer_group = "world_state_group"
        self.consumer_name = "world_state_consumer_1"
        self.action_event_stream = "action_events"
        self.committed_event_stream = "world_state_committed_events"

    async def process_action_event(self, event_data: dict):
        """
        Processes a single ActionEvent, updates the world state,
        and publishes a WorldStateCommittedEvent.
        """
        try:
            action_event = ActionEvent.model_validate(event_data)
            logger.info("Processing ActionEvent", event_id=action_event.event_id)

            db: Session = self.session_factory()
            try:
                # Find the agent
                agent = db.query(Agent).filter(Agent.id == action_event.entity_id).first()
                if not agent:
                    logger.warning("Agent not found", agent_id=action_event.entity_id)
                    return

                previous_state = {"position": agent.position}
                
                if action_event.action_type == "move":
                    new_position = action_event.payload.get("new_position")
                    if new_position:
                        agent.position = new_position
                        logger.info("Agent moved", agent_id=agent.id, new_position=new_position)
                
                elif action_event.action_type == "interact_with_object":
                    object_id = action_event.payload.get("object_id")
                    target_object = db.query(WorldObject).filter(WorldObject.id == object_id).first()
                    if target_object:
                        # Example interaction: deplete a resource
                        if target_object.properties.get("resource_level", 0) > 0:
                            target_object.properties["resource_level"] -= 1
                        logger.info("Agent interacted with object", agent_id=agent.id, object_id=object_id)

                db.commit()
                db.refresh(agent)
                new_state = {"position": agent.position}
                logger.info("Committed state change", agent_id=agent.id)

                # Create and publish the committed event
                committed_event = WorldStateCommittedEvent(
                    event_id=action_event.event_id,
                    sequence=action_event.sequence,
                    entity_id=action_event.entity_id,
                    action_event=action_event,
                    previous_state=previous_state,
                    new_state=new_state
                )
                await self.event_bus.publish(
                    self.committed_event_stream,
                    committed_event.model_dump(mode='json')
                )
                logger.info("Published WorldStateCommittedEvent", event_id=action_event.event_id)

            except SQLAlchemyError as e:
                db.rollback()
                logger.error("Database error processing event", event_id=action_event.event_id, error=e)
                # Optionally publish a failure event
            finally:
                db.close()

        except Exception as e:
            logger.error("Error parsing or processing event data", event_data=event_data, error=e)

    async def run_consumer(self):
        """
        Continuously listens for ActionEvents and processes them.
        """
        logger.info("WorldStateSystem consumer starting...")
        await self.event_bus.connect()
        try:
            async for event_data in self.event_bus.subscribe(
                self.action_event_stream,
                self.consumer_group,
                self.consumer_name
            ):
                await self.process_action_event(event_data)
        except asyncio.CancelledError:
            logger.info("WorldStateSystem consumer stopped.")
        finally:
            await self.event_bus.disconnect()

async def main():
    # Example usage
    event_bus = EventBus()
    world_system = WorldStateSystem(event_bus, session_factory=get_session)
    try:
        await world_system.run_consumer()
    except KeyboardInterrupt:
        logger.info("Shutting down WorldStateSystem.")

if __name__ == "__main__":
    asyncio.run(main())
