# Ví Dụ Plugins Phức Tạp

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp các ví dụ plugins phức tạp và thực tế cho Agentic SDLC. Mỗi ví dụ minh họa các patterns và techniques khác nhau để xây dựng plugins production-ready.

## Example 1: Database Plugin

Plugin tích hợp với PostgreSQL database.

```python
"""
PostgreSQL Database Plugin
Provides database operations for agents.
"""

from agentic_sdlc.plugins import Plugin, PluginError
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


class PostgreSQLPlugin(Plugin):
    """Plugin for PostgreSQL database operations.
    
    Configuration:
        host (str): Database host
        port (int): Database port (default: 5432)
        database (str): Database name
        username (str): Database username
        password (str): Database password
        pool_size (int): Connection pool size (default: 5)
    
    Example:
        >>> plugin = PostgreSQLPlugin()
        >>> plugin.initialize({
        ...     "host": "localhost",
        ...     "database": "mydb",
        ...     "username": "user",
        ...     "password": "pass"
        ... })
        >>> results = plugin.query("SELECT * FROM users")
    """
    
    @property
    def name(self) -> str:
        return "postgresql-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize database connection."""
        self.config = config or {}
        
        # Validate configuration
        self._validate_config()
        
        # Connection parameters
        self.host = self.config["host"]
        self.port = self.config.get("port", 5432)
        self.database = self.config["database"]
        self.username = self.config["username"]
        self.password = self.config["password"]
        self.pool_size = self.config.get("pool_size", 5)
        
        # Create connection pool
        self.pool = self._create_pool()
        
        logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}/{self.database}")
    
    def shutdown(self) -> None:
        """Close all database connections."""
        if hasattr(self, 'pool'):
            for conn in self.pool:
                conn.close()
            logger.info("Closed all database connections")
    
    def query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
            
        Raises:
            PluginError: If query fails
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except psycopg2.Error as e:
            raise PluginError(f"Query failed: {e}")
        finally:
            self._release_connection(conn)
    
    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE query.
        
        Args:
            sql: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
            
        Raises:
            PluginError: If execution fails
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.rowcount
        except psycopg2.Error as e:
            conn.rollback()
            raise PluginError(f"Execution failed: {e}")
        finally:
            self._release_connection(conn)
    
    def transaction(self, operations: List[tuple]) -> None:
        """Execute multiple operations in a transaction.
        
        Args:
            operations: List of (sql, params) tuples
            
        Raises:
            PluginError: If transaction fails
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                for sql, params in operations:
                    cursor.execute(sql, params)
                conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            raise PluginError(f"Transaction failed: {e}")
        finally:
            self._release_connection(conn)
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        required = ["host", "database", "username", "password"]
        for field in required:
            if field not in self.config:
                raise PluginError(f"Missing required config: {field}")
    
    def _create_pool(self) -> List:
        """Create connection pool."""
        pool = []
        for _ in range(self.pool_size):
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            pool.append(conn)
        return pool
    
    def _get_connection(self):
        """Get connection from pool."""
        if not self.pool:
            raise PluginError("No available connections")
        return self.pool.pop(0)
    
    def _release_connection(self, conn) -> None:
        """Return connection to pool."""
        self.pool.append(conn)
```text

### Usage Example

```python
from agentic_sdlc.plugins import get_plugin_registry

# Register plugin
registry = get_plugin_registry()
db = PostgreSQLPlugin()
registry.register(db)

# Initialize
db.initialize({
    "host": "localhost",
    "database": "myapp",
    "username": "admin",
    "password": "secret"
})

# Query data
users = db.query("SELECT * FROM users WHERE active = %s", (True,))
for user in users:
    print(f"User: {user['name']}, Email: {user['email']}")

# Insert data
db.execute(
    "INSERT INTO users (name, email) VALUES (%s, %s)",
    ("John Doe", "john@example.com")
)

# Transaction
db.transaction([
    ("UPDATE accounts SET balance = balance - 100 WHERE id = %s", (1,)),
    ("UPDATE accounts SET balance = balance + 100 WHERE id = %s", (2,))
])
```text

## Example 2: Slack Integration Plugin

Plugin tích hợp với Slack API.

