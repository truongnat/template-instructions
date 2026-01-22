import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
try:
    from agentic_sdlc.infrastructure.release.release import ReleaseManager
    print("ReleaseManager imported")
    rm = ReleaseManager()
    print(f"Current version: {rm.get_current_version()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
