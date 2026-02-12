"""Deprecation utilities for backward compatibility.

This module provides utilities for emitting deprecation warnings
when old import paths are used, guiding users to the new locations.
"""

import warnings
from typing import Any, Dict, Optional


def emit_deprecation_warning(
    old_path: str,
    new_path: str,
    name: str,
    stacklevel: int = 3,
) -> None:
    """Emit a deprecation warning for an old import path.
    
    Args:
        old_path: The old import path (e.g., "agentic_sdlc.infrastructure.autogen.agents")
        new_path: The new import path (e.g., "agentic_sdlc.orchestration.agents")
        name: The name of the symbol being imported
        stacklevel: Stack level for the warning (default 3 for __getattr__)
    """
    message = (
        f"Importing {name} from '{old_path}' is deprecated and will be removed in v4.0.0. "
        f"Use 'from {new_path} import {name}' instead."
    )
    warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)


def create_getattr_handler(
    mappings: Dict[str, tuple[str, str]],
    module_path: str,
) -> Any:
    """Create a __getattr__ handler for a module with deprecation warnings.
    
    Args:
        mappings: Dictionary mapping old names to (new_module_path, new_name) tuples
        module_path: The current module path for error messages
    
    Returns:
        A __getattr__ function that handles deprecated imports
    
    Example:
        mappings = {
            "create_agent_by_role": ("agentic_sdlc.orchestration.agents", "create_agent"),
            "Agent": ("agentic_sdlc.orchestration.agents", "Agent"),
        }
        __getattr__ = create_getattr_handler(mappings, "agentic_sdlc.infrastructure.autogen.agents")
    """
    def __getattr__(name: str) -> Any:
        if name in mappings:
            new_module_path, new_name = mappings[name]
            emit_deprecation_warning(module_path, new_module_path, name, stacklevel=2)
            
            # Import and return the new symbol
            import importlib
            module = importlib.import_module(new_module_path)
            return getattr(module, new_name)
        
        raise AttributeError(f"module '{module_path}' has no attribute '{name}'")
    
    return __getattr__


def create_module_deprecation_handler(
    old_module_path: str,
    new_module_path: str,
    lenient: bool = False,
) -> Any:
    """Create a __getattr__ handler that redirects all imports to a new module.
    
    Args:
        old_module_path: The old module path
        new_module_path: The new module path
        lenient: If True, return a Mock for missing names instead of raising AttributeError.
                 This is useful for allowing legacy tests to be collectable even if some
                 classes have been removed.
    
    Returns:
        A __getattr__ function that redirects to the new module
    """
    def __getattr__(name: str) -> Any:
        emit_deprecation_warning(old_module_path, new_module_path, name, stacklevel=2)
        
        # Import and return from the new module
        import importlib
        try:
            module = importlib.import_module(new_module_path)
            return getattr(module, name)
        except (ImportError, AttributeError):
            if lenient:
                from unittest.mock import MagicMock
                mock = MagicMock(name=f"{old_module_path}.{name}")
                return mock
            raise
    
    return __getattr__
