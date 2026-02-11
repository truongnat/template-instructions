"""Resource loading utilities for accessing package data.

This module provides functions for loading resources (templates, workflows, rules)
that are packaged with the SDK.
"""

from pathlib import Path
from typing import Optional


def get_resource_path(resource_type: str, resource_name: str) -> Optional[Path]:
    """Get the path to a resource file.
    
    Args:
        resource_type: Type of resource ('templates', 'workflows', 'rules')
        resource_name: Name of the resource file or directory
    
    Returns:
        Path to the resource, or None if not found
    
    Raises:
        ValueError: If resource_type is invalid
    """
    valid_types = {"templates", "workflows", "rules"}
    if resource_type not in valid_types:
        raise ValueError(f"Invalid resource type: {resource_type}. Must be one of {valid_types}")
    
    # Get the package directory (src/agentic_sdlc)
    package_dir = Path(__file__).parent.parent.parent
    
    # Resources are at the root level, so go up one more level from src
    root_dir = package_dir.parent
    resource_path = root_dir / "resources" / resource_type / resource_name
    
    if resource_path.exists():
        return resource_path
    
    # If not found, return None
    return None


def load_resource_text(resource_type: str, resource_name: str) -> Optional[str]:
    """Load a text resource file.
    
    Args:
        resource_type: Type of resource ('templates', 'workflows', 'rules')
        resource_name: Name of the resource file
    
    Returns:
        Content of the resource file, or None if not found
    
    Raises:
        ValueError: If resource_type is invalid
        IOError: If the resource file cannot be read
    """
    resource_path = get_resource_path(resource_type, resource_name)
    if resource_path is None:
        return None
    
    if not resource_path.is_file():
        raise IOError(f"Resource is not a file: {resource_path}")
    
    return resource_path.read_text(encoding="utf-8")


def list_resources(resource_type: str) -> list[str]:
    """List all resources of a given type.
    
    Args:
        resource_type: Type of resource ('templates', 'workflows', 'rules')
    
    Returns:
        List of resource names
    
    Raises:
        ValueError: If resource_type is invalid
    """
    valid_types = {"templates", "workflows", "rules"}
    if resource_type not in valid_types:
        raise ValueError(f"Invalid resource type: {resource_type}. Must be one of {valid_types}")
    
    # Get the package directory (src/agentic_sdlc)
    package_dir = Path(__file__).parent.parent.parent
    
    # Resources are at the root level, so go up one more level from src
    root_dir = package_dir.parent
    resource_dir = root_dir / "resources" / resource_type
    
    if not resource_dir.exists():
        return []
    
    # List all files and directories in the resource directory
    resources = []
    for item in resource_dir.iterdir():
        resources.append(item.name)
    
    return sorted(resources)
