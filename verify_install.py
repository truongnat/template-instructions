
import agentic_sdlc
import os
import sys
from pathlib import Path

def inspect():
    print(f"Python: {sys.executable}")
    print(f"Agentic SDLC Version: {agentic_sdlc.__version__}")
    
    pkg_file = Path(agentic_sdlc.__file__)
    print(f"Package File: {pkg_file}")
    
    pkg_root = pkg_file.parent
    print(f"Package Root: {pkg_root}")

    defaults = pkg_root / "defaults"
    print(f"Defaults Dir: {defaults}")
    
    if not defaults.exists():
        print("❌ Defaults directory DOES NOT EXIST")
        return

    print("✅ Defaults directory exists")
    
    # Check subdirs
    for subdir in ['skills', 'workflows', 'templates', 'rules']:
        d = defaults / subdir
        if d.exists():
            count = len(list(d.rglob('*')))
            print(f"  ✅ {subdir}/ found ({count} items)")
        else:
            print(f"  ❌ {subdir}/ NOT FOUND")

    # List some files to be sure
    print("\nSample files in defaults:")
    files = list(defaults.rglob("*"))
    for f in files[:5]:
        print(f" - {f.relative_to(defaults)}")

if __name__ == "__main__":
    inspect()