```python
"""
Slack Integration Plugin
Send notifications and messages to Slack.
"""

from agentic_sdlc.plugins import Plugin, PluginError
from typing import Dict, Any, Optional, List
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)


class SlackPlugin(Plugin):
    """Plugin for Slack integration.
    
    Configuration:
        slack_token (str): Slack bot token
        default_channel (str): Default channel for messages
        username (str): Bot username (optional)
        icon_emoji (str): Bot icon emoji (optional)
    
    Example:
        >>> plugin = SlackPlugin()
        >>> plugin.initialize({
        ...     "slack_token": "xoxb-your-token",
        ...     "default_channel": "#general"
        ... })
        >>> plugin.send_message("Hello from Agentic SDLC!")
    """
    
    @property
    def name(self) -> str:
        return "slack-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Slack client."""
        self.config = config or {}
        
        # Validate configuration
        self._validate_config()
        
        # Load settings
        self.token = self.config["slack_token"]
        self.default_channel = self.config.get("default_channel", "#general")
        self.username = self.config.get("username", "Agentic SDLC Bot")
        self.icon_emoji = self.config.get("icon_emoji", ":robot_face:")
        
        # Initialize Slack client
        self.client = WebClient(token=self.token)
        
        # Test connection
        self._test_connection()
        
        logger.info(f"Connected to Slack workspace")
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        logger.info("Slack plugin shutdown")
    
    def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        attachments: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send message to Slack channel.
        
        Args:
            text: Message text
            channel: Channel name (uses default if not specified)
            attachments: Message attachments
            
        Returns:
            Slack API response
            
        Raises:
            PluginError: If message sending fails
        """
        channel = channel or self.default_channel
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                username=self.username,
                icon_emoji=self.icon_emoji,
                attachments=attachments
            )
            return response.data
        except SlackApiError as e:
            raise PluginError(f"Failed to send message: {e.response['error']}")
    
    def send_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send formatted notification.
        
        Args:
            title: Notification title
            message: Notification message
            level: Notification level (info, warning, error, success)
            channel: Channel name
            
        Returns:
            Slack API response
        """
        colors = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "error": "#ff0000",
            "success": "#00ff00"
        }
        
        attachments = [{
            "color": colors.get(level, "#36a64f"),
            "title": title,
            "text": message,
            "footer": "Agentic SDLC",
            "ts": int(time.time())
        }]
        
        return self.send_message(
            text=f"*{title}*",
            channel=channel,
            attachments=attachments
        )
    
    def send_workflow_status(
        self,
        workflow_name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send workflow status update.
        
        Args:
            workflow_name: Name of workflow
            status: Workflow status (running, completed, failed)
            details: Additional details
            channel: Channel name
            
        Returns:
            Slack API response
        """
        status_emoji = {
            "running": ":hourglass:",
            "completed": ":white_check_mark:",
            "failed": ":x:"
        }
        
        emoji = status_emoji.get(status, ":question:")
        text = f"{emoji} Workflow: *{workflow_name}* - Status: *{status}*"
        
        attachments = []
        if details:
            fields = [
                {"title": key, "value": str(value), "short": True}
                for key, value in details.items()
            ]
            attachments.append({
                "fields": fields,
                "color": "#36a64f" if status == "completed" else "#ff0000"
            })
        
        return self.send_message(
            text=text,
            channel=channel,
            attachments=attachments
        )
    
    def upload_file(
        self,
        file_path: str,
        channel: Optional[str] = None,
        title: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload file to Slack.
        
        Args:
            file_path: Path to file
            channel: Channel name
            title: File title
            comment: File comment
            
        Returns:
            Slack API response
            
        Raises:
            PluginError: If upload fails
        """
        channel = channel or self.default_channel
        
        try:
            response = self.client.files_upload(
                channels=channel,
                file=file_path,
                title=title,
                initial_comment=comment
            )
            return response.data
        except SlackApiError as e:
            raise PluginError(f"Failed to upload file: {e.response['error']}")
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if "slack_token" not in self.config:
            raise PluginError("Missing required config: slack_token")
    
    def _test_connection(self) -> None:
        """Test Slack connection."""
        try:
            response = self.client.auth_test()
            logger.info(f"Connected to workspace: {response['team']}")
        except SlackApiError as e:
            raise PluginError(f"Failed to connect to Slack: {e.response['error']}")
```text

### Usage Example

