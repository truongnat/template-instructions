#!/usr/bin/env python3
"""
Common utility functions for agent scripts
Cross-platform compatible with Windows encoding support
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
# if sys.platform == 'win32':
#     try:
#         sys.stdout.reconfigure(encoding='utf-8', errors='replace')
#         sys.stderr.reconfigure(encoding='utf-8', errors='replace')
#     except (AttributeError, OSError):
#         pass

# Symbols with ASCII fallback
def _get_symbol(unicode_char, ascii_fallback):
    try:
        unicode_char.encode(sys.stdout.encoding or 'utf-8')
        return unicode_char
    except (UnicodeEncodeError, LookupError):
        return ascii_fallback

SYM_CHECK = _get_symbol('✓', '[OK]')
SYM_CROSS = _get_symbol('✗', '[ERR]')
SYM_WARN = _get_symbol('⚠', '[WARN]')
SYM_INFO = _get_symbol('ℹ', '[INFO]')


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass


def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    print(f"{Colors.GREEN}{SYM_CHECK} {message}{Colors.ENDC}")


def print_error(message):
    print(f"{Colors.RED}{SYM_CROSS} {message}{Colors.ENDC}", file=sys.stderr)


def print_warning(message):
    print(f"{Colors.YELLOW}{SYM_WARN} {message}{Colors.ENDC}")


def print_info(message):
    print(f"{Colors.BLUE}{SYM_INFO} {message}{Colors.ENDC}")


def get_project_root():
    """
    Get project root directory by searching for .agent directory or agentic.yaml.
    Starts from current working directory (runtime context).
    """
    current = Path.cwd().resolve()
    
    # Check current and parents
    for path in [current] + list(current.parents):
        if (path / '.agent').exists() or (path / 'agentic.yaml').exists():
            return path
            
    # Fallback to current working directory if no marker found
    return current

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)

def load_config():
    """
    Load project configuration from agentic.yaml or .agent/config.json.
    """
    root = get_project_root()
    
    # Priority 1: agentic.yaml
    yaml_config = root / 'agentic.yaml'
    if yaml_config.exists():
        try:
            import yaml
            with open(yaml_config, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            print_warning("PyYAML not installed, skipping agentic.yaml")
        except Exception as e:
            print_error(f"Error loading agentic.yaml: {e}")
    
    # Priority 2: .agent/config.json
    json_config = root / '.agent' / 'config.json'
    if json_config.exists():
        try:
            with open(json_config, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print_error(f"Error loading config.json: {e}")
    
    # Default config
    return {
        "project_name": root.name,
        "kb_enabled": True,
        "auto_compound": True
    }

def save_config(config):
    """Save project configuration to .agent/config.json"""
    root = get_project_root()
    config_dir = root / '.agent'
    ensure_dir(config_dir)
    
    config_file = config_dir / 'config.json'
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def get_timestamp():
    return datetime.now().isoformat()

def get_date():
    return datetime.now().strftime("%Y-%m-%d")

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print_error(f"Failed to read {filepath}: {str(e)}")
        return None

def write_file(filepath, content):
    try:
        ensure_dir(Path(filepath).parent)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print_error(f"Failed to write {filepath}: {str(e)}")
        return False

def append_file(filepath, content):
    try:
        ensure_dir(Path(filepath).parent)
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print_error(f"Failed to append to {filepath}: {str(e)}")
        return False

def list_files(directory, pattern="*"):
    try:
        return list(Path(directory).glob(pattern))
    except Exception as e:
        print_error(f"Failed to list files in {directory}: {str(e)}")
        return []

def file_exists(filepath):
    return Path(filepath).exists()

def confirm(message, default=False):
    default_str = "Y/n" if default else "y/N"
    response = input(f"{message} ({default_str}): ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']

def select_option(message, options):
    print(f"\n{message}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = input("\nSelect option (number): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(options):
                return options[index]
            else:
                print_error("Invalid option. Try again.")
        except ValueError:
            print_error("Please enter a number.")
        except KeyboardInterrupt:
            print_error("\nCancelled by user.")
            sys.exit(1)

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def truncate_string(text, max_length=80):
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


if __name__ == "__main__":
    print_header("Testing Common Utilities")
    print(f"\nProject root: {get_project_root()}")