# Triển Khai (Deployment)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp hướng dẫn chi tiết về cách deploy Agentic SDLC vào các môi trường khác nhau, bao gồm local development, Docker containers, và Kubernetes clusters.

## Mục Tiêu Học Tập

Sau khi đọc tài liệu này, bạn sẽ có thể:
- Deploy hệ thống locally cho development
- Containerize application với Docker
- Deploy lên Kubernetes cluster
- Setup monitoring và logging cho production
- Implement CI/CD pipelines

## Local Deployment

### 1. Development Setup

Setup môi trường development local:

```bash
# Clone repository
git clone https://github.com/your-org/agentic-sdlc.git
cd agentic-sdlc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Setup environment variables
cp .env.template .env
# Edit .env với your API keys

# Initialize database (if needed)
python scripts/init_db.py

# Run tests
pytest

# Start development server
python -m agentic_sdlc.cli run --dev
```text

### 2. Configuration Management

Manage configuration cho different environments:

```python
# config/development.yaml
environment: development
debug: true

model_clients:
  openai:
    provider: openai
    model_name: gpt-3.5-turbo
    api_key: ${OPENAI_API_KEY}
    timeout: 30

logging:
  level: DEBUG
  format: detailed
  output: console

database:
  url: sqlite:///dev.db

cache:
  enabled: true
  backend: memory
  size_mb: 512
```text

```python
# config/production.yaml
environment: production
debug: false

model_clients:
  openai:
    provider: openai
    model_name: gpt-4
    api_key: ${OPENAI_API_KEY}
    timeout: 60
    max_retries: 3

logging:
  level: INFO
  format: json
  output: file
  file_path: /var/log/agentic-sdlc/app.log

database:
  url: postgresql://user:pass@db-host:5432/agentic_sdlc
  pool_size: 20

cache:
  enabled: true
  backend: redis
  redis_url: redis://cache-host:6379
  size_mb: 2048
```text

```python
# Load configuration based on environment
from agentic_sdlc.core.config import load_config
import os

env = os.getenv("ENVIRONMENT", "development")
config = load_config(f"config/{env}.yaml")
```text

### 3. Running Locally

Run application locally:

```python
# run_local.py
from agentic_sdlc import initialize_system
from agentic_sdlc.core.config import load_config
from agentic_sdlc.orchestration.agent import create_agent, AgentType
from agentic_sdlc.orchestration.workflow import WorkflowBuilder

def main():
    """Run application locally."""
    # Load config
    config = load_config("config/development.yaml")
    
    # Initialize system
    initialize_system(config)
    
    # Create agents
    pm_agent = create_agent("pm", AgentType.PROJECT_MANAGER)
    dev_agent = create_agent("dev", AgentType.DEVELOPER)
    
    # Build workflow
    builder = WorkflowBuilder("local-workflow")
    builder.add_step(...)
    workflow = builder.build()
    
    # Execute
    result = workflow.execute()
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
```text

## Docker Deployment

### 1. Dockerfile

Create Dockerfile cho application:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install application
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "agentic_sdlc.cli", "run", "--host", "0.0.0.0", "--port", "8000"]
```text

### 2. Docker Compose

Setup multi-container application với Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/agentic_sdlc
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    networks:
      - agentic-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=agentic_sdlc
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - agentic-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - agentic-network

  worker:
    build: .
    command: python -m agentic_sdlc.worker
    environment:
      - ENVIRONMENT=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/agentic_sdlc
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - agentic-network
    deploy:
      replicas: 3

volumes:
  postgres-data:
  redis-data:

networks:
  agentic-network:
    driver: bridge
```text

### 3. Building và Running

Build và run Docker containers:

```bash
# Build image
docker build -t agentic-sdlc:latest .

# Run single container
docker run -d \
  --name agentic-sdlc \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  agentic-sdlc:latest

# Run với Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Scale workers
docker-compose up -d --scale worker=5

# Stop containers
docker-compose down
```text

## Kubernetes Deployment

### 1. Kubernetes Manifests

