"""Installer for compatibility shims.

This module registers compatibility shim modules in sys.modules
to enable old import paths to work with deprecation warnings.
"""

import sys
from types import ModuleType
from typing import Dict, Tuple

from .._internal.deprecation import create_module_deprecation_handler


def install_compatibility_shims() -> None:
    """Install all compatibility shims into sys.modules.
    
    This function registers fake modules in sys.modules that redirect
    old import paths to new locations with deprecation warnings.
    
    Old imports like:
        from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role
    
    Will now work but emit a DeprecationWarning directing users to:
        from agentic_sdlc.orchestration.agents import create_agent
    """
    
    # Mapping of old module paths to new module paths
    shim_mappings: Dict[str, str] = {
        # Infrastructure autogen -> Orchestration agents
        "agentic_sdlc.infrastructure.autogen": "agentic_sdlc.orchestration",
        "agentic_sdlc.infrastructure.autogen.agents": "agentic_sdlc.orchestration.agents",
        
        # Intelligence learning (same location, just for consistency)
        "agentic_sdlc.intelligence.learning": "agentic_sdlc.intelligence.learning",
        
        # Core config (same location, just for consistency)
        "agentic_sdlc.core.config": "agentic_sdlc.core.config",
    }
    
    for old_path, new_path in shim_mappings.items():
        if old_path not in sys.modules:
            # Create a fake module with __getattr__ handler
            module = ModuleType(old_path)
            module.__getattr__ = create_module_deprecation_handler(old_path, new_path)
            sys.modules[old_path] = module


# Install shims when this module is imported
install_compatibility_shims()
