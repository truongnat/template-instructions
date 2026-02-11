# Bảo Mật (Security)

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


## Giới Thiệu

Tài liệu này cung cấp hướng dẫn toàn diện về security best practices cho Agentic SDLC, bao gồm API key management, data encryption, access control, và secure deployment.

## Mục Tiêu Học Tập

Sau khi đọc tài liệu này, bạn sẽ có thể:
- Quản lý API keys và credentials một cách an toàn
- Implement encryption cho sensitive data
- Thiết lập access control và authentication
- Secure communication giữa components
- Audit và monitor security events

## API Key Management

### 1. Environment Variables

Store API keys trong environment variables, không hardcode:

```python
import os
from agentic_sdlc.orchestration.model_client import ModelConfig

# ❌ BAD: Hardcoded API key
config = ModelConfig(
    provider="openai",
    api_key="sk-1234567890abcdef"  # NEVER DO THIS!
)

# ✅ GOOD: Load từ environment variable
config = ModelConfig(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Validate API key exists
if not config.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
```text

### 2. Secrets Management

Sử dụng secrets management tools:

```python
from agentic_sdlc.core.secrets import SecretsManager

class SecretsManager:
    """Manage secrets securely."""
    
    def __init__(self, backend="env"):
        """
        Initialize secrets manager.
        
        Backends:
        - env: Environment variables
        - vault: HashiCorp Vault
        - aws: AWS Secrets Manager
        - azure: Azure Key Vault
        """
        self.backend = backend
        self._initialize_backend()
    
    def get_secret(self, key):
        """Get secret value."""
        if self.backend == "env":
            return os.getenv(key)
        
        elif self.backend == "vault":
            return self._get_from_vault(key)
        
        elif self.backend == "aws":
            return self._get_from_aws(key)
        
        elif self.backend == "azure":
            return self._get_from_azure(key)
    
    def set_secret(self, key, value):
        """Set secret value."""
        if self.backend == "vault":
            self._set_in_vault(key, value)
        elif self.backend == "aws":
            self._set_in_aws(key, value)
        elif self.backend == "azure":
            self._set_in_azure(key, value)
        else:
            raise ValueError("Cannot set secrets in env backend")
    
    def _get_from_vault(self, key):
        """Get secret từ HashiCorp Vault."""
        import hvac
        client = hvac.Client(url=os.getenv("VAULT_ADDR"))
        client.token = os.getenv("VAULT_TOKEN")
        
        secret = client.secrets.kv.v2.read_secret_version(
            path=key,
            mount_point="secret"
        )
        return secret["data"]["data"]["value"]

# Sử dụng secrets manager
secrets = SecretsManager(backend="vault")

# Get API keys
openai_key = secrets.get_secret("openai_api_key")
anthropic_key = secrets.get_secret("anthropic_api_key")

# Create model client với secure keys
config = ModelConfig(
    provider="openai",
    api_key=openai_key
)
```text

### 3. Key Rotation

Implement automatic key rotation:

```python
from agentic_sdlc.core.security import KeyRotationManager
import time

class KeyRotationManager:
    """Manage API key rotation."""
    
    def __init__(self, secrets_manager, rotation_interval=86400):
        """
        Initialize key rotation manager.
        
        Args:
            secrets_manager: SecretsManager instance
            rotation_interval: Rotation interval in seconds (default: 24 hours)
        """
        self.secrets = secrets_manager
        self.rotation_interval = rotation_interval
        self.last_rotation = {}
    
    def get_key(self, key_name):
        """Get key và check if rotation needed."""
        # Check if rotation needed
        if self._should_rotate(key_name):
            self._rotate_key(key_name)
        
        return self.secrets.get_secret(key_name)
    
    def _should_rotate(self, key_name):
        """Check if key should be rotated."""
        if key_name not in self.last_rotation:
            return False
        
        elapsed = time.time() - self.last_rotation[key_name]
        return elapsed >= self.rotation_interval
    
    def _rotate_key(self, key_name):
        """Rotate API key."""
        # Generate new key (implementation depends on provider)
        new_key = self._generate_new_key(key_name)
        
        # Update in secrets manager
        self.secrets.set_secret(key_name, new_key)
        
        # Update rotation timestamp
        self.last_rotation[key_name] = time.time()
        
        print(f"Rotated key: {key_name}")

# Sử dụng key rotation
rotation_manager = KeyRotationManager(secrets, rotation_interval=86400)

# Get key với automatic rotation
api_key = rotation_manager.get_key("openai_api_key")
```text

