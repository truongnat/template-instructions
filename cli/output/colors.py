"""
Color and styling utilities for CLI output.

Provides ANSI color codes and styling functions for terminal output.
"""

from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    
    # Reset
    RESET = "\033[0m"
    
    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bold colors
    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_MAGENTA = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_WHITE = "\033[1;37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"


def colorize(text: str, color: str, bold: bool = False) -> str:
    """
    Apply color to text.
    
    Args:
        text: Text to colorize
        color: Color code from Colors class
        bold: Whether to make text bold
        
    Returns:
        Colorized text with reset code
    """
    style = Colors.BOLD if bold else ""
    return f"{style}{color}{text}{Colors.RESET}"


def success(text: str) -> str:
    """Format text as success (green)."""
    return colorize(text, Colors.GREEN)


def error(text: str) -> str:
    """Format text as error (red)."""
    return colorize(text, Colors.RED, bold=True)


def warning(text: str) -> str:
    """Format text as warning (yellow)."""
    return colorize(text, Colors.YELLOW)


def info(text: str) -> str:
    """Format text as info (blue)."""
    return colorize(text, Colors.BLUE)


def highlight(text: str) -> str:
    """Format text as highlighted (cyan, bold)."""
    return colorize(text, Colors.CYAN, bold=True)


def dim(text: str) -> str:
    """Format text as dimmed."""
    return f"{Colors.DIM}{text}{Colors.RESET}"


def bold(text: str) -> str:
    """Format text as bold."""
    return f"{Colors.BOLD}{text}{Colors.RESET}"


def underline(text: str) -> str:
    """Format text as underlined."""
    return f"{Colors.UNDERLINE}{text}{Colors.RESET}"
