#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Base CLI - Cross-platform
Supports Windows, Linux, and macOS

Usage:
    kb [command] [args]
    kb.bat [command] [args]  (Windows)
"""

import sys
import os
import platform
import argparse
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Add lib directory to path
SCRIPT_DIR = Path(__file__).parent
LIB_DIR = SCRIPT_DIR / "lib"
sys.path.insert(0, str(LIB_DIR))

# Import KB modules
try:
    from kb_search import search_kb
    from kb_add import add_entry
    from kb_index import update_index
    from kb_stats import show_stats
    from kb_list import list_entries
    from kb_compound import compound_operation
except ImportError as e:
    print(f"Error: Could not import KB modules: {e}")
    print(f"Make sure all required files are in {LIB_DIR}")
    sys.exit(1)


class Colors:
    """ANSI color codes that work cross-platform"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    @staticmethod
    def enable_windows_colors():
        """Enable ANSI colors on Windows"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass


def print_header():
    """Print CLI header"""
    Colors.enable_windows_colors()
    print(f"{Colors.CYAN}{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}📚 Knowledge Base - Command Line Interface{Colors.RESET}")
    print(f"{Colors.MAGENTA}   🧠 Integrated with Neo4j Brain{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print()


def print_help():
    """Print help message"""
    print_header()
    print(f"{Colors.WHITE}{Colors.BOLD}Usage:{Colors.RESET} kb [command] [args]")
    print()
    print(f"{Colors.YELLOW}{Colors.BOLD}Commands:{Colors.RESET}")
    print()
    print(f"  {Colors.WHITE}search <term>{Colors.RESET}        🔍 Search knowledge base")
    print(f"                          Example: kb search 'react hydration'")
    print()
    print(f"  {Colors.WHITE}add{Colors.RESET}                  ➕ Add new entry (interactive)")
    print(f"                          Example: kb add")
    print()
    print(f"  {Colors.WHITE}index{Colors.RESET}                📇 Update INDEX.md")
    print(f"                          Example: kb index")
    print()
    print(f"  {Colors.WHITE}stats{Colors.RESET}                📊 Show statistics")
    print(f"                          Example: kb stats")
    print()
    print(f"  {Colors.WHITE}list [category]{Colors.RESET}      📋 List all entries (optional: by category)")
    print(f"                          Example: kb list bugs")
    print()
    print(f"  {Colors.WHITE}recent [n]{Colors.RESET}           📅 Show recent entries (default: 10)")
    print(f"                          Example: kb recent 5")
    print()
    print(f"  {Colors.MAGENTA}{Colors.BOLD}compound <action>{Colors.RESET}    🧠 Compound mode with Neo4j integration")
    print(f"                          Example: kb compound search 'oauth'")
    print()
    print(f"  {Colors.WHITE}help{Colors.RESET}                 ❓ Show this help")
    print()
    print(f"{Colors.MAGENTA}{Colors.BOLD}Compound Actions:{Colors.RESET}")
    print(f"  compound search <term>  - Search both file system and Neo4j brain")
    print(f"  compound add            - Add entry and sync to Neo4j")
    print(f"  compound sync           - Full sync to Neo4j brain")
    print(f"  compound query <term>   - Intelligent Neo4j query")
    print(f"  compound stats          - Show compound system health")
    print()
    print(f"{Colors.YELLOW}{Colors.BOLD}Examples:{Colors.RESET}")
    print(f"  kb search oauth")
    print(f"  {Colors.MAGENTA}kb compound search oauth{Colors.RESET}")
    print(f"  kb add")
    print(f"  {Colors.MAGENTA}kb compound add{Colors.RESET}")
    print(f"  kb stats")
    print()
    print(f"{Colors.CYAN}{Colors.BOLD}💡 Quick Start:{Colors.RESET}")
    print(f"   1. Search before solving: {Colors.MAGENTA}kb compound search 'your problem'{Colors.RESET}")
    print(f"   2. Add after solving: {Colors.MAGENTA}kb compound add{Colors.RESET}")
    print(f"   3. Sync to brain: {Colors.MAGENTA}kb compound sync{Colors.RESET}")
    print()
    print(f"{Colors.MAGENTA}{Colors.BOLD}🧠 Neo4j Brain:{Colors.RESET}")
    print(f"   The compound mode connects KB to Neo4j for intelligent")
    print(f"   relationship mapping and contextual queries")
    print()


def main():
    """Main CLI entry point"""
    Colors.enable_windows_colors()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Knowledge Base CLI',
        add_help=False
    )
    parser.add_argument('command', nargs='?', default='help')
    parser.add_argument('args', nargs='*')
    
    args = parser.parse_args()
    command = args.command.lower()
    command_args = args.args
    
    try:
        # Execute command
        if command == 'help' or command == '-h' or command == '--help':
            print_help()
        
        elif command == 'search':
            if not command_args:
                print(f"{Colors.RED}❌ Search term required!{Colors.RESET}")
                print(f"{Colors.YELLOW}Usage: kb search 'term'{Colors.RESET}")
                sys.exit(1)
            search_term = ' '.join(command_args)
            search_kb(search_term)
        
        elif command == 'add':
            add_entry()
        
        elif command == 'index':
            update_index()
        
        elif command == 'stats':
            show_stats()
        
        elif command == 'list':
            category = command_args[0] if command_args else None
            list_entries(category)
        
        elif command == 'recent':
            count = int(command_args[0]) if command_args else 10
            list_entries(recent=count)
        
        elif command == 'compound':
            if not command_args:
                print(f"{Colors.RED}❌ Compound action required!{Colors.RESET}")
                print(f"{Colors.YELLOW}Usage: kb compound [search|add|sync|query|stats]{Colors.RESET}")
                sys.exit(1)
            
            action = command_args[0].lower()
            action_args = command_args[1:] if len(command_args) > 1 else []
            
            if action in ['search', 'query'] and not action_args:
                print(f"{Colors.RED}❌ Search/Query term required!{Colors.RESET}")
                sys.exit(1)
            
            search_term = ' '.join(action_args) if action_args else None
            compound_operation(action, search_term)
        
        else:
            print(f"{Colors.RED}❌ Unknown command: {command}{Colors.RESET}")
            print()
            print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Operation cancelled by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
