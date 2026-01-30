#!/bin/bash
# Rename project from sdlc-kit to sdlc-kit

echo "🔄 Renaming project from 'sdlc-kit' to 'sdlc-kit'..."
echo ""

# Files to update (excluding build directory and node_modules)
find . -type f \( -name "*.md" -o -name "*.txt" -o -name "*.sh" -o -name "*.py" \) \
  ! -path "./build/*" \
  ! -path "./node_modules/*" \
  ! -path "./.venv/*" \
  ! -path "./.git/*" \
  ! -path "./dist/*" \
  ! -path "*.egg-info/*" \
  -exec sed -i '' 's/sdlc-kit/sdlc-kit/g' {} +

echo "✅ Updated references in .md, .txt, .sh, and .py files"
echo ""
echo "📝 Summary of changes:"
echo "  - Package name: sdlc-kit → sdlc-kit"
echo "  - Repository URLs updated"
echo "  - Documentation updated"
echo ""
echo "⚠️  Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Rebuild package: rm -rf dist/ && python -m pip wheel --no-deps -w dist ."
echo "  3. Update PyPI package name when publishing"
