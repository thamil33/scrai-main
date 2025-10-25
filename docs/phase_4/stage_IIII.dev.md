# ScrAI Development Plan - Phase 4: Scale & Analytics

## 1. Overview

This phase marks the transition from a single-process simulation to a scalable, distributed system. The primary goals are to decouple agent cognition from the main application server to support a large number of concurrent agents and to introduce a narrative analytics layer to derive high-level insights from emergent behaviors.

---

## 2. Part 1: Distributed Agent Architecture

**Objective:** Decouple agent cognitive cycles from the main API server, enabling the simulation to scale horizontally.

### 2.1. Containerize the Agent Worker
- **Task:** Create a standalone Python script (`run_agent_worker.py`) responsible for initializing and running the `tick()` loop of a single `CognitiveAgent`. This script will accept an `agent_id` as a command-line argument.
- **Task:** Generalize the project's `Dockerfile` to support multiple entry points. This will allow us to spin up containers for the FastAPI web server, the agent worker, and other background services independently.
- **Task:** Update the `docker-compose.yml` to define a new `agent-worker` service. This will allow us to easily launch and manage multiple agent containers.

### 2.2. Implement a Dynamic Agent Spawner
- **Task:** Create a new "Agent Spawner" service. This service will be responsible for reading a scenario configuration file (e.g., `scenarios/default.yml`) and dynamically launching a dedicated worker process or container for each agent defined in the scenario.
- **Rationale:** This change removes the hardcoded agent initialization from the main application's startup sequence, making the simulation fully modular and configurable without requiring code changes.

---

## 3. Part 2: Narrative Analytics System

**Objective:** Build an independent subsystem that analyzes the event stream to produce high-level insights about the narrative and agent relationships.

### 3.1. Create the Analytics Subsystem
- **Task:** Develop a new `AnalyticsSystem` class that subscribes to the `world_state_committed_events` stream, similar to the `MemoryConsolidator`. This system will run as a separate, long-running background process.
- **Task:** Implement logic within this system to process events and identify key patterns, such as agent proximity, interactions with specific world objects, or significant movement trends.


### 3.3. Build Analytics API and Frontend
- **Task:** Add a new `/api/analytics` endpoint to the FastAPI application. This endpoint will serve the processed narrative data, such as the social graph, in a structured format.
- **Task:** Enhance the frontend with a new visualization panel dedicated to analytics. A simple graph visualization (using a library like D3.js, Vis.js, or Chart.js) will be implemented to display the emergent social network between agents in real-time.

---

## 4. Success Criteria

Phase 4 will be considered complete when:
- Agents run in separate, containerized processes, managed by Docker Compose.
- The simulation can be configured and launched from a scenario file without code modifications.
- The `AnalyticsSystem` correctly processes events and populates the social graph tables.
- The frontend dashboard features a new panel that successfully visualizes the emergent relationships between agents.


# After Action - 
- The project should then undergo general maitenance, code cleanup and light optimization. 

- Then, all tests should be updated and overhauled.