#!/usr/bin/env python3
"""Script to automatically fix common documentation issues.

This script fixes:
1. Missing language specifications in code blocks
2. Adds metadata (version and last updated) where missing
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def fix_code_blocks(content: str) -> tuple[str, int]:
    """Fix code blocks missing language specification.
    
    Args:
        content: Document content
        
    Returns:
        Tuple of (fixed content, number of fixes)
    """
    fixes = 0
    
    # Find code blocks without language specification
    def replace_code_block(match):
        nonlocal fixes
        code = match.group(1)
        
        # Try to detect language from content
        if 'import ' in code or 'def ' in code or 'class ' in code:
            lang = 'python'
        elif 'function' in code or 'const ' in code or 'let ' in code:
            lang = 'javascript'
        elif '#!/bin/bash' in code or 'echo ' in code:
            lang = 'bash'
        elif 'graph ' in code or 'sequenceDiagram' in code:
            lang = 'mermaid'
        else:
            lang = 'text'
        
        fixes += 1
        return f'```{lang}\n{code}```'
    
    # Replace code blocks without language
    fixed = re.sub(r'```\n(.*?)```', replace_code_block, content, flags=re.DOTALL)
    
    return fixed, fixes


def add_metadata(content: str, file_path: Path) -> tuple[str, bool]:
    """Add version and last updated metadata if missing.
    
    Args:
        content: Document content
        file_path: Path to the document
        
    Returns:
        Tuple of (fixed content, whether changes were made)
    """
    # Check if metadata already exists
    has_version = re.search(r'\*\*Phiên bản\*\*:', content) or \
                 re.search(r'\*\*Version\*\*:', content)
    has_updated = re.search(r'\*\*Cập nhật lần cuối\*\*:', content) or \
                 re.search(r'\*\*Last Updated\*\*:', content)
    
    if has_version and has_updated:
        return content, False
    
    # Find the title (first H1)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if not title_match:
        return content, False
    
    title_end = title_match.end()
    
    # Build metadata section
    metadata_lines = []
    if not has_version:
        metadata_lines.append('**Phiên bản**: 3.0.0')
    if not has_updated:
        today = datetime.now().strftime('%d/%m/%Y')
        metadata_lines.append(f'**Cập nhật lần cuối**: {today}')
    
    if not metadata_lines:
        return content, False
    
    metadata = '\n\n' + '  \n'.join(metadata_lines) + '\n'
    
    # Insert metadata after title
    fixed = content[:title_end] + metadata + content[title_end:]
    
    return fixed, True


def fix_document(file_path: Path) -> dict:
    """Fix issues in a single document.
    
    Args:
        file_path: Path to the document
        
    Returns:
        Dictionary with fix statistics
    """
    stats = {
        'code_blocks_fixed': 0,
        'metadata_added': False,
        'errors': []
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Fix code blocks
        content, code_fixes = fix_code_blocks(content)
        stats['code_blocks_fixed'] = code_fixes
        
        # Add metadata
        content, metadata_added = add_metadata(content, file_path)
        stats['metadata_added'] = metadata_added
        
        # Write back if changes were made
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            
    except Exception as e:
        stats['errors'].append(str(e))
    
    return stats


def main():
    """Fix all documentation files."""
    docs_root = Path(__file__).parent.parent / "docs" / "vi"
    
    if not docs_root.exists():
        print(f"Error: Documentation directory not found: {docs_root}")
        sys.exit(1)
    
    print(f"Fixing documentation issues in: {docs_root}")
    print("=" * 80)
    
    # Find all markdown files
    md_files = list(docs_root.rglob("*.md"))
    print(f"\nProcessing {len(md_files)} markdown files...")
    
    total_code_fixes = 0
    total_metadata_added = 0
    files_with_errors = []
    
    for md_file in md_files:
        relative_path = md_file.relative_to(docs_root)
        stats = fix_document(md_file)
        
        if stats['code_blocks_fixed'] > 0 or stats['metadata_added']:
            fixes = []
            if stats['code_blocks_fixed'] > 0:
                fixes.append(f"{stats['code_blocks_fixed']} code blocks")
                total_code_fixes += stats['code_blocks_fixed']
            if stats['metadata_added']:
                fixes.append("metadata")
                total_metadata_added += 1
            
            print(f"✓ {relative_path}: Fixed {', '.join(fixes)}")
        
        if stats['errors']:
            files_with_errors.append((relative_path, stats['errors']))
    
    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"- Code blocks fixed: {total_code_fixes}")
    print(f"- Files with metadata added: {total_metadata_added}")
    
    if files_with_errors:
        print(f"\n⚠️  Files with errors: {len(files_with_errors)}")
        for file_path, errors in files_with_errors:
            print(f"  - {file_path}: {', '.join(errors)}")
    else:
        print("\n✓ All files processed successfully!")


if __name__ == "__main__":
    main()
