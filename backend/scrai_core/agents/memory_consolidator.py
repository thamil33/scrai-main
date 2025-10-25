import time
from typing import List
from scrai_core.core.persistence import get_session
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import WorldStateCommittedEvent
from scrai_core.agents.models import EpisodicMemory
from sentence_transformers import SentenceTransformer

class MemoryConsolidator:
    """
    A worker that consumes world state events, consolidates them into
    agent memories, and stores them in long-term storage.
    """
    def __init__(self, event_bus: EventBus, buffer_threshold: int = 100):
        self.event_bus = event_bus
        self.buffer_threshold = buffer_threshold
        self.event_buffer: List[WorldStateCommittedEvent] = []
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def _summarize_event(self, event: WorldStateCommittedEvent) -> str:
        """
        Generates a simple summary from a WorldStateCommittedEvent.
        """
        # Initial simple summarization logic
        if event.action_event.action_type == "move":
            old_position = event.previous_state.get("position", "unknown")
            new_position = event.new_state.get("position", "unknown")
            return f"Agent moved from {old_position} to {new_position}."
        return f"Agent performed action: {event.action_event.action_type}."

    def _process_buffer(self):
        """
        Processes the event buffer, creating and saving memories.
        """
        if not self.event_buffer:
            return

        print(f"Processing {len(self.event_buffer)} events from buffer...")
        session = next(get_session())
        try:
            for event in self.event_buffer:
                summary = self._summarize_event(event)
                embedding = self.embedding_model.encode(summary)
                memory = EpisodicMemory(
                    agent_id=event.entity_id,
                    content=summary,
                    embedding=embedding,
                    event_type=event.action_event.action_type,
                )
                session.add(memory)
            session.commit()
        finally:
            session.close()
        
        self.event_buffer.clear()
        print("Buffer processed and cleared.")

    def run(self):
        """
        Main loop to consume events and trigger consolidation.
        """
        print("Memory Consolidator worker started...")
        while True:
            events = self.event_bus.consume_world_state_events()
            if events:
                for event in events:
                    self.event_buffer.append(event)
            
            if len(self.event_buffer) >= self.buffer_threshold:
                self._process_buffer()
            
            time.sleep(1) # Prevent busy-waiting

if __name__ == "__main__":
    # Example of how to run the worker
    # This would typically be managed by a process manager
    bus = EventBus()
    consolidator = MemoryConsolidator(event_bus=bus)
    consolidator.run()
