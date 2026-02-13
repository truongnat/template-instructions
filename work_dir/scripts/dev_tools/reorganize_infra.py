
import os
import shutil
from pathlib import Path

# Infrastructure Mapping
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

INFRA_DIR = Path('agentic_sdlc/infrastructure')

def reorganize_infra():
    # 1. Create Concern directories
    concerns = set(INFRA_MAPPING.values())
    for concern in concerns:
        (INFRA_DIR / concern).mkdir(exist_ok=True)
        (INFRA_DIR / concern / '__init__.py').touch()

    # 2. Move modules
    for mod, concern in INFRA_MAPPING.items():
        src = INFRA_DIR / mod
        dst = INFRA_DIR / concern / mod
        if src.exists() and src.is_dir():
            print(f"Moving infra {mod} -> {concern}/{mod}")
            if dst.exists():
                shutil.rmtree(dst)
            shutil.move(str(src), str(dst))

    # 3. Move MCP to infra/bridge
    mcp_src = Path('agentic_sdlc/mcp')
    mcp_dst = INFRA_DIR / 'bridge' / 'mcp'
    if mcp_src.exists():
        print(f"Moving mcp -> infra/bridge/mcp")
        if mcp_dst.exists():
            shutil.rmtree(mcp_dst)
        shutil.move(str(mcp_src), str(mcp_dst))

    # 4. Update all imports in agentic_sdlc
    root_dir = Path('agentic_sdlc')
    for py_file in root_dir.rglob('*.py'):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content
        
        # Infrastructure replacements
        for mod, concern in INFRA_MAPPING.items():
            # Absolute
            old_abs = f'agentic_sdlc.infrastructure.{mod}'
            new_abs = f'agentic_sdlc.infrastructure.{concern}.{mod}'
            new_content = new_content.replace(old_abs, new_abs)
            
            # Relative
            old_rel = f'from . import {mod}'
            new_rel = f'from .{concern} import {mod}'
            new_content = new_content.replace(old_rel, new_rel)

        # MCP replacements
        # from agentic_sdlc.mcp -> from agentic_sdlc.infrastructure.bridge.mcp
        new_content = new_content.replace('agentic_sdlc.mcp', 'agentic_sdlc.infrastructure.bridge.mcp')
        # from agentic_sdlc import mcp -> from agentic_sdlc.infrastructure.bridge import mcp? 
        # Actually standard is absolute imports usually.

        if new_content != content:
            print(f"Updating imports in {py_file}")
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

if __name__ == "__main__":
    reorganize_infra()
