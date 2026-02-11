"""
General helper functions for CLI.

Provides utility functions used across CLI commands.
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root
    """
    # CLI is at cli/utils/helpers.py, root is 2 levels up
    return Path(__file__).resolve().parent.parent.parent


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user to confirm an action.
    
    Args:
        message: Confirmation message
        default: Default response if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(message + suffix).strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']


def read_file(file_path: str) -> str:
    """
    Read file contents.
    
    Args:
        file_path: Path to file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return path.read_text()


def write_file(file_path: str, content: str) -> None:
    """
    Write content to file.
    
    Args:
        file_path: Path to file
        content: Content to write
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def list_files(directory: str, pattern: str = "*") -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern
        
    Returns:
        List of matching file paths
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    return list(dir_path.glob(pattern))


def parse_key_value_pairs(pairs: List[str]) -> Dict[str, str]:
    """
    Parse key=value pairs from command line.
    
    Args:
        pairs: List of "key=value" strings
        
    Returns:
        Dictionary of key-value pairs
        
    Raises:
        ValueError: If pair is not in key=value format
    """
    result = {}
    for pair in pairs:
        if '=' not in pair:
            raise ValueError(f"Invalid key=value pair: {pair}")
        
        key, value = pair.split('=', 1)
        result[key.strip()] = value.strip()
    
    return result


def truncate_string(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
