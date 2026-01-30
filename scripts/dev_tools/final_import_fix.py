
import os
from pathlib import Path

def fix_doubled_imports(root_dir):
    root = Path(root_dir)
    concerns = ['monitoring', 'reasoning', 'learning', 'collaborating', 'bridge', 'engine', 'automation', 'lifecycle']
    
    for py_file in root.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            changed = False
            for line in lines:
                new_line = line
                for concern in concerns:
                    # Fix absolute imports
                    bad = f'intelligence.{concern}.{concern}'
                    if bad in new_line:
                        new_line = new_line.replace(bad, f'intelligence.{concern}')
                        changed = True
                    
                    bad_infra = f'infrastructure.{concern}.{concern}'
                    if bad_infra in new_line:
                        new_line = new_line.replace(bad_infra, f'infrastructure.{concern}')
                        changed = True

                new_lines.append(new_line)
            
            if changed:
                print(f"Fixed doubled imports in {py_file}")
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
        except Exception as e:
            # Skip files with permission issues
            pass

if __name__ == "__main__":
    fix_doubled_imports('agentic_sdlc')
    fix_doubled_imports('tests')
    fix_doubled_imports('bin')
