# Publishing to PyPI

This guide explains how to publish the `agentic-sdlc` package to PyPI.

## Prerequisites

1. Install build tools:
```bash
uv pip install build twine
```

2. Create PyPI account at https://pypi.org/account/register/

3. Create API token at https://pypi.org/manage/account/token/

## Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates:
- `dist/agentic_sdlc-1.0.0-py3-none-any.whl` (wheel)
- `dist/agentic-sdlc-1.0.0.tar.gz` (source)

## Test Locally

Before publishing, test the package locally:

```bash
# Install in editable mode
uv pip install -e .

# Test the CLI
agentic-sdlc --help
asdlc --help
```

## Publish to TestPyPI (Optional)

Test on TestPyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

Then test installation:
```bash
uv pip install --index-url https://test.pypi.org/simple/ agentic-sdlc
```

## Publish to PyPI

When ready, publish to production PyPI:

```bash
python -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

## Verify Installation

After publishing, verify users can install:

```bash
uv pip install agentic-sdlc
```

## Update Version

To publish a new version:

1. Update version in `pyproject.toml`
2. Update version in `agentic_sdlc/__init__.py`
3. Commit changes
4. Create git tag: `git tag v1.0.1`
5. Rebuild and republish

## Automation (GitHub Actions)

For automated publishing, see `.github/workflows/publish-pypi.yml`

## Troubleshooting

### Package already exists
- Increment version number in `pyproject.toml`
- You cannot overwrite existing versions on PyPI

### Import errors after install
- Check `pyproject.toml` `packages` configuration
- Ensure all dependencies are listed

### CLI not found
- Check `[project.scripts]` in `pyproject.toml`
- Reinstall: `uv pip uninstall agentic-sdlc && uv pip install agentic-sdlc`
