"""
Configuration settings for the Multi-Agent Orchestration System

This module defines configuration classes and provides functions to load
and manage system settings from environment variables and configuration files.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..models.agent import AgentType, ModelTier, DEFAULT_MODEL_ASSIGNMENTS


@dataclass
class ModelConfig:
    """Configuration for model assignments and API settings"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_timeout: int = 300  # seconds
    max_retries: int = 3
    rate_limit_requests_per_minute: int = 60
    model_assignments: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Load model assignments from environment or use defaults
        if not self.model_assignments:
            self.model_assignments = {
                assignment.role_type.value: {
                    "model_tier": assignment.model_tier.value,
                    "recommended_model": assignment.recommended_model,
                    "fallback_model": assignment.fallback_model,
                    "max_concurrent_instances": assignment.max_concurrent_instances,
                    "cost_per_token": assignment.cost_per_token
                }
                for assignment in DEFAULT_MODEL_ASSIGNMENTS
            }


@dataclass
class AgentPoolConfig:
    """Configuration for agent pool management"""
    default_max_instances: int = 3
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3
    instance_startup_timeout: int = 60  # seconds
    health_check_interval: int = 30  # seconds
    max_queue_size: int = 100
    load_balancing_strategy: str = "least_loaded"  # round_robin, least_loaded, random
    
    # Per-agent-type overrides
    agent_specific_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def get_max_instances_for_agent(self, agent_type: AgentType) -> int:
        """Get max instances for a specific agent type"""
        agent_config = self.agent_specific_configs.get(agent_type.value, {})
        return agent_config.get("max_instances", self.default_max_instances)


@dataclass
class LoggingConfig:
    """Configuration for logging system"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    
    # Component-specific log levels
    component_levels: Dict[str, str] = field(default_factory=dict)
    
    def get_level_for_component(self, component: str) -> str:
        """Get log level for a specific component"""
        return self.component_levels.get(component, self.level)


@dataclass
class DatabaseConfig:
    """Configuration for state persistence"""
    type: str = "sqlite"  # sqlite, postgresql, mysql
    connection_string: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # SQLite specific
    sqlite_path: str = "orchestration_state.db"
    
    def get_connection_string(self) -> str:
        """Get the database connection string"""
        if self.connection_string:
            return self.connection_string
        
        if self.type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        
        raise ValueError(f"No connection string configured for database type: {self.type}")


@dataclass
class SecurityConfig:
    """Configuration for security settings"""
    enable_authentication: bool = False
    jwt_secret_key: Optional[str] = None
    jwt_expiration_hours: int = 24
    allowed_origins: List[str] = field(default_factory=list)
    rate_limiting_enabled: bool = True
    max_requests_per_minute: int = 100


@dataclass
class OrchestrationConfig:
    """Main configuration class for the orchestration system"""
    # Core settings
    environment: str = "development"
    debug: bool = False
    
    # Component configurations
    model: ModelConfig = field(default_factory=ModelConfig)
    agent_pool: AgentPoolConfig = field(default_factory=AgentPoolConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Workflow settings
    default_workflow_timeout: int = 3600  # seconds (1 hour)
    max_concurrent_workflows: int = 10
    checkpoint_interval: int = 300  # seconds (5 minutes)
    
    # CLI settings
    cli_process_timeout: int = 1800  # seconds (30 minutes)
    cli_heartbeat_interval: int = 30  # seconds
    cli_max_retries: int = 3
    
    # Integration settings
    enable_external_apis: bool = True
    external_api_timeout: int = 60  # seconds
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'OrchestrationConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Update basic settings
        for key, value in config_dict.items():
            if hasattr(config, key) and not isinstance(getattr(config, key), (ModelConfig, AgentPoolConfig, LoggingConfig, DatabaseConfig, SecurityConfig)):
                setattr(config, key, value)
        
        # Update component configurations
        if "model" in config_dict:
            config.model = ModelConfig(**config_dict["model"])
        
        if "agent_pool" in config_dict:
            config.agent_pool = AgentPoolConfig(**config_dict["agent_pool"])
        
        if "logging" in config_dict:
            config.logging = LoggingConfig(**config_dict["logging"])
        
        if "database" in config_dict:
            config.database = DatabaseConfig(**config_dict["database"])
        
        if "security" in config_dict:
            config.security = SecurityConfig(**config_dict["security"])
        
        return config


def load_config_from_file(config_path: str) -> OrchestrationConfig:
    """Load configuration from YAML file"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    return OrchestrationConfig.from_dict(config_dict)


