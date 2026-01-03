---
description: Cleanup and Maintenance - Archive → Fix Drift → Update Index
---

# /housekeeping - Cleanup and Maintenance

**When to Use:** Before git push, end of sprint, weekly maintenance
**Flow:** Archive → Fix Drift → Update Index → Verify
**Output:** Clean workspace, updated indexes

## Overview
The `/housekeeping` workflow maintains system health by archiving completed work, fixing documentation drift, and ensuring knowledge base indexes are current.

## Workflow Steps

### 1. Archive Completed Work
**Identify Completed Items:**
- Closed GitHub issues
- Merged pull requests
- Completed sprint artifacts
- Resolved incidents

**Archive Actions:**
```bash
# Move completed sprint artifacts
# Keep active sprints, archive old ones
docs/sprints/sprint-[N]/ → docs/archive/sprint-[N]/
```

**Retention Policy:**
- **Active:** Current sprint + last 2 sprints
- **Archive:** Older sprints (keep for reference)
- **Purge:** Never (all sprints are historical record)

### 2. Fix Documentation Drift
**Check for Drift:**
- [ ] README.md matches current state
- [ ] CHANGELOG.md is up to date
- [ ] API docs match implementation
- [ ] Architecture diagrams current
- [ ] Deployment docs accurate

**Common Drift Issues:**
```markdown
❌ Outdated version numbers
❌ Removed features still documented
❌ New features not documented
❌ Broken internal links
❌ Stale screenshots
❌ Old configuration examples
```

**Fix Actions:**
1. Update version references
2. Remove deprecated content
3. Add missing documentation
4. Fix broken links
5. Update screenshots
6. Refresh examples

### 3. Update Knowledge Base Index
**Verify Index Completeness:**
```bash
# Check for unindexed KB entries
find .agent/knowledge-base -name "KB-*.md" | while read file; do
  grep -q "$(basename $file)" .agent/knowledge-base/INDEX.md || echo "Missing: $file"
done
```

**Update INDEX.md:**
- Add new entries
- Update categories
- Fix broken links
- Sort by date (newest first)
- Update statistics

**Index Structure:**
```markdown
# Knowledge Base Index

**Last Updated:** YYYY-MM-DD
**Total Entries:** [N]

## Statistics
- Bugs: [N] entries
- Features: [N] entries
- Architecture: [N] entries
- Security: [N] entries
- Performance: [N] entries

## Recent Entries (Last 30 Days)
### Bugs - Critical
- **KB-YYYY-MM-DD-###:** [Title] - [One-line summary]
  - Tags: [tag1, tag2]
  - Time Saved: [X hours]

[Continue for all categories...]
```

### 4. Validate YAML Frontmatter
**Check All KB Entries:**
```bash
# Validate YAML in all KB entries
for file in .agent/knowledge-base/**/*.md; do
  # Check for required fields
  grep -q "^title:" "$file" || echo "Missing title: $file"
  grep -q "^category:" "$file" || echo "Missing category: $file"
  grep -q "^date:" "$file" || echo "Missing date: $file"
done
```

**Required Fields:**
- title
- category
- priority
- sprint
- date
- tags

### 5. Clean Up Temporary Files

**Use `/cleanup` workflow for comprehensive cleanup:**
```
@ORCHESTRATOR /cleanup
```

**Quick Cleanup (Manual):**
- [ ] `.DS_Store` files
- [ ] Temporary test files
- [ ] Old log files
- [ ] Unused screenshots
- [ ] Draft documents

**Keep:**
- All KB entries
- All sprint artifacts
- All templates
- All workflows

**See:** `.agent/workflows/cleanup.md` for full cleanup workflow

### 6. Update Metrics Dashboard
**Generate Current Metrics:**
```markdown
## 📊 System Health Dashboard

**Generated:** YYYY-MM-DD

### Knowledge Base
- Total Entries: [N]
- This Week: +[X]
- This Month: +[Y]
- Time Saved: [Z hours]

### Sprints
- Active Sprint: sprint-[N]
- Completed Sprints: [N]
- Total Features: [N]
- Total Bugs Fixed: [N]

### Code Quality
- Test Coverage: [X%]
- Documentation Coverage: [Y%]
- KB Coverage: [Z%]

### Compound Effectiveness
- Reuse Rate: [X%]
- First-Time Fix Rate: [Y%]
- Pattern Adoption: [Z%]
```

### 7. Verify Git Status
**Check Repository Health:**
```bash
# Ensure clean state
git status

# Check for large files
find . -type f -size +10M

# Verify .gitignore
git check-ignore -v [file]
```

**Pre-Push Checklist:**
- [ ] All changes committed
- [ ] Commit messages follow convention
- [ ] No large files (> 10MB)
- [ ] No sensitive data
- [ ] Tests passing
- [ ] Documentation updated

### 8. Optimize File Structure
**Check for Issues:**
- Duplicate files
- Misplaced artifacts
- Inconsistent naming
- Deep nesting (> 4 levels)

**Reorganize if Needed:**
```bash
# Example: Move misplaced artifacts
mv docs/Design-Spec.md docs/sprints/sprint-3/designs/
```

## Usage Examples

### Example 1: End of Sprint
```
@ORCHESTRATOR /housekeeping - End of sprint-3 cleanup
```

