Here is a comprehensive list of the different technology stacks and their exact library IDs, formatted as instructions for an agent with `context7 mcp` access.

---

### **Context7 MCP Instruction Set: ScrAI Project Dependencies**

**Objective:** To provide a canonical list of all required software packages, libraries, and tools for the ScrAI project. Use these exact IDs for installation via their respective package managers (PyPI for Python, npm for Node.js).

---

### **1. Backend Technology Stack (Python via PyPI)**

*   **Instruction:** The following libraries are to be managed by Poetry or PDM and listed in the `pyproject.toml` file.

| Technology | Canonical Library ID | Purpose in ScrAI |
| :--- | :--- | :--- |
| **Cognitive Engine** | | |
| LangChain | `langchain` | Core framework for orchestrating LLM interactions, prompts, and tools. |
| LangGraph | `langgraph` | Defines the cyclical, stateful reasoning graphs for agent cognition. |
| **Web Framework & API**| | |
| FastAPI | `fastapi` | High-performance asynchronous web framework for the REST and WebSocket API. |
| Uvicorn | `uvicorn[standard]` | ASGI server required to run the FastAPI application. |
| **Database & Persistence**| | |
| PostgreSQL ORM | `sqlalchemy` | The core Object-Relational Mapper for interacting with the world state. |
| PostgreSQL Driver | `psycopg2-binary` | The adapter that allows SQLAlchemy to communicate with PostgreSQL. |
| Event Bus Client | `redis` | The client library for connecting to Redis Streams, the event bus backbone. |
| Vector DB Client (Chroma)| `chromadb` | Client for the vector store used for agent episodic memory. |
| Vector DB Client (Lance)| `lancedb` | Alternative client for the vector store. |
| **Data Validation** | | |
| Pydantic | `pydantic` | Enforces the strict data schemas for all events and API models. |
| **LLM Provider SDKs** | | |
| OpenAI Integration | `langchain-openai` | LangChain-specific package for integrating with OpenAI models (GPT-4, etc.). |
| Google Vertex AI | `langchain-google-vertexai` | LangChain package for Google models (Gemini). |
| Anthropic Integration| `langchain-anthropic` | LangChain package for Anthropic models (Claude). |
| **Observability** | | |
| Prometheus Client | `prometheus-client` | Exposes application metrics (e.g., event counts) for monitoring. |

---

### **2. Frontend Technology Stack (JavaScript/TypeScript via npm)**

*   **Instruction:** The following libraries are to be managed by npm or yarn and listed in the `package.json` file.

| Technology | Canonical Library ID | Purpose in ScrAI |
| :--- | :--- | :--- |
| **Core Framework** | | |
| Next.js | `next` | The React framework for building the frontend user interface. |
| React | `react` | The core UI library for building components. |
| React DOM | `react-dom` | Connects React to the browser's DOM. |
| **AI/LLM Integration** | | |
| Vercel AI SDK | `ai` | Powers streaming UI components, especially for the Event Log and Chat Console. |
| **Styling** | | |
| Tailwind CSS | `tailwindcss` | A utility-first CSS framework for rapid UI development. |
| PostCSS | `postcss` | A tool for transforming CSS with plugins (required by Tailwind). |
| Autoprefixer | `autoprefixer` | A PostCSS plugin to parse CSS and add vendor prefixes. |
| **State Management** | | |
| Zustand | `zustand` | A lightweight, minimalist state management library for React. |
| **Language & Tooling** | | |
| TypeScript | `typescript` | The language for building a type-safe frontend. |
| React Types | `@types/react` | TypeScript type definitions for React. |

---

### **3. Infrastructure & Runtimes (System-Level Tools)**

*   **Instruction:** These tools are prerequisites for the development environment and are not managed by language-specific package managers.

| Technology | Canonical Name | Purpose in ScrAI |
| :--- | :--- | :--- |
| **Containerization** | `Docker` | The core containerization engine. |
| Container Orchestration | `Docker Compose` | Tool for defining and running the multi-container application (PostgreSQL, Redis). |
| **Language Runtimes** | `Python 3.11+` | The required version for the backend runtime. |
| | `Node.js 18+` | The required version for the frontend runtime and build process. |