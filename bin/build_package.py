#!/usr/bin/env python3
"""
Build and publish script for sdlc-kit
"""
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd, check=True):
    """Run a command and return result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result

def main():
    root = Path(__file__).parent.parent
    
    print("=" * 60)
    print("Building sdlc-kit package")
    print("=" * 60)
    
    # Clean old builds
    print("\n1. Cleaning old builds...")
    for pattern in ['dist', 'build', '*.egg-info']:
        for path in root.glob(pattern):
            if path.is_dir():
                import shutil
                try:
                    shutil.rmtree(path)
                    print(f"  Removed: {path}")
                except Exception as e:
                    print(f"  Warning: Could not remove {path}: {e}")
    
    # Build using pip wheel (works without build module)
    print("\n2. Building package...")
    result = run_cmd([
        sys.executable, '-m', 'pip', 'wheel',
        '--no-deps',
        '-w', 'dist',
        '.'
    ], check=False)
    
    if result.returncode != 0:
        print("\nError: Build failed!")
        sys.exit(1)
    
    # List built files
    print("\n3. Built files:")
    dist_dir = root / 'dist'
    if dist_dir.exists():
        for f in dist_dir.iterdir():
            print(f"  ✓ {f.name}")
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print("\nTo publish to PyPI:")
    print("  python -m twine upload dist/*")
    print("\nTo publish to TestPyPI:")
    print("  python -m twine upload --repository testpypi dist/*")

if __name__ == '__main__':
    main()
