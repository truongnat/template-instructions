"""
Secrets Manager for SDLC Kit.

Manages API keys and sensitive credentials with optional encryption.
"""

import os
import json
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet


class SecretsManager:
    """Manage API keys and sensitive credentials."""
    
    def __init__(self, encryption_key: Optional[str] = None, storage_path: Optional[str] = None):
        """
        Initialize secrets manager with optional encryption key.
        
        Args:
            encryption_key: Optional encryption key for securing secrets.
                          If not provided, checks ENCRYPTION_KEY environment variable.
            storage_path: Optional path to secrets storage file.
                         Defaults to .secrets/secrets.enc
        """
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")
        self.cipher = None
        
        if self.encryption_key:
            try:
                self.cipher = Fernet(self.encryption_key.encode())
            except Exception:
                # If key is invalid, generate a new one
                self.encryption_key = Fernet.generate_key().decode()
                self.cipher = Fernet(self.encryption_key.encode())
        
        self.storage_path = Path(storage_path or ".secrets/secrets.enc")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing secrets from storage
        self._secrets_cache = self._load_secrets()
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a secret by key.
        
        Checks environment variables first, then encrypted storage.
        
        Args:
            key: The secret key to retrieve
            
        Returns:
            The secret value if found, None otherwise
        """
        # First check environment variables
        value = os.getenv(key)
        if value:
            return value
        
        # Then check encrypted storage
        return self._get_from_storage(key)
    
    def set_secret(self, key: str, value: str, encrypt: bool = True) -> None:
        """
        Store a secret with optional encryption.
        
        Args:
            key: The secret key
            value: The secret value (will not be logged)
            encrypt: Whether to encrypt the value (default: True)
        """
        if encrypt and self.cipher:
            encrypted_value = self.cipher.encrypt(value.encode()).decode()
            self._secrets_cache[key] = encrypted_value
        else:
            self._secrets_cache[key] = value
        
        self._save_secrets()
    
    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret from storage.
        
        Args:
            key: The secret key to delete
            
        Returns:
            True if secret was deleted, False if not found
        """
        if key in self._secrets_cache:
            del self._secrets_cache[key]
            self._save_secrets()
            return True
        return False
    
    def list_secret_keys(self) -> list:
        """
        List all secret keys (not values).
        
        Returns:
            List of secret keys
        """
        return list(self._secrets_cache.keys())
    
    def _get_from_storage(self, key: str) -> Optional[str]:
        """
        Retrieve secret from secure storage.
        
        Args:
            key: The secret key
            
        Returns:
            Decrypted secret value if found, None otherwise
        """
        if key not in self._secrets_cache:
            return None
        
        encrypted_value = self._secrets_cache[key]
        
        # Try to decrypt if cipher is available
        if self.cipher:
            try:
                decrypted = self.cipher.decrypt(encrypted_value.encode()).decode()
                return decrypted
            except Exception:
                # If decryption fails, return as-is (might be unencrypted)
                return encrypted_value
        
        return encrypted_value
    
    def _load_secrets(self) -> dict:
        """
        Load secrets from storage file.
        
        Returns:
            Dictionary of secrets
        """
        if not self.storage_path.exists():
            return {}
        
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_secrets(self) -> None:
        """Save secrets to storage file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self._secrets_cache, f, indent=2)
        except Exception as e:
            # Never log the actual secret values
            raise RuntimeError(f"Failed to save secrets to storage: {type(e).__name__}")
