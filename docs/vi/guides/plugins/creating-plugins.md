# Tạo Plugins Tùy Chỉnh

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này hướng dẫn chi tiết cách tạo plugins tùy chỉnh cho Agentic SDLC. Bạn sẽ học cách implement Plugin base class, define plugin interface, và integrate plugin vào hệ thống.

## Plugin Base Class

### Cấu Trúc Cơ Bản

Mọi plugin phải kế thừa từ `Plugin` base class:

```python
from agentic_sdlc.plugins import Plugin
from typing import Dict, Any, Optional, List

class MyCustomPlugin(Plugin):
    """Custom plugin template."""
    
    @property
    def name(self) -> str:
        """Return unique plugin name.
        
        Returns:
            str: Plugin name (kebab-case recommended)
        """
        return "my-custom-plugin"
    
    @property
    def version(self) -> str:
        """Return plugin version.
        
        Returns:
            str: Semantic version (e.g., "1.0.0")
        """
        return "1.0.0"
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            PluginError: If initialization fails
        """
        # Initialize plugin state
        self.config = config or {}
        self._setup()
    
    def shutdown(self) -> None:
        """Cleanup plugin resources.
        
        Called when plugin is unloaded or system shuts down.
        """
        # Cleanup resources
        self._cleanup()
    
    def _setup(self) -> None:
        """Internal setup logic."""
        pass
    
    def _cleanup(self) -> None:
        """Internal cleanup logic."""
        pass
```text

### Required Methods

Mỗi plugin PHẢI implement các methods sau:

#### 1. name Property

```python
@property
def name(self) -> str:
    """Unique identifier for the plugin.
    
    Naming conventions:
    - Use kebab-case: "my-plugin-name"
    - Be descriptive: "postgresql-database"
    - Avoid generic names: "plugin1", "db"
    """
    return "my-plugin"
```text

#### 2. version Property

```python
@property
def version(self) -> str:
    """Plugin version using semantic versioning.
    
    Format: MAJOR.MINOR.PATCH
    - MAJOR: Breaking changes
    - MINOR: New features (backward compatible)
    - PATCH: Bug fixes
    """
    return "1.0.0"
```text

#### 3. initialize Method

```python
def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
    """Initialize plugin with configuration.
    
    This method is called when plugin is registered.
    Use it to:
    - Load configuration
    - Setup connections
    - Initialize resources
    - Validate dependencies
    
    Args:
        config: Configuration dictionary with plugin settings
        
    Raises:
        PluginError: If initialization fails
    """
    self.config = config or {}
    
    # Validate configuration
    self._validate_config()
    
    # Setup resources
    self._setup_resources()
```text

#### 4. shutdown Method

```python
def shutdown(self) -> None:
    """Cleanup plugin resources.
    
    This method is called when:
    - Plugin is unregistered
    - System is shutting down
    
    Use it to:
    - Close connections
    - Release resources
    - Save state
    - Cleanup temporary files
    """
    # Close connections
    if hasattr(self, 'connection'):
        self.connection.close()
    
    # Release resources
    if hasattr(self, 'resource'):
        self.resource.release()
```text

## Step-by-Step Plugin Creation

### Step 1: Define Plugin Class

```python
from agentic_sdlc.plugins import Plugin
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WeatherPlugin(Plugin):
    """Plugin to fetch weather information."""
    
    @property
    def name(self) -> str:
        return "weather-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
```text

### Step 2: Add Configuration

```python
class WeatherPlugin(Plugin):
    """Plugin to fetch weather information."""
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with API configuration."""
        self.config = config or {}
        
        # Get API key from config
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise PluginError("Missing required config: api_key")
        
        # Get optional settings
        self.base_url = self.config.get(
            "base_url",
            "https://api.weather.com"
        )
        self.timeout = self.config.get("timeout", 30)
        
        # Initialize HTTP client
        self.client = self._create_client()
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def _create_client(self):
        """Create HTTP client."""
        import requests
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.api_key}"
        })
        return session
```text

### Step 3: Implement Core Functionality

```python
class WeatherPlugin(Plugin):
    """Plugin to fetch weather information."""
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Weather data dictionary
            
        Raises:
            PluginError: If API request fails
        """
        try:
            response = self.client.get(
                f"{self.base_url}/current",
                params={"city": city},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise PluginError(f"Failed to fetch weather: {e}")
    
    def get_forecast(self, city: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get weather forecast.
        
        Args:
            city: City name
            days: Number of days (1-14)
            
        Returns:
            List of daily forecasts
        """
        try:
            response = self.client.get(
                f"{self.base_url}/forecast",
                params={"city": city, "days": days},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["forecast"]
        except Exception as e:
            raise PluginError(f"Failed to fetch forecast: {e}")
```text

### Step 4: Add Cleanup Logic

```python
class WeatherPlugin(Plugin):
    """Plugin to fetch weather information."""
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info(f"Closed HTTP client for {self.name}")
```text

