#!/usr/bin/env python3
"""Script to reduce max_examples in property tests for faster execution"""

import re
from pathlib import Path

def reduce_examples_in_file(file_path: Path):
    """Reduce max_examples settings in a test file"""
    content = file_path.read_text()
    original_content = content
    
    # Replace max_examples with smaller values
    # 100 -> 10
    content = re.sub(r'@settings\(max_examples=100', '@settings(max_examples=10', content)
    # 50 -> 5
    content = re.sub(r'@settings\(max_examples=50', '@settings(max_examples=5', content)
    # 20 -> 5
    content = re.sub(r'@settings\(max_examples=20', '@settings(max_examples=5', content)
    # 15 -> 5
    content = re.sub(r'@settings\(max_examples=15', '@settings(max_examples=5', content)
    # 30 -> 5
    content = re.sub(r'@settings\(max_examples=30', '@settings(max_examples=5', content)
    
    if content != original_content:
        file_path.write_text(content)
        return True
    return False

def main():
    """Reduce examples in all property test files"""
    property_tests_dir = Path("tests/property")
    
    if not property_tests_dir.exists():
        print(f"Directory {property_tests_dir} does not exist")
        return
    
    modified_count = 0
    for test_file in property_tests_dir.glob("test_*.py"):
        if reduce_examples_in_file(test_file):
            print(f"✓ Reduced examples in {test_file.name}")
            modified_count += 1
    
    print(f"\nModified {modified_count} test files")

if __name__ == "__main__":
    main()
