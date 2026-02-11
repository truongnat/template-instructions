# Docker Deployment Guide for SDLC Kit

This guide explains how to run the Agentic SDLC Kit using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose 2.0+
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

### Production Deployment

Run the complete stack with all services:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop all services
docker-compose down
```

The application will be available at:
- Streamlit Dashboard: http://localhost:8501
- Neo4j Browser: http://localhost:7474 (username: neo4j, password: sdlc_password)

### Development Mode

Run in development mode with hot-reload:

```bash
# Start with development profile
docker-compose --profile dev up -d app-dev

# Access the development container
docker-compose exec app-dev /bin/bash

# Inside the container, run commands
asdlc --help
asdlc workflow cycle "Add feature"
```

### Monitoring Stack

Enable Prometheus and Grafana for monitoring:

```bash
# Start with monitoring profile
docker-compose --profile monitoring up -d

# Access monitoring services
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (username: admin, password: admin)
```

## Docker Images

### Production Image (Dockerfile)

Multi-stage build optimized for production:
- Based on Python 3.11-slim
- Minimal runtime dependencies
- Non-root user for security
- Health checks enabled
- Size: ~1.5GB

Build manually:
```bash
docker build -t sdlc-kit:latest .
```

Run standalone:
```bash
docker run -it --rm sdlc-kit:latest asdlc --help
```

### Development Image (Dockerfile.dev)

Development-optimized image with additional tools:
- Includes dev dependencies (pytest, black, mypy, etc.)
- Hot-reload support via volume mounts
- Debugging tools (vim, nano)
- Python debugger port exposed (5678)
- Size: ~2.5GB

Build manually:
```bash
docker build -f Dockerfile.dev -t sdlc-kit:dev .
```

Run standalone:
```bash
docker run -it --rm -v $(pwd):/app sdlc-kit:dev /bin/bash
```

## Services

### app (Production Application)

Main application service running in production mode.

**Environment Variables:**
- `ENVIRONMENT=production`
- `NEO4J_URI=bolt://neo4j:7687`
- `NEO4J_USER=neo4j`
- `NEO4J_PASSWORD=sdlc_password`

**Volumes:**
- `./logs:/app/logs` - Application logs
- `./data:/app/data` - Application data
- `./states:/app/states` - State files
- `./config:/app/config` - Configuration files

**Ports:**
- `8501` - Streamlit dashboard

### app-dev (Development Application)

Development service with hot-reload and debugging support.

**Additional Features:**
- Full source code mounted for hot-reload
- Interactive shell access
- Python debugger support

**Ports:**
- `8501` - Streamlit dashboard
- `5678` - Python debugger (debugpy)

### neo4j (Graph Database)

Neo4j graph database for knowledge management.

**Configuration:**
- Version: 5.15-community
- APOC plugin enabled
- Memory: 512MB initial, 2GB max heap

**Ports:**
- `7474` - HTTP interface
- `7687` - Bolt protocol

**Volumes:**
- `neo4j-data` - Database data
- `neo4j-logs` - Database logs
- `neo4j-import` - Import directory
- `neo4j-plugins` - Plugins directory

### prometheus (Monitoring - Optional)

Prometheus metrics collection and monitoring.

**Ports:**
- `9090` - Prometheus UI

**Profile:** `monitoring`

### grafana (Visualization - Optional)

Grafana dashboards for metrics visualization.

**Ports:**
- `3000` - Grafana UI

**Default Credentials:**
- Username: `admin`
- Password: `admin`

**Profile:** `monitoring`

## Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

### Execute Commands

```bash
# Run CLI command in production container
docker-compose exec app asdlc --help

# Run CLI command in development container
docker-compose exec app-dev asdlc workflow cycle "Task description"

# Access shell
docker-compose exec app /bin/bash
docker-compose exec app-dev /bin/bash
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart app

# Rebuild and restart
docker-compose up -d --build app
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers, volumes, and networks
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Complete cleanup
docker-compose down -v --rmi all --remove-orphans
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application
ENVIRONMENT=production
PYTHONUNBUFFERED=1

# Neo4j
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=sdlc_password

# OpenAI (if needed)
OPENAI_API_KEY=your_api_key_here

# Anthropic (if needed)
ANTHROPIC_API_KEY=your_api_key_here
```

Docker Compose will automatically load this file.

### Custom Configuration

Mount custom configuration files:

```yaml
services:
  app:
    volumes:
      - ./my-config.yaml:/app/config/custom.yaml
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose logs app
```

Verify dependencies:
```bash
docker-compose ps
```

### Database Connection Issues

Ensure Neo4j is healthy:
```bash
docker-compose ps neo4j
```

Test connection:
```bash
docker-compose exec app python -c "from neo4j import GraphDatabase; print('OK')"
```

### Permission Issues

If you encounter permission errors with volumes:

```bash
# Fix ownership
sudo chown -R $(id -u):$(id -g) logs data states config
```

### Out of Memory

Increase Docker memory limit in Docker Desktop settings or adjust Neo4j memory:

```yaml
services:
  neo4j:
    environment:
      - NEO4J_dbms_memory_heap_max__size=1G  # Reduce from 2G
```

### Port Conflicts

If ports are already in use, modify the port mappings:

```yaml
services:
  app:
    ports:
      - "8502:8501"  # Use different host port
```

## Performance Optimization

### Production Optimizations

1. **Use specific Python version:**
   ```dockerfile
   FROM python:3.11.7-slim
   ```

2. **Enable BuildKit:**
   ```bash
   DOCKER_BUILDKIT=1 docker-compose build
   ```

3. **Use layer caching:**
   - Requirements are copied before code
   - Changes to code don't invalidate dependency layers

4. **Multi-stage builds:**
   - Builder stage compiles dependencies
   - Runtime stage only includes necessary files

### Resource Limits

Add resource limits to services:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Security Considerations

1. **Non-root user:** Both images run as non-root user `sdlc` (UID 1000)
2. **Secrets management:** Use Docker secrets or environment variables
3. **Network isolation:** Services communicate via internal network
4. **Health checks:** All services have health checks configured
5. **Minimal base images:** Using slim Python images reduces attack surface

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build Docker image
  run: docker build -t sdlc-kit:${{ github.sha }} .

- name: Run tests in container
  run: |
    docker run --rm sdlc-kit:${{ github.sha }} pytest tests/
```

### GitLab CI

```yaml
docker-build:
  stage: build
  script:
    - docker build -t sdlc-kit:$CI_COMMIT_SHA .
    - docker run --rm sdlc-kit:$CI_COMMIT_SHA pytest tests/
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Neo4j Docker Documentation](https://neo4j.com/docs/operations-manual/current/docker/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
