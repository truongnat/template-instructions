# Project Renamed: agentic-sdlc → sdlc-kit

## Changes Made

### Package Configuration
- ✅ `pyproject.toml`: name = "sdlc-kit"
- ✅ `package.json`: name = "sdlc-kit"
- ✅ Repository URLs updated to github.com/truongnat/sdlc-kit

### Documentation
- ✅ All `.md` files updated
- ✅ All `.txt` files updated  
- ✅ All `.sh` scripts updated
- ✅ All `.py` files updated

### What This Means

**Old Name:** `agentic-sdlc`
**New Name:** `sdlc-kit`

**Installation:**
```bash
# Old
pip install agentic-sdlc

# New
pip install sdlc-kit
```

**CLI Command:** (stays the same)
```bash
asdlc --version
asdlc init
```

**Repository:**
- Old: https://github.com/truongnat/agentic-sdlc
- New: https://github.com/truongnat/sdlc-kit

## Next Steps

1. **Commit Changes**
   ```bash
   git add -A
   git commit -m "refactor: rename project from agentic-sdlc to sdlc-kit"
   ```

2. **Update GitHub Repository Name**
   - Go to GitHub repository settings
   - Rename repository from `agentic-sdlc` to `sdlc-kit`

3. **Rebuild Package**
   ```bash
   sudo rm -rf agentic_sdlc.egg-info build
   rm -rf dist/
   python -m pip wheel --no-deps -w dist .
   ```

4. **Publish to PyPI as New Package**
   ```bash
   ./bin/upload_to_pypi.sh
   ```

## Important Notes

- The Python package directory `agentic_sdlc/` stays the same (internal structure)
- Only the **package name** changes (what users install)
- The CLI command `asdlc` remains unchanged
- This will be published as a **new package** on PyPI: `sdlc-kit`
- The old `agentic-sdlc` package will remain on PyPI but won't be updated

## Version

Current version: **2.7.0**

This rename will be part of the v2.7.0 release.
