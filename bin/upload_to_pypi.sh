#!/bin/bash
# Upload to PyPI using curl (no twine needed)

# Check if file exists
if [ ! -f "dist/agentic_sdlc-2.7.0-py3-none-any.whl" ]; then
    echo "❌ Error: Package file not found!"
    echo "Expected: dist/agentic_sdlc-2.7.0-py3-none-any.whl"
    exit 1
fi

echo "📦 Uploading sdlc-kit 2.7.0 to PyPI..."
echo ""
echo "You will need your PyPI API token."
echo "Get it from: https://pypi.org/manage/account/token/"
echo ""
read -p "Enter your PyPI API token (starts with 'pypi-'): " PYPI_TOKEN

if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ Error: No token provided"
    exit 1
fi

echo ""
echo "Uploading..."

curl -X POST https://upload.pypi.org/legacy/ \
  -F ":action=file_upload" \
  -F "protocol_version=1" \
  -F "content=@dist/agentic_sdlc-2.7.0-py3-none-any.whl" \
  -u "__token__:$PYPI_TOKEN"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Upload complete!"
    echo ""
    echo "Verify at: https://pypi.org/project/sdlc-kit/"
    echo ""
    echo "Users can now install with:"
    echo "  pip install --upgrade sdlc-kit"
else
    echo ""
    echo "❌ Upload failed!"
    echo ""
    echo "Alternative: Upload via web interface"
    echo "  1. Go to https://pypi.org/manage/account/"
    echo "  2. Use the web upload form"
    echo "  3. Upload: dist/agentic_sdlc-2.7.0-py3-none-any.whl"
fi