## Data Encryption

### 1. Encryption at Rest

Encrypt sensitive data khi lưu trữ:

```python
from cryptography.fernet import Fernet
from agentic_sdlc.core.security import DataEncryption

class DataEncryption:
    """Encrypt/decrypt sensitive data."""
    
    def __init__(self, encryption_key=None):
        """
        Initialize encryption.
        
        Args:
            encryption_key: Base64-encoded encryption key.
                          If None, generates new key.
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> bytes:
        """Encrypt string data."""
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted_data).decode()
    
    def encrypt_dict(self, data: dict) -> bytes:
        """Encrypt dictionary."""
        import json
        json_data = json.dumps(data)
        return self.encrypt(json_data)
    
    def decrypt_dict(self, encrypted_data: bytes) -> dict:
        """Decrypt to dictionary."""
        import json
        json_data = self.decrypt(encrypted_data)
        return json.loads(json_data)

# Sử dụng encryption
# Generate và save encryption key
encryption_key = Fernet.generate_key()
# Store key securely (e.g., in secrets manager)

# Encrypt sensitive data
encryptor = DataEncryption(encryption_key)

sensitive_data = {
    "api_key": "sk-1234567890",
    "database_password": "secret123",
    "user_token": "token_xyz"
}

encrypted = encryptor.encrypt_dict(sensitive_data)

# Save encrypted data
with open("encrypted_config.bin", "wb") as f:
    f.write(encrypted)

# Decrypt khi cần
with open("encrypted_config.bin", "rb") as f:
    encrypted = f.read()

decrypted = encryptor.decrypt_dict(encrypted)
```text

### 2. Encryption in Transit

Encrypt data khi truyền qua network:

```python
from agentic_sdlc.infrastructure.distributed import SecureChannel
import ssl

class SecureChannel:
    """Secure communication channel với TLS."""
    
    def __init__(self, cert_file, key_file):
        """
        Initialize secure channel.
        
        Args:
            cert_file: Path to SSL certificate
            key_file: Path to SSL private key
        """
        self.cert_file = cert_file
        self.key_file = key_file
        self.context = self._create_ssl_context()
    
    def _create_ssl_context(self):
        """Create SSL context."""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(self.cert_file, self.key_file)
        
        # Enforce TLS 1.2+
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        return context
    
    def send_secure(self, host, port, data):
        """Send data securely."""
        import socket
        
        with socket.create_connection((host, port)) as sock:
            with self.context.wrap_socket(sock, server_hostname=host) as ssock:
                ssock.sendall(data.encode())
                response = ssock.recv(4096)
                return response.decode()

# Sử dụng secure channel
channel = SecureChannel(
    cert_file="/path/to/cert.pem",
    key_file="/path/to/key.pem"
)

# Send data securely
response = channel.send_secure("node1.example.com", 8443, "sensitive data")
```text

### 3. Secure Storage

Store sensitive data securely:

```python
from agentic_sdlc.core.security import SecureStorage

class SecureStorage:
    """Secure storage cho sensitive data."""
    
    def __init__(self, storage_path, encryption_key):
        self.storage_path = storage_path
        self.encryptor = DataEncryption(encryption_key)
    
    def save(self, key, value):
        """Save encrypted value."""
        encrypted = self.encryptor.encrypt(value)
        
        file_path = os.path.join(self.storage_path, f"{key}.enc")
        with open(file_path, "wb") as f:
            f.write(encrypted)
    
    def load(self, key):
        """Load và decrypt value."""
        file_path = os.path.join(self.storage_path, f"{key}.enc")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, "rb") as f:
            encrypted = f.read()
        
        return self.encryptor.decrypt(encrypted)
    
    def delete(self, key):
        """Delete stored value."""
        file_path = os.path.join(self.storage_path, f"{key}.enc")
        if os.path.exists(file_path):
            os.remove(file_path)

# Sử dụng secure storage
storage = SecureStorage(
    storage_path="/secure/storage",
    encryption_key=encryption_key
)

# Save sensitive data
storage.save("api_key", "sk-1234567890")
storage.save("db_password", "secret123")

# Load data
api_key = storage.load("api_key")
```text

