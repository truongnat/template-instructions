"""
AutoGen Tools Registry Module

Wraps existing project tools as AutoGen-compatible functions.
These tools allow agents to interact with the filesystem and execute commands.
"""

import subprocess
import os
from pathlib import Path
from typing import Annotated

# Project root for relative path resolution
PROJECT_ROOT = Path(__file__).parent.parent.parent


def read_file(
    file_path: Annotated[str, "Absolute or relative path to the file to read"]
) -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file (absolute or relative to project root)
    
    Returns:
        File contents as string, or error message
    """
    try:
        path = Path(file_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        
        if not path.exists():
            return f"Error: File not found: {path}"
        
        if not path.is_file():
            return f"Error: Not a file: {path}"
        
        content = path.read_text(encoding="utf-8")
        
        # Truncate very long files
        max_chars = 10000
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... [Truncated, {len(content)} total chars]"
        
        return content
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(
    file_path: Annotated[str, "Path to the file to write"],
    content: Annotated[str, "Content to write to the file"]
) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file (absolute or relative to project root)
        content: Content to write
    
    Returns:
        Success message or error
    """
    try:
        path = Path(file_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote {len(content)} chars to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def list_directory(
    dir_path: Annotated[str, "Path to the directory to list"] = "."
) -> str:
    """
    List contents of a directory.
    
    Args:
        dir_path: Path to directory (defaults to project root)
    
    Returns:
        Directory listing or error
    """
    try:
        path = Path(dir_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        
        if not path.exists():
            return f"Error: Directory not found: {path}"
        
        if not path.is_dir():
            return f"Error: Not a directory: {path}"
        
        items = []
        for item in sorted(path.iterdir()):
            prefix = "[DIR] " if item.is_dir() else "[FILE]"
            items.append(f"{prefix} {item.name}")
        
        if not items:
            return f"Directory is empty: {path}"
        
        return f"Contents of {path}:\n" + "\n".join(items[:50])  # Limit to 50 items
    except Exception as e:
        return f"Error listing directory: {e}"


def search_in_files(
    pattern: Annotated[str, "Text pattern to search for"],
    search_path: Annotated[str, "Path to search in (file or directory)"] = "."
) -> str:
    """
    Search for a pattern in files using grep-like functionality.
    
    Args:
        pattern: Text pattern to search for
        search_path: Path to search in
    
    Returns:
        Matching lines with file:line format, or error
    """
    try:
        path = Path(search_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        
        results = []
        
        def search_file(file_path: Path):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for i, line in enumerate(content.split("\n"), 1):
                    if pattern.lower() in line.lower():
                        results.append(f"{file_path.relative_to(PROJECT_ROOT)}:{i}: {line.strip()[:100]}")
            except Exception:
                pass
        
        if path.is_file():
            search_file(path)
        elif path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix in (".py", ".js", ".ts", ".md", ".json", ".yaml", ".yml"):
                    search_file(file_path)
                    if len(results) >= 50:  # Limit results
                        break
        
        if not results:
            return f"No matches found for '{pattern}' in {path}"
        
        return f"Found {len(results)} matches:\n" + "\n".join(results)
    except Exception as e:
        return f"Error searching: {e}"


def run_command(
    command: Annotated[str, "Shell command to execute"],
    working_dir: Annotated[str, "Working directory for the command"] = "."
) -> str:
    """
    Execute a shell command and return output.
    
    Args:
        command: Command to run
        working_dir: Working directory
    
    Returns:
        Command output or error
    """
    try:
        cwd = Path(working_dir)
        if not cwd.is_absolute():
            cwd = PROJECT_ROOT / cwd
        
        # Safety check - block dangerous commands
        dangerous = ["rm -rf", "del /", "format", "mkfs", ":(){", "dd if="]
        if any(d in command.lower() for d in dangerous):
            return "Error: Command blocked for safety reasons"
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]: {result.stderr}"
        
        if result.returncode != 0:
            output += f"\n[Exit code: {result.returncode}]"
        
        # Truncate long output
        if len(output) > 5000:
            output = output[:5000] + "\n... [Truncated]"
        
        return output if output.strip() else "[No output]"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds"
    except Exception as e:
        return f"Error running command: {e}"


def run_python_test(
    test_path: Annotated[str, "Path to test file or directory"] = "tests"
) -> str:
    """
    Run pytest on the specified path.
    
    Args:
        test_path: Path to test file or directory
    
    Returns:
        Test results
    """
    return run_command(f"python -m pytest {test_path} -v --tb=short")


# List of all available tools for registration
AVAILABLE_TOOLS = [
    read_file,
    write_file,
    list_directory,
    search_in_files,
    run_command,
    run_python_test,
]


def get_tools_for_role(role: str) -> list:
    """
    Get appropriate tools based on agent role.
    
    Args:
        role: Agent role (dev, tester, orchestrator)
    
    Returns:
        List of tool functions
    """
    role = role.lower()
    
    if role in ("dev", "developer"):
        return [read_file, write_file, list_directory, search_in_files, run_command]
    elif role in ("tester", "qa"):
        return [read_file, list_directory, search_in_files, run_python_test, run_command]
    elif role in ("orchestrator", "coordinator"):
        return [read_file, list_directory, search_in_files]
    else:
        return AVAILABLE_TOOLS