Create Kubernetes deployment manifests:

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: agentic-sdlc
```text

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agentic-config
  namespace: agentic-sdlc
data:
  config.yaml: |
    environment: production
    debug: false
    logging:
      level: INFO
      format: json
```text

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: agentic-secrets
  namespace: agentic-sdlc
type: Opaque
stringData:
  openai-api-key: your-openai-key
  database-url: postgresql://user:pass@postgres:5432/agentic_sdlc
  redis-url: redis://redis:6379
```text

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentic-sdlc
  namespace: agentic-sdlc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentic-sdlc
  template:
    metadata:
      labels:
        app: agentic-sdlc
    spec:
      containers:
      - name: app
        image: agentic-sdlc:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agentic-secrets
              key: openai-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agentic-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: agentic-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: config
        configMap:
          name: agentic-config
      - name: logs
        emptyDir: {}
```text

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: agentic-sdlc
  namespace: agentic-sdlc
spec:
  selector:
    app: agentic-sdlc
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```text

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agentic-sdlc-hpa
  namespace: agentic-sdlc
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agentic-sdlc
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```text

### 2. Helm Chart

Create Helm chart cho easier deployment:

```yaml
# helm/agentic-sdlc/Chart.yaml
apiVersion: v2
name: agentic-sdlc
description: Agentic SDLC Helm Chart
type: application
version: 1.0.0
appVersion: "3.0.0"
```text

```yaml
# helm/agentic-sdlc/values.yaml
replicaCount: 3

image:
  repository: agentic-sdlc
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

config:
  environment: production
  debug: false
  logging:
    level: INFO
    format: json

secrets:
  openaiApiKey: ""
  databaseUrl: ""
  redisUrl: ""

postgresql:
  enabled: true
  auth:
    database: agentic_sdlc
    username: postgres
    password: password

redis:
  enabled: true
  auth:
    enabled: false
```text

### 3. Deploying to Kubernetes

Deploy application to Kubernetes:

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic agentic-secrets \
  --from-literal=openai-api-key=your-key \
  --from-literal=database-url=postgresql://... \
  --from-literal=redis-url=redis://... \
  -n agentic-sdlc

# Apply manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Or deploy với Helm
helm install agentic-sdlc ./helm/agentic-sdlc \
  --namespace agentic-sdlc \
  --create-namespace \
  --set secrets.openaiApiKey=your-key

# Check deployment
kubectl get pods -n agentic-sdlc
kubectl get svc -n agentic-sdlc

# View logs
kubectl logs -f deployment/agentic-sdlc -n agentic-sdlc

# Scale deployment
kubectl scale deployment agentic-sdlc --replicas=5 -n agentic-sdlc

# Update deployment
kubectl set image deployment/agentic-sdlc \
  app=agentic-sdlc:v2.0.0 \
  -n agentic-sdlc
```text

## Monitoring và Logging

### 1. Prometheus Monitoring

Setup Prometheus monitoring:

```yaml
# k8s/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: agentic-sdlc
  namespace: agentic-sdlc
spec:
  selector:
    matchLabels:
      app: agentic-sdlc
  endpoints:
  - port: metrics
    interval: 30s
```text

```python
# Add Prometheus metrics endpoint
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Flask, Response

app = Flask(__name__)

# Define metrics
agent_executions = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_type', 'status']
)

workflow_duration = Histogram(
    'workflow_duration_seconds',
    'Workflow execution duration',
    ['workflow_name']
)

active_agents = Gauge(
    'active_agents',
    'Number of active agents',
    ['agent_type']
)

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), mimetype='text/plain')
```text

### 2. Grafana Dashboards

Create Grafana dashboard cho visualization:

```json
{
  "dashboard": {
    "title": "Agentic SDLC Monitoring",
    "panels": [
      {
        "title": "Agent Executions",
        "targets": [
          {
            "expr": "rate(agent_executions_total[5m])"
          }
        ]
      },
      {
        "title": "Workflow Duration",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, workflow_duration_seconds)"
          }
        ]
      },
      {
        "title": "Active Agents",
        "targets": [
          {
            "expr": "active_agents"
          }
        ]
      }
    ]
  }
}
```text

### 3. Centralized Logging

Setup centralized logging với ELK stack:

```yaml
# k8s/filebeat.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: agentic-sdlc
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*agentic-sdlc*.log
      processors:
        - add_kubernetes_metadata:
            host: ${NODE_NAME}
            matchers:
            - logs_path:
                logs_path: "/var/log/containers/"
    
    output.elasticsearch:
      hosts: ['${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT}']
      username: ${ELASTICSEARCH_USERNAME}
      password: ${ELASTICSEARCH_PASSWORD}