**Actions:**
1. Archive sprint-1 artifacts
2. Update CHANGELOG.md with sprint-3 features
3. Rebuild KB index
4. Validate all YAML
5. Generate metrics dashboard
6. Verify git status

### Example 2: Weekly Maintenance
```
@ORCHESTRATOR /housekeeping - Weekly maintenance
```

**Actions:**
1. Update KB index with new entries
2. Fix documentation drift
3. Clean temporary files
4. Update metrics
5. Verify links

### Example 3: Pre-Release
```
@ORCHESTRATOR /housekeeping - Pre-release v2.0.0
```

**Actions:**
1. Update all version references
2. Verify documentation accuracy
3. Update CHANGELOG.md
4. Generate release notes
5. Verify git tags

## Automation Scripts

### Script 1: KB Index Generator
```bash
#!/bin/bash
# tools/housekeeping/update-kb-index.sh

echo "# Knowledge Base Index" > .agent/knowledge-base/INDEX.md
echo "" >> .agent/knowledge-base/INDEX.md
echo "**Last Updated:** $(date +%Y-%m-%d)" >> .agent/knowledge-base/INDEX.md
echo "" >> .agent/knowledge-base/INDEX.md

# Count entries by category
for category in bugs features architecture security performance; do
  count=$(find .agent/knowledge-base/$category -name "KB-*.md" | wc -l)
  echo "- $category: $count entries" >> .agent/knowledge-base/INDEX.md
done

# List recent entries
echo "" >> .agent/knowledge-base/INDEX.md
echo "## Recent Entries" >> .agent/knowledge-base/INDEX.md
find .agent/knowledge-base -name "KB-*.md" -mtime -30 | sort -r | while read file; do
  title=$(grep "^title:" "$file" | cut -d'"' -f2)
  echo "- $(basename $file): $title" >> .agent/knowledge-base/INDEX.md
done
```

### Script 2: Documentation Drift Checker
```bash
#!/bin/bash
# tools/housekeeping/check-drift.sh

echo "Checking for documentation drift..."

# Check README version
readme_version=$(grep "version" README.md | head -1)
package_version=$(grep "version" package.json | head -1)
if [ "$readme_version" != "$package_version" ]; then
  echo "❌ Version mismatch: README vs package.json"
fi

# Check for broken links
echo "Checking for broken links..."
find docs -name "*.md" -exec grep -H "\[.*\](.*)" {} \; | while read line; do
  # Extract and verify links
  # (simplified - use proper link checker)
  echo "Checking: $line"
done

echo "✅ Drift check complete"
```

### Script 3: YAML Validator
```bash
#!/bin/bash
# tools/housekeeping/validate-yaml.sh

echo "Validating YAML frontmatter..."

find .agent/knowledge-base -name "KB-*.md" | while read file; do
  # Check required fields
  for field in title category priority sprint date tags; do
    if ! grep -q "^$field:" "$file"; then
      echo "❌ Missing $field in $file"
    fi
  done
done

echo "✅ YAML validation complete"
```

## Integration with Roles

### @ORCHESTRATOR
- Primary user of /housekeeping
- Runs automated maintenance
- Generates health reports

### @REPORTER
- Updates documentation
- Fixes drift issues
- Maintains CHANGELOG

### @DEV
- Cleans up code artifacts
- Updates technical docs
- Fixes broken links

## Success Criteria

**Housekeeping Complete When:**
- [ ] Old sprints archived
- [ ] Documentation drift fixed
- [ ] KB index updated
- [ ] YAML validated
- [ ] Temporary files removed
- [ ] Metrics generated
- [ ] Git status clean
- [ ] File structure optimized

## Metrics

Track housekeeping effectiveness:
- **Drift Rate:** % of docs needing updates
- **Index Accuracy:** % of KB entries indexed
- **YAML Validity:** % of entries with valid YAML
- **Cleanup Frequency:** Days between housekeeping
- **Time Spent:** Hours per housekeeping session

## Housekeeping Checklist

```markdown
## 🧹 Housekeeping Checklist

### Archive
- [ ] Identify completed sprints
- [ ] Move to archive directory
- [ ] Update sprint index

### Documentation
- [ ] Update README.md
- [ ] Update CHANGELOG.md
- [ ] Fix broken links
- [ ] Update screenshots
- [ ] Verify examples

### Knowledge Base
- [ ] Update INDEX.md
- [ ] Validate YAML
- [ ] Fix broken references
- [ ] Update statistics

### Cleanup
- [ ] Remove temporary files
- [ ] Clean old logs
- [ ] Remove unused assets
- [ ] Optimize file structure

### Metrics
- [ ] Generate dashboard
- [ ] Update statistics
- [ ] Calculate compound metrics

### Git
- [ ] Verify clean status
- [ ] Check for large files
- [ ] Verify .gitignore
- [ ] Update .gitattributes

### Verification
- [ ] Run automated checks
- [ ] Verify all links
- [ ] Test documentation
- [ ] Confirm metrics accuracy
```

## Handoff Template

```markdown
### /housekeeping Complete
- **Duration:** [X minutes]
- **Sprints Archived:** [N]
- **Docs Updated:** [N]
- **KB Entries Indexed:** [N]
- **Issues Fixed:** [N]
- **Metrics Generated:** ✅
- **Git Status:** Clean
- **Next Housekeeping:** [Date]

#housekeeping #maintenance #cleanup
```

#workflow #housekeeping #maintenance