### Step 5: Add Helper Methods

```python
class WeatherPlugin(Plugin):
    """Plugin to fetch weather information."""
    
    def _validate_config(self) -> None:
        """Validate plugin configuration."""
        required = ["api_key"]
        for field in required:
            if field not in self.config:
                raise PluginError(f"Missing required config: {field}")
    
    def _format_weather(self, data: Dict[str, Any]) -> str:
        """Format weather data for display."""
        return (
            f"Temperature: {data['temp']}°C\n"
            f"Condition: {data['condition']}\n"
            f"Humidity: {data['humidity']}%"
        )
```text

## Complete Plugin Example

```python
"""
Weather Plugin for Agentic SDLC
Provides weather information for agents.
"""

from agentic_sdlc.plugins import Plugin, PluginError
from typing import Dict, Any, Optional, List
import logging
import requests

logger = logging.getLogger(__name__)


class WeatherPlugin(Plugin):
    """Plugin to fetch weather information from external API.
    
    Configuration:
        api_key (str): API key for weather service
        base_url (str): Base URL for API (optional)
        timeout (int): Request timeout in seconds (default: 30)
    
    Example:
        >>> plugin = WeatherPlugin()
        >>> plugin.initialize({"api_key": "your-key"})
        >>> weather = plugin.get_weather("Hanoi")
        >>> print(weather)
    """
    
    @property
    def name(self) -> str:
        """Plugin name."""
        return "weather-plugin"
    
    @property
    def version(self) -> str:
        """Plugin version."""
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """Plugin description."""
        return "Fetch weather information from external API"
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            PluginError: If configuration is invalid
        """
        self.config = config or {}
        
        # Validate configuration
        self._validate_config()
        
        # Load settings
        self.api_key = self.config["api_key"]
        self.base_url = self.config.get(
            "base_url",
            "https://api.weather.com"
        )
        self.timeout = self.config.get("timeout", 30)
        
        # Initialize HTTP client
        self.client = self._create_client()
        
        logger.info(f"Initialized {self.name} v{self.version}")
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info(f"Shutdown {self.name}")
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city.
        
        Args:
            city: City name
            
        Returns:
            Weather data dictionary with keys:
            - temp: Temperature in Celsius
            - condition: Weather condition
            - humidity: Humidity percentage
            - wind_speed: Wind speed in km/h
            
        Raises:
            PluginError: If API request fails
        """
        try:
            response = self.client.get(
                f"{self.base_url}/current",
                params={"city": city},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise PluginError(f"Failed to fetch weather: {e}")
    
    def get_forecast(self, city: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get weather forecast.
        
        Args:
            city: City name
            days: Number of days (1-14)
            
        Returns:
            List of daily forecasts
            
        Raises:
            PluginError: If API request fails
        """
        if not 1 <= days <= 14:
            raise PluginError("Days must be between 1 and 14")
        
        try:
            response = self.client.get(
                f"{self.base_url}/forecast",
                params={"city": city, "days": days},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["forecast"]
        except requests.RequestException as e:
            raise PluginError(f"Failed to fetch forecast: {e}")
    
    def format_weather(self, data: Dict[str, Any]) -> str:
        """Format weather data for display.
        
        Args:
            data: Weather data dictionary
            
        Returns:
            Formatted weather string
        """
        return (
            f"🌡️  Temperature: {data['temp']}°C\n"
            f"☁️  Condition: {data['condition']}\n"
            f"💧 Humidity: {data['humidity']}%\n"
            f"💨 Wind: {data['wind_speed']} km/h"
        )
    
    def _validate_config(self) -> None:
        """Validate plugin configuration.
        
        Raises:
            PluginError: If configuration is invalid
        """
        required = ["api_key"]
        for field in required:
            if field not in self.config:
                raise PluginError(f"Missing required config: {field}")
        
        # Validate types
        if not isinstance(self.config["api_key"], str):
            raise PluginError("api_key must be a string")
    
    def _create_client(self) -> requests.Session:
        """Create HTTP client with authentication.
        
        Returns:
            Configured requests Session
        """
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"AgenticSDLC-{self.name}/{self.version}"
        })
        return session
```text

## Using Your Plugin

### Register Plugin

```python
from agentic_sdlc.plugins import get_plugin_registry
from my_plugins import WeatherPlugin

# Get registry
registry = get_plugin_registry()

# Create and register plugin
weather_plugin = WeatherPlugin()
registry.register(weather_plugin)

# Initialize with config
weather_plugin.initialize({
    "api_key": "your-api-key-here",
    "timeout": 30
})
```text

### Use Plugin in Agent

```python
from agentic_sdlc import create_agent

# Create agent
agent = create_agent(
    name="weather-agent",
    role="Weather Reporter",
    model_name="gpt-4"
)

# Get plugin
registry = get_plugin_registry()
weather = registry.get("weather-plugin")

# Use plugin in agent task
def report_weather(city: str) -> str:
    """Agent task using weather plugin."""
    data = weather.get_weather(city)
    return weather.format_weather(data)

# Agent executes task
result = report_weather("Hanoi")
print(result)
```text

