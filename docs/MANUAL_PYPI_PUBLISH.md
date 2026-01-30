# Manual PyPI Publishing Guide

## Current Situation

The automated build is failing due to permission issues with `agentic_sdlc.egg-info` files. These files have special permissions that prevent modification.

## Solution: Manual Publishing

### Step 1: Fix Permissions (One-time)

```bash
cd /Users/truongdq/Documents/GitHub/sdlc-kit

# Remove protected files
sudo rm -rf agentic_sdlc.egg-info build

# Or change ownership
sudo chown -R $(whoami) agentic_sdlc.egg-info build
```

### Step 2: Install Build Tools (If Needed)

```bash
pip install --user build twine
```

### Step 3: Build the Package

```bash
# Clean old builds
rm -rf dist/

# Build using python -m build (recommended)
python -m build

# OR use pip wheel if build module not available
python -m pip wheel --no-deps -w dist .
```

### Step 4: Verify the Build

```bash
ls -lh dist/
# Should show:
# agentic_sdlc-2.7.0-py3-none-any.whl
# agentic_sdlc-2.7.0.tar.gz
```

### Step 5: Check Package

```bash
python -m twine check dist/*
```

### Step 6: Publish to TestPyPI (Optional - Test First)

```bash
python -m twine upload --repository testpypi dist/*
```

### Step 7: Publish to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI credentials or API token.

## Alternative: Use GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: \${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

Then add your PyPI API token to GitHub Secrets as `PYPI_API_TOKEN`.

## Quick Fix for Current Release

Since v2.7.0 is already tagged, you can:

1. Fix permissions
2. Build manually
3. Publish to PyPI

```bash
# One-liner (after fixing permissions)
rm -rf dist/ && python -m pip wheel --no-deps -w dist . && python -m twine upload dist/*
```

## Current Version Status

- **Git Tag**: v2.7.0 ✅
- **GitHub**: v2.7.0 ✅  
- **package.json**: 2.7.0 ✅
- **pyproject.toml**: 2.7.0 ✅
- **__init__.py**: 2.7.0 ✅
- **PyPI**: 1.0.0 ❌ (needs manual publish)

## Next Steps

1. Fix the permission issue with egg-info files
2. Build the package
3. Publish to PyPI
4. Verify on PyPI that version 2.7.0 is available

After publishing, users can install with:
```bash
pip install --upgrade sdlc-kit
# Will install version 2.7.0
```
