"""
Basic usage example of Agentic SDLC SDK
"""
import sys
from pathlib import Path

# Ensure we can import the package if running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_sdlc import Learner, SprintManager, get_project_root

def main():
    print(f"Project Root: {get_project_root()}")
    
    # Use Learner
    if Learner:
        learner = Learner()
        # Mock learning event
        result = learner.learn("SDK is easier to use than raw scripts")
        print(f"Learned: {result['recorded']}")
        
        rec = learner.get_recommendation("SDK")
        if rec:
            print(f"Recommendation: {rec['recommendation']}")
    else:
        print("Learner module not available")
        
    # Use SprintManager
    if SprintManager:
        sm = SprintManager()
        active = sm.get_active_sprint()
        if active:
            print(f"Active Sprint: {active.name}")
        else:
            print("No active sprint.")
            
            # Create one
            sprint = sm.create_sprint("Example Sprint", "Demonstrate SDK")
            print(f"Created: {sprint.name}")
    else:
        print("SprintManager module not available")

if __name__ == "__main__":
    main()