## Access Control

### 1. Role-Based Access Control (RBAC)

Implement RBAC cho agents và users:

```python
from agentic_sdlc.core.security import AccessControl, Role, Permission
from enum import Enum

class Permission(Enum):
    """System permissions."""
    READ_CONFIG = "read_config"
    WRITE_CONFIG = "write_config"
    CREATE_AGENT = "create_agent"
    DELETE_AGENT = "delete_agent"
    EXECUTE_WORKFLOW = "execute_workflow"
    VIEW_LOGS = "view_logs"
    ADMIN = "admin"

class Role:
    """User role với permissions."""
    
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = set(permissions)
    
    def has_permission(self, permission):
        """Check if role has permission."""
        return (
            permission in self.permissions or
            Permission.ADMIN in self.permissions
        )

# Define roles
ROLES = {
    "admin": Role("admin", [Permission.ADMIN]),
    
    "developer": Role("developer", [
        Permission.READ_CONFIG,
        Permission.CREATE_AGENT,
        Permission.EXECUTE_WORKFLOW,
        Permission.VIEW_LOGS
    ]),
    
    "viewer": Role("viewer", [
        Permission.READ_CONFIG,
        Permission.VIEW_LOGS
    ])
}

class AccessControl:
    """Access control manager."""
    
    def __init__(self):
        self.user_roles = {}
    
    def assign_role(self, user_id, role_name):
        """Assign role to user."""
        if role_name not in ROLES:
            raise ValueError(f"Unknown role: {role_name}")
        
        self.user_roles[user_id] = ROLES[role_name]
    
    def check_permission(self, user_id, permission):
        """Check if user has permission."""
        if user_id not in self.user_roles:
            return False
        
        role = self.user_roles[user_id]
        return role.has_permission(permission)
    
    def require_permission(self, user_id, permission):
        """Require permission or raise exception."""
        if not self.check_permission(user_id, permission):
            raise PermissionError(
                f"User {user_id} does not have permission: {permission.value}"
            )

# Sử dụng access control
ac = AccessControl()

# Assign roles
ac.assign_role("user1", "admin")
ac.assign_role("user2", "developer")
ac.assign_role("user3", "viewer")

# Check permissions
def create_agent(user_id, agent_config):
    """Create agent với permission check."""
    ac.require_permission(user_id, Permission.CREATE_AGENT)
    
    # Create agent
    agent = create_agent(**agent_config)
    return agent

# User2 (developer) có thể create agent
agent = create_agent("user2", {"name": "dev-agent", "type": "DEVELOPER"})

# User3 (viewer) không thể create agent
try:
    agent = create_agent("user3", {"name": "dev-agent", "type": "DEVELOPER"})
except PermissionError as e:
    print(f"Access denied: {e}")
```text

### 2. Authentication

Implement authentication cho API access:

```python
from agentic_sdlc.core.security import AuthenticationManager
import jwt
import hashlib
from datetime import datetime, timedelta

class AuthenticationManager:
    """Manage user authentication."""
    
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.users = {}  # In production, use database
    
    def register_user(self, username, password):
        """Register new user."""
        # Hash password
        password_hash = self._hash_password(password)
        
        self.users[username] = {
            "password_hash": password_hash,
            "created_at": datetime.now()
        }
    
    def authenticate(self, username, password):
        """Authenticate user và return JWT token."""
        if username not in self.users:
            raise ValueError("Invalid username or password")
        
        # Verify password
        password_hash = self._hash_password(password)
        if password_hash != self.users[username]["password_hash"]:
            raise ValueError("Invalid username or password")
        
        # Generate JWT token
        token = self._generate_token(username)
        return token
    
    def verify_token(self, token):
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            return payload["username"]
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    def _hash_password(self, password):
        """Hash password với SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self, username):
        """Generate JWT token."""
        payload = {
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token

# Sử dụng authentication
auth = AuthenticationManager(secret_key="your-secret-key")

# Register user
auth.register_user("john", "secure_password123")

# Login
token = auth.authenticate("john", "secure_password123")

# Verify token
username = auth.verify_token(token)
print(f"Authenticated user: {username}")
```text