```python
# Register plugin
slack = SlackPlugin()
registry.register(slack)

# Initialize
slack.initialize({
    "slack_token": "xoxb-your-token",
    "default_channel": "#dev-notifications"
})

# Send simple message
slack.send_message("Deployment started!")

# Send notification
slack.send_notification(
    title="Build Completed",
    message="Build #123 completed successfully",
    level="success"
)

# Send workflow status
slack.send_workflow_status(
    workflow_name="CI/CD Pipeline",
    status="completed",
    details={
        "Duration": "5m 32s",
        "Tests Passed": "142/142",
        "Coverage": "94%"
    }
)

# Upload log file
slack.upload_file(
    file_path="build.log",
    title="Build Log",
    comment="Build log for deployment #123"
)
```text

## Example 3: GitHub Integration Plugin

Plugin tích hợp với GitHub API.

```python
"""
GitHub Integration Plugin
Interact with GitHub repositories.
"""

from agentic_sdlc.plugins import Plugin, PluginError
from typing import Dict, Any, Optional, List
from github import Github, GithubException
import logging

logger = logging.getLogger(__name__)


class GitHubPlugin(Plugin):
    """Plugin for GitHub integration.
    
    Configuration:
        github_token (str): GitHub personal access token
        default_repo (str): Default repository (owner/repo)
    
    Example:
        >>> plugin = GitHubPlugin()
        >>> plugin.initialize({
        ...     "github_token": "ghp_your_token",
        ...     "default_repo": "owner/repo"
        ... })
        >>> issues = plugin.list_issues()
    """
    
    @property
    def name(self) -> str:
        return "github-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize GitHub client."""
        self.config = config or {}
        
        # Validate configuration
        self._validate_config()
        
        # Load settings
        self.token = self.config["github_token"]
        self.default_repo = self.config.get("default_repo")
        
        # Initialize GitHub client
        self.client = Github(self.token)
        
        # Test connection
        self._test_connection()
        
        logger.info("Connected to GitHub")
    
    def shutdown(self) -> None:
        """Cleanup resources."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("GitHub client closed")
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create GitHub issue.
        
        Args:
            title: Issue title
            body: Issue body
            labels: Issue labels
            assignees: Issue assignees
            repo: Repository (owner/repo)
            
        Returns:
            Issue data
            
        Raises:
            PluginError: If creation fails
        """
        repo_name = repo or self.default_repo
        if not repo_name:
            raise PluginError("No repository specified")
        
        try:
            repository = self.client.get_repo(repo_name)
            issue = repository.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            return {
                "number": issue.number,
                "url": issue.html_url,
                "state": issue.state
            }
        except GithubException as e:
            raise PluginError(f"Failed to create issue: {e}")
    
    def list_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        repo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List GitHub issues.
        
        Args:
            state: Issue state (open, closed, all)
            labels: Filter by labels
            repo: Repository (owner/repo)
            
        Returns:
            List of issues
        """
        repo_name = repo or self.default_repo
        if not repo_name:
            raise PluginError("No repository specified")
        
        try:
            repository = self.client.get_repo(repo_name)
            issues = repository.get_issues(state=state, labels=labels or [])
            
            return [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "url": issue.html_url,
                    "labels": [label.name for label in issue.labels]
                }
                for issue in issues
            ]
        except GithubException as e:
            raise PluginError(f"Failed to list issues: {e}")
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create pull request.
        
        Args:
            title: PR title
            body: PR body
            head: Head branch
            base: Base branch
            repo: Repository (owner/repo)
            
        Returns:
            Pull request data
        """
        repo_name = repo or self.default_repo
        if not repo_name:
            raise PluginError("No repository specified")
        
        try:
            repository = self.client.get_repo(repo_name)
            pr = repository.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            return {
                "number": pr.number,
                "url": pr.html_url,
                "state": pr.state
            }
        except GithubException as e:
            raise PluginError(f"Failed to create PR: {e}")
    
    def add_comment(
        self,
        issue_number: int,
        comment: str,
        repo: Optional[str] = None
    ) -> None:
        """Add comment to issue or PR.
        
        Args:
            issue_number: Issue/PR number
            comment: Comment text
            repo: Repository (owner/repo)
        """
        repo_name = repo or self.default_repo
        if not repo_name:
            raise PluginError("No repository specified")
        
        try:
            repository = self.client.get_repo(repo_name)
            issue = repository.get_issue(issue_number)
            issue.create_comment(comment)
        except GithubException as e:
            raise PluginError(f"Failed to add comment: {e}")
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if "github_token" not in self.config:
            raise PluginError("Missing required config: github_token")
    
    def _test_connection(self) -> None:
        """Test GitHub connection."""
        try:
            user = self.client.get_user()
            logger.info(f"Authenticated as: {user.login}")
        except GithubException as e:
            raise PluginError(f"Failed to connect to GitHub: {e}")
```text

