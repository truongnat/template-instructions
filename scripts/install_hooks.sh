#!/bin/bash
#
# Install Git Hooks
# 
# This script installs git hooks for automatic version management.
# Run this after cloning the repository.

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Copy post-commit hook
if [ -f "$REPO_ROOT/scripts/hooks/post-commit" ]; then
    cp "$REPO_ROOT/scripts/hooks/post-commit" "$HOOKS_DIR/post-commit"
    chmod +x "$HOOKS_DIR/post-commit"
    echo "  ✓ Installed post-commit hook"
else
    echo "  ⚠ post-commit hook template not found"
fi

echo ""
echo "✓ Git hooks installed successfully!"
echo ""
echo "Hooks installed:"
echo "  - post-commit: Auto-bump version and create tags"
echo ""
echo "Commit message format:"
echo "  - feat: ... → minor bump (3.0.0 → 3.1.0)"
echo "  - fix: ... → patch bump (3.0.0 → 3.0.1)"
echo "  - BREAKING CHANGE: ... → major bump (3.0.0 → 4.0.0)"
