"""
Agentic SDLC CLI Entry Point
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.core.brain.brain_cli import main as brain_main

def main():
    """Main CLI entry point"""
    brain_main()

if __name__ == "__main__":
    main()
