### Project Overview — ScrAI Backend

This backend powers ScrAI, an AI-driven, multi-agent simulation environment. It simulates agents with memory and decision-making abilities, orchestrated by LLMs and an event-based core.

---

### Core Architecture & Design

- Event-driven architecture decouples components and enables scalable interactions.
- Central simulation loop:
    - Implemented by `Simulation` (`main.py`, `scrai_core/core/simulation.py`).
    - Runs as a background task and ticks every 2 seconds (configurable).
    - API endpoints allow pausing, resuming, single-step ticking, and resetting.
- Event bus:
    - `EventBus` (`scrai_core/events/bus.py`) uses Redis to publish/subscribe events between systems.
- Background systems:
    - World State System (`scrai_core/world/systems.py`): subscribes to action events, updates `WorldObject`s in the DB.
    - Memory Consolidator (`scrai_core/agents/memory_consolidator.py`): converts agent experiences into persistent `EpisodicMemory` entries.

---

### Technology Stack

- Web: FastAPI + Uvicorn (async, high-performance).
- Database: PostgreSQL with SQLAlchemy ORM.
- Vector storage & embeddings:
    - `pgvector`, `sentence-transformers`, and `torch` for embedding and similarity search (RAG-style memory).
- AI frameworks:
    - LangChain and LangGraph for agent cognition and stateful reasoning.
    - Integrations for multiple LLM providers (e.g., OpenAI, Google).
- Monitoring: Prometheus metrics exposed via `/metrics` (instrumented counters like `events_processed_total`).
- Validation: Pydantic models for API and event schema validation.
- Requirements: Python 3.12+.

---

### Key Concepts & Data Models

- Agent (`scrai_core/agents/models.py`): primary actors, with attributes like name and location (lat/long).
- Episodic Memory (`scrai_core/agents/models.py`): timestamped records of experiences for long-term recall/learning.
- World Object (`scrai_core/world/models.py`): environment entities agents can perceive and manipulate.
- Event schemas (`scrai_core/events/`): standardized messages passed through the event bus.

---

### API Surface (`main.py`)

- Dashboard: `GET /api/dashboard` — current state of agents and recent memories (for front-end).
- Simulation control: endpoints under `/api/simulation/` to `pause`, `resume`, `tick`, and `reset`.
- Metrics: `/metrics` exposed for Prometheus scraping.

---

### Directory Outline (`scrai_core/`)

- `agents/`: models, cognition, memory systems, schemas.
- `core/`: DB init, simulation loop, persistence, logging.
- `events/`: event bus and event schemas.
- `world/`: world models and systems that process events.
- `scenarios/`: loaders for initial simulation setups.
- `tests/`: test suite covering core behavior.

---

### Summary & Suggested Next Steps

- The backend is modular, asynchronous, and production-ready in design.
- Next steps for development:
    - Add configuration-driven tick interval and graceful shutdown handling.
    - Harden event schemas and retry/poison-queue strategies for failed events.
    - Expand observability (traces, more metrics, structured logs).
    - Add integration tests for the simulation loop + event processing pipeline.
    - Provide a minimal frontend or CLI to visualize and control simulation state.

This cleaned summary preserves the original analysis while removing interim artifacts and focusing on actionable structure and next steps.
