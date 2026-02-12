
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Simulate conftest logic
PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

print("Installing shims...")
try:
    from agentic_sdlc._compat import install_compatibility_shims
    install_compatibility_shims()
    print("Shims installed.")
except Exception as e:
    print(f"Failed to install shims: {e}")
    sys.exit(1)

print("\nTesting import of legacy path:")
try:
    import agentic_sdlc.orchestration.api_model_management.registry
    print(f"SUCCESS: agentic_sdlc.orchestration.api_model_management.registry is {agentic_sdlc.orchestration.api_model_management.registry}")
    from agentic_sdlc.orchestration.api_model_management.registry import ModelRegistry
    print(f"SUCCESS: ModelRegistry is {ModelRegistry}")
except Exception as e:
    print(f"FAILED import: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting import from intelligence legacy:")
try:
    from agentic_sdlc.intelligence.collaborating.state.state_manager import StateManager
    print(f"SUCCESS: StateManager is {StateManager}")
except Exception as e:
    print(f"FAILED import: {e}")

print("\nVerifying sys.modules for a shim path:")
print(f"agentic_sdlc.orchestration.api_model_management in sys.modules: {'agentic_sdlc.orchestration.api_model_management' in sys.modules}")