def load_config_from_env() -> OrchestrationConfig:
    """Load configuration from environment variables"""
    config = OrchestrationConfig()
    
    # Basic settings
    config.environment = os.getenv("ORCHESTRATION_ENV", "development")
    config.debug = os.getenv("ORCHESTRATION_DEBUG", "false").lower() == "true"
    
    # Model configuration
    config.model.openai_api_key = os.getenv("OPENAI_API_KEY")
    config.model.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    config.model.default_timeout = int(os.getenv("MODEL_TIMEOUT", "300"))
    config.model.max_retries = int(os.getenv("MODEL_MAX_RETRIES", "3"))
    
    # Agent pool configuration
    config.agent_pool.default_max_instances = int(os.getenv("AGENT_POOL_MAX_INSTANCES", "3"))
    config.agent_pool.scale_up_threshold = float(os.getenv("AGENT_POOL_SCALE_UP_THRESHOLD", "0.8"))
    config.agent_pool.scale_down_threshold = float(os.getenv("AGENT_POOL_SCALE_DOWN_THRESHOLD", "0.3"))
    
    # Logging configuration
    config.logging.level = os.getenv("LOG_LEVEL", "INFO")
    config.logging.file_path = os.getenv("LOG_FILE_PATH")
    config.logging.enable_console = os.getenv("LOG_ENABLE_CONSOLE", "true").lower() == "true"
    config.logging.enable_file = os.getenv("LOG_ENABLE_FILE", "true").lower() == "true"
    
    # Database configuration
    config.database.type = os.getenv("DB_TYPE", "sqlite")
    config.database.connection_string = os.getenv("DB_CONNECTION_STRING")
    config.database.sqlite_path = os.getenv("DB_SQLITE_PATH", "orchestration_state.db")
    
    # Security configuration
    config.security.enable_authentication = os.getenv("ENABLE_AUTH", "false").lower() == "true"
    config.security.jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    
    # Workflow settings
    config.default_workflow_timeout = int(os.getenv("WORKFLOW_TIMEOUT", "3600"))
    config.max_concurrent_workflows = int(os.getenv("MAX_CONCURRENT_WORKFLOWS", "10"))
    
    return config


def load_config(config_path: Optional[str] = None) -> OrchestrationConfig:
    """Load configuration from file or environment variables"""
    if config_path and os.path.exists(config_path):
        return load_config_from_file(config_path)
    
    # Try to find default config file
    default_paths = [
        "orchestration_config.yaml",
        "config/orchestration.yaml",
        os.path.expanduser("~/.agentic_sdlc/orchestration_config.yaml")
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return load_config_from_file(path)
    
    # Fall back to environment variables
    return load_config_from_env()


def get_default_config() -> OrchestrationConfig:
    """Get default configuration"""
    return OrchestrationConfig()


def save_config_template(output_path: str):
    """Save a configuration template file"""
    template_config = {
        "environment": "development",
        "debug": False,
        "model": {
            "openai_api_key": "your-openai-api-key",
            "anthropic_api_key": "your-anthropic-api-key",
            "default_timeout": 300,
            "max_retries": 3,
            "rate_limit_requests_per_minute": 60
        },
        "agent_pool": {
            "default_max_instances": 3,
            "scale_up_threshold": 0.8,
            "scale_down_threshold": 0.3,
            "instance_startup_timeout": 60,
            "health_check_interval": 30,
            "max_queue_size": 100,
            "load_balancing_strategy": "least_loaded"
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file_path": "logs/orchestration.log",
            "max_file_size": 10485760,
            "backup_count": 5,
            "enable_console": True,
            "enable_file": True
        },
        "database": {
            "type": "sqlite",
            "sqlite_path": "orchestration_state.db",
            "pool_size": 5,
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600
        },
        "security": {
            "enable_authentication": False,
            "jwt_secret_key": "your-jwt-secret-key",
            "jwt_expiration_hours": 24,
            "allowed_origins": [],
            "rate_limiting_enabled": True,
            "max_requests_per_minute": 100
        },
        "default_workflow_timeout": 3600,
        "max_concurrent_workflows": 10,
        "checkpoint_interval": 300,
        "cli_process_timeout": 1800,
        "cli_heartbeat_interval": 30,
        "cli_max_retries": 3,
        "enable_external_apis": True,
        "external_api_timeout": 60
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(template_config, f, default_flow_style=False, indent=2)