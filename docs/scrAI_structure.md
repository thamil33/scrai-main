Utilizes a **monorepo** structure, as the backend and frontend are tightly coupled components of a single product. This simplifies dependency management and cross-component type sharing.

---

###  The Domain-Driven Monorepo (Feature-First)**

This is the modern, recommended approach for a project like ScrAI. It organizes code around the core *concepts* or *domains* of the application (e.g., Agents, World, Events). When you work on a feature, most of the code you need to touch is co-located in one place.

**Philosophy:** "Group code that changes together." If you're improving agent memory, the agent's cognitive graph, data model, and API endpoint are all found within the `agents` domain.

**Pros:**
*   **High Cohesion:** Features are self-contained, making the codebase easier to understand and navigate.
*   **Faster Development:** Less jumping between disparate folders to implement a single feature.
*   **Clear Ownership:** Easier to assign ownership of a specific domain (e.g., "The Agent Team").

**Cons:**
*   **Potential for Circular Dependencies:** Requires discipline to ensure domains don't become improperly coupled (the Event Bus helps mitigate this).

---

#### **Organization Chart (Domain-Driven)**

```
/scrai/
├── .gitignore
├── docker-compose.yml       # For PostgreSQL, Redis, etc.
├── README.md
│
├── backend/                 # Python Backend Root
│   ├── pyproject.toml       # Project metadata and dependencies (using Poetry or PDM)
│   ├── main.py              # FastAPI application entrypoint
│   │
│   └── scrai_core/          # The main Python package
│       ├── __init__.py
│       │
│       ├── api/             # API layer: Defines endpoints and schemas
│       │   ├── __init__.py
│       │   ├── dependencies.py # Shared dependencies (e.g., get_db_session)
│       │   ├── routers/
│       │   │   ├── agents.py     # Endpoints for /agents/...
│       │   │   └── simulations.py# Endpoints for /simulations/...
│       │   └── websockets.py     # WebSocket manager for UI streaming
│       │
│       ├── agents/          # --- AGENT DOMAIN ---
│       │   ├── __init__.py
│       │   ├── cognition.py    # LangGraph cognitive architecture definition
│       │   ├── memory.py       # Tiered memory system logic (RAG, consolidation)
│       │   ├── models.py       # SQLAlchemy ORM model for Agent
│       │   └── schemas.py      # Pydantic schemas for Agent data
│       │
│       ├── world/           # --- WORLD DOMAIN ---
│       │   ├── __init__.py
│       │   ├── models.py       # SQLAlchemy models for WorldObject, etc.
│       │   ├── schemas.py      # Pydantic schemas for World data
│       │   └── systems.py      # Game logic systems (e.g., MovementSystem, PhysicsSystem)
│       │
│       ├── events/          # --- EVENTS DOMAIN (Central Truth) ---
│       │   ├── __init__.py
│       │   ├── bus.py          # Interface for the Event Bus (e.g., RedisStreamsBus)
│       │   ├── schemas.py      # Pydantic models for ALL event types
│       │   └── subscribers.py  # Defines the core system subscribers (WorldState, Memory)
│       │
│       ├── scenarios/      # --- SCENARIO DOMAIN ---
│       │   ├── __init__.py
│       │   ├── loader.py       # Logic to parse YAML prefabs
│       │   └── schemas.py      # Pydantic models for scenario file structure
│       │
│       ├── core/            # Low-level, cross-domain logic
│       │   ├── __init__.py
│       │   ├── simulation.py   # The main simulation loop runner
│       │   └── persistence.py  # Database session setup (SQLAlchemy, VectorDB client)
│
└── frontend/                # Next.js Frontend Root
    ├── package.json
    ├── next.config.js
    ├── tsconfig.json
    │
    ├── public/              # Static assets (images, fonts)
    └── src/
        ├── app/             # Next.js App Router
        │   ├── layout.tsx     # Root layout
        │   ├── page.tsx       # Landing/Home page
        │   └── (dashboard)/   # Route group for the main simulation UI
        │       ├── layout.tsx   # Dashboard shell (sidebar, header)
        │       ├── page.tsx     # Main dashboard overview
        │       └── agents/
        │           └── [agentId]/
        │               ├── page.tsx  # Agent Inspector page
        │               └── components/
        │                   └── MemoryQuery.tsx # Component specific to this page
        │
        ├── components/      # Reusable UI components
        │   ├── dashboard/     # High-level dashboard components
        │   │   ├── AgentInspector.tsx
        │   │   ├── EventLog.tsx
        │   │   └── WorldViewer.tsx
        │   └── ui/            # Generic, headless components (Button, Card, Dialog)
        │
        ├── lib/             # Core client-side logic
        │   ├── api.ts         # Type-safe wrappers for backend REST API calls
        │   ├── socket.ts      # WebSocket connection and event handling
        │   └── constants.ts   # Shared constants
        │
        ├── hooks/           # Custom React hooks
        │   └── useSimulationState.ts # Hook to manage and subscribe to simulation data
        │
        └── store/           # Client-side state management (Zustand, Jotai)
            └── simulationStore.ts
```

