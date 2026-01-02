"""
Common utilities for KB operations
Cross-platform helper functions
"""

import os
import re
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class KBConfig:
    """KB configuration"""
    def __init__(self):
        self.root_dir = Path.cwd()
        self.kb_path = self.root_dir / ".agent" / "knowledge-base"
        self.docs_path = self.root_dir / "docs"
        self.index_path = self.kb_path / "INDEX.md"
        self.platform = platform.system()
    
    def get_kb_path(self) -> Path:
        """Get KB path"""
        return self.kb_path
    
    def get_docs_path(self) -> Path:
        """Get docs path"""
        return self.docs_path
    
    def get_all_kb_paths(self) -> List[Path]:
        """Get all knowledge base paths (KB + docs)"""
        return [self.kb_path, self.docs_path]
    
    def get_index_path(self) -> Path:
        """Get INDEX.md path"""
        return self.index_path
    
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return self.platform == 'Windows'
    
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        return self.platform == 'Linux'
    
    def is_macos(self) -> bool:
        """Check if running on macOS"""
        return self.platform == 'Darwin'


class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    @staticmethod
    def enable_windows():
        """Enable ANSI colors on Windows"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass


def parse_frontmatter(content: str) -> Dict:
    """Parse YAML frontmatter from markdown"""
    metadata = {}
    
    # Extract frontmatter
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        
        # Parse simple YAML
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                # Handle arrays
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                
                metadata[key] = value
    
    return metadata


def get_kb_entries(kb_path: Path, pattern: str = "KB-*.md") -> List[Path]:
    """Get all KB entries"""
    return list(kb_path.rglob(pattern))


def get_all_kb_entries(paths: List[Path]) -> List[Path]:
    """Get all KB entries from multiple paths"""
    entries = []
    for path in paths:
        if path.exists():
            # Get KB-*.md files from knowledge-base
            if path.name == "knowledge-base":
                entries.extend(list(path.rglob("KB-*.md")))
            
            # Get all markdown files from docs/ (excluding sprints)
            elif path.name == "docs":
                for md_file in path.rglob("*.md"):
                    # Skip sprint artifacts
                    if "sprints" in str(md_file):
                        continue
                    entries.append(md_file)
    
    return entries


def format_time_ago(file_path: Path) -> str:
    """Format time ago string"""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    now = datetime.now()
    delta = now - mtime
    
    days = delta.days
    if days == 0:
        return "Today"
    elif days == 1:
        return "Yesterday"
    else:
        return f"{days} days ago"


def get_priority_icon(priority: str) -> str:
    """Get priority icon"""
    icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    return icons.get(priority.lower(), '⚪')


def get_category_icon(category: str) -> str:
    """Get category icon"""
    icons = {
        'bug': '🐛',
        'feature': '✨',
        'architecture': '🏗️',
        'security': '🔒',
        'performance': '⚡',
        'platform': '💻'
    }
    return icons.get(category.lower(), '📄')


def print_separator(char='━', length=60, color=Colors.CYAN):
    """Print separator line"""
    print(f"{color}{char * length}{Colors.RESET}")


def print_header(title: str, subtitle: str = None):
    """Print section header"""
    Colors.enable_windows()
    print_separator()
    print(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")
    if subtitle:
        print(f"{Colors.MAGENTA}   {subtitle}{Colors.RESET}")
    print_separator()
    print()


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")
