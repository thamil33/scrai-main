# ScrAI

ScrAI is a simulation environment for proactive, intelligent agents featuring memory, cognition, and a dynamic world.


## Docker Setup (PostgreSQL & Redis)

1. **Start PostgreSQL and Redis with Docker Compose:**
    From the root directory (`scrai/`), run:
    ```bash
    docker compose up -d
    ```

    This will start PostgreSQL (with the pgvector extension enabled automatically) and Redis using the configuration in `docker-compose.yml`.

2. **pgvector Extension:**
    The container is configured to run the SQL script in `postgres-init/01_enable_pgvector.sql` on first startup, enabling the `pgvector` extension for semantic search support.

3. **Database Connection Details:**
    - Host: `localhost`
    - Port: `5432`
    - User: `user`
    - Password: `admin`
    - Database: `scrai_db`

---

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/thamil33/scrai.git
    cd scrai
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv .venv

    # Activate it (Windows PowerShell)
    .venv\Scripts\activate

    # Or on macOS/Linux
    # source .venv/bin/activate
    ```

3.  **Install dependencies using uv:**

    ```bash
    cd backend
    

    uv pip install --link-mode=copy -r requirements.txt

    ```
npm install -g firebase-tools



## Running the Simulation

1.  **Start the FastAPI server:**
    ```bash
    uvicorn backend.main:app --reload
    ```

2.  **Access the Admin UI:**
    Open your web browser and navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

    The UI provides a real-time visualization of agent positions and their latest memories.

## Using the API

You can control the simulation via the following API endpoints:

-   `POST /api/simulation/pause`: Pauses the simulation.
-   `POST /api/simulation/resume`: Resumes the simulation.
-   `POST /api/simulation/tick`: Manually requests a simulation tick for debugging.
