# ScrAI Development: Phase III Goals

### **🎯 Phase III Goal: Evolve the agent's simple memory log into a sophisticated, multi-tiered memory system, enabling true context-aware reasoning through Retrieval-Augmented Generation (RAG).**

---

### **Milestone 1: Implementing Vector Memory (Episodic Memory)**
*Goal: Replace the simple text-based memory table with a vector store to enable semantic memory retrieval.*

- **Integrate pgvector:**
    - Add the `pgvector` extension to the PostgreSQL setup.
    - Install the necessary Python library (`pgvector`) and configure SQLAlchemy to use the `VECTOR` type.
- **Create `EpisodicMemory` Model:**
    - Design a new SQLAlchemy model, `EpisodicMemory`, to store vector embeddings alongside rich metadata (e.g., `agent_id`, `timestamp`, `salience_score`, `event_type`).
- **Upgrade Memory Consolidator:**
    - Modify the `MemoryConsolidator` to use a sentence-transformer model (e.g., from Hugging Face) to generate embeddings for incoming `WorldStateCommittedEvent`s.
    - Instead of writing plain text summaries, the worker will now populate the `episodic_memories` table with these embeddings.
- **Implement Vector Search:**
    - Create a core retrieval function, `get_relevant_memories(agent_id, query_embedding, k=10)`, that performs cosine similarity searches against the `episodic_memories` table.

---

### **Milestone 2: Integrating RAG into Agent Cognition (The Recall Node)**
*Goal: Empower agents to query their memories and use the results to inform their decisions.*

- **Add `Recall` Node to LangGraph:**
    - Introduce a new `Recall` node into the `CognitiveAgent`'s LangGraph, positioned between the `Perceive` and `Reason` nodes.
- **Implement Recall Logic:**
    - The `Recall` node will generate a query embedding based on the agent's current perceived state.
    - It will then call the `get_relevant_memories` function to fetch the most relevant memories from the vector store.
- **Enhance the Reasoning Prompt:**
    - Update the `Reason` node's prompt to include a new dynamic section: "Relevant Memories."
    - The memories retrieved by the `Recall` node will be injected into this section, providing the LLM with crucial context for its decision-making process.

---

### **Milestone 3: Implementing Reflective Memory (The Reflection Node)**
*Goal: Enable agents to form higher-level insights and abstractions by summarizing and reflecting on their experiences.*

- **Add `Reflection` Node to LangGraph:**
    - Add a new `Reflection` node to the `CognitiveAgent`'s graph. This node will be triggered periodically (e.g., after a set number of ticks or when the agent's state is idle).
- **Implement Reflection Logic:**
    - The `Reflection` node will retrieve a broad set of recent episodic memories.
    - It will use an LLM with a specialized prompt to generate high-level summaries or insights from these memories. (e.g., "I have been spending a lot of time near the northern resource," or "My interactions with Agent B have been negative.").
- **Store Reflections:**
    - These generated reflections will be converted into embeddings and stored as a distinct memory type (e.g., `memory_type='reflection'`) in the `episodic_memories` table, allowing them to be recalled in future reasoning cycles.

---

### **Milestone 4: Refinement and End-to-End Validation**
*Goal: Ensure the new cognitive architecture is robust, testable, and observable.*

- **Create RAG Integration Test:**
    - Write a new test (`test_rag_loop.py`) that creates a scenario where an agent must rely on memory to act logically.
    - **Example:** An agent is told a piece of information, moves to a new location, and must recall that information later to complete a task.
- **Write Reflection Test:**
    - Create a test to verify that the `Reflection` node correctly generates and stores summaries after a series of events.
- **Update Frontend:**
    - Enhance the Agent Inspector UI to display the memories being retrieved and injected by the `Recall` node during each cognitive tick, making the RAG process transparent and debuggable.


