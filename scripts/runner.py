import subprocess
import os
from pathlib import Path

def run_and_save(cmd, filename):
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\nRETURN CODE: {result.returncode}\n")
        print(f"Saved to {filename}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_and_save("python agentic_sdlc/infrastructure/release/release.py preview", "debug_release_real.txt")
