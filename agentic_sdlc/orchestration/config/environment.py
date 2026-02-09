"""
Environment detection and management for the Multi-Agent Orchestration System

This module provides utilities for detecting the current environment
and adjusting system behavior accordingly.
"""

import os
from enum import Enum
from typing import Optional


class Environment(Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


def get_environment() -> Environment:
    """Get the current environment"""
    env_str = os.getenv("ORCHESTRATION_ENV", "development").lower()
    
    try:
        return Environment(env_str)
    except ValueError:
        # Default to development if unknown environment
        return Environment.DEVELOPMENT


def is_development() -> bool:
    """Check if running in development environment"""
    return get_environment() == Environment.DEVELOPMENT


def is_testing() -> bool:
    """Check if running in testing environment"""
    return get_environment() == Environment.TESTING


def is_staging() -> bool:
    """Check if running in staging environment"""
    return get_environment() == Environment.STAGING


def is_production() -> bool:
    """Check if running in production environment"""
    return get_environment() == Environment.PRODUCTION


def get_log_level() -> str:
    """Get appropriate log level for current environment"""
    env = get_environment()
    
    if env == Environment.DEVELOPMENT:
        return "DEBUG"
    elif env == Environment.TESTING:
        return "WARNING"
    elif env == Environment.STAGING:
        return "INFO"
    else:  # PRODUCTION
        return "WARNING"


def get_database_url() -> Optional[str]:
    """Get database URL based on environment"""
    env = get_environment()
    
    # Check for explicit database URL first
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # Environment-specific defaults
    if env == Environment.TESTING:
        return "sqlite:///test_orchestration.db"
    elif env == Environment.DEVELOPMENT:
        return "sqlite:///dev_orchestration.db"
    elif env == Environment.STAGING:
        return os.getenv("STAGING_DATABASE_URL")
    else:  # PRODUCTION
        return os.getenv("PRODUCTION_DATABASE_URL")


def should_enable_debug_features() -> bool:
    """Check if debug features should be enabled"""
    if is_development() or is_testing():
        return True
    
    # Allow explicit override in other environments
    return os.getenv("ENABLE_DEBUG", "false").lower() == "true"


def get_max_concurrent_workflows() -> int:
    """Get max concurrent workflows based on environment"""
    env = get_environment()
    
    # Environment-specific defaults
    if env == Environment.TESTING:
        return 2
    elif env == Environment.DEVELOPMENT:
        return 5
    elif env == Environment.STAGING:
        return 10
    else:  # PRODUCTION
        return 20


def get_default_timeout() -> int:
    """Get default timeout based on environment"""
    env = get_environment()
    
    # Environment-specific defaults (in seconds)
    if env == Environment.TESTING:
        return 60  # Shorter timeouts for tests
    elif env == Environment.DEVELOPMENT:
        return 300  # 5 minutes
    elif env == Environment.STAGING:
        return 600  # 10 minutes
    else:  # PRODUCTION
        return 1800  # 30 minutes


def get_checkpoint_interval() -> int:
    """Get checkpoint interval based on environment"""
    env = get_environment()
    
    # Environment-specific defaults (in seconds)
    if env == Environment.TESTING:
        return 30  # Frequent checkpoints for tests
    elif env == Environment.DEVELOPMENT:
        return 120  # 2 minutes
    elif env == Environment.STAGING:
        return 300  # 5 minutes
    else:  # PRODUCTION
        return 600  # 10 minutes


def should_use_external_apis() -> bool:
    """Check if external APIs should be used"""
    if is_testing():
        # Don't use external APIs in tests by default
        return os.getenv("USE_EXTERNAL_APIS_IN_TESTS", "false").lower() == "true"
    
    return os.getenv("ENABLE_EXTERNAL_APIS", "true").lower() == "true"


def get_rate_limit() -> int:
    """Get rate limit based on environment"""
    env = get_environment()
    
    # Environment-specific defaults (requests per minute)
    if env == Environment.TESTING:
        return 10
    elif env == Environment.DEVELOPMENT:
        return 30
    elif env == Environment.STAGING:
        return 60
    else:  # PRODUCTION
        return 100