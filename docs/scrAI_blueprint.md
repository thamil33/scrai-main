# ScrAI: The Synthetic Cognition and Reasoning Architecture Interface
### Master Development Blueprint v3.0 — “Emergent Intelligence Through Event-Driven Worlds”

---

## 1. Introduction

### 1.1. Overview
**ScrAI**  is not merely a simulation engine or a narrative sandbox. It is a **narrative laboratory**—a dynamic “what-if” engine designed for creators, researchers, and theorists who wish to witness **emergent intelligence and storytelling** unfold from first principles.  

At its core, ScrAI is a **persistent, single-player world** where autonomous AI agents—powered by **LangGraph** and advanced LLM reasoning systems—develop, act, and evolve independently. Each agent possesses persistent memories, goals, and cognitive models, enabling them to generate believable, contextually consistent behavior and dialogue.  

The user acts as **director and observer**, setting initial conditions, designing agents and factions, and then watching the emergent narrative evolve. Whether simulating political intrigue, post-human societies, or historical campaigns, ScrAI turns your hypotheses into living experiments.

---

## 2. Design Philosophy

| Principle | Description |
|------------|-------------|
| **Agent Autonomy** | Agents act, reason, and evolve independently, guided by internal states, not direct scripting. |
| **Emergent Narrative** | No pre-written plots. Stories arise from the interplay between memory, goals, and environment. |
| **Persistence & Evolution** | All world states and agent memories persist between sessions, ensuring continuity. |
| **Event-Driven Synchronization** | All systems communicate via the Event Bus—no direct state mutation. |
| **Radical Modularity** | Every subsystem (agent cognition, world logic, UI, data layer) is replaceable. |
| **Observability** | Every decision, state change, and memory is transparent and inspectable in real-time. |

---

## 3. System Architecture


ScrAI is composed of two cooperative layers:

### 3.4 LLM Provider Configuration Template (`factory.py`)
The `factory.py` module serves as a canonical template for configuring and instantiating LLM providers. It centralizes environment-based provider selection (e.g., OpenAI-compatible, Gemini, OpenRouter) and parameterization (temperature, max tokens, etc.), ensuring that all LLM integrations are consistent and easily swappable. When LLM integration is required, this template will be extended to inject provider-specific credentials and runtime options, supporting both local and cloud-based models. All future LLM-related features should utilize this factory to ensure modularity and maintainability.

### 3.1 Backend Simulation Core (Python 3.11+)
Responsible for cognition, state management, persistence, and the canonical event flow.

### 3.2 Frontend Interactive Layer (Next.js + Vercel AI SDK)
An immersive analytical dashboard that visualizes the simulation in real time and allows user interventions or scenario creation.

### 3.3 Technology Stack
| Layer | Stack | Notes |
|--------|--------|-------|
| **Core Runtime** | Python 3.11+, FastAPI | Asynchronous backend with REST + WebSocket API. |
| **Cognitive Engine** | LangGraph + LangChain | Hierarchical reasoning graphs define agent “brains.” |
| **Event Bus** | Redis Streams (default) | Central nervous system ensuring consistency and decoupling. |
| **Structured Store** | PostgreSQL (SQLAlchemy ORM) | Canonical world state with transactional guarantees. |
| **Vector Memory Store** | ChromaDB / LanceDB (prototype) → pgvector (future) | Persistent semantic memory storage. |
| **Frontend** | Next.js + React + Vercel AI SDK + Tailwind CSS | Visualization, querying, and live streaming interface. |
| **Observability** | Prometheus + Grafana | Real-time metrics, event throughput, error tracking. |

---

## 4. Event-Driven Core

### 4.1. Event Bus: The System’s Heartbeat
All changes in the simulation pass through the Event Bus, ensuring deterministic, replayable, and auditable state transitions.

#### Implementation
- **Default:** Redis Streams (persistent, ordered, partitioned by entity).
- **Alternate:** Kafka or NATS JetStream for distributed scaling.

#### Event Schema (Pydantic-Enforced)
```json
{
  "event_id": "uuid-v4",
  "type": "ActionEvent | WorldStateCommittedEvent | ...",
  "origin": "agent:uuid",
  "entity_id": "agent:uuid",
  "sequence": 123,
  "timestamp": "ISO-8601",
  "payload": {...},
  "trace_id": "uuid-v4",
  "schema_version": "1.1"
}
```

#### Event Guarantees
- **Idempotency:** Each subscriber tracks `event_id` to prevent duplicate processing.
- **Ordering:** Guaranteed per-entity via sequence counters.
- **Atomicity:** Memory and UI logs trigger only after successful `WorldStateCommittedEvent`.
- **Error Recovery:** Retry/backoff with DLQ for permanent failures.
- **Observability:** Each event carries a trace ID for distributed tracing.

---

## 5. Canonical Event Flow

1. **Action Publication:**  
   An agent’s LangGraph “act” node emits an `ActionEvent`. Agents **never** write to databases directly.

2. **State Validation & Commitment:**  
   The `WorldStateSystem` consumes the event, validates it, and updates PostgreSQL inside a transaction.  
   - On success → emits `WorldStateCommittedEvent`.  
   - On failure → emits `WorldStateRejectedEvent`.

3. **Memory Encoding:**  
   The `MemorySystem` subscribes **only** to `WorldStateCommittedEvent`.  
   It converts events into natural-language narratives, embeds them, and stores them in the vector DB.

4. **Logging & UI:**  
   The `LoggingSystem` streams all event types to the dashboard via WebSockets for real-time observability.

5. **Optional Subsystems:**  
   Analytics and summarization systems can subscribe independently without disrupting existing flow.

---

## 6. Memory System

### 6.1. Tiered Memory Architecture
| Tier | Role | Persistence |
|------|------|-------------|
| **Short-Term Buffer** | High-resolution event cache (RAM). | Ephemeral |
| **Episodic Memory (Vector DB)** | Embeddings of natural-language memories with metadata. | Persistent |
| **Reflective Memory** | LLM-generated summaries for abstraction and compression. | Persistent |

### 6.2. Lifecycle
1. Raw events accumulate in the short-term buffer.
2. Background process translates them into structured sentences → vector embeddings.
3. `MemoryConsolidator` clusters similar memories → produces summarized reflective memories.
4. Archived data stored or pruned based on salience, recency, and relevance.

### 6.3. Retrieval & RAG
When agents reason:
- They query their vector memory filtered by metadata (time, agent, location, type).
- Relevant memories are injected into LangGraph nodes as contextual input.
- This creates continuity of personality, intent, and consequence.

---

## 7. Agent Cognition Engine (LangGraph)

### 7.1. Structure
Each agent’s “brain” is implemented as a **LangGraph** reasoning graph—a directed flow of cognitive nodes.

#### Core Nodes
- **Perception Node:** Parses incoming events.
- **Recall Node:** Queries vector memory.
- **Deliberation Node:** Uses LLM (via LangChain) to reason on perception + recall.
- **Action Node:** Chooses an action and emits an event.
- **Reflection Node:** Updates self-state and memory summarization.

### 7.2. Modularity
Each node is replaceable. Developers can plug in:
- Custom reasoning logic.
- Domain-specific prompt templates.
- External tool-calling nodes for sandboxed operations.

LangGraph ensures clear, modular, observable agent cognition flows that can be extended via custom graph modules.

---

## 8. Frontend Layer (Next.js + Vercel AI SDK)

### 8.1. Role
Acts as both **control console** and **window into cognition**.  
Powered by the **Vercel AI SDK**, it supports real-time LLM chat and streaming narrative interfaces.

### 8.2. Core Components
| Component | Function |
|------------|-----------|
| **World Viewer** | Map/grid-based visualization of agents and objects. |
| **Agent Inspector** | Queryable cognitive state (memory, goals, traits). |
| **Event Stream Log** | Real-time feed of all events from Redis Streams via WebSockets. |
| **Scenario Loader** | Load prefab worlds or define new ones via YAML. |
| **LLM Chat Console** | Direct conversation with agents using Vercel AI SDK + LangChain endpoints. |

### 8.3. Modularity
- Built using **Next.js server components**, allowing modular UI loading.
- The frontend queries all backends via REST, GraphQL, or WebSockets.
- Designed for easy extension—e.g., new panels for analytics or agent dialogue replay.

---

## 9. Operational Rigor & Testing

### 9.1. Testing Mandates
- **Integration Tests:** Spin up ephemeral PostgreSQL + Redis containers to validate end-to-end event flow.
- **Chaos Testing:** Random subscriber terminations test idempotency and event reprocessing.
- **Replay Validation:** All event logs must be replayable from any snapshot deterministically.

### 9.2. Observability & Monitoring
- **Metrics:** Event throughput, consumer lag, DB write latency (Prometheus).
- **Tracing:** Use `trace_id` for correlation (Grafana + OpenTelemetry).
- **DLQ Auditing:** All failed events logged for manual review.

---

## 10. Ethical Guardrails & Security

| Policy | Description |
|---------|--------------|
| **Sandboxed Execution** | Tool-calling restricted to isolated sandboxes. |
| **LLM Rate Limits** | Prevent token exhaustion and runaway simulations. |
| **Scenario Ethics Docs** | Every social/historical simulation must declare goals and boundaries. |
| **Data Privacy** | Even synthetic populations treated as sensitive for analysis. |

---

## 11. Development Roadmap

| Phase | Goal | Deliverables |
|--------|------|--------------|
| **Phase 1 – Core Event Loop** | Establish canonical Action → Commit flow. | Event Bus, FastAPI, one agent prototype. |
| **Phase 2 – Dashboard** | Build Next.js observer window. | World Viewer, Event Log, Agent Inspector. |
| **Phase 3 – Cognitive Depth** | Add full LangGraph brain with reflective memory. | MemoryConsolidator, RAG-based reasoning. |
| **Phase 4 – Scale & Analytics** | Distributed agents + narrative metrics. | Redis/Kafka scaling, social network analytics. |
| **Phase 5 – Multi-User Mode** | Enable shared simulation observation. | Auth layer, collaboration dashboard. |

---

## 12. Summary of Guarantees

| Domain | Guarantee |
|---------|------------|
| **Consistency** | All state changes flow through the Event Bus pipeline. |
| **Resilience** | Each subsystem is decoupled, idempotent, and retry-safe. |
| **Persistence** | Agent and world state are permanent and replayable. |
| **Transparency** | Every event and reasoning step observable via frontend. |
| **Extensibility** | Modular graph-based agent design and pluggable systems. |
| **Scalability** | Redis → Kafka migration path ensures high concurrency readiness. |

---

## 13. Closing Vision

ScrAI represents the convergence of **LLM cognition**, **modular simulation architecture**, and **emergent narrative design**.  
It transforms the relationship between creator and simulation—turning storytelling into systems thinking, and turning AI reasoning into observable art.  

With LangGraph providing structure, Redis ensuring heartbeat, PostgreSQL grounding persistence, and Vercel’s AI SDK connecting mind to interface, ScrAI is not a story engine. It’s a **thought engine**—a world that thinks back.

