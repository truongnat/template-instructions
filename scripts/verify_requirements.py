#!/usr/bin/env python3
"""
Verify requirements.txt and requirements-dev.txt files.

This script checks that:
1. Requirements files exist
2. Requirements files are properly formatted
3. No duplicate packages are listed
4. All package names are valid
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Set


def parse_requirements_file(filepath: Path) -> Tuple[List[str], List[str]]:
    """
    Parse a requirements file and return packages and errors.
    
    Args:
        filepath: Path to requirements file
        
    Returns:
        Tuple of (packages, errors)
    """
    packages = []
    errors = []
    
    if not filepath.exists():
        errors.append(f"File not found: {filepath}")
        return packages, errors
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Skip -r includes
            if line.startswith('-r '):
                continue
            
            # Basic validation of package line
            # Format: package==version or package>=version or package
            if not re.match(r'^[a-zA-Z0-9_\-\[\]]+([><=!]+[0-9\.]+.*)?$', line):
                errors.append(f"Line {line_num}: Invalid format: {line}")
                continue
            
            # Extract package name (before any version specifier)
            package_name = re.split(r'[><=!]', line)[0].strip()
            packages.append(package_name.lower())
    
    return packages, errors


def check_duplicates(packages: List[str]) -> List[str]:
    """Check for duplicate packages."""
    seen: Set[str] = set()
    duplicates = []
    
    for pkg in packages:
        if pkg in seen:
            duplicates.append(pkg)
        seen.add(pkg)
    
    return duplicates


def main():
    """Main verification function."""
    print("Verifying requirements files...")
    print("=" * 60)
    
    all_errors = []
    
    # Check requirements.txt
    print("\n1. Checking requirements.txt...")
    req_file = Path("requirements.txt")
    packages, errors = parse_requirements_file(req_file)
    
    if errors:
        all_errors.extend(errors)
        for error in errors:
            print(f"  ✗ {error}")
    else:
        print(f"  ✓ File format is valid")
        print(f"  ✓ Found {len(packages)} packages")
    
    # Check for duplicates
    duplicates = check_duplicates(packages)
    if duplicates:
        all_errors.append(f"Duplicate packages in requirements.txt: {', '.join(duplicates)}")
        print(f"  ✗ Found duplicate packages: {', '.join(duplicates)}")
    else:
        print(f"  ✓ No duplicate packages")
    
    # Check requirements-dev.txt
    print("\n2. Checking requirements-dev.txt...")
    dev_file = Path("requirements-dev.txt")
    dev_packages, dev_errors = parse_requirements_file(dev_file)
    
    if dev_errors:
        all_errors.extend(dev_errors)
        for error in dev_errors:
            print(f"  ✗ {error}")
    else:
        print(f"  ✓ File format is valid")
        print(f"  ✓ Found {len(dev_packages)} additional dev packages")
    
    # Check for duplicates in dev file
    dev_duplicates = check_duplicates(dev_packages)
    if dev_duplicates:
        all_errors.append(f"Duplicate packages in requirements-dev.txt: {', '.join(dev_duplicates)}")
        print(f"  ✗ Found duplicate packages: {', '.join(dev_duplicates)}")
    else:
        print(f"  ✓ No duplicate packages")
    
    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print(f"❌ Verification FAILED with {len(all_errors)} error(s)")
        for error in all_errors:
            print(f"  - {error}")
        return 1
    else:
        print("✅ All requirements files are valid!")
        print(f"\nSummary:")
        print(f"  - Core dependencies: {len(packages)}")
        print(f"  - Dev dependencies: {len(dev_packages)}")
        print(f"  - Total unique packages: {len(set(packages + dev_packages))}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
