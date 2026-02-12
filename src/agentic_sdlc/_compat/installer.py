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
        # Orchestration API Model Management -> Orchestration models (lenient because many items removed)
        "agentic_sdlc.orchestration.api_model_management": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.models": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.registry": "agentic_sdlc.orchestration.agents",
        "agentic_sdlc.orchestration.api_model_management.selector": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.health_checker": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.rate_limiter": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.failover_manager": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.api_client": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.evaluator": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.cache_manager": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.cost_tracker": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.performance_monitor": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.api_key_manager": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.database": "agentic_sdlc.orchestration.models",
        "agentic_sdlc.orchestration.api_model_management.adapters.base": "agentic_sdlc.orchestration.models",
        
        # Intelligence collaboration/collaborating
        "agentic_sdlc.intelligence.collaborating": "agentic_sdlc.intelligence.collaboration",
        "agentic_sdlc.intelligence.collaborating.state": "agentic_sdlc.intelligence.collaboration",
        "agentic_sdlc.intelligence.collaborating.state.state_manager": "agentic_sdlc.intelligence.collaboration",
        
        # Intelligence learning
        "agentic_sdlc.intelligence.learning.self_healing": "agentic_sdlc.intelligence.learning",
        
        # Infrastructure lifecycle
        "agentic_sdlc.infrastructure.lifecycle.release": "agentic_sdlc.infrastructure.lifecycle",
        "agentic_sdlc.infrastructure.lifecycle.release.release": "agentic_sdlc.infrastructure.lifecycle",
        
        # Infrastructure automation
        "agentic_sdlc.infrastructure.automation": "agentic_sdlc.infrastructure",
        
        # Orchestration engine/interfaces
        "agentic_sdlc.orchestration.engine": "agentic_sdlc.orchestration",
        "agentic_sdlc.orchestration.interfaces": "agentic_sdlc.cli",
        "agentic_sdlc.orchestration.agents.main_agent": "agentic_sdlc.orchestration.agents",

        # Infrastructure autogen -> Orchestration agents
        "agentic_sdlc.infrastructure.autogen": "agentic_sdlc.orchestration",
        "agentic_sdlc.infrastructure.autogen.agents": "agentic_sdlc.orchestration.agents",
    }
    
    for old_path, new_path in shim_mappings.items():
        if old_path == new_path:
            continue
            
        if old_path not in sys.modules:
            # Create a fake module with __getattr__ handler
            module = ModuleType(old_path)
            # Use lenient mode for legacy paths to allow test collection
            is_lenient = (
                "api_model_management" in old_path or 
                "collaborating" in old_path or 
                "release" in old_path or
                "automation" in old_path
            )
            module.__getattr__ = create_module_deprecation_handler(old_path, new_path, lenient=is_lenient)
            sys.modules[old_path] = module
            
            # Safely attach it to its parent if the parent exists in sys.modules
            if "." in old_path:
                parent_path, child_name = old_path.rsplit(".", 1)
                if parent_path in sys.modules:
                    parent_module = sys.modules[parent_path]
                    # ONLY attach if the parent doesn't already have this attribute
                    if not hasattr(parent_module, child_name):
                        try:
                            setattr(parent_module, child_name, module)
                        except (AttributeError, TypeError):
                            # Some modules (built-ins or locked) might not allow setattr
                            pass


# Install shims when this module is imported
install_compatibility_shims()
