
import os
from pathlib import Path

CONCERNS = ['monitoring', 'reasoning', 'learning', 'collaborating', 'bridge', 'engine', 'lifecycle', 'automation']

def fix_corruption(target_path):
    target_dir = Path(target_path)
    if not target_dir.exists():
        return

    for py_file in target_dir.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # Fix double concern prefixing
            for concern in CONCERNS:
                # agentic_sdlc.intelligence.monitoring.monitoring.judge -> agentic_sdlc.intelligence.monitoring.judge
                # Note: we need to be careful. if concern is 'monitoring' and next is 'monitor'?
                # Actually most doubling happened because 'monitoring' contains 'monitor'.
                
                bad_pattern = f'agentic_sdlc.intelligence.{concern}.{concern}'
                good_pattern = f'agentic_sdlc.intelligence.{concern}'
                new_content = new_content.replace(bad_pattern, good_pattern)
                
                # Also for infrastructure
                bad_infra = f'agentic_sdlc.infrastructure.{concern}.{concern}'
                good_infra = f'agentic_sdlc.infrastructure.{concern}'
                new_content = new_content.replace(bad_infra, good_infra)
                
                # Also for relative imports
                bad_rel = f'from .{concern}.{concern}'
                good_rel = f'from .{concern}'
                new_content = new_content.replace(bad_rel, good_rel)

            if new_content != content:
                print(f"Fixing corruption in {py_file}")
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

if __name__ == "__main__":
    fix_corruption('agentic_sdlc')
    fix_corruption('bin')
    fix_corruption('tests')
