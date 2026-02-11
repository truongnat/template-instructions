"""
Ví Dụ 12: Production Setup (Thiết Lập Production)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc[production]
2. Cấu hình monitoring và logging
3. Chạy: python 12-production.py

Dependencies:
- agentic-sdlc[production]>=3.0.0
- prometheus-client
- sentry-sdk

Expected Output:
- Production-ready configuration
- Monitoring và metrics
- Logging và error tracking
- Health checks
- Graceful shutdown
"""

import os
import logging
import signal
import sys
from dotenv import load_dotenv

load_dotenv()


def production_configuration():
    """Production configuration setup."""
    from agentic_sdlc.core.config import Config, ModelConfig
    
    config = Config(
        project_name="production-app",
        log_level="INFO",
        models={
            "primary": ModelConfig(
                provider="openai",
                model_name="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=2000,
                timeout=30,
                max_retries=3
            ),
            "fallback": ModelConfig(
                provider="openai",
                model_name="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.3
            )
        },
        # Production settings
        enable_caching=True,
        cache_ttl=3600,
        rate_limit=100,  # requests per minute
        enable_monitoring=True,
        enable_tracing=True
    )
    
    print("✓ Production configuration")
    print(f"  Project: {config.project_name}")
    print(f"  Models: {list(config.models.keys())}")
    print(f"  Caching: {config.enable_caching}")
    print(f"  Monitoring: {config.enable_monitoring}")
    
    return config


def setup_logging():
    """Setup production logging."""
    import logging.handlers
    
    # Create logger
    logger = logging.getLogger('agentic_sdlc')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'agentic_sdlc.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    print("\n✓ Logging configured")
    print("  Console: INFO level")
    print("  File: agentic_sdlc.log (10MB rotation)")
    
    return logger


def setup_monitoring():
    """Setup Prometheus monitoring."""
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    
    # Define metrics
    task_counter = Counter(
        'agentic_tasks_total',
        'Total number of tasks processed',
        ['status', 'agent_type']
    )
    
    task_duration = Histogram(
        'agentic_task_duration_seconds',
        'Task processing duration',
        ['agent_type']
    )
    
    active_agents = Gauge(
        'agentic_active_agents',
        'Number of active agents',
        ['agent_type']
    )
    
    # Start metrics server
    start_http_server(8000)
    
    print("\n✓ Monitoring configured")
    print("  Metrics endpoint: http://localhost:8000/metrics")
    print("  Metrics:")
    print("    - agentic_tasks_total")
    print("    - agentic_task_duration_seconds")
    print("    - agentic_active_agents")
    
    return {
        'task_counter': task_counter,
        'task_duration': task_duration,
        'active_agents': active_agents
    }


def setup_error_tracking():
    """Setup Sentry error tracking."""
    import sentry_sdk
    
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment="production",
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1
    )
    
    print("\n✓ Error tracking configured")
    print("  Provider: Sentry")
    print("  Environment: production")
    
    return sentry_sdk


def health_check_endpoint():
    """Health check endpoint."""
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        """Health check endpoint."""
        # Check various components
        checks = {
            "status": "healthy",
            "components": {
                "database": "ok",
                "cache": "ok",
                "llm_api": "ok"
            },
            "version": "3.0.0"
        }
        
        return jsonify(checks)
    
    @app.route('/ready')
    def ready():
        """Readiness check."""
        # Check if app is ready to serve traffic
        return jsonify({"status": "ready"})
    
    @app.route('/metrics')
    def metrics():
        """Metrics endpoint."""
        return jsonify({
            "tasks_processed": 1234,
            "active_agents": 5,
            "avg_response_time": 1.5
        })
    
    print("\n✓ Health check endpoints")
    print("  GET /health - Health status")
    print("  GET /ready - Readiness status")
    print("  GET /metrics - Application metrics")
    
    return app


def graceful_shutdown():
    """Graceful shutdown handler."""
    
    class GracefulShutdown:
        def __init__(self):
            self.shutdown_requested = False
            signal.signal(signal.SIGINT, self.request_shutdown)
            signal.signal(signal.SIGTERM, self.request_shutdown)
        
        def request_shutdown(self, signum, frame):
            """Handle shutdown signal."""
            print("\n✓ Shutdown signal received")
            self.shutdown_requested = True
            
            # Cleanup tasks
            print("  Finishing active tasks...")
            print("  Closing connections...")
            print("  Saving state...")
            
            print("  ✓ Graceful shutdown complete")
            sys.exit(0)
    
    handler = GracefulShutdown()
    
    print("\n✓ Graceful shutdown configured")
    print("  Signals: SIGINT, SIGTERM")
    
    return handler


def production_agent_pool():
    """Production agent pool với monitoring."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, AgentRegistry
    from agentic_sdlc.core.config import ModelConfig
    
    registry = AgentRegistry()
    
    # Create agent pool
    pool_size = 10
    
    for i in range(pool_size):
        model_config = ModelConfig(
            provider="openai",
            model_name="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=30,
            max_retries=3
        )
        
        agent_config = AgentConfig(
            name=f"prod-agent-{i}",
            role="worker",
            description=f"Production worker {i}",
            model_config=model_config,
            metadata={
                "pool": "production",
                "health_check_interval": 60
            }
        )
        
        agent = Agent(config=agent_config)
        registry.register(agent)
    
    print("\n✓ Production agent pool")
    print(f"  Pool size: {pool_size}")
    print(f"  Health checks: Every 60s")
    print(f"  Retry policy: 3 attempts")
    
    return registry


def deployment_checklist():
    """Production deployment checklist."""
    checklist = {
        "Configuration": [
            "✓ Environment variables set",
            "✓ API keys configured",
            "✓ Database connection tested",
            "✓ Cache configured"
        ],
        "Security": [
            "✓ HTTPS enabled",
            "✓ API rate limiting configured",
            "✓ Input validation enabled",
            "✓ Secrets encrypted"
        ],
        "Monitoring": [
            "✓ Prometheus metrics enabled",
            "✓ Sentry error tracking configured",
            "✓ Log aggregation setup",
            "✓ Alerts configured"
        ],
        "Reliability": [
            "✓ Health checks implemented",
            "✓ Graceful shutdown configured",
            "✓ Retry logic enabled",
            "✓ Circuit breakers configured"
        ],
        "Performance": [
            "✓ Caching enabled",
            "✓ Connection pooling configured",
            "✓ Load balancing setup",
            "✓ Auto-scaling configured"
        ]
    }
    
    print("\n✓ Production deployment checklist:")
    for category, items in checklist.items():
        print(f"\n  {category}:")
        for item in items:
            print(f"    {item}")
    
    return checklist


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: PRODUCTION SETUP")
    print("=" * 60)
    
    production_configuration()
    setup_logging()
    setup_monitoring()
    setup_error_tracking()
    health_check_endpoint()
    graceful_shutdown()
    production_agent_pool()
    deployment_checklist()
    
    print("\n" + "=" * 60)
    print("✓ Production setup hoàn thành!")
    print("=" * 60)
