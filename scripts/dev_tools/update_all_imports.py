
import os
from pathlib import Path

# Mapping of module to its new concern category
INTEL_MAPPING = {
    'research': 'reasoning',
    'router': 'reasoning',
    'skills': 'reasoning',
    'task_manager': 'reasoning',
    'knowledge_graph': 'reasoning',
    'judge': 'monitoring',
    'evaluation': 'monitoring',
    'observer': 'monitoring',
    'monitor': 'monitoring',
    'workflow_validator': 'monitoring',
    'hitl': 'monitoring',
    'self_learning': 'learning',
    'ab_test': 'learning',
    'dspy_integration': 'learning',
    'self_healing': 'learning',
    'performance': 'learning',
    'cost': 'learning',
    'concurrent': 'collaborating',
    'synthesis': 'collaborating',
    'communication': 'collaborating',
    'state': 'collaborating',
    'dashboard': 'collaborating',
    'artifact_gen': 'collaborating'
}

INFRA_MAPPING = {
    'agent': 'automation',
    'aop': 'engine',
    'autogen': 'engine',
    'communication': 'bridge',
    'git': 'bridge',
    'github': 'bridge',
    'local_llm': 'engine',
    'release': 'lifecycle',
    'sandbox': 'engine',
    'setup': 'lifecycle',
    'update': 'lifecycle',
    'validation': 'automation',
    'workflows': 'automation',
}

def update_imports(target_path):
    target_dir = Path(target_path)
    if not target_dir.exists():
        print(f"Path {target_path} not found")
        return

    for py_file in target_dir.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # Intelligence Replacements
            for mod, concern in INTEL_MAPPING.items():
                old_abs = f'agentic_sdlc.intelligence.{mod}'
                new_abs = f'agentic_sdlc.intelligence.{concern}.{mod}'
                new_content = new_content.replace(old_abs, new_abs)
            
            # Infrastructure Replacements
            for mod, concern in INFRA_MAPPING.items():
                old_abs = f'agentic_sdlc.infrastructure.{mod}'
                new_abs = f'agentic_sdlc.infrastructure.{concern}.{mod}'
                new_content = new_content.replace(old_abs, new_abs)

            # MCP Replacements
            new_content = new_content.replace('agentic_sdlc.mcp', 'agentic_sdlc.infrastructure.bridge.mcp')

            if new_content != content:
                print(f"Updating imports in {py_file}")
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

if __name__ == "__main__":
    update_imports('tests')
    update_imports('bin')
    update_imports('agentic_sdlc') # Just in case I missed anything
