import os
from typing import List, TypedDict
from scrai_core.core.llm_provider_factory import get_chat_model_from_env
from langgraph.graph import StateGraph, END, START
from scrai_core.agents.models import Agent, EpisodicMemory
from scrai_core.events.bus import EventBus
from scrai_core.events.schemas import ActionEvent
from scrai_core.agents.memory import get_relevant_memories, get_memories_for_agent
from scrai_core.core.persistence import get_session
from sentence_transformers import SentenceTransformer
from scrai_core.world.models import WorldObject
import uuid
import random

class ProtoAgentPublisher:
    """
    A simple agent stub that publishes a predefined action.
    This is a placeholder for a more complex cognitive agent.
    """
    def __init__(self, agent_model: Agent, event_bus: EventBus):
        self.agent_model = agent_model
        self.event_bus = event_bus
        self.sequence = 0

    async def publish_action(self):
        """Publishes a simple 'move' action."""
        self.sequence += 1
        action = ActionEvent(
            event_id=str(uuid.uuid4()),
            entity_id=self.agent_model.id,
            sequence=self.sequence,
            action_type="move",
            payload={"new_position": f"sim_{self.sequence},{self.sequence}"}
        )
        await self.event_bus.publish("action_events", action.model_dump(mode='json'))
        print(f"ProtoAgent {self.agent_model.name} published action: move")

class AgentState(TypedDict):
    agent_model: Agent
    memories: List[str]
    relevant_memories: List[str]
    nearby_objects: List[WorldObject]
    next_action: ActionEvent

class CognitiveAgent:
    def __init__(self, agent_model: Agent, event_bus: EventBus):
        self.agent_model = agent_model
        self.event_bus = event_bus
        self.llm = get_chat_model_from_env()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("perceive", self._perceive)
        graph.add_node("recall", self._recall)
        graph.add_node("reason", self._reason)
        graph.add_node("reflect", self._reflect)
        graph.add_node("act", self._act)

        graph.add_edge(START, "perceive")
        graph.add_edge("perceive", "recall")
        graph.add_edge("recall", "reason")
        graph.add_edge("reason", "reflect")
        graph.add_edge("reflect", "act")
        graph.add_edge("act", END)

        return graph.compile()

    async def _perceive(self, state: AgentState) -> AgentState:
        """Fetches the agent's current state, recent memories, and nearby objects."""
        print(f"Agent {self.agent_model.name}: Perceiving...")
        session = next(get_session())
        try:
            agent_model = session.query(Agent).filter(Agent.id == self.agent_model.id).one()
            # Simple perception: get all objects for now
            nearby_objects = session.query(WorldObject).all()
        finally:
            session.close()
        
        return {
            **state,
            "agent_model": agent_model,
            "nearby_objects": nearby_objects,
        }
    
    async def _recall(self, state: AgentState) -> AgentState:
        """Retrieves relevant memories based on the current state."""
        print(f"Agent {self.agent_model.name}: Recalling...")
        
        # Create a query string from the current perception
        perception_summary = f"Current position: {state['agent_model'].position}. Nearby objects: {len(state['nearby_objects'])}."
        query_embedding = self.embedding_model.encode(perception_summary)
        
        relevant_memories = get_relevant_memories(self.agent_model.id, query_embedding)
        memory_content = [mem.content for mem in relevant_memories]
        
        return {**state, "relevant_memories": memory_content}

    async def _reflect(self, state: AgentState) -> AgentState:
        """Generates high-level insights from recent memories."""
        print(f"Agent {self.agent_model.name}: Reflecting...")
        
        recent_memories = get_memories_for_agent(self.agent_model.id, limit=50)
        memory_content = [mem.content for mem in recent_memories]
        
        if not memory_content:
            return state
            
        prompt = f"""
        You are Agent {state['agent_model'].name}.
        Based on the following recent memories, what are 1-3 high-level insights or reflections?
        Memories: {memory_content}
        
        Example response:
        - "I have been spending a lot of time near the northern resource."
        - "My interactions with Agent B have been negative."
        """
        
        response = await self.llm.ainvoke(prompt)
        reflections = response.content.strip().split('\n')
        
        session = next(get_session())
        try:
            for reflection in reflections:
                if not reflection:
                    continue
                embedding = self.embedding_model.encode(reflection)
                memory = EpisodicMemory(
                    agent_id=self.agent_model.id,
                    content=reflection,
                    embedding=embedding,
                    event_type='reflection',
                )
                session.add(memory)
            session.commit()
        finally:
            session.close()
            
        return state

    async def _reason(self, state: AgentState) -> AgentState:
        """Uses an LLM to decide the next action."""
        print(f"Agent {self.agent_model.name}: Reasoning...")
        
        objects_prompt = "\n".join([f"- Object ID: {obj.id}, Type: {obj.object_type}, Position: {obj.position}" for obj in state["nearby_objects"]])
        
        # Generate a random example position to avoid biasing the LLM
        random_x = random.randint(1, 50)
        random_y = random.randint(1, 50)
        
        prompt = f"""
        You are Agent {state['agent_model'].name}.
        Your current position is {state['agent_model'].position}.
        Your relevant memories are: {state['relevant_memories']}.
        Nearby objects are:
        {objects_prompt}
        
        What is your next logical action? Consider your memories, but also prioritize exploring new areas if you seem to be stuck in a loop. Your response must be a JSON object representing an ActionEvent. You can either "move" or "interact_with_object".
        
        Example for moving: {{"action_type": "move", "payload": {{"new_position": "{random_x},{random_y}"}}}}
        Example for interacting: {{"action_type": "interact_with_object", "payload": {{"object_id": "some_object_id"}}}}
        """
        
        response = await self.llm.ainvoke(prompt)
        action_json = response.content
        
        # Basic validation and parsing
        import json
        action_data = json.loads(action_json)
        
        next_action = ActionEvent(
            entity_id=self.agent_model.id,
            sequence=0, # Placeholder
            action_type=action_data["action_type"],
            payload=action_data["payload"]
        )
        
        return {**state, "next_action": next_action}

    async def _act(self, state: AgentState):
        """Publishes the decided action to the event bus."""
        print(f"Agent {self.agent_model.name}: Acting...")
        await self.event_bus.publish("action_events", state["next_action"].model_dump(mode='json'))
        return state

    async def tick(self):
        """Runs one cycle of the agent's cognitive loop."""
        initial_state = {
            "agent_model": self.agent_model,
            "memories": [],
            "relevant_memories": [],
            "nearby_objects": [],
            "next_action": None
        }
        await self.graph.ainvoke(initial_state)
