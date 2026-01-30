# Docker Setup for Agentic SDLC

This guide explains how to run the full Agentic SDLC stack using Docker.

## Components

The Docker setup orchestrates the following services:

1.  **agentic-sdlc-core (`app`)**: The main Python application, CLI, and workflows.
2.  **agentic-sdlc-memgraph (`memgraph`)**: The Knowledge Graph database (Memgraph Platform).
3.  **agentic-sdlc-ollama (`ollama`)**: Local LLM server.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed and running.
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop).

## Quick Start

Run the helper script:

```bash
./run_docker.sh
```

Or manually:

```bash
docker-compose up -d --build
```

## Accessing Services

- **Memgraph Lab**: Open [http://localhost:3000](http://localhost:3000)
    - **Connect via Bolt**: `bolt://memgraph:7687` (inside docker) or `bolt://localhost:7687` (local).
    - **Username/Password**: `memgraph` / `memgraph` (defined in `docker-compose.yaml`).
- **Core App Shell**:
    ```bash
    docker-compose exec app bash
    ```
    From here you can run CLI commands:
    ```bash
    agentic-sdlc brain status
    python tools/research/research_agent.py --task "Test"
    ```
- **Streamlit Dashboard** (if running): [http://localhost:8501](http://localhost:8501)

## Development

The `docker-compose.yaml` mounts the current directory to `/app` in the container. Changes you make locally will be reflected inside the container immediately (for Python scripts).

## Troubleshooting

- **Memgraph Connection**: Ensure the `MEMGRAPH_URI` in `.env` (if running locally) or `docker-compose.yaml` (if running in docker) is correct.
    - Inside Docker: `bolt://memgraph:7687`
    - Localhost: `bolt://localhost:7687`
- **Ollama Models**: You may need to pull models first.
    ```bash
    docker-compose exec ollama ollama pull llama3
    ```
