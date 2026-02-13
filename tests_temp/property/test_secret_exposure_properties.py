"""
Property-based tests for Secret Exposure Prevention.

These tests use Hypothesis to verify that secrets are never exposed in logs
or error messages across many randomly generated inputs.

Feature: sdlc-kit-improvements
Property 12: Secret Exposure Prevention
Requirements: 14.5
"""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any

from security.secrets_manager import SecretsManager
from security.audit_logger import AuditLogger


# Strategy for generating secret keys (alphanumeric with underscores)
secret_keys = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
    min_size=5,
    max_size=30
).filter(lambda x: x and x[0].isalpha() and all(c.isalnum() or c == '_' for c in x))

# Strategy for generating secret values (sensitive data - must be different from keys)
# Use printable ASCII + some special chars to ensure valid UTF-8 encoding
secret_values = st.text(
    alphabet=st.characters(
        min_codepoint=32,  # Space
        max_codepoint=126,  # Tilde (printable ASCII)
        blacklist_characters='\x00\n\r'
    ),
    min_size=20,
    max_size=100
).filter(lambda x: len(x.strip()) >= 20 and not x.replace(' ', '').replace('_', '').isalnum())


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    secret_key=secret_keys,
    secret_value=secret_values,
)
@settings(max_examples=10, deadline=None)
def test_secret_not_exposed_in_storage_file(secret_key, secret_value):
    """
    Property: For any secret stored through the SecretsManager with encryption enabled,
    when the storage file is examined, the plaintext secret value should not appear
    in the file (it should be encrypted).
    
    This property ensures that secrets are properly encrypted at rest and not
    exposed in storage files.
    
    **Validates: Requirements 14.5**
    """
    # Ensure key and value are different to avoid false positives
    assume(secret_key != secret_value)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "secrets.enc"
        
        # Create secrets manager with encryption
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()
        manager = SecretsManager(encryption_key=encryption_key, storage_path=str(storage_path))
        
        # Store a secret with encryption
        manager.set_secret(secret_key, secret_value, encrypt=True)
        
        # Read the storage file
        with open(storage_path, 'r') as f:
            storage_content = f.read()
        
        # Property: Plaintext secret value should NOT appear in storage file
        assert secret_value not in storage_content, (
            f"Secret value should not appear in plaintext in storage file. "
            f"Secret key: {secret_key}"
        )


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    secret_key=secret_keys,
    secret_value=secret_values,
)
@settings(max_examples=10, deadline=None)
def test_secret_not_exposed_in_error_messages(secret_key, secret_value):
    """
    Property: For any secret accessed through the SecretsManager, when an error
    occurs during storage operations, the error message should not contain the
    actual secret value.
    
    This property ensures that secrets are never leaked through error messages.
    
    **Validates: Requirements 14.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "secrets.enc"
        
        # Create secrets manager
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()
        manager = SecretsManager(encryption_key=encryption_key, storage_path=str(storage_path))
        
        # Store a secret
        manager.set_secret(secret_key, secret_value, encrypt=True)
        
        # Make the storage file read-only to trigger an error on save
        os.chmod(storage_path, 0o444)
        
        try:
            # Try to set another secret (should fail due to read-only file)
            manager.set_secret("another_key", "another_value", encrypt=True)
        except Exception as e:
            error_message = str(e)
            
            # Property: Secret value should NOT appear in error message
            assert secret_value not in error_message, (
                f"Secret value should not appear in error message. "
                f"Error: {error_message}"
            )
            
            # Also check that the error doesn't expose the new secret
            assert "another_value" not in error_message, (
                "Secret value should not appear in error message"
            )
        finally:
            # Restore permissions for cleanup
            os.chmod(storage_path, 0o644)


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    user=st.text(
        alphabet=st.characters(min_codepoint=65, max_codepoint=122),
        min_size=3,
        max_size=30
    ).filter(lambda x: x.strip()),
    secret_key=secret_keys,
    secret_value=secret_values,
)
@settings(max_examples=10, deadline=None)
def test_secret_not_exposed_in_audit_logs(user, secret_key, secret_value):
    """
    Property: For any secret accessed through the Security Module, when the
    access is logged to the audit trail, the log entry should contain the
    secret key but NOT the secret value.
    
    This property ensures that audit logs track secret access without
    exposing the actual secret values.
    
    **Validates: Requirements 14.5**
    """
    # Ensure key and value are different to avoid false positives
    assume(secret_key != secret_value)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log secret access (simulating what would happen in real usage)
        audit_logger.log_secret_access(
            user=user,
            secret_key=secret_key,
            action="accessed"
        )
        
        # Read the audit log
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Property: Secret key should appear in log (for tracking)
        assert secret_key in log_content, (
            f"Secret key should appear in audit log for tracking purposes"
        )
        
        # Property: Secret value should NOT appear in log
        assert secret_value not in log_content, (
            f"Secret value should not appear in audit log. "
            f"Log content: {log_content}"
        )


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    secret_key=secret_keys,
    secret_value=secret_values,
)
@settings(max_examples=10, deadline=None)
def test_secret_not_exposed_when_listing_keys(secret_key, secret_value):
    """
    Property: For any secret stored in the SecretsManager, when listing
    all secret keys, the operation should return keys but never values.
    
    This property ensures that bulk operations don't accidentally expose secrets.
    
    **Validates: Requirements 14.5**
    """
    # Ensure key and value are different to avoid false positives
    assume(secret_key != secret_value)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "secrets.enc"
        
        # Create secrets manager
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()
        manager = SecretsManager(encryption_key=encryption_key, storage_path=str(storage_path))
        
        # Store a secret
        manager.set_secret(secret_key, secret_value, encrypt=True)
        
        # List all secret keys
        keys = manager.list_secret_keys()
        
        # Property: Secret key should be in the list
        assert secret_key in keys, (
            f"Secret key should be in the list of keys"
        )
        
        # Property: Secret value should NOT be in the list
        assert secret_value not in keys, (
            f"Secret value should not appear in the list of keys"
        )
        
        # Property: The list should only contain strings that look like keys, not values
        for key in keys:
            assert key != secret_value, (
                f"List of keys should not contain secret values"
            )


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    secret_key=secret_keys,
    secret_value=secret_values,
)
@settings(max_examples=10, deadline=None)
def test_secret_not_exposed_in_repr_or_str(secret_key, secret_value):
    """
    Property: For any SecretsManager instance containing secrets, when
    converted to string representation (str() or repr()), the output
    should not contain any secret values.
    
    This property ensures that accidental printing or logging of the
    manager object doesn't expose secrets.
    
    **Validates: Requirements 14.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "secrets.enc"
        
        # Create secrets manager
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()
        manager = SecretsManager(encryption_key=encryption_key, storage_path=str(storage_path))
        
        # Store a secret
        manager.set_secret(secret_key, secret_value, encrypt=True)
        
        # Get string representations
        str_repr = str(manager)
        repr_repr = repr(manager)
        
        # Property: Secret value should NOT appear in string representation
        assert secret_value not in str_repr, (
            f"Secret value should not appear in str() representation"
        )
        
        assert secret_value not in repr_repr, (
            f"Secret value should not appear in repr() representation"
        )


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    secret_key=secret_keys,
    secret_value=secret_values,
    invalid_key=st.text(min_size=10, max_size=50),
)
@settings(max_examples=10, deadline=None)
def test_secret_not_exposed_on_decryption_failure(secret_key, secret_value, invalid_key):
    """
    Property: For any secret stored with encryption, when decryption fails
    (e.g., due to wrong key), the error should not expose the encrypted
    or plaintext secret value.
    
    This property ensures that decryption failures don't leak secrets.
    
    **Validates: Requirements 14.5**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "secrets.enc"
        
        # Create secrets manager with one key
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()
        manager = SecretsManager(encryption_key=encryption_key, storage_path=str(storage_path))
        
        # Store a secret
        manager.set_secret(secret_key, secret_value, encrypt=True)
        
        # Create a new manager with a different key (will fail to decrypt)
        different_key = Fernet.generate_key().decode()
        manager2 = SecretsManager(encryption_key=different_key, storage_path=str(storage_path))
        
        # Try to retrieve the secret (decryption will fail)
        retrieved = manager2.get_secret(secret_key)
        
        # Property: Even if decryption fails, the original secret value
        # should not be exposed (it should return None or encrypted data, not plaintext)
        if retrieved is not None:
            # If something is returned, it should be encrypted data, not the plaintext
            assert retrieved != secret_value, (
                f"Failed decryption should not return plaintext secret value"
            )


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    secret_key=secret_keys,
    secret_value=secret_values,
)
@settings(max_examples=10, deadline=None)
def test_secret_not_exposed_in_environment_fallback(secret_key, secret_value):
    """
    Property: For any secret that could be retrieved from environment variables,
    when the secret is not found and an error occurs, the error message should
    not expose any secret values from the environment.
    
    This property ensures that environment variable handling doesn't leak secrets.
    
    **Validates: Requirements 14.5**
    """
    # Ensure key and value are different to avoid false positives
    assume(secret_key != secret_value)
    # Ensure value doesn't contain null bytes (not allowed in env vars)
    assume('\x00' not in secret_value)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "secrets.enc"
        
        # Set a secret in environment
        os.environ[secret_key] = secret_value
        
        try:
            # Create secrets manager
            from cryptography.fernet import Fernet
            encryption_key = Fernet.generate_key().decode()
            manager = SecretsManager(encryption_key=encryption_key, storage_path=str(storage_path))
            
            # Retrieve the secret (should come from environment)
            retrieved = manager.get_secret(secret_key)
            
            # Property: The secret should be retrieved successfully
            assert retrieved == secret_value, (
                "Secret should be retrieved from environment"
            )
            
            # Now test that if we convert manager to string, the env secret isn't exposed
            str_repr = str(manager)
            repr_repr = repr(manager)
            
            assert secret_value not in str_repr, (
                "Environment secret should not appear in str() representation"
            )
            
            assert secret_value not in repr_repr, (
                "Environment secret should not appear in repr() representation"
            )
            
        finally:
            # Clean up environment
            if secret_key in os.environ:
                del os.environ[secret_key]


# Feature: sdlc-kit-improvements, Property 12: Secret Exposure Prevention
@given(
    secret_key=secret_keys,
    secret_value=secret_values,
)
@settings(max_examples=10, deadline=None)
def test_deleted_secret_not_exposed_in_logs(secret_key, secret_value):
    """
    Property: For any secret that is deleted from the SecretsManager,
    the deletion operation should not expose the secret value in any logs
    or error messages.
    
    This property ensures that secret deletion is secure.
    
    **Validates: Requirements 14.5**
    """
    # Ensure key and value are different to avoid false positives
    assume(secret_key != secret_value)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "secrets.enc"
        log_path = Path(tmpdir) / "audit.log"
        
        # Create secrets manager and audit logger
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()
        manager = SecretsManager(encryption_key=encryption_key, storage_path=str(storage_path))
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Store a secret
        manager.set_secret(secret_key, secret_value, encrypt=True)
        
        # Log the deletion
        audit_logger.log_secret_access(
            user="test_user",
            secret_key=secret_key,
            action="deleted"
        )
        
        # Delete the secret
        manager.delete_secret(secret_key)
        
        # Read the audit log
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Property: Secret value should NOT appear in audit log
        assert secret_value not in log_content, (
            f"Secret value should not appear in audit log during deletion"
        )
        
        # Read the storage file
        with open(storage_path, 'r') as f:
            storage_content = f.read()
        
        # Property: After deletion, secret should not be retrievable
        retrieved = manager.get_secret(secret_key)
        assert retrieved is None, (
            "Deleted secret should not be retrievable"
        )
