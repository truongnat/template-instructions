"""
Input validation utilities for CLI.

Provides functions for validating user input in CLI commands.
"""

import re
from pathlib import Path
from typing import Optional


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a file exists.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file exists, False otherwise
    """
    return Path(file_path).is_file()


def validate_directory_exists(dir_path: str) -> bool:
    """
    Validate that a directory exists.
    
    Args:
        dir_path: Path to directory
        
    Returns:
        True if directory exists, False otherwise
    """
    return Path(dir_path).is_dir()


def validate_identifier(identifier: str) -> bool:
    """
    Validate that a string is a valid identifier.
    
    Args:
        identifier: String to validate
        
    Returns:
        True if valid identifier, False otherwise
    """
    # Must start with letter or underscore, contain only alphanumeric and underscores
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_-]*$'
    return bool(re.match(pattern, identifier))


def validate_version(version: str) -> bool:
    """
    Validate semantic version string.
    
    Args:
        version: Version string to validate
        
    Returns:
        True if valid semantic version, False otherwise
    """
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))


def validate_yaml_file(file_path: str) -> bool:
    """
    Validate that a file is a YAML file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file has .yaml or .yml extension, False otherwise
    """
    return file_path.endswith('.yaml') or file_path.endswith('.yml')


def validate_json_file(file_path: str) -> bool:
    """
    Validate that a file is a JSON file.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file has .json extension, False otherwise
    """
    return file_path.endswith('.json')
