"""Bridge for integrating external systems."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Bridge(ABC):
    """Abstract base class for integration bridges.
    
    A Bridge provides a connection between the SDK and external systems,
    allowing data and commands to flow between them.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the bridge name.
        
        Returns:
            The name of this bridge.
        """
        pass
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the external system.
        
        Raises:
            RuntimeError: If connection fails.
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the external system."""
        pass
    
    @abstractmethod
    def send(self, data: Dict[str, Any]) -> Any:
        """Send data to the external system.
        
        Args:
            data: Data to send.
            
        Returns:
            Response from the external system.
        """
        pass
    
    @abstractmethod
    def receive(self) -> Optional[Dict[str, Any]]:
        """Receive data from the external system.
        
        Returns:
            Data received from the external system, or None if no data available.
        """
        pass


class BridgeRegistry:
    """Registry for managing integration bridges.
    
    The BridgeRegistry maintains a collection of available bridges and
    provides methods to register, unregister, and retrieve them.
    """
    
    def __init__(self) -> None:
        """Initialize the bridge registry."""
        self._bridges: Dict[str, Bridge] = {}
    
    def register(self, bridge: Bridge) -> None:
        """Register a bridge.
        
        Args:
            bridge: The bridge to register.
            
        Raises:
            ValueError: If a bridge with the same name is already registered.
        """
        if bridge.name in self._bridges:
            raise ValueError(f"Bridge '{bridge.name}' is already registered")
        self._bridges[bridge.name] = bridge
    
    def unregister(self, name: str) -> None:
        """Unregister a bridge.
        
        Args:
            name: The name of the bridge to unregister.
            
        Raises:
            KeyError: If the bridge is not found.
        """
        if name not in self._bridges:
            raise KeyError(f"Bridge '{name}' not found")
        del self._bridges[name]
    
    def get(self, name: str) -> Optional[Bridge]:
        """Get a registered bridge by name.
        
        Args:
            name: The name of the bridge.
            
        Returns:
            The bridge if found, None otherwise.
        """
        return self._bridges.get(name)
    
    def list_bridges(self) -> list[str]:
        """List all registered bridge names.
        
        Returns:
            List of registered bridge names.
        """
        return list(self._bridges.keys())
