# scrAI - A Narrative Laboratory (Cloud IDE Guide)

This document provides instructions for running the scrAI project within the pre-configured cloud development environment. For instructions on setting up the project on a local machine, please see `readme.md`.

## Getting Started in the Cloud IDE

This cloud environment is pre-configured to run the entire scrAI simulation. The necessary services (PostgreSQL, Redis, Docker) and packages (Node.js) are automatically managed.

### 1. Start the Backend Services

The backend, database, and Redis are all managed by Docker Compose. To start everything, run the following command from the project's root directory:

```bash
docker-compose up --build
```
This will build the containers and start the FastAPI server. The backend will be available at `http://127.0.0.1:8000`.

### 2. Run the Frontend

In a **separate terminal**, navigate to the frontend directory to install dependencies and start the development server:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

### 3. Access the Admin UI

Once the frontend server is running, it will provide a local URL (usually `http://localhost:5173`). Open this URL in your web browser.

The UI provides a real-time visualization of agent positions on a map and their latest memories.

---

## Interacting with the Simulation

You can control the simulation and create agents via the following API endpoints. A Postman collection or `curl` can be used for this.

*   `POST /api/agents` - Create a new agent.
    *   **Body:** `{ "name": "string", "latitude": float, "longitude": float }`
*   `GET /api/dashboard` - Retrieve the current state of all agents and recent memories.
*   `POST /api/simulation/pause` - Pauses the simulation loop.
*   `POST /api/simulation/resume` - Resumes the simulation loop.
*   `POST /api/simulation/tick` - Manually advances the simulation by one step.
*   `POST /api/simulation/reset` - Resets the simulation by clearing all agents and memories.
