# Validation & Health Check

System validation and health monitoring tools for the Agentic SDLC project.

## 📋 Features

- **Workflow Validation**: Verify tool references in workflow files
- **Health Monitoring**: Comprehensive system health checks
- **Deep Validation**: In-depth project structure validation
- **Path Verification**: Detect broken file references and hardcoded paths
- **Automated Reports**: Generate validation reports with health scores

## 🚀 Quick Start

### Health Check

```bash
python agentic_sdlc/infrastructure/validation/health-check.py
```

### Workflow Validation

```bash
python agentic_sdlc/infrastructure/validation/validate.py
```

### Deep Validation

```bash
python agentic_sdlc/infrastructure/validation/deep_validate.py
```

## 📝 Scripts

### 1. `health-check.py` - System Health Monitoring

Comprehensive system health check covering multiple aspects of the project.

**Usage:**
```bash
python agentic_sdlc/infrastructure/validation/health-check.py
```

**Checks:**
- ✅ Artifact placement validation
- ✅ Documentation drift detection
- ✅ YAML frontmatter validation
- ✅ KB index integrity
- ✅ Sprint structure verification
- ✅ Git status check

**Output Example:**
```
📊 System Health Check
✅ Artifacts: All in correct locations
✅ Documentation: No drift detected
✅ KB Index: Up to date
⚠️  Git: 3 uncommitted files
```

### 2. `validate.py` - Workflow Tool Reference Validator

Scans workflow files for `python tools/...` commands and file path references, verifies they exist.

**Usage:**
```bash
# Full validation
python agentic_sdlc/infrastructure/validation/validate.py

# Suggest fixes for broken references
python agentic_sdlc/infrastructure/validation/validate.py --fix

# Generate validation report
python agentic_sdlc/infrastructure/validation/validate.py --report
```

**Features:**
- Scans all `.agent/workflows/*.md` files
- Detects broken tool references
- Identifies hardcoded paths (Windows, Linux, macOS)
- Calculates health score (0-100)
- Generates detailed reports

**Output Example:**
```
============================================================
  Workflow Tool Reference Validator
============================================================

ℹ️  Project root: /path/to/agentic-sdlc
ℹ️  Scanning workflows for tool references...
ℹ️  Checking for hardcoded paths...

============================================================
  Validation Results
============================================================
  Workflows scanned: 23
  Total references:  45
  Valid references:  43
  Broken references: 2
  Hardcoded paths:   1

  Health Score: 85/100
```

### 3. `deep_validate.py` - Deep Project Structure Validation

In-depth validation of project structure, dependencies, and configuration.

**Usage:**
```bash
python agentic_sdlc/infrastructure/validation/deep_validate.py
```

**Checks:**
- Project structure integrity
- Required directories and files
- Configuration file validity
- Dependency consistency
- Module imports

## 🔧 Configuration

No configuration required. Validators automatically:
- Detect project root directory
- Scan relevant directories
- Generate reports in `docs/reports/`

## 📚 Examples

### Example: Full Validation Workflow

```bash
# 1. Run health check
python agentic_sdlc/infrastructure/validation/health-check.py

# 2. Validate workflow references
python agentic_sdlc/infrastructure/validation/validate.py

# 3. Generate validation report
python agentic_sdlc/infrastructure/validation/validate.py --report

# 4. Deep validation
python agentic_sdlc/infrastructure/validation/deep_validate.py
```

### Example: Fix Broken References

```bash
# 1. Find broken references with suggested fixes
python agentic_sdlc/infrastructure/validation/validate.py --fix

# Output:
# ❌ orchestrator.md:42 - tools/brain/old_script.py - File not found
# ℹ️  tools/brain/old_script.py -> agentic_sdlc/core/brain/brain_cli.py

# 2. Update the workflow file manually
# 3. Re-validate
python agentic_sdlc/infrastructure/validation/validate.py
```

### Example: Automated CI/CD Integration

```bash
# In CI/CD pipeline
python agentic_sdlc/infrastructure/validation/validate.py --report
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "Validation failed! Check the report."
  exit 1
fi
```

## 📊 Health Score Calculation

The validation system calculates a health score from 0-100:

**Formula:**
```
Health Score = (Valid References / Total References) × 100 - Hardcoded Path Penalty
```

**Penalties:**
- Hardcoded path: -5 points each (max -20)

**Interpretation:**
- **100**: Perfect - No issues
- **90-99**: Excellent - Minor issues
- **70-89**: Good - Some issues to address
- **50-69**: Fair - Multiple issues
- **0-49**: Poor - Critical issues

## 🛡️ Validation Reports

Reports are generated in Brain Protocol format with:

**Frontmatter:**
```yaml
---
category: report
tags: [validation, health-check, workflow-audit]
date: 2026-01-29
author: @VALIDATOR
status: automated
---
```

**Sections:**
1. **Problem/Challenge**: What is being validated
2. **Solution/Implementation**: Scan results and statistics
3. **Artifacts/Output**: Health score and status
4. **Issues**: Broken references and hardcoded paths
5. **Next Steps/Actions**: Recommended fixes

**Location:** `docs/reports/Validation-Report-YYYY-MM-DD.md`

## 🔗 Integration

### Called By:

- **Kiro IDE**: `/housekeeping` command
- **CLI**: `agentic-sdlc health`
- **CI/CD**: Pre-deployment checks
- **Pre-commit Hooks**: Automated validation

### NPM Scripts:

Add to `package.json`:
```json
{
  "scripts": {
    "validate": "python agentic_sdlc/infrastructure/validation/validate.py",
    "health": "python agentic_sdlc/infrastructure/validation/health-check.py",
    "validate:report": "python agentic_sdlc/infrastructure/validation/validate.py --report"
  }
}
```

## 🚨 Troubleshooting

### Broken Tool References

**Issue:**
```
❌ workflow.md:42 - tools/old/script.py - File not found
```

**Solutions:**
1. Use `--fix` flag to find similar files
2. Update the workflow file with correct path
3. Create the missing script if needed

### Hardcoded Paths

**Issue:**
```
⚠️  workflow.md:15 - Windows absolute path
```

**Solution:**
Replace absolute paths with relative paths:
```bash
# Bad
C:\Users\username\project\tools\script.py

# Good
tools/script.py
```

### Low Health Score

**Issue:**
```
Health Score: 45/100
```

**Actions:**
1. Fix all broken references first
2. Remove hardcoded paths
3. Re-run validation
4. Aim for score ≥ 90

## 📦 Dependencies

```bash
pip install pyyaml
```

## 🧪 Testing

Run validation on itself:

```bash
# Validate the validation workflows
python agentic_sdlc/infrastructure/validation/validate.py

# Should show 100/100 health score
```

## 🔗 Related Documentation

- **Tools Overview**: `../../README_TOOLS.md`
- **Workflows**: `../../.agent/workflows/README.md`
- **Critical Patterns**: `../../.kiro/steering/critical-patterns.md`

---

**Version:** 1.0.0  
**Platform:** Cross-platform (Windows, Linux, macOS)  
**Author:** @VALIDATOR
