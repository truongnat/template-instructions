"""Unit tests for bridge registry components."""

import pytest
from typing import Any, Dict, Optional
from agentic_sdlc.infrastructure.bridge import Bridge, BridgeRegistry


class MockBridge(Bridge):
    """Mock bridge for testing."""
    
    def __init__(self, name: str = "mock_bridge"):
        self._name = name
        self._connected = False
    
    @property
    def name(self) -> str:
        return self._name
    
    def connect(self) -> None:
        self._connected = True
    
    def disconnect(self) -> None:
        self._connected = False
    
    def send(self, data: Dict[str, Any]) -> Any:
        return {"sent": data}
    
    def receive(self) -> Optional[Dict[str, Any]]:
        return {"received": "data"}


class TestBridgeRegistry:
    """Tests for BridgeRegistry class."""
    
    def test_bridge_registry_initialization(self):
        """Test that BridgeRegistry initializes correctly."""
        registry = BridgeRegistry()
        assert registry is not None
        assert registry.list_bridges() == []
    
    def test_register_bridge(self):
        """Test registering a bridge."""
        registry = BridgeRegistry()
        bridge = MockBridge("test_bridge")
        registry.register(bridge)
        
        assert "test_bridge" in registry.list_bridges()
        assert registry.get("test_bridge") is bridge
    
    def test_register_duplicate_bridge(self):
        """Test that registering duplicate bridge raises error."""
        registry = BridgeRegistry()
        bridge1 = MockBridge("test_bridge")
        bridge2 = MockBridge("test_bridge")
        
        registry.register(bridge1)
        with pytest.raises(ValueError, match="Bridge 'test_bridge' is already registered"):
            registry.register(bridge2)
    
    def test_unregister_bridge(self):
        """Test unregistering a bridge."""
        registry = BridgeRegistry()
        bridge = MockBridge("test_bridge")
        registry.register(bridge)
        
        assert "test_bridge" in registry.list_bridges()
        registry.unregister("test_bridge")
        assert "test_bridge" not in registry.list_bridges()
    
    def test_unregister_nonexistent_bridge(self):
        """Test that unregistering nonexistent bridge raises error."""
        registry = BridgeRegistry()
        with pytest.raises(KeyError, match="Bridge 'nonexistent' not found"):
            registry.unregister("nonexistent")
    
    def test_get_bridge(self):
        """Test getting a registered bridge."""
        registry = BridgeRegistry()
        bridge = MockBridge("test_bridge")
        registry.register(bridge)
        
        retrieved = registry.get("test_bridge")
        assert retrieved is bridge
    
    def test_get_nonexistent_bridge(self):
        """Test getting a nonexistent bridge returns None."""
        registry = BridgeRegistry()
        assert registry.get("nonexistent") is None
    
    def test_list_bridges(self):
        """Test listing all registered bridges."""
        registry = BridgeRegistry()
        bridge1 = MockBridge("bridge1")
        bridge2 = MockBridge("bridge2")
        bridge3 = MockBridge("bridge3")
        
        registry.register(bridge1)
        registry.register(bridge2)
        registry.register(bridge3)
        
        bridges = registry.list_bridges()
        assert len(bridges) == 3
        assert "bridge1" in bridges
        assert "bridge2" in bridges
        assert "bridge3" in bridges
    
    def test_multiple_bridges(self):
        """Test managing multiple bridges."""
        registry = BridgeRegistry()
        bridges = [MockBridge(f"bridge_{i}") for i in range(5)]
        
        for bridge in bridges:
            registry.register(bridge)
        
        assert len(registry.list_bridges()) == 5
        
        # Verify all bridges are retrievable
        for bridge in bridges:
            assert registry.get(bridge.name) is bridge