```text

```python
# Configure structured logging
import logging
import json

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'agent_id'):
            log_data['agent_id'] = record.agent_id
        
        return json.dumps(log_data)

# Setup logger
logger = logging.getLogger("agentic_sdlc")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```text

## CI/CD Pipeline

### 1. GitHub Actions

Setup CI/CD với GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          pytest --cov=agentic_sdlc
      
      - name: Run linting
        run: |
          flake8 src/
          black --check src/
          mypy src/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t agentic-sdlc:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker tag agentic-sdlc:${{ github.sha }} your-registry/agentic-sdlc:latest
          docker push your-registry/agentic-sdlc:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/agentic-sdlc \
            app=your-registry/agentic-sdlc:latest \
            -n agentic-sdlc
          
          kubectl rollout status deployment/agentic-sdlc -n agentic-sdlc
```text

### 2. GitLab CI

Setup CI/CD với GitLab CI:

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: python:3.11
  script:
    - pip install -e ".[dev]"
    - pytest --cov=agentic_sdlc
    - flake8 src/
    - black --check src/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker push $DOCKER_IMAGE
  only:
    - main

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT
    - kubectl set image deployment/agentic-sdlc app=$DOCKER_IMAGE -n agentic-sdlc
    - kubectl rollout status deployment/agentic-sdlc -n agentic-sdlc
  only:
    - main
  environment:
    name: production
```text

## Best Practices

### 1. Health Checks

Implement health check endpoints:

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

@app.route('/ready')
def ready():
    """Readiness check endpoint."""
    # Check dependencies
    db_ready = check_database()
    redis_ready = check_redis()
    
    if db_ready and redis_ready:
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "not ready"}), 503
```text

### 2. Graceful Shutdown

Implement graceful shutdown:

```python
import signal
import sys

class Application:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
    
    def shutdown(self, signum, frame):
        """Graceful shutdown."""
        print("Shutting down gracefully...")
        self.running = False
        
        # Cleanup resources
        self.cleanup_agents()
        self.close_connections()
        
        sys.exit(0)
    
    def run(self):
        """Main application loop."""
        while self.running:
            # Process tasks
            pass
```text

### 3. Configuration Validation

Validate configuration on startup:

```python
from agentic_sdlc.core.config import Config

def validate_config(config: Config):
    """Validate configuration."""
    errors = []
    
    # Check required fields
    if not config.model_clients:
        errors.append("No model clients configured")
    
    # Check API keys
    for name, client_config in config.model_clients.items():
        if not client_config.api_key:
            errors.append(f"API key missing for {name}")
    
    # Check database
    if not config.database.url:
        errors.append("Database URL not configured")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
```

## Troubleshooting

### Issue: Container Fails to Start

**Triệu chứng**: Container exits immediately

**Giải pháp**:
1. Check logs: `docker logs container-id`
2. Verify environment variables
3. Check file permissions
4. Validate configuration

### Issue: High Memory Usage

**Triệu chứng**: Container OOM killed

**Giải pháp**:
1. Increase memory limits
2. Implement memory profiling
3. Enable cache eviction
4. Optimize agent configurations

### Issue: Slow Startup Time

**Triệu chứng**: Container takes long to become ready

**Giải pháp**:
1. Optimize initialization code
2. Use lazy loading
3. Parallelize startup tasks
4. Adjust readiness probe timing

## Tài Liệu Liên Quan

- [Performance Guide](performance.md) - Performance optimization
- [Scalability Guide](scalability.md) - Scaling strategies
- [Security Guide](security.md) - Security best practices
- [Configuration Guide](../../getting-started/configuration.md) - Configuration management
- [Production Example](../../examples/advanced/12-production.py) - Production setup example
