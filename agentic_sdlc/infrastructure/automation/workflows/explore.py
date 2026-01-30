#!/usr/bin/env python3
"""
Explore Workflow Script
Deep investigation and multi-order analysis.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_sdlc.core.utils.console import print_header, print_step, print_success, print_info, print_warning

ORDERS = [
    ("First-Order", "Surface Level", "What does the user want?"),
    ("Second-Order", "Dependencies", "What does this depend on?"),
    ("Third-Order", "Implications", "What are the ripple effects?"),
    ("Fourth-Order", "Hidden Risks", "What could go wrong that we haven't considered?"),
]


def run_explore(topic: str, output: str = None):
    """Run deep exploration workflow."""
    print_header("Explore Workflow - Multi-Order Analysis")
    print_info(f"Topic: {topic}")
    print()
    
    for order, level, question in ORDERS:
        print_step(order, f"{level}")
        print(f"   Question: {question}")
        print()
    
    print_warning("For each order, document:")
    print("   - Findings")
    print("   - Evidence")
    print("   - Implications")
    print()
    
    if output:
        # Generate exploration template
        template = f"""# Exploration Report: {topic}

**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}
**Author:** @SA

## Executive Summary
[1-2 paragraph summary]

## First-Order Analysis
### User Requirements
- ...

## Second-Order Analysis
### Dependencies
- ...

## Third-Order Analysis
### Implications
- ...

## Fourth-Order Analysis
### Hidden Risks
- ...

## Risk Matrix
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| ... | ... | ... | ... |

## Recommendation
[Recommended approach with rationale]

## Alternatives Considered
1. ...
2. ...

## Open Questions
- [ ] ...
"""
        Path(output).write_text(template, encoding='utf-8')
        print_success(f"Template saved to: {output}")
    
    print_success("Explore workflow guidance complete!")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Explore - Deep Investigation Workflow")
    parser.add_argument("topic", help="Topic to investigate")
    parser.add_argument("--output", "-o", help="Output file for exploration template")
    
    args = parser.parse_args()
    return run_explore(args.topic, args.output)


if __name__ == "__main__":
    sys.exit(main())
