# Best Practices cho Plugin Development

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp các best practices, patterns, và guidelines để phát triển plugins chất lượng cao, maintainable, và production-ready cho Agentic SDLC.

## Error Handling

### 1. Sử Dụng Custom Exceptions

Luôn sử dụng `PluginError` hoặc custom exceptions:

```python
from agentic_sdlc.plugins import Plugin, PluginError

class MyPlugin(Plugin):
    def execute_task(self, task: str) -> Any:
        """Execute task with proper error handling."""
        try:
            result = self._do_task(task)
            return result
        except ValueError as e:
            raise PluginError(f"Invalid task parameter: {e}")
        except ConnectionError as e:
            raise PluginError(f"Connection failed: {e}")
        except Exception as e:
            raise PluginError(f"Unexpected error: {e}")
```text

### 2. Validate Input Parameters

Validate tất cả inputs trước khi xử lý:

```python
class MyPlugin(Plugin):
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data with validation."""
        # Validate required fields
        required_fields = ["id", "name", "type"]
        for field in required_fields:
            if field not in data:
                raise PluginError(f"Missing required field: {field}")
        
        # Validate types
        if not isinstance(data["id"], int):
            raise PluginError("Field 'id' must be an integer")
        
        if not isinstance(data["name"], str):
            raise PluginError("Field 'name' must be a string")
        
        # Validate values
        if data["id"] <= 0:
            raise PluginError("Field 'id' must be positive")
        
        if len(data["name"]) == 0:
            raise PluginError("Field 'name' cannot be empty")
        
        # Process validated data
        return self._process(data)
```text

### 3. Handle Partial Failures Gracefully

Xử lý partial failures mà không crash toàn bộ operation:

```python
class BatchPlugin(Plugin):
    def process_batch(self, items: List[Dict]) -> Dict[str, Any]:
        """Process batch with partial failure handling."""
        results = {
            "successful": [],
            "failed": [],
            "errors": []
        }
        
        for item in items:
            try:
                result = self._process_item(item)
                results["successful"].append(result)
            except Exception as e:
                results["failed"].append(item)
                results["errors"].append({
                    "item": item,
                    "error": str(e)
                })
                logger.error(f"Failed to process item {item}: {e}")
        
        return results
```text

### 4. Implement Retry Logic

Thêm retry logic cho transient failures:

```python
import time
from typing import Callable, Any

class ResilientPlugin(Plugin):
    def with_retry(
        self,
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0
    ) -> Any:
        """Execute function with retry logic.
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retries
            delay: Initial delay between retries
            backoff: Backoff multiplier
            
        Returns:
            Function result
            
        Raises:
            PluginError: If all retries fail
        """
        last_error = None
        current_delay = delay
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        raise PluginError(
            f"Failed after {max_retries} retries: {last_error}"
        )
    
    def fetch_data(self, url: str) -> Dict[str, Any]:
        """Fetch data with retry."""
        return self.with_retry(
            lambda: self._fetch(url),
            max_retries=3,
            delay=1.0
        )
```text

## Logging

### 1. Use Structured Logging

Sử dụng structured logging với context:

```python
import logging

logger = logging.getLogger(__name__)

class MyPlugin(Plugin):
    def execute_task(self, task_id: str, params: Dict) -> Any:
        """Execute task with structured logging."""
        logger.info(
            "Executing task",
            extra={
                "plugin": self.name,
                "task_id": task_id,
                "params": params
            }
        )
        
        try:
            result = self._execute(task_id, params)
            
            logger.info(
                "Task completed successfully",
                extra={
                    "plugin": self.name,
                    "task_id": task_id,
                    "duration": result.get("duration")
                }
            )
            
            return result
        except Exception as e:
            logger.error(
                "Task execution failed",
                extra={
                    "plugin": self.name,
                    "task_id": task_id,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
```text

### 2. Log at Appropriate Levels

Sử dụng đúng log levels:

```python
class MyPlugin(Plugin):
    def process(self, data: Any) -> Any:
        """Process data with appropriate logging."""
        # DEBUG: Detailed information for debugging
        logger.debug(f"Processing data: {data}")
        
        # INFO: General informational messages
        logger.info(f"Started processing {len(data)} items")
        
        # WARNING: Warning messages for recoverable issues
        if len(data) > 1000:
            logger.warning(f"Large dataset detected: {len(data)} items")
        
        try:
            result = self._process(data)
            logger.info("Processing completed successfully")
            return result
        except Exception as e:
            # ERROR: Error messages for failures
            logger.error(f"Processing failed: {e}", exc_info=True)
            raise
```text

### 3. Never Log Sensitive Information

Không bao giờ log passwords, tokens, hoặc sensitive data:

```python
class SecurePlugin(Plugin):
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with secure logging."""
        self.config = config or {}
        
        # BAD: Logs sensitive data
        # logger.info(f"Config: {self.config}")
        
        # GOOD: Masks sensitive data
        safe_config = {
            k: "***" if k in ["password", "token", "api_key"] else v
            for k, v in self.config.items()
        }
        logger.info(f"Initialized with config: {safe_config}")
        
        self.api_key = self.config.get("api_key")
        
        # BAD: Logs API key
        # logger.info(f"Using API key: {self.api_key}")
        
        # GOOD: Masks API key
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if self.api_key else None
        logger.info(f"Using API key: {masked_key}")
```text

## Testing

### 1. Write Unit Tests

Test mỗi method độc lập:

```python
import pytest
from my_plugins import MyPlugin

class TestMyPlugin:
    """Unit tests for MyPlugin."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.plugin = MyPlugin()
        self.plugin.initialize({"api_key": "test-key"})
    
    def teardown_method(self):
        """Cleanup after tests."""
        self.plugin.shutdown()
    
    def test_initialization(self):
        """Test plugin initialization."""
        assert self.plugin.name == "my-plugin"
        assert self.plugin.version == "1.0.0"
        assert self.plugin.api_key == "test-key"
    
    def test_process_valid_data(self):
        """Test processing valid data."""
        data = {"id": 1, "name": "test"}
        result = self.plugin.process(data)
        assert result is not None
        assert "processed" in result
    
    def test_process_invalid_data(self):
        """Test processing invalid data."""
        with pytest.raises(PluginError):
            self.plugin.process({})  # Missing required fields
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(PluginError) as exc_info:
            self.plugin.process({"id": -1, "name": "test"})
        assert "must be positive" in str(exc_info.value)
```text

### 2. Write Integration Tests

Test plugin integration với external services:

```python
import pytest
from my_plugins import DatabasePlugin

@pytest.mark.integration
class TestDatabasePluginIntegration:
    """Integration tests for DatabasePlugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        plugin = DatabasePlugin()
        plugin.initialize({
            "host": "localhost",
            "database": "test_db",
            "username": "test_user",
            "password": "test_pass"
        })
        yield plugin
        plugin.shutdown()
    
    def test_query_execution(self, plugin):
        """Test actual database query."""
        results = plugin.query("SELECT 1 as value")
        assert len(results) == 1
        assert results[0]["value"] == 1
    
    def test_transaction(self, plugin):
        """Test database transaction."""
        plugin.execute("CREATE TABLE test (id INT, name TEXT)")
        plugin.transaction([
            ("INSERT INTO test VALUES (%s, %s)", (1, "Alice")),
            ("INSERT INTO test VALUES (%s, %s)", (2, "Bob"))
        ])
        results = plugin.query("SELECT * FROM test")
        assert len(results) == 2
```text

### 3. Mock External Dependencies

Sử dụng mocks cho external services trong unit tests:

```python
from unittest.mock import Mock, patch
import pytest

class TestWeatherPlugin:
    """Unit tests with mocking."""
    
    @patch('requests.Session')
    def test_get_weather(self, mock_session):
        """Test weather fetching with mocked HTTP client."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {
            "temp": 25,
            "condition": "Sunny"
        }
        mock_session.return_value.get.return_value = mock_response
        
        # Test
        plugin = WeatherPlugin()
        plugin.initialize({"api_key": "test-key"})
        weather = plugin.get_weather("Hanoi")
        
        # Assertions
        assert weather["temp"] == 25
        assert weather["condition"] == "Sunny"
        mock_session.return_value.get.assert_called_once()
```text

### 4. Test Error Scenarios

Test tất cả error paths:

```python
class TestErrorScenarios:
    """Test error handling."""
    
    def test_missing_config(self):
        """Test initialization with missing config."""
        plugin = MyPlugin()
        with pytest.raises(PluginError) as exc_info:
            plugin.initialize({})
        assert "Missing required config" in str(exc_info.value)
    
    def test_invalid_config_type(self):
        """Test initialization with invalid config type."""
        plugin = MyPlugin()
        with pytest.raises(PluginError) as exc_info:
            plugin.initialize({"api_key": 123})  # Should be string
        assert "must be a string" in str(exc_info.value)
    
    def test_connection_failure(self):
        """Test handling of connection failures."""
        plugin = MyPlugin()
        plugin.initialize({"api_key": "test-key"})
        
        with patch.object(plugin, '_connect', side_effect=ConnectionError):
            with pytest.raises(PluginError) as exc_info:
                plugin.execute_task("test")
            assert "Connection failed" in str(exc_info.value)
```text

## Configuration Management

### 1. Use Environment Variables

Support environment variables cho sensitive config:

```python
import os

class ConfigurablePlugin(Plugin):
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with environment variable support."""
        self.config = config or {}
        
        # Prefer environment variables for sensitive data
        self.api_key = (
            os.getenv("PLUGIN_API_KEY") or
            self.config.get("api_key")
        )
        
        self.endpoint = (
            os.getenv("PLUGIN_ENDPOINT") or
            self.config.get("endpoint", "https://api.example.com")
        )
        
        if not self.api_key:
            raise PluginError(
                "API key not found. Set PLUGIN_API_KEY environment "
                "variable or provide in config."
            )
```text

### 2. Provide Sensible Defaults

Cung cấp default values hợp lý:

```python
class DefaultsPlugin(Plugin):
    # Class-level defaults
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BATCH_SIZE = 100
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with defaults."""
        self.config = config or {}
        
        # Use defaults for optional settings
        self.timeout = self.config.get("timeout", self.DEFAULT_TIMEOUT)
        self.max_retries = self.config.get("max_retries", self.DEFAULT_MAX_RETRIES)
        self.batch_size = self.config.get("batch_size", self.DEFAULT_BATCH_SIZE)
        
        # Required settings have no defaults
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise PluginError("Missing required config: api_key")
```text

### 3. Validate Configuration Schema

Validate configuration structure:

```python
from typing import Any, Dict
from jsonschema import validate, ValidationError

class ValidatedPlugin(Plugin):
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "api_key": {"type": "string", "minLength": 1},
            "endpoint": {"type": "string", "format": "uri"},
            "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
            "max_retries": {"type": "integer", "minimum": 0, "maximum": 10}
        },
        "required": ["api_key"]
    }
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with schema validation."""
        self.config = config or {}
        
        try:
            validate(instance=self.config, schema=self.CONFIG_SCHEMA)
        except ValidationError as e:
            raise PluginError(f"Invalid configuration: {e.message}")
        
        # Configuration is valid, proceed with initialization
        self.api_key = self.config["api_key"]
        self.endpoint = self.config.get("endpoint", "https://api.example.com")
```text

## Resource Management

### 1. Cleanup Resources Properly

Luôn cleanup resources trong `shutdown()`:

```python
class ResourcePlugin(Plugin):
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize resources."""
        self.config = config or {}
        
        # Open resources
        self.connection = self._create_connection()
        self.file_handle = open("data.txt", "w")
        self.temp_files = []
    
    def shutdown(self) -> None:
        """Cleanup all resources."""
        # Close connection
        if hasattr(self, 'connection') and self.connection:
            try:
                self.connection.close()
                logger.info("Connection closed")
            except Exception as e:
                logger.error(f"Failed to close connection: {e}")
        
        # Close file handle
        if hasattr(self, 'file_handle') and self.file_handle:
            try:
                self.file_handle.close()
                logger.info("File handle closed")
            except Exception as e:
                logger.error(f"Failed to close file: {e}")
        
        # Delete temporary files
        if hasattr(self, 'temp_files'):
            for temp_file in self.temp_files:
                try:
                    os.remove(temp_file)
                    logger.info(f"Deleted temp file: {temp_file}")
                except Exception as e:
                    logger.error(f"Failed to delete {temp_file}: {e}")
```text

### 2. Use Context Managers

Sử dụng context managers cho resource management:

```python
from contextlib import contextmanager

class ContextPlugin(Plugin):
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
            logger.info("Transaction committed")
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            self._release_connection(conn)
    
    def execute_operations(self, operations: List[tuple]) -> None:
        """Execute operations in transaction."""
        with self.transaction() as conn:
            cursor = conn.cursor()
            for sql, params in operations:
                cursor.execute(sql, params)
```text

### 3. Implement Connection Pooling

Sử dụng connection pooling cho efficiency:

```python
from queue import Queue, Empty
import threading

class PooledPlugin(Plugin):
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with connection pool."""
        self.config = config or {}
        self.pool_size = self.config.get("pool_size", 5)
        
        # Create connection pool
        self.pool = Queue(maxsize=self.pool_size)
        self.lock = threading.Lock()
        
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self.pool.put(conn)
    
    def get_connection(self, timeout: float = 5.0):
        """Get connection from pool."""
        try:
            return self.pool.get(timeout=timeout)
        except Empty:
            raise PluginError("No available connections in pool")
    
    def release_connection(self, conn) -> None:
        """Return connection to pool."""
        try:
            self.pool.put(conn, block=False)
        except:
            logger.warning("Failed to return connection to pool")
    
    def shutdown(self) -> None:
        """Close all connections in pool."""
        while not self.pool.empty():
            try:
                conn = self.pool.get(block=False)
                conn.close()
            except:
                pass
```text

## Performance Optimization

### 1. Cache Expensive Operations

Cache results của expensive operations:

```python
from functools import lru_cache
import hashlib
import json

class CachedPlugin(Plugin):
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize with cache."""
        self.config = config or {}
        self.cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 3600)
    
    def _cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def fetch_data(self, url: str, params: Dict = None) -> Dict:
        """Fetch data with caching."""
        cache_key = self._cache_key(url, params)
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for {url}")
                return cached_data
        
        # Fetch and cache
        logger.debug(f"Cache miss for {url}")
        data = self._fetch(url, params)
        self.cache[cache_key] = (data, time.time())
        return data
```text

### 2. Batch Operations

Batch multiple operations together:

```python
class BatchPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.batch_size = 100
        self.pending_operations = []
    
    def add_operation(self, operation: Dict) -> None:
        """Add operation to batch."""
        self.pending_operations.append(operation)
        
        # Execute batch when size reached
        if len(self.pending_operations) >= self.batch_size:
            self.flush()
    
    def flush(self) -> None:
        """Execute all pending operations."""
        if not self.pending_operations:
            return
        
        logger.info(f"Executing batch of {len(self.pending_operations)} operations")
        
        try:
            self._execute_batch(self.pending_operations)
            self.pending_operations.clear()
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise
    
    def shutdown(self) -> None:
        """Flush pending operations before shutdown."""
        self.flush()
```text

### 3. Use Async for I/O Operations

Sử dụng async cho I/O-bound operations:

```python
import asyncio
import aiohttp

class AsyncPlugin(Plugin):
    async def fetch_multiple(self, urls: List[str]) -> List[Dict]:
        """Fetch multiple URLs concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_one(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
    
    async def _fetch_one(self, session, url: str) -> Dict:
        """Fetch single URL."""
        async with session.get(url) as response:
            return await response.json()
```text