### 3. API Authentication

Secure API endpoints:

```python
from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)
auth = AuthenticationManager(secret_key="your-secret-key")
ac = AccessControl()

def require_auth(permission=None):
    """Decorator để require authentication."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token từ header
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "No token provided"}), 401
            
            # Remove "Bearer " prefix
            if token.startswith("Bearer "):
                token = token[7:]
            
            try:
                # Verify token
                username = auth.verify_token(token)
                
                # Check permission if specified
                if permission:
                    ac.require_permission(username, permission)
                
                # Add username to request
                request.username = username
                
                return f(*args, **kwargs)
                
            except ValueError as e:
                return jsonify({"error": str(e)}), 401
            except PermissionError as e:
                return jsonify({"error": str(e)}), 403
        
        return decorated_function
    return decorator

# Protected endpoints
@app.route("/api/agents", methods=["POST"])
@require_auth(permission=Permission.CREATE_AGENT)
def create_agent_endpoint():
    """Create agent endpoint với authentication."""
    agent_config = request.json
    agent = create_agent(**agent_config)
    return jsonify({"agent_id": agent.id})

@app.route("/api/workflows/<workflow_id>", methods=["POST"])
@require_auth(permission=Permission.EXECUTE_WORKFLOW)
def execute_workflow_endpoint(workflow_id):
    """Execute workflow endpoint với authentication."""
    workflow = load_workflow(workflow_id)
    result = execute_workflow(workflow)
    return jsonify({"result": result})
```text

## Audit Logging

### 1. Security Event Logging

Log tất cả security events:

```python
from agentic_sdlc.core.security import SecurityAuditLogger
import logging

class SecurityAuditLogger:
    """Log security events."""
    
    def __init__(self, log_file="security_audit.log"):
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def log_authentication(self, username, success, ip_address=None):
        """Log authentication attempt."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"AUTH {status}: user={username}, ip={ip_address}"
        )
    
    def log_authorization(self, username, permission, granted):
        """Log authorization check."""
        status = "GRANTED" if granted else "DENIED"
        self.logger.info(
            f"AUTHZ {status}: user={username}, permission={permission}"
        )
    
    def log_data_access(self, username, resource, action):
        """Log data access."""
        self.logger.info(
            f"DATA ACCESS: user={username}, resource={resource}, action={action}"
        )
    
    def log_config_change(self, username, config_key, old_value, new_value):
        """Log configuration change."""
        self.logger.info(
            f"CONFIG CHANGE: user={username}, key={config_key}, "
            f"old={old_value}, new={new_value}"
        )
    
    def log_security_event(self, event_type, details):
        """Log generic security event."""
        self.logger.warning(
            f"SECURITY EVENT: type={event_type}, details={details}"
        )

# Sử dụng audit logger
audit = SecurityAuditLogger()

# Log authentication
audit.log_authentication("john", success=True, ip_address="192.168.1.100")

# Log authorization
audit.log_authorization("john", Permission.CREATE_AGENT, granted=True)

# Log data access
audit.log_data_access("john", "workflow-123", "execute")

# Log security event
audit.log_security_event("SUSPICIOUS_ACTIVITY", "Multiple failed login attempts")
```text

### 2. Monitoring Security Metrics

Monitor security-related metrics:

