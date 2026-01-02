"""
KB Search Module
Cross-platform search functionality
"""

import re
from pathlib import Path
from typing import List, Dict
from kb_common import (
    KBConfig, Colors, parse_frontmatter, get_kb_entries, get_all_kb_entries,
    print_header, print_success, print_warning, get_priority_icon
)


def search_kb(search_term: str):
    """Search knowledge base"""
    config = KBConfig()
    Colors.enable_windows()
    
    print_header(
        f"🔍 Searching Knowledge Base for: '{search_term}'",
        "File System Search"
    )
    
    # Search INDEX.md first
    results_from_index = search_index(config, search_term)
    
    # Search all KB files
    results_from_files = search_files(config, search_term)
    
    # Display results
    total_results = len(results_from_index) + len(results_from_files)
    
    if total_results == 0:
        print_warning(f"No results found for '{search_term}'")
        print()
        print(f"{Colors.CYAN}💡 Tips:{Colors.RESET}")
        print(f"   - Try different keywords")
        print(f"   - Use broader search terms")
        print(f"   - Check spelling")
        print(f"   - Try compound search: {Colors.MAGENTA}kb compound search '{search_term}'{Colors.RESET}")
    else:
        print()
        print(f"{Colors.GREEN}📊 Search Results: {total_results} entries found{Colors.RESET}")
    
    print()


def search_index(config: KBConfig, search_term: str) -> List[str]:
    """Search INDEX.md"""
    if not config.get_index_path().exists():
        return []
    
    content = config.get_index_path().read_text(encoding='utf-8')
    results = []
    
    # Search for term in index
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    
    for line in content.split('\n'):
        if pattern.search(line) and line.strip().startswith('-'):
            results.append(line.strip())
    
    if results:
        print(f"{Colors.GREEN}✅ Found in INDEX:{Colors.RESET}")
        for result in results[:5]:  # Show first 5
            print(f"  {result}")
        print()
    
    return results


def search_files(config: KBConfig, search_term: str) -> List[Dict]:
    """Search all KB files (KB + docs)"""
    all_paths = config.get_all_kb_paths()
    entries = get_all_kb_entries(all_paths)
    
    results = []
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    
    for entry_path in entries:
        try:
            content = entry_path.read_text(encoding='utf-8')
            
            # Check if term is in content
            if pattern.search(content):
                metadata = parse_frontmatter(content)
                
                # Extract context (line with match)
                context_lines = []
                for line in content.split('\n'):
                    if pattern.search(line):
                        context_lines.append(line.strip())
                        if len(context_lines) >= 3:
                            break
                
                results.append({
                    'path': entry_path,
                    'title': metadata.get('title', 'Unknown'),
                    'category': metadata.get('category', 'unknown'),
                    'priority': metadata.get('priority', 'unknown'),
                    'context': context_lines
                })
        except Exception as e:
            continue
    
    # Display file results
    if results:
        for i, result in enumerate(results, 1):
            icon = get_priority_icon(result['priority'])
            print(f"{Colors.GREEN}✅ Found: {result['title']}{Colors.RESET}")
            print(f"   {icon} File: {result['path'].relative_to(config.root_dir)}")
            print(f"   Category: {result['category']} | Priority: {result['priority']}")
            
            if result['context']:
                print(f"   {Colors.CYAN}Context:{Colors.RESET}")
                for ctx in result['context'][:2]:
                    print(f"     {ctx[:80]}...")
            print()
    
    return results
