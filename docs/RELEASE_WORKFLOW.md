# Release Workflow - Updated

The release workflow has been enhanced to automatically update Python package versions and publish to PyPI.

## Features

### Automatic Version Management
- ✅ Updates `package.json` (for npm)
- ✅ Updates `pyproject.toml` (for Python package)
- ✅ Updates `agentic_sdlc/__init__.py` (Python version constant)
- ✅ Updates `CHANGELOG.md` with categorized commits
- ✅ Creates git tags
- ✅ Commits and pushes changes

### Publishing Support
- ✅ Publish to npm/bun registry
- ✅ Build Python package (wheel + sdist)
- ✅ Publish to PyPI
- ✅ Publish to TestPyPI (for testing)

## Usage

### Preview Release
See what would be released without making changes:
```bash
python asdlc.py release preview
```

### Full Release (Recommended)
Complete release with all steps:
```bash
python asdlc.py release release \
  --commit \
  --tag \
  --push \
  --build-python \
  --publish-pypi
```

This will:
1. Detect version bump type from commits (major/minor/patch)
2. Update CHANGELOG.md
3. Update package.json version
4. Update pyproject.toml version
5. Update agentic_sdlc/__init__.py version
6. Commit all changes
7. Create git tag (e.g., v2.7.0)
8. Build Python package
9. Push changes and tags to GitHub
10. Publish to PyPI

### Manual Version Bump
Specify the version bump type:
```bash
python asdlc.py release release --bump minor --commit --tag
```

### Dry Run
Preview what would happen without making changes:
```bash
python asdlc.py release release --dry-run
```

### Test PyPI First
Test publishing to TestPyPI before production:
```bash
python asdlc.py release release \
  --commit \
  --tag \
  --build-python \
  --publish-pypi \
  --test-pypi
```

## Command-Line Options

### Release Command
```bash
python asdlc.py release release [OPTIONS]
```

**Options:**
- `--sprint N` - Include sprint number in changelog
- `--version X.Y.Z` - Explicit version (overrides auto-detection)
- `--bump [major|minor|patch]` - Manual version bump type
- `--commit` - Commit release files
- `--tag` - Create git tag
- `--push` - Push changes and tags to remote
- `--publish` - Publish to npm/bun registry
- `--build-python` - Build Python package
- `--publish-pypi` - Publish to PyPI
- `--test-pypi` - Use TestPyPI instead of PyPI
- `--dry-run` - Preview only, don't make changes

## Version Bump Detection

The system automatically detects the version bump type based on conventional commits:

| Commit Type | Bump Type | Example |
|-------------|-----------|---------|
| `feat:` or `feat!:` | minor | `feat: add new feature` |
| `fix:` | patch | `fix: resolve bug` |
| `BREAKING CHANGE` or `!` | major | `feat!: breaking change` |
| `chore:`, `docs:`, etc. | patch | `chore: update deps` |

## Examples

### Simple Patch Release
```bash
# Fix a bug
git commit -m "fix: resolve login issue"

# Release
python asdlc.py release release --commit --tag --push
```

### Feature Release with PyPI
```bash
# Add a feature
git commit -m "feat: add new authentication method"

# Release to both npm and PyPI
python asdlc.py release release \
  --commit \
  --tag \
  --push \
  --publish \
  --build-python \
  --publish-pypi
```

### Breaking Change Release
```bash
# Make breaking change
git commit -m "feat!: redesign API interface"

# Preview first
python asdlc.py release preview

# Release
python asdlc.py release release \
  --commit \
  --tag \
  --push \
  --build-python \
  --publish-pypi
```

## Prerequisites

### For Python Publishing
```bash
# Install build tools
pip install build twine

# Configure PyPI credentials
# Create ~/.pypirc with your API token
```

### For npm Publishing
```bash
# Login to npm
npm login
```

## Troubleshooting

### Build Fails
If Python package build fails due to permissions:
```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info

# Try manual build
python -m pip wheel --no-deps -w dist .
```

### PyPI Upload Fails
```bash
# Check credentials
python -m twine check dist/*

# Upload manually
python -m twine upload dist/*
```

## Workflow Integration

The release workflow integrates with:
- **Git**: Automatic tagging and pushing
- **Conventional Commits**: Automatic version detection
- **CHANGELOG.md**: Automatic changelog generation
- **npm**: Package publishing
- **PyPI**: Python package publishing

## Best Practices

1. **Always preview first**: Use `preview` command before releasing
2. **Test on TestPyPI**: Use `--test-pypi` for first-time releases
3. **Use conventional commits**: Ensures correct version bumping
4. **Keep CHANGELOG updated**: Review generated changelog before release
5. **Tag releases**: Always use `--tag` for version tracking
