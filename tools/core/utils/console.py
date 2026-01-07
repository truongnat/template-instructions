#!/usr/bin/env python3
"""
Console utilities for workflow scripts.
Re-exports from common.py and adds additional helpers.
"""

from .common import (
    print_header,
    print_success,
    print_error,
    print_warning,
    print_info,
    Colors,
)


def print_step(step_num, title):
    """Print a numbered step."""
    print(f"{Colors.BOLD}{Colors.CYAN}Step {step_num}: {title}{Colors.ENDC}")


def print_checklist(items, checked=None):
    """Print a checklist of items."""
    checked = checked or set()
    for item in items:
        symbol = "[x]" if item in checked else "[ ]"
        print(f"   {symbol} {item}")


__all__ = [
    'print_header',
    'print_success',
    'print_error',
    'print_warning',
    'print_info',
    'print_step',
    'print_checklist',
    'Colors',
]
