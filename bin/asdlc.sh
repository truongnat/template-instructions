#!/bin/bash
# Agentic SDLC - Command Wrapper
# Usage: ./bin/asdlc <command> [args]

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$ROOT_DIR/.venv/bin/python" ]; then
    PYTHON="$ROOT_DIR/.venv/bin/python"
else
    PYTHON="python3"
fi

# Run via module
$PYTHON -m agentic_sdlc.cli "$@"