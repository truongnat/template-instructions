#!/bin/bash
# 
# Usage: ./scripts/utils/load_context.sh
# 
# Aggregates key project context files into a single stream for LLM consumption.
# Find project root, assuming script is in scripts/utils/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "# Project Context"
echo ""

# 1. Main Context
if [ -f "$PROJECT_ROOT/CONTEXT.md" ]; then
    echo "## Context Overview (CONTEXT.md)"
    cat "$PROJECT_ROOT/CONTEXT.md"
    echo ""
fi

# 2. Integration Guide
if [ -f "$PROJECT_ROOT/INTEGRATIONS.md" ]; then
    echo "## Integration Guide (INTEGRATIONS.md)"
    cat "$PROJECT_ROOT/INTEGRATIONS.md"
    echo ""
fi

# 3. Core Configuration (Source)
if [ -f "$PROJECT_ROOT/src/agentic_sdlc/core/config.py" ]; then
    echo "## Configuration Source (src/agentic_sdlc/core/config.py)"
    echo '```python'
    cat "$PROJECT_ROOT/src/agentic_sdlc/core/config.py"
    echo '```'
    echo ""
fi
