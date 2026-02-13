
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

print("Installing shims...")
from agentic_sdlc._compat import install_compatibility_shims
install_compatibility_shims()
print("Shims installed.\n")

def test_import(path, name):
    print(f"Testing: from {path} import {name}")
    try:
        # We use __import__ to simulate actual import behavior
        module = __import__(path, fromlist=[name])
        attr = getattr(module, name)
        print(f"SUCCESS: {attr}\n")
    except Exception as e:
        print(f"FAILED: {e}\n")

# Existing shims
test_import("agentic_sdlc.orchestration.api_model_management.registry", "ModelRegistry")
test_import("agentic_sdlc.intelligence.collaborating.state.state_manager", "StateManager")

# New shims
test_import("agentic_sdlc.comparison.models", "ComparisonResult")
test_import("agentic_sdlc.orchestration.engine.execution_planner", "ExecutionPlanner")
test_import("agentic_sdlc.orchestration.models.workflow", "Workflow")
test_import("agentic_sdlc.version", "__version__")

print("Verifying parent access:")
import agentic_sdlc
try:
    print(f"agentic_sdlc.comparison: {agentic_sdlc.comparison}")
    print(f"agentic_sdlc.orchestration.api_model_management: {agentic_sdlc.orchestration.api_model_management}")
except Exception as e:
    print(f"FAILED parent access: {e}")
