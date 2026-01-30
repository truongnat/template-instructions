
import os
import shutil
from pathlib import Path

# Mapping of module to its new concern category
MAPPING = {
    # REASONING: Core cognitive functions
    'research': 'reasoning',
    'router': 'reasoning',
    'skills': 'reasoning',
    'task_manager': 'reasoning',
    'knowledge_graph': 'reasoning',
    
    # MONITORING: Quality, compliance and safety
    'judge': 'monitoring',
    'evaluation': 'monitoring',
    'observer': 'monitoring',
    'monitor': 'monitoring',
    'workflow_validator': 'monitoring',
    'hitl': 'monitoring',
    
    # LEARNING: Improvement and optimization
    'self_learning': 'learning',
    'ab_test': 'learning',
    'dspy_integration': 'learning',
    'self_healing': 'learning',
    'performance': 'learning',
    'cost': 'learning',
    
    # COLLABORATING: Multi-agent execution and outputs
    'concurrent': 'collaborating',
    'synthesis': 'collaborating',
    'communication': 'collaborating',
    'state': 'collaborating',
    'dashboard': 'collaborating',
    'artifact_gen': 'collaborating'
}

INTEL_DIR = Path('agentic_sdlc/intelligence')

def reorganize():
    # 1. Create Concern directories
    concerns = set(MAPPING.values())
    for concern in concerns:
        (INTEL_DIR / concern).mkdir(exist_ok=True)
        # Create __init__.py for sub-packages
        (INTEL_DIR / concern / '__init__.py').touch()

    # 2. Move modules
    for mod, concern in MAPPING.items():
        src = INTEL_DIR / mod
        dst = INTEL_DIR / concern / mod
        if src.exists() and src.is_dir():
            print(f"Moving {mod} -> {concern}/{mod}")
            if dst.exists():
                shutil.rmtree(dst)
            shutil.move(str(src), str(dst))

    # 3. Update all imports in agentic_sdlc
    root_dir = Path('agentic_sdlc')
    for py_file in root_dir.rglob('*.py'):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        for mod, concern in MAPPING.items():
            # Replace absolute imports
            old_abs = f'agentic_sdlc.intelligence.{mod}'
            new_abs = f'agentic_sdlc.intelligence.{concern}.{mod}'
            new_content = new_content.replace(old_abs, new_abs)
            
            # Replace relative imports (harder, but we can try)
            # from .research import -> from .reasoning.research import
            # This is only relevant inside intelligence/__init__.py or between siblings
            old_rel = f'from .{mod}'
            new_rel = f'from .{concern}.{mod}'
            new_content = new_content.replace(old_rel, new_rel)

        if new_content != content:
            print(f"Updating imports in {py_file}")
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

if __name__ == "__main__":
    reorganize()
