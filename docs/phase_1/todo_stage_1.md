Of course. Here is a comprehensive and concise to-do list for Stage I, formatted with Markdown checkboxes. This list incorporates the refined action plan and is designed to be a direct, actionable guide for development.

---

### **ScrAI Development: Stage I To-Do List**

#### **🎯 Stage I Goal: Establish a fully-functional, end-to-end, agent-initiated event pipeline with foundational observability and a robust testing framework.**

---

### **Milestone 1: Foundational Setup (The Bedrock)**
*Goal: Prepare the project environment, core infrastructure, and central data contracts.*

- [x] **Project Scaffolding:**
    - [x] Initialize a monorepo with `backend/` and `frontend/` directories.
    - [x] Set up the backend Python project with Poetry/PDM (`pyproject.toml`).
    - [x] Create the Domain-Driven directory structure (`scrai_core/`, `events/`, `world/`, `agents/`, `core/`).
- [x] **Infrastructure (`docker-compose.yml`):**
    - [x] Define a `postgres` service with a persistent data volume. Document connection info in `.env` as `DATABASE_URL`.
    - [x] Define a `redis` service with a persistent data volume.
- [x] **Core Data Contracts (`events/schemas.py`):**
    - [x] Create Pydantic model for `ActionEvent`.
    - [x] Create Pydantic model for `WorldStateCommittedEvent`.
    - [x] **Crucial:** Ensure all event schemas include `event_id`, `sequence`, `entity_id`, and `schema_version`.
- [x] **Initial World Model (`world/models.py`):**
    - [x] Create a minimal SQLAlchemy `Agent` model (`id`, `name`, `position`).

---

### **Milestone 2: The World's Heartbeat (Event Consumer Pipeline)**
*Goal: Prove the system can reliably and transactionally process events and commit state changes.*

- [x] **Database Connection (`core/persistence.py`):**
    - [x] Implement SQLAlchemy setup and session management for PostgreSQL.
    - [x] Use `DATABASE_URL` from `.env` for all connections (e.g. `postgresql://postgres:admin@localhost:5433/scrai_db`).
- [x] **Event Bus Connection (`events/bus.py`):**
    - [x] Implement a Redis Streams client wrapper for publishing and subscribing.
- [x] **World State Subscriber (`world/systems.py`):**
    - [x] Create the `WorldStateSystem` subscriber.
    - [x] Implement logic to consume `ActionEvent` from Redis.
    - [x] Implement transactional database update logic using SQLAlchemy.
    - [x] Implement logic to publish `WorldStateCommittedEvent` back to Redis on success.
- [x] **Memory System Stub (`agents/memory.py`):**
    - [x] Create a placeholder `MemorySystem` subscriber.
    - [x] Implement logic to consume **only** `WorldStateCommittedEvent`.
    - [x] For now, simply log the received event to the console to confirm delivery.
- [x] **Integration Test (`tests/test_heartbeat.py`):**
    - [x] Write a test that programmatically publishes an `ActionEvent`.
    - [x] Assert that the agent's position is updated correctly in PostgreSQL (using `.env` connection info).
    - [x] Assert that a `WorldStateCommittedEvent` is published to Redis.
    - [x] **Crucial:** Add a test case to verify idempotency (publishing the same event twice results in only one state change).

---

### **Milestone 3: The First Spark (Agent Producer Pipeline)**
*Goal: Prove an agent can successfully initiate an action and trigger the full event loop.*

- [x] **Scenario Loader Stub (`scenarios/loader.py`):**
    - [x] Implement a basic function to create and save a new agent to PostgreSQL for testing (using `.env` connection info).
- [x] **Proto-Agent Stub (`agents/cognition.py`):**
    - [x] Create a simple `ProtoAgentPublisher` class (no LangGraph needed yet).
    - [x] Implement a method that publishes a hardcoded `ActionEvent` to the Event Bus.
- [x] **Simulation Loop (`core/simulation.py`):**
    - [x] Create the main `Simulation` class.
    - [x] Implement a `tick()` method that loads all agents and calls their `publish_action()` method once.
- [x] **End-to-End Test (`tests/test_full_loop.py`):**
    - [x] Write a test that uses the `Scenario Loader` to create an agent.
    - [x] Runs a single `simulation.tick()`.
    - [x] Asserts that the agent's state changed in the database, proving the entire loop from producer to consumer is functional (using `.env` connection info).

---

### **Milestone 4: Design & Observability (Future-Proofing)**
*Goal: Establish good operational practices and design patterns before adding complexity.*

- [x] **Memory Consolidator Design (`agents/memory_consolidator_design.md`):**
    - [x] Create a Markdown document outlining the proposed trigger logic (e.g., event count, time-based) for memory summarization.
- [x] **Basic Observability:**
    - [x] Configure the FastAPI app with a `/metrics` endpoint (using a Prometheus client).
    - [x] Instrument the `WorldStateSystem` to increment a counter for `events_processed_total`.