### Use Plugin in Workflow

```python
from agentic_sdlc import Workflow, WorkflowStep

# Create workflow
workflow = Workflow(name="weather-report-workflow")

# Add step using plugin
workflow.add_step(
    WorkflowStep(
        name="fetch-weather",
        action=lambda: weather.get_weather("Hanoi"),
        description="Fetch current weather"
    )
)

workflow.add_step(
    WorkflowStep(
        name="format-report",
        action=lambda data: weather.format_weather(data),
        description="Format weather report",
        dependencies=["fetch-weather"]
    )
)

# Execute workflow
result = workflow.execute()
```text

## Advanced Plugin Features

### Plugin with Dependencies

```python
class AdvancedPlugin(Plugin):
    """Plugin that depends on other plugins."""
    
    @property
    def dependencies(self) -> List[str]:
        """List of required plugin names."""
        return ["database-plugin", "cache-plugin"]
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with dependency checking."""
        self.config = config or {}
        
        # Get plugin registry
        registry = get_plugin_registry()
        
        # Check dependencies
        for dep in self.dependencies:
            plugin = registry.get(dep)
            if not plugin:
                raise PluginError(f"Missing dependency: {dep}")
        
        # Store dependency references
        self.db = registry.get("database-plugin")
        self.cache = registry.get("cache-plugin")
```text

### Plugin with State Management

```python
class StatefulPlugin(Plugin):
    """Plugin that maintains state."""
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with state."""
        self.config = config or {}
        self.state = {
            "requests_count": 0,
            "last_request": None,
            "cache": {}
        }
    
    def execute_task(self, task: str) -> Any:
        """Execute task and update state."""
        # Update state
        self.state["requests_count"] += 1
        self.state["last_request"] = datetime.now()
        
        # Check cache
        if task in self.state["cache"]:
            return self.state["cache"][task]
        
        # Execute and cache
        result = self._do_task(task)
        self.state["cache"][task] = result
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get plugin statistics."""
        return {
            "requests": self.state["requests_count"],
            "last_request": self.state["last_request"],
            "cache_size": len(self.state["cache"])
        }
```text

### Plugin with Async Support

```python
import asyncio
from typing import Coroutine

class AsyncPlugin(Plugin):
    """Plugin with async operations."""
    
    async def async_initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Async initialization."""
        self.config = config or {}
        self.client = await self._create_async_client()
    
    async def fetch_data(self, url: str) -> Dict[str, Any]:
        """Async data fetching."""
        async with self.client.get(url) as response:
            return await response.json()
    
    def shutdown(self) -> None:
        """Cleanup async resources."""
        if hasattr(self, 'client'):
            asyncio.run(self.client.close())
```text

## Testing Your Plugin

### Unit Tests

```python
import pytest
from my_plugins import WeatherPlugin

def test_plugin_initialization():
    """Test plugin initialization."""
    plugin = WeatherPlugin()
    config = {"api_key": "test-key"}
    
    plugin.initialize(config)
    
    assert plugin.name == "weather-plugin"
    assert plugin.version == "1.0.0"
    assert plugin.api_key == "test-key"

def test_plugin_missing_config():
    """Test plugin with missing config."""
    plugin = WeatherPlugin()
    
    with pytest.raises(PluginError):
        plugin.initialize({})  # Missing api_key

def test_plugin_shutdown():
    """Test plugin cleanup."""
    plugin = WeatherPlugin()
    plugin.initialize({"api_key": "test-key"})
    
    # Should not raise
    plugin.shutdown()
```text

### Integration Tests

```python
def test_plugin_in_registry():
    """Test plugin registration."""
    from agentic_sdlc.plugins import get_plugin_registry
    
    registry = get_plugin_registry()
    plugin = WeatherPlugin()
    
    # Register
    registry.register(plugin)
    plugin.initialize({"api_key": "test-key"})
    
    # Retrieve
    retrieved = registry.get("weather-plugin")
    assert retrieved is plugin
    
    # Cleanup
    plugin.shutdown()
    registry.unregister("weather-plugin")
```

## Tài Liệu Liên Quan

- [Plugin Overview](overview.md)
- [Plugin Examples](plugin-examples.md)
- [Best Practices](best-practices.md)
- [Plugin Registry API](../../api-reference/plugins/registry.md)

## Tóm Tắt

Để tạo plugin tùy chỉnh:

1. Kế thừa từ `Plugin` base class
2. Implement required methods: `name`, `version`, `initialize`, `shutdown`
3. Add core functionality methods
4. Handle errors và cleanup properly
5. Test thoroughly
6. Document API và usage

Plugin của bạn giờ đã sẵn sàng để integrate vào Agentic SDLC!
