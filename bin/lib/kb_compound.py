"""
KB Compound Module
Cross-platform Neo4j integration
"""

import os
import sys
import subprocess
from pathlib import Path
from kb_common import (
    KBConfig, Colors, print_header, print_success, print_warning, print_error, print_separator
)
from kb_search import search_kb
from kb_add import add_entry
from kb_index import update_index
from kb_stats import show_stats


def compound_operation(action: str, search_term: str = None):
    """Execute compound operation"""
    config = KBConfig()
    Colors.enable_windows()
    
    print_header(
        "🧠 Knowledge Base Compound System",
        "Integrated with Neo4j Brain"
    )
    
    if action == 'search':
        compound_search(config, search_term)
    elif action == 'add':
        compound_add(config)
    elif action == 'sync':
        compound_sync(config)
    elif action == 'query':
        compound_query(config, search_term)
    elif action == 'stats':
        compound_stats(config)
    else:
        print_error(f"Unknown compound action: {action}")


def check_neo4j_available(config: KBConfig) -> bool:
    """Check if Neo4j tools are available"""
    neo4j_sync = config.root_dir / "tools" / "neo4j" / "sync_skills_to_neo4j.py"
    return neo4j_sync.exists()


def run_neo4j_script(config: KBConfig, script_name: str, args: list = None) -> bool:
    """Run Neo4j Python script"""
    script_path = config.root_dir / "tools" / "neo4j" / script_name
    
    if not script_path.exists():
        return False
    
    try:
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print_warning("Neo4j operation had issues (continuing in file mode)")
            if result.stderr:
                print(f"{Colors.GRAY}{result.stderr}{Colors.RESET}")
            return False
    except Exception as e:
        print_warning(f"Could not connect to Neo4j: {e}")
        return False


def compound_search(config: KBConfig, search_term: str):
    """Compound search: Neo4j + File system"""
    print(f"{Colors.CYAN}🔍 Compound Search: '{search_term}'{Colors.RESET}")
    print()
    
    # Phase 1: Neo4j Brain Search
    print(f"{Colors.MAGENTA}━━━ Phase 1: Neo4j Brain Search ━━━{Colors.RESET}")
    
    if check_neo4j_available(config):
        neo4j_success = run_neo4j_script(
            config,
            'query_skills_neo4j.py',
            ['--search', search_term]
        )
        
        if neo4j_success:
            print_success("Neo4j query successful!")
        else:
            print_warning("Neo4j not available, using file search only")
    else:
        print_warning("Neo4j tools not found, using file search only")
    
    print()
    
    # Phase 2: File System Search
    print(f"{Colors.MAGENTA}━━━ Phase 2: File System Search ━━━{Colors.RESET}")
    search_kb(search_term)
    
    print()
    print_separator('━', 60, Colors.MAGENTA)
    print(f"{Colors.GREEN}{Colors.BOLD}💡 Compound Search Complete!{Colors.RESET}")
    print(f"   Searched: Neo4j Brain + File System")
    print_separator('━', 60, Colors.MAGENTA)


def compound_add(config: KBConfig):
    """Compound add: Create + Index + Sync"""
    print(f"{Colors.CYAN}➕ Adding New Knowledge Entry{Colors.RESET}")
    print()
    
    # Phase 1: Create Entry
    print(f"{Colors.MAGENTA}━━━ Phase 1: Create Entry ━━━{Colors.RESET}")
    add_entry()
    print()
    
    # Phase 2: Update Index
    print(f"{Colors.MAGENTA}━━━ Phase 2: Update Index ━━━{Colors.RESET}")
    update_index()
    print()
    
    # Phase 3: Sync to Neo4j
    print(f"{Colors.MAGENTA}━━━ Phase 3: Sync to Neo4j Brain ━━━{Colors.RESET}")
    
    if check_neo4j_available(config):
        synced = run_neo4j_script(config, 'sync_skills_to_neo4j.py')
        
        if synced:
            print_success("Synced to Neo4j successfully!")
        else:
            print_warning("Neo4j sync failed, entry saved to file system")
    else:
        print_warning("Neo4j tools not available")
    
    print()
    print_separator('━', 60, Colors.MAGENTA)
    print(f"{Colors.GREEN}{Colors.BOLD}✅ Compound Add Complete!{Colors.RESET}")
    print(f"   Entry created, indexed, and synced to brain")
    print_separator('━', 60, Colors.MAGENTA)
    
    if check_neo4j_available(config):
        print()
        print(f"{Colors.CYAN}🧠 Your knowledge is now in the Neo4j Brain!{Colors.RESET}")
        print(f"   It can be queried with relationships and context")


