"""
Encryption utilities for SDLC Kit.

Provides encryption and decryption functions using Fernet symmetric encryption.
"""

from typing import Optional
from cryptography.fernet import Fernet


def generate_key() -> str:
    """
    Generate a new Fernet encryption key.
    
    Returns:
        A new encryption key as a string
    """
    return Fernet.generate_key().decode()


def encrypt(data: str, key: str) -> str:
    """
    Encrypt data using Fernet symmetric encryption.
    
    Args:
        data: The plaintext data to encrypt
        key: The encryption key
        
    Returns:
        Encrypted data as a string
        
    Raises:
        ValueError: If key is invalid
        RuntimeError: If encryption fails
    """
    try:
        cipher = Fernet(key.encode())
        encrypted = cipher.encrypt(data.encode())
        return encrypted.decode()
    except Exception as e:
        if "Invalid" in str(e) or "key" in str(e).lower():
            raise ValueError(f"Invalid encryption key: {type(e).__name__}")
        raise RuntimeError(f"Encryption failed: {type(e).__name__}")


def decrypt(encrypted_data: str, key: str) -> str:
    """
    Decrypt data using Fernet symmetric encryption.
    
    Args:
        encrypted_data: The encrypted data to decrypt
        key: The encryption key
        
    Returns:
        Decrypted plaintext data
        
    Raises:
        ValueError: If key is invalid or data cannot be decrypted
        RuntimeError: If decryption fails
    """
    try:
        cipher = Fernet(key.encode())
        decrypted = cipher.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception as e:
        if "Invalid" in str(e) or "key" in str(e).lower() or "token" in str(e).lower():
            raise ValueError(f"Invalid key or corrupted data: {type(e).__name__}")
        raise RuntimeError(f"Decryption failed: {type(e).__name__}")


def encrypt_file(input_path: str, output_path: str, key: str) -> None:
    """
    Encrypt a file using Fernet symmetric encryption.
    
    Args:
        input_path: Path to the file to encrypt
        output_path: Path where encrypted file will be saved
        key: The encryption key
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If key is invalid
        RuntimeError: If encryption fails
    """
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
        
        cipher = Fernet(key.encode())
        encrypted = cipher.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        if "Invalid" in str(e) or "key" in str(e).lower():
            raise ValueError(f"Invalid encryption key: {type(e).__name__}")
        raise RuntimeError(f"File encryption failed: {type(e).__name__}")


def decrypt_file(input_path: str, output_path: str, key: str) -> None:
    """
    Decrypt a file using Fernet symmetric encryption.
    
    Args:
        input_path: Path to the encrypted file
        output_path: Path where decrypted file will be saved
        key: The encryption key
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If key is invalid or data cannot be decrypted
        RuntimeError: If decryption fails
    """
    try:
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
        
        cipher = Fernet(key.encode())
        decrypted = cipher.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except Exception as e:
        if "Invalid" in str(e) or "key" in str(e).lower() or "token" in str(e).lower():
            raise ValueError(f"Invalid key or corrupted data: {type(e).__name__}")
        raise RuntimeError(f"File decryption failed: {type(e).__name__}")
