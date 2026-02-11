#!/usr/bin/env python3
"""Script to validate all generated documentation.

This script runs the DocumentValidator on all documentation files
and generates a validation report.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_sdlc.documentation.validator import DocumentValidator


def main():
    """Run validation on all documentation."""
    docs_root = Path(__file__).parent.parent / "docs" / "vi"
    
    if not docs_root.exists():
        print(f"Error: Documentation directory not found: {docs_root}")
        sys.exit(1)
    
    print(f"Validating documentation in: {docs_root}")
    print("=" * 80)
    
    # Create validator
    validator = DocumentValidator(str(docs_root))
    
    # Validate all documents
    print(f"\nScanning {len(validator.all_doc_files)} markdown files...")
    results = validator.validate_all_documents()
    
    # Generate report
    report = validator.generate_report(results)
    print("\n" + report)
    
    # Save report to file
    report_path = docs_root / "validation_report.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\nValidation report saved to: {report_path}")
    
    # Exit with error code if there are errors
    error_count = sum(
        1 for errors in results.values() 
        for error in errors 
        if error.severity == "error"
    )
    
    if error_count > 0:
        print(f"\n❌ Validation failed with {error_count} errors")
        sys.exit(1)
    else:
        print("\n✓ Validation passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