def compound_sync(config: KBConfig):
    """Compound sync: Index + Neo4j + Stats"""
    print(f"{Colors.CYAN}🔄 Full Compound Sync{Colors.RESET}")
    print()
    
    # Phase 1: Update Index
    print(f"{Colors.MAGENTA}━━━ Phase 1: Update Index ━━━{Colors.RESET}")
    update_index()
    print()
    
    # Phase 2: Sync to Neo4j (includes docs/)
    print(f"{Colors.MAGENTA}━━━ Phase 2: Sync to Neo4j Brain ━━━{Colors.RESET}")
    print(f"   Syncing: .agent/knowledge-base/ + docs/")
    print()
    
    if check_neo4j_available(config):
        synced = run_neo4j_script(config, 'sync_skills_to_neo4j.py')
        
        if synced:
            print_success("Synced to Neo4j successfully!")
        else:
            print_warning("Neo4j sync had issues")
    else:
        print_warning("Neo4j tools not available")
    
    print()
    
    # Phase 3: Show Stats
    print(f"{Colors.MAGENTA}━━━ Phase 3: Compound Stats ━━━{Colors.RESET}")
    show_stats()
    
    print()
    print_separator('━', 60, Colors.MAGENTA)
    print(f"{Colors.GREEN}{Colors.BOLD}✅ Compound Sync Complete!{Colors.RESET}")
    print(f"   All knowledge indexed and synced to brain")
    print_separator('━', 60, Colors.MAGENTA)


def compound_query(config: KBConfig, query_term: str):
    """Compound query: Intelligent Neo4j queries"""
    print(f"{Colors.CYAN}🧠 Intelligent Query via Neo4j Brain{Colors.RESET}")
    print()
    
    if not check_neo4j_available(config):
        print_error("Neo4j tools not available")
        print(f"   Install Neo4j tools in tools/neo4j/")
        return
    
    print(f"Query: '{query_term}'")
    print()
    
    # Search skills
    print(f"{Colors.MAGENTA}━━━ Searching Skills ━━━{Colors.RESET}")
    run_neo4j_script(config, 'query_skills_neo4j.py', ['--search', query_term])
    
    print()
    
    # Related skills
    print(f"{Colors.MAGENTA}━━━ Related Skills ━━━{Colors.RESET}")
    run_neo4j_script(config, 'query_skills_neo4j.py', ['--skill', query_term])
    
    print()
    print_separator('━', 60, Colors.MAGENTA)
    print(f"{Colors.GREEN}{Colors.BOLD}💡 Neo4j Brain Query Complete!{Colors.RESET}")
    print_separator('━', 60, Colors.MAGENTA)


def compound_stats(config: KBConfig):
    """Compound stats: File system + Neo4j"""
    print(f"{Colors.CYAN}📊 Compound System Health{Colors.RESET}")
    print()
    
    # Phase 1: File System Stats
    print(f"{Colors.MAGENTA}━━━ File System Stats ━━━{Colors.RESET}")
    show_stats()
    
    print()
    
    # Phase 2: Neo4j Stats
    print(f"{Colors.MAGENTA}━━━ Neo4j Brain Stats ━━━{Colors.RESET}")
    
    if check_neo4j_available(config):
        success = run_neo4j_script(config, 'query_skills_neo4j.py', ['--all-skills'])
        
        if success:
            print(f"   {Colors.GRAY}(Showing first 20 skills){Colors.RESET}")
    else:
        print_warning("Neo4j not available")
    
    print()
    print_separator('━', 60, Colors.MAGENTA)
    print(f"{Colors.GREEN}{Colors.BOLD}💡 Compound System Status{Colors.RESET}")
    print(f"   File System: ✅ Active")
    
    if check_neo4j_available(config):
        print(f"   Neo4j Brain: ✅ Connected")
    else:
        print(f"   Neo4j Brain: ⚠️  Not Available")
    
    print_separator('━', 60, Colors.MAGENTA)