```python
from agentic_sdlc.intelligence.monitor import Monitor

class SecurityMonitor:
    """Monitor security metrics."""
    
    def __init__(self):
        self.monitor = Monitor()
        self.failed_auth_attempts = {}
    
    def record_auth_attempt(self, username, success):
        """Record authentication attempt."""
        self.monitor.record_metric(
            "auth_attempts",
            1,
            {"username": username, "success": success}
        )
        
        # Track failed attempts
        if not success:
            if username not in self.failed_auth_attempts:
                self.failed_auth_attempts[username] = 0
            
            self.failed_auth_attempts[username] += 1
            
            # Alert if too many failures
            if self.failed_auth_attempts[username] >= 5:
                self._alert_suspicious_activity(username)
    
    def record_permission_check(self, username, permission, granted):
        """Record permission check."""
        self.monitor.record_metric(
            "permission_checks",
            1,
            {"username": username, "permission": permission, "granted": granted}
        )
    
    def _alert_suspicious_activity(self, username):
        """Alert về suspicious activity."""
        print(f"ALERT: Suspicious activity detected for user {username}")
        # Send alert (email, Slack, PagerDuty, etc.)

# Sử dụng security monitor
sec_monitor = SecurityMonitor()

# Record metrics
sec_monitor.record_auth_attempt("john", success=True)
sec_monitor.record_permission_check("john", Permission.CREATE_AGENT, granted=True)
```text

## Best Practices

### 1. Principle of Least Privilege

Chỉ cấp minimum permissions cần thiết:

```python
# ✅ GOOD: Specific permissions
developer_role = Role("developer", [
    Permission.READ_CONFIG,
    Permission.CREATE_AGENT,
    Permission.EXECUTE_WORKFLOW
])

# ❌ BAD: Too broad permissions
developer_role = Role("developer", [Permission.ADMIN])
```text

### 2. Defense in Depth

Implement multiple layers of security:

```python
# Layer 1: Network security (firewall, VPN)
# Layer 2: Authentication
# Layer 3: Authorization
# Layer 4: Encryption
# Layer 5: Audit logging

def secure_operation(user_id, operation, data):
    """Multi-layer security."""
    # Layer 2: Authenticate
    token = request.headers.get("Authorization")
    username = auth.verify_token(token)
    
    # Layer 3: Authorize
    ac.require_permission(username, operation.permission)
    
    # Layer 4: Encrypt sensitive data
    if operation.requires_encryption:
        data = encryptor.encrypt_dict(data)
    
    # Execute operation
    result = operation.execute(data)
    
    # Layer 5: Audit log
    audit.log_data_access(username, operation.name, "execute")
    
    return result
```text

### 3. Regular Security Audits

Thực hiện regular security audits:

```python
from agentic_sdlc.core.security import SecurityAuditor

class SecurityAuditor:
    """Perform security audits."""
    
    def audit_permissions(self):
        """Audit user permissions."""
        issues = []
        
        for user_id, role in ac.user_roles.items():
            # Check for overly broad permissions
            if Permission.ADMIN in role.permissions:
                issues.append(f"User {user_id} has admin permissions")
        
        return issues
    
    def audit_api_keys(self):
        """Audit API keys."""
        issues = []
        
        # Check for expired keys
        # Check for keys not rotated recently
        # Check for keys with excessive permissions
        
        return issues
    
    def audit_encryption(self):
        """Audit encryption usage."""
        issues = []
        
        # Check for unencrypted sensitive data
        # Check for weak encryption algorithms
        
        return issues

# Run security audit
auditor = SecurityAuditor()
issues = auditor.audit_permissions()

if issues:
    print("Security issues found:")
    for issue in issues:
        print(f"  - {issue}")
```text

## Common Security Pitfalls

### ❌ Pitfall 1: Hardcoded Credentials

```python
# BAD
api_key = "sk-1234567890"

# GOOD
api_key = os.getenv("API_KEY")
```text

### ❌ Pitfall 2: Insufficient Input Validation

```python
# BAD
def execute_command(command):
    os.system(command)  # Command injection vulnerability!

# GOOD
def execute_command(command):
    # Validate command
    allowed_commands = ["ls", "pwd", "date"]
    if command not in allowed_commands:
        raise ValueError("Invalid command")
    
    os.system(command)
```text

### ❌ Pitfall 3: Logging Sensitive Data

```python
# BAD
logger.info(f"User logged in with password: {password}")

# GOOD
logger.info(f"User logged in: {username}")
```

## Tài Liệu Liên Quan

- [Deployment Guide](deployment.md) - Secure deployment
- [Configuration Guide](../../getting-started/configuration.md) - Secure configuration
- [API Reference](../../api-reference/core/config.md) - Security APIs
- [Production Example](../../examples/advanced/12-production.py) - Production security setup
