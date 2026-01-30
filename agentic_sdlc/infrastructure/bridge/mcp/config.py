"""
MCP Configuration

Configuration management for MCP connectors.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ConnectorConfig:
    """Configuration for a single connector."""
    name: str
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    settings: Dict = field(default_factory=dict)


@dataclass
class MCPConfig:
    """Main MCP configuration."""
    enabled: bool = True
    log_level: str = "info"
    max_connections: int = 10
    project_root: Optional[Path] = None
    connectors: Dict[str, ConnectorConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.project_root is None:
            self.project_root = Path.cwd()
        
        # Register default connectors
        if not self.connectors:
            self.connectors = {
                "filesystem": ConnectorConfig("filesystem", enabled=True),
                "github": ConnectorConfig("github", enabled=True),
                "database": ConnectorConfig("database", enabled=False),
                "api": ConnectorConfig("api", enabled=True),
                "deep_search": ConnectorConfig(
                    "deep_search", 
                    enabled=True,
                    timeout=60,
                    settings={
                        "github_token": os.getenv("GITHUB_TOKEN"),
                        "cache_enabled": True,
                        "cache_ttl_hours": 24
                    }
                ),
            }
    
    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Load configuration from environment variables."""
        return cls(
            enabled=os.getenv("MCP_ENABLED", "true").lower() == "true",
            log_level=os.getenv("MCP_LOG_LEVEL", "info"),
            max_connections=int(os.getenv("MCP_MAX_CONNECTIONS", "10")),
            project_root=Path(os.getenv("MCP_PROJECT_ROOT", str(Path.cwd())))
        )
    
    def get_connector_config(self, name: str) -> Optional[ConnectorConfig]:
        """Get configuration for a specific connector."""
        return self.connectors.get(name)
    
    def is_connector_enabled(self, name: str) -> bool:
        """Check if a connector is enabled."""
        config = self.connectors.get(name)
        return config.enabled if config else False
    
    def enable_connector(self, name: str):
        """Enable a connector."""
        if name in self.connectors:
            self.connectors[name].enabled = True
    
    def disable_connector(self, name: str):
        """Disable a connector."""
        if name in self.connectors:
            self.connectors[name].enabled = False


# Global config instance
_config: Optional[MCPConfig] = None


def get_config() -> MCPConfig:
    """Get the global MCP configuration."""
    global _config
    if _config is None:
        _config = MCPConfig.from_env()
    return _config


def set_config(config: MCPConfig):
    """Set the global MCP configuration."""
    global _config
    _config = config
