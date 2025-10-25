# ScrAI Development: Phase II Goals

### **🎯 Phase II Goal: Evolve from a reactive event pipeline to a proactive, intelligent agent system with memory, cognition, and a more dynamic world.**

---

### **Milestone 1: Implementing Agent Memory (The Scribe)**
*Goal: Build the memory consolidation pipeline designed in Phase I to give agents a persistent, queryable long-term memory.*

- **Implement Memory Consolidator Worker:**
    - Create a worker process that triggers based on the logic in `memory_consolidator_design.md` (event count and simulated time).
    - The worker will read `WorldStateCommittedEvent`s from the short-term buffer (Redis).
    - **Initial Logic:** For the first pass, the consolidator will perform simple summarization (e.g., "Agent moved from X to Y") and store these summaries in a new PostgreSQL table (`agent_memories`).
- **Long-Term Memory Storage:**
    - Create a SQLAlchemy `Memory` model to store the consolidated memories.
    - Implement basic retrieval functions (e.g., `get_memories_for_agent(agent_id)`).
- **Integration Test:**
    - Write a test that generates >100 events for an agent.
    - Assert that the Memory Consolidator worker runs and creates summarized entries in the `agent_memories` table.

---

### **Milestone 2: True Agent Cognition (The Spark of Thought)**
*Goal: Replace the `ProtoAgentPublisher` stub with a genuine cognitive loop, enabling agents to make decisions based on their state and memories.*

- **Integrate LangGraph:**
    - Replace the `ProtoAgentPublisher` with a `CognitiveAgent` class that uses LangGraph to manage its internal state machine (e.g., PERCEIVE -> REASON -> ACT).
- **Perception Step:**
    - The agent's cognitive loop will start by fetching its current state from the database (`agents` table).
    - It will also retrieve recent memories from the new `agent_memories` table.
- **Reasoning Step:**
    - Implement a simple reasoning prompt using an LLM.
    - **Example Prompt:** "You are Agent {agent.name}. Your current position is {agent.position}. Your recent memories are: {memories}. What is your next logical action?"
    - The output of the LLM will be a structured `ActionEvent` (e.g., `{"action_type": "move", "payload": {"new_position": "20,20"}}`).
- **Action Step:**
    - The agent will publish the LLM-generated `ActionEvent` to the event bus.
- **End-to-End Test:**
    - Write a test that initializes an agent, runs a single `tick()` of the simulation, and asserts that an LLM-generated action was published and correctly applied to the agent's state in the database.

---

### **Milestone 3: A More Dynamic World (Expanding Interactions)**
*Goal: Move beyond simple "move" actions to create a richer simulation environment.*

- **Introduce World Objects:**
    - Create a new SQLAlchemy `WorldObject` model (`id`, `object_type`, `position`, `properties` JSONB).
    - Add objects to the simulation scenario (e.g., a "resource" object).
- **Expand Action Schema:**
    - Add new action types to `events/schemas.py`, such as `interact_with_object` (e.g., `{"action_type": "interact", "payload": {"object_id": "obj_1", "interaction": "gather"}}`).
- **Update WorldStateSystem:**
    - Add logic to the `WorldStateSystem` to handle the new action types and modify the state of `WorldObject`s.
- **Update Agent Cognition:**
    - Enhance the reasoning prompt to make agents aware of world objects and capable of deciding to interact with them.
- **Integration Test:**
    - Create a test scenario with an agent and a resource object.
    - Assert that the agent can perceive the object, decide to interact with it, and that the object's state is correctly updated in the database.

---

### **Milestone 4: Enhanced Observability & Tooling (The Watchtower)**
*Goal: Improve our ability to debug, monitor, and understand the complex agent behaviors that will emerge.*

- **Structured Logging:**
    - Integrate a library like `structlog` to produce JSON-formatted logs.
    - Add `agent_id`, `event_id`, and `sequence` to log records to make tracing an agent's lifecycle easier.
- **Simple Admin UI:**
    - Create a basic web frontend (using the existing FastAPI backend) to visualize agent positions and latest memories.
    - This provides a real-time view into the state of the simulation.
- **Refine Simulation Controls:**
    - Add API endpoints to the FastAPI app to `pause`, `resume`, and `tick` the simulation manually.
