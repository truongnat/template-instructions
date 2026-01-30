# Quick PyPI Publishing Guide

## ✅ Package Built Successfully!

Your package `agentic_sdlc-2.7.0-py3-none-any.whl` is ready in the `dist/` folder!

## Option 1: Install Twine with User Flag (Recommended)

```bash
# Install twine to user directory (bypasses permission issues)
python3 -m pip install --user twine

# Publish to PyPI
python3 -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

## Option 2: Use pipx (If Available)

```bash
# Install twine via pipx (isolated environment)
pipx install twine

# Publish
twine upload dist/*
```

## Option 3: Manual Upload via PyPI Web Interface

1. Go to https://pypi.org/manage/account/
2. Generate an API token if you don't have one
3. Go to https://pypi.org/project/agentic-sdlc/
4. Click "Manage" → "Upload files"
5. Upload `dist/agentic_sdlc-2.7.0-py3-none-any.whl`

## Option 4: Fix Permissions and Retry

```bash
# Fix venv permissions
sudo chown -R $(whoami) .venv/

# Install twine in venv
source .venv/bin/activate
pip install twine

# Publish
python -m twine upload dist/*
```

## What You Have Now

```
dist/
└── agentic_sdlc-2.7.0-py3-none-any.whl  ✅ Ready to publish!
```

## After Publishing

Once published, users can install with:
```bash
pip install --upgrade agentic-sdlc
# Will install version 2.7.0
```

## Verify After Publishing

Check that it's live:
- https://pypi.org/project/agentic-sdlc/
- Should show version 2.7.0

Test installation:
```bash
pip install agentic-sdlc==2.7.0
asdlc --version
# Should output: asdlc 2.7.0
```