### Usage Example

```python
# Register plugin
github = GitHubPlugin()
registry.register(github)

# Initialize
github.initialize({
    "github_token": "ghp_your_token",
    "default_repo": "myorg/myrepo"
})

# Create issue
issue = github.create_issue(
    title="Bug: Login not working",
    body="Users cannot login after latest deployment",
    labels=["bug", "high-priority"],
    assignees=["developer1"]
)
print(f"Created issue #{issue['number']}: {issue['url']}")

# List open issues
issues = github.list_issues(state="open", labels=["bug"])
for issue in issues:
    print(f"#{issue['number']}: {issue['title']}")

# Create pull request
pr = github.create_pull_request(
    title="Fix login bug",
    body="This PR fixes the login issue",
    head="fix/login-bug",
    base="main"
)
print(f"Created PR #{pr['number']}: {pr['url']}")

# Add comment
github.add_comment(
    issue_number=123,
    comment="This issue has been fixed in PR #456"
)
```text

## Example 4: Caching Plugin

Plugin cung cấp caching capabilities với Redis.

```python
"""
Redis Caching Plugin
Provides caching functionality using Redis.
"""

from agentic_sdlc.plugins import Plugin, PluginError
from typing import Dict, Any, Optional
import redis
import json
import pickle
import logging

logger = logging.getLogger(__name__)


class RedisCachePlugin(Plugin):
    """Plugin for Redis caching.
    
    Configuration:
        host (str): Redis host
        port (int): Redis port (default: 6379)
        db (int): Redis database number (default: 0)
        password (str): Redis password (optional)
        default_ttl (int): Default TTL in seconds (default: 3600)
    
    Example:
        >>> plugin = RedisCachePlugin()
        >>> plugin.initialize({"host": "localhost"})
        >>> plugin.set("key", "value", ttl=300)
        >>> value = plugin.get("key")
    """
    
    @property
    def name(self) -> str:
        return "redis-cache-plugin"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Redis connection."""
        self.config = config or {}
        
        # Load settings
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 6379)
        self.db = self.config.get("db", 0)
        self.password = self.config.get("password")
        self.default_ttl = self.config.get("default_ttl", 3600)
        
        # Create Redis client
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=False
        )
        
        # Test connection
        self._test_connection()
        
        logger.info(f"Connected to Redis at {self.host}:{self.port}")
    
    def shutdown(self) -> None:
        """Close Redis connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("Redis connection closed")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            serialized = pickle.dumps(value)
            ttl = ttl or self.default_ttl
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted
        """
        try:
            return self.client.delete(key) > 0
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists
        """
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all keys in current database.
        
        Returns:
            True if successful
        """
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def _test_connection(self) -> None:
        """Test Redis connection."""
        try:
            self.client.ping()
        except Exception as e:
            raise PluginError(f"Failed to connect to Redis: {e}")
```text

### Usage Example

```python
# Register plugin
cache = RedisCachePlugin()
registry.register(cache)

# Initialize
cache.initialize({
    "host": "localhost",
    "port": 6379,
    "default_ttl": 3600
})

# Cache data
cache.set("user:123", {"name": "John", "email": "john@example.com"})

# Retrieve data
user = cache.get("user:123")
print(user)  # {'name': 'John', 'email': 'john@example.com'}

# Check existence
if cache.exists("user:123"):
    print("User found in cache")

# Delete key
cache.delete("user:123")

# Clear all cache
cache.clear()
```

## Tài Liệu Liên Quan

- [Plugin Overview](overview.md)
- [Creating Plugins](creating-plugins.md)
- [Best Practices](best-practices.md)

## Tóm Tắt

Các ví dụ plugins này minh họa:

- **Database Plugin**: Connection pooling, transactions, error handling
- **Slack Plugin**: API integration, formatted messages, file uploads
- **GitHub Plugin**: Repository operations, issue/PR management
- **Cache Plugin**: Redis integration, serialization, TTL management

Sử dụng các patterns này làm template cho plugins của bạn!