## Documentation

### 1. Write Comprehensive Docstrings

Document tất cả public methods:

```python
class WellDocumentedPlugin(Plugin):
    """Plugin for doing awesome things.
    
    This plugin provides functionality to interact with external services
    and process data efficiently.
    
    Configuration:
        api_key (str): API key for authentication (required)
        endpoint (str): API endpoint URL (default: https://api.example.com)
        timeout (int): Request timeout in seconds (default: 30)
        max_retries (int): Maximum retry attempts (default: 3)
    
    Example:
        >>> plugin = WellDocumentedPlugin()
        >>> plugin.initialize({"api_key": "your-key"})
        >>> result = plugin.process_data({"id": 1, "name": "test"})
        >>> print(result)
        {'status': 'success', 'data': {...}}
    
    Attributes:
        name: Plugin name
        version: Plugin version
        api_key: Configured API key
        endpoint: Configured endpoint URL
    """
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data and return results.
        
        This method validates the input data, sends it to the external API,
        and returns the processed results.
        
        Args:
            data: Input data dictionary with required fields:
                - id (int): Unique identifier
                - name (str): Item name
                - type (str): Item type (optional)
        
        Returns:
            Dictionary containing:
                - status (str): Processing status ('success' or 'error')
                - data (dict): Processed data
                - message (str): Status message
        
        Raises:
            PluginError: If data validation fails or API request fails
            
        Example:
            >>> result = plugin.process_data({
            ...     "id": 123,
            ...     "name": "example",
            ...     "type": "test"
            ... })
            >>> print(result['status'])
            'success'
        """
        pass
```text

### 2. Provide Usage Examples

Include practical examples trong documentation:

```python
"""
Example Usage
=============

Basic Usage:
-----------
>>> from my_plugins import MyPlugin
>>> plugin = MyPlugin()
>>> plugin.initialize({"api_key": "your-key"})
>>> result = plugin.execute_task("task-1")

Advanced Usage:
--------------
>>> # With custom configuration
>>> plugin = MyPlugin()
>>> plugin.initialize({
...     "api_key": "your-key",
...     "endpoint": "https://custom.api.com",
...     "timeout": 60,
...     "max_retries": 5
... })
>>> 
>>> # Process batch of items
>>> items = [{"id": 1}, {"id": 2}, {"id": 3}]
>>> results = plugin.process_batch(items)
>>> 
>>> # Handle errors
>>> try:
...     result = plugin.execute_task("invalid-task")
... except PluginError as e:
...     print(f"Error: {e}")

Integration with Agents:
-----------------------
>>> from agentic_sdlc import create_agent
>>> from agentic_sdlc.plugins import get_plugin_registry
>>> 
>>> # Register plugin
>>> registry = get_plugin_registry()
>>> registry.register(MyPlugin())
>>> 
>>> # Use in agent
>>> agent = create_agent(name="my-agent", role="Developer")
>>> plugin = registry.get("my-plugin")
>>> result = plugin.execute_task("agent-task")
"""
```

## Tài Liệu Liên Quan

- [Plugin Overview](overview.md)
- [Creating Plugins](creating-plugins.md)
- [Plugin Examples](plugin-examples.md)

## Tóm Tắt

Best practices cho plugin development:

1. **Error Handling**: Validate inputs, handle failures gracefully, implement retry logic
2. **Logging**: Use structured logging, appropriate levels, never log sensitive data
3. **Testing**: Write unit tests, integration tests, mock external dependencies
4. **Configuration**: Support environment variables, provide defaults, validate schema
5. **Resources**: Cleanup properly, use context managers, implement pooling
6. **Performance**: Cache expensive operations, batch requests, use async for I/O
7. **Documentation**: Write comprehensive docstrings, provide examples

Follow các practices này để tạo plugins chất lượng cao và production-ready!
