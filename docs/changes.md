# Change Log

## [0.3.0] - 2025-10-25

### Added
- **Simulation Reset Endpoint:** Implemented an `/api/simulation/reset` endpoint to clear all database tables (`agents`, `episodic_memories`, `world_objects`) and re-initialize the simulation to a clean state.
- **Frontend Reset Button:** Added a "Reset Simulation" button to the admin dashboard for easy access to the reset functionality.

### Fixed
- **API Serialization:** Resolved a `500 Internal Server Error` on the `/api/dashboard` endpoint by creating Pydantic schemas for `Agent` and `EpisodicMemory` models, ensuring proper JSON serialization of SQLAlchemy objects.
- **Event Bus Consumption:** Fixed a critical `AttributeError` in the `MemoryConsolidator` by refactoring its `run` method to be asynchronous and correctly use the `EventBus.subscribe` method to consume events from the `world_state_committed_events` stream.
- **Database Session Handling:** Corrected an `AttributeError: 'generator' object has no attribute 'query'` in the `WorldStateSystem` by properly consuming the session generator using `next()`, ensuring a valid database session is used.
- **Agent Behavior Loop:** Addressed the agent's repetitive behavior by enhancing the reasoning prompt in `CognitiveAgent` to encourage exploration and prevent it from getting stuck in a logic loop.
- **Code Cleanup:** Removed unnecessary and confusing commented-out code related to old API key handling.

## [0.2.0] - 2025-10-25

### Added
- **Cognitive Agent:** Replaced the simple `ProtoAgentPublisher` with a `CognitiveAgent` that uses LangGraph for a full "perceive-reason-act" cognitive loop.
- **Dynamic World:** Introduced `WorldObject` models and `interact_with_object` actions to create a richer, more interactive simulation environment.
- **LLM Provider Factory:** Implemented a factory pattern to make the language model provider configurable via a `.env` file, supporting multiple backends like local proxies and cloud services.
- **Simulation Controls:** Added and fully implemented API endpoints (`/pause`, `/resume`, `/tick`) to allow for real-time control over the simulation's execution.
- **Observability:** Integrated `structlog` for structured, JSON-formatted logging and created a simple HTML/JS frontend to visualize agent state and memories.
- **Project Documentation:** Added a root `README.md` with comprehensive installation and usage instructions.

### Fixed
- **Asynchronous Logic:** Refactored the entire agent cognitive loop to be fully asynchronous, resolving critical bugs where events were not being published correctly.
- **Test Suite Stability:** Overhauled the test suite to fix a wide range of issues, including:
    - Resolved `TypeError`s by replacing incorrect context manager usage for database sessions.
    - Eliminated `AuthenticationError` by integrating the LLM provider factory and removing direct API calls in tests.
    - Fixed `UndefinedTable` and `DetachedInstanceError` by implementing a transaction-based database fixture in `conftest.py` for complete test isolation.
    - Solved `NoResultFound` errors by patching `get_session` in tests to ensure a consistent session between the test setup and the application code.
    - Updated all relevant tests to correctly use `async` and `await` with `AsyncMock`.

## [0.1.0] - 2025-10-24

### Added
- **End-to-End Event Pipeline:** Implemented the full event-driven pipeline, from agent action to world state commitment.
- **Testing Framework:** Established a robust testing framework with passing tests for the heartbeat and full simulation loop.
- **Docker Infrastructure:** Added a `docker-compose.yml` file to manage PostgreSQL and Redis services.
- **Domain-Driven Structure:** Refactored the project to align with the domain-driven architecture, including relocating the `Agent` model.
- **Memory Consolidator Design:** Created an initial design document for the memory consolidator system.

### Fixed
- **Database Initialization:** Resolved `UndefinedTable` errors by implementing a test fixture that correctly creates and tears down the database schema.
- **JSON Serialization:** Fixed `TypeError`s related to UUID serialization by using Pydantic's `model_dump(mode='json')` method.
- **Dependency Injection:** Refactored the `WorldStateSystem` and `Simulation` classes to accept a database session, ensuring transactional integrity during tests.
- **Import Standardization:** Corrected import paths across the `scrai_core` package to resolve module loading conflicts and ensure consistency.
