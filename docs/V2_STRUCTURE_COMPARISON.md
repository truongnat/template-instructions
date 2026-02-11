# V2 Structure Comparison

## Overview

The V2 Structure Comparison feature provides a comprehensive analysis tool that compares your current project structure against the proposed v2 improvements documented in `claude_suggestion/v2/`. It helps you:

- **Identify gaps** between current and proposed structure
- **Track progress** on implementing v2 suggestions
- **Detect conflicts** that may arise from structural changes
- **Generate tasks** with priorities and effort estimates
- **Create migration scripts** to automate structural changes
- **Monitor completion** over time with status tracking

## Quick Start

### Using the CLI

The simplest way to run a comparison:

```bash
sdlc-kit compare
```

This will:
1. Scan your current project structure
2. Parse v2 suggestion documents from `claude_suggestion/v2/`
3. Generate a comparison report saved to `comparison_report.md`

### Using Python API

```python
from agentic_sdlc.comparison.engine import ComparisonEngine

# Initialize the engine
engine = ComparisonEngine(
    project_root=".",
    v2_docs_path="claude_suggestion/v2"
)

# Run the comparison
result = engine.run_comparison()

# Save the report
engine.save_report(result['report'], "comparison_report.md")
```

## CLI Usage

### Basic Commands

**Run a basic comparison:**
```bash
sdlc-kit compare
```

**Specify custom paths:**
```bash
sdlc-kit compare --project-root /path/to/project --v2-docs /path/to/v2/docs
```

**Generate migration scripts:**
```bash
sdlc-kit compare --generate-scripts
```

**Use status tracking:**
```bash
sdlc-kit compare --status-file .comparison_status.json
```

**Verbose output:**
```bash
sdlc-kit compare --verbose
```

### Command Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--project-root` | `-p` | Path to project root directory | `.` (current directory) |
| `--v2-docs` | `-d` | Path to v2 suggestion documents | `claude_suggestion/v2` |
| `--output` | `-o` | Output file for comparison report | `comparison_report.md` |
| `--status-file` | `-s` | Path to status tracking file | None |
| `--generate-scripts` | `-g` | Generate migration scripts | False |
| `--scripts-output` | | Output directory for migration scripts | `migration_scripts` |
| `--no-validation` | | Skip validation checks | False |
| `--verbose` | `-v` | Enable verbose output | False |

### Examples

**Complete workflow with all features:**
```bash
sdlc-kit compare \
  --project-root . \
  --v2-docs claude_suggestion/v2 \
  --output detailed_report.md \
  --status-file .comparison_status.json \
  --generate-scripts \
  --scripts-output ./migration_scripts \
  --verbose
```

**Quick check without validation:**
```bash
sdlc-kit compare --no-validation --output quick_check.md
```

**Generate only migration scripts:**
```bash
sdlc-kit compare --generate-scripts --scripts-output ./scripts
```

## Programmatic API

### ComparisonEngine

The main class for running comparisons.

#### Initialization

```python
from agentic_sdlc.comparison.engine import ComparisonEngine

engine = ComparisonEngine(
    project_root=".",                    # Path to project root
    v2_docs_path="claude_suggestion/v2", # Path to v2 docs
    status_file_path=None                # Optional status file
)
```

#### Running Comparisons

```python
result = engine.run_comparison(
    generate_migration_scripts=False,  # Generate migration scripts
    check_validation=True              # Check for superseded suggestions
)
```

**Returns a dictionary with:**
- `comparison`: ComparisonResult object
- `gaps`: List of Gap objects
- `conflicts`: List of Conflict objects
- `tasks`: List of Task objects
- `report`: Markdown report string
- `migration_scripts`: Dict of migration scripts (if enabled)
- `validation_results`: Dict of validation results (if enabled)
- `current_structure`: ProjectStructure object
- `proposed_structure`: ProposedStructure object

#### Saving Results

```python
# Save the report
engine.save_report(result['report'], "comparison_report.md")

# Save migration scripts
if result.get('migration_scripts'):
    engine.save_migration_scripts(
        result['migration_scripts'],
        "migration_scripts"
    )
```

### Data Models

#### ComparisonResult

```python
@dataclass
class ComparisonResult:
    directory_statuses: Dict[str, DirectoryStatus]
    completion_percentage: float
    implemented_count: int
    partial_count: int
    missing_count: int
```

#### Gap

```python
@dataclass
class Gap:
    category: str
    description: str
    priority: str          # "High", "Medium", "Low"
    effort: str           # "Quick Win", "Medium", "Large"
    related_requirement: str
    proposed_action: str
```

#### Conflict

```python
@dataclass
class Conflict:
    type: str             # "directory_exists", "import_break", "config_conflict"
    description: str
    affected_paths: List[str]
    severity: str         # "High", "Medium", "Low"
    mitigation: str
```

#### Task

```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: str         # "High", "Medium", "Low"
    effort_hours: float
    category: str
    files_to_create: List[str]
    files_to_modify: List[str]
    dependencies: List[str]
    reference: str
```

### Working with Results

#### Accessing Gaps

```python
result = engine.run_comparison()

# Get all gaps
gaps = result['gaps']

# Filter by priority
high_priority = [g for g in gaps if g.priority == "High"]
quick_wins = [g for g in gaps if g.effort == "Quick Win"]

# Group by category
from collections import defaultdict
by_category = defaultdict(list)
for gap in gaps:
    by_category[gap.category].append(gap)
```

#### Accessing Conflicts

```python
conflicts = result['conflicts']

# Filter by severity
critical = [c for c in conflicts if c.severity == "High"]

# Group by type
by_type = defaultdict(list)
for conflict in conflicts:
    by_type[conflict.type].append(conflict)
```

#### Accessing Tasks

```python
tasks = result['tasks']

# Get quick wins
quick_wins = [t for t in tasks if t.effort_hours < 4]

# Get tasks by priority
high_priority_tasks = [t for t in tasks if t.priority == "High"]

# Get tasks with no dependencies
independent_tasks = [t for t in tasks if not t.dependencies]
```

### Custom Reports

You can create custom reports using the raw data:

```python
result = engine.run_comparison()

# Create custom report
report_lines = []
report_lines.append("# My Custom Report")
report_lines.append("")

# Add summary
comparison = result['comparison']
report_lines.append(f"Completion: {comparison.completion_percentage:.1f}%")
report_lines.append("")

# Add high priority gaps
gaps = result['gaps']
high_priority = [g for g in gaps if g.priority == "High"]

report_lines.append("## High Priority Items")
for gap in high_priority:
    report_lines.append(f"- {gap.description}")
    report_lines.append(f"  Action: {gap.proposed_action}")

# Save custom report
custom_report = "\n".join(report_lines)
Path("custom_report.md").write_text(custom_report)
```

## Features

### 1. Structure Scanning

The scanner analyzes your current project structure:

- Identifies all directories up to 3 levels deep
- Detects configuration files (pyproject.toml, requirements.txt, etc.)
- Analyzes the `lib/` directory for bundled dependencies
- Records file counts and directory metadata

### 2. V2 Document Parsing

The parser extracts structured data from v2 documents:

- **SDLC_Improvement_Suggestions.md**: 15 improvement categories
- **Proposed_Structure.md**: Complete proposed directory tree
- **Quick_Action_Checklist.md**: Prioritized action items

### 3. Gap Analysis

Identifies missing or incomplete implementations:

- Compares current vs proposed structure
- Assigns status to each directory: IMPLEMENTED, PARTIAL, MISSING, or CONFLICT
- Calculates overall completion percentage
- Categorizes gaps by priority and effort

### 4. Conflict Detection

Identifies potential issues:

- Directories that exist but don't match proposed organization
- File moves that may break import statements
- Configuration conflicts
- CI/CD compatibility issues

### 5. Task Generation

Creates actionable tasks from gaps:

- Generates specific task descriptions
- Estimates effort in hours
- Identifies task dependencies
- Groups related tasks into work packages
- Prioritizes by impact and effort

### 6. Migration Scripts

Generates scripts to automate structural changes:

- **lib_cleanup.sh**: Converts bundled dependencies to requirements.txt
- **backup.sh**: Backs up directories before destructive operations
- **directory_moves.sh**: Git mv commands for reorganization
- **import_updates.sh**: Updates import statements after file moves

### 7. Status Tracking

Monitors progress over time:

- Maintains a JSON status file
- Records completion dates
- Tracks intentional deviations
- Supports marking items as "Intentionally Skipped" with reasons

### 8. Validation Checks

Identifies outdated suggestions:

- Detects superseded suggestions (goal achieved differently)
- Flags potentially inapplicable suggestions
- Validates against current project decisions

## Report Structure

The generated comparison report includes:

### 1. Executive Summary
- Overall completion percentage
- Count of implemented, partial, and missing items
- High-level progress overview

### 2. Directory Status Breakdown
- Status of each proposed directory
- Subdirectory verification results
- Configuration file presence

### 3. Gap Analysis
- Detailed list of all gaps
- Categorized by improvement category
- Prioritized by impact and effort

### 4. Conflicts
- Potential conflicts with severity levels
- Affected paths
- Mitigation suggestions

### 5. Quick Wins
- High-value, low-effort improvements
- Estimated time for each
- Specific action items

### 6. High Priority Gaps
- Critical missing items
- Detailed descriptions
- Proposed actions

### 7. Generated Tasks
- Actionable task list
- Grouped by priority
- Effort estimates
- Dependencies

### 8. Progress Visualization
- ASCII progress bar
- Category breakdown chart

### 9. Deviations (if applicable)
- Intentionally skipped suggestions
- Reasons for deviations

## Status Tracking

### Enabling Status Tracking

```bash
sdlc-kit compare --status-file .comparison_status.json
```

Or programmatically:

```python
engine = ComparisonEngine(
    project_root=".",
    v2_docs_path="claude_suggestion/v2",
    status_file_path=".comparison_status.json"
)
```

### Status File Format

The status file is a JSON file that tracks:

```json
{
  "improvements": {
    "category_name": {
      "status": "implemented",
      "completion_date": "2024-01-15T10:30:00",
      "notes": "Completed as part of sprint 3"
    }
  },
  "deviations": {
    "category_name": {
      "status": "skipped",
      "reason": "Not applicable to our use case",
      "date": "2024-01-10T14:20:00"
    }
  }
}
```

### Working with Status

```python
from agentic_sdlc.comparison.status import StatusTracker

tracker = StatusTracker(".comparison_status.json")

# Mark an improvement as complete
tracker.mark_complete("Directory Structure", notes="Reorganized all modules")

# Mark as intentionally skipped
tracker.mark_skipped(
    "Lib Cleanup",
    reason="We use lib/ for vendored dependencies intentionally"
)

# Update a deviation reason
tracker.update_deviation_reason(
    "Lib Cleanup",
    "Updated: We need lib/ for offline deployment"
)

# Get status
status = tracker.get_status("Directory Structure")
```

## Migration Scripts

### Generating Scripts

```bash
sdlc-kit compare --generate-scripts --scripts-output ./migration_scripts
```

Or programmatically:

```python
result = engine.run_comparison(generate_migration_scripts=True)

if result.get('migration_scripts'):
    engine.save_migration_scripts(
        result['migration_scripts'],
        "migration_scripts"
    )
```

### Script Types

#### 1. backup.sh
Backs up directories before destructive operations:

```bash
#!/bin/bash
# Backup script generated by V2 Structure Comparison

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup lib/
if [ -d "lib/" ]; then
    cp -r lib/ "$BACKUP_DIR/lib/"
fi

echo "Backup completed: $BACKUP_DIR"
```

#### 2. lib_cleanup.sh
Converts bundled dependencies to requirements.txt:

```bash
#!/bin/bash
# Lib cleanup script

# Extract package names from lib/
find lib/ -maxdepth 1 -type d | sed 's|lib/||' > requirements.txt

# Remove lib/ directory
rm -rf lib/

echo "Lib cleanup completed"
```

### Using Migration Scripts

1. **Review the scripts** before running
2. **Run backup script first**: `./migration_scripts/backup.sh`
3. **Run migration scripts**: `./migration_scripts/lib_cleanup.sh`
4. **Verify changes**: Check that everything works
5. **Commit changes**: `git add . && git commit -m "Apply v2 structure changes"`

## Troubleshooting

### Common Issues

#### 1. "Cannot access project directory"

**Problem**: Permission denied when scanning project.

**Solution**:
- Check file permissions: `ls -la`
- Ensure you have read access to all directories
- Run with appropriate permissions

#### 2. "No v2 documents could be parsed"

**Problem**: V2 suggestion documents not found or malformed.

**Solution**:
- Verify v2 docs path: `ls claude_suggestion/v2/`
- Check that required files exist:
  - SDLC_Improvement_Suggestions.md
  - Proposed_Structure.md
- Ensure files are valid markdown

#### 3. "Comparison failed: Invalid project directory"

**Problem**: Project root path is incorrect.

**Solution**:
- Verify project root path exists
- Use absolute path if relative path fails
- Check for typos in path

#### 4. Migration scripts fail to execute

**Problem**: Scripts have syntax errors or missing permissions.

**Solution**:
- Make scripts executable: `chmod +x migration_scripts/*.sh`
- Review script contents for errors
- Run with bash explicitly: `bash migration_scripts/backup.sh`

#### 5. Status file not updating

**Problem**: Status tracking file not being written.

**Solution**:
- Check write permissions in directory
- Ensure status file path is valid
- Verify no other process is locking the file

### Debug Mode

Enable verbose output for debugging:

```bash
sdlc-kit compare --verbose
```

This will show:
- Detailed progress messages
- File paths being processed
- Parsing results
- Error stack traces

### Logging

The comparison engine uses Python's logging module. Configure logging in your code:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('agentic_sdlc.comparison')
logger.setLevel(logging.DEBUG)
```

## Best Practices

### 1. Run Comparisons Regularly

Run comparisons periodically to track progress:

```bash
# Weekly comparison
sdlc-kit compare --status-file .comparison_status.json --output weekly_report.md
```

### 2. Use Status Tracking

Enable status tracking to maintain history:

```python
engine = ComparisonEngine(
    project_root=".",
    v2_docs_path="claude_suggestion/v2",
    status_file_path=".comparison_status.json"
)
```

### 3. Review Before Applying

Always review migration scripts before running:

```bash
# Generate scripts
sdlc-kit compare --generate-scripts

# Review each script
cat migration_scripts/backup.sh
cat migration_scripts/lib_cleanup.sh

# Run backup first
./migration_scripts/backup.sh

# Then run migrations
./migration_scripts/lib_cleanup.sh
```

### 4. Document Deviations

If you intentionally skip a suggestion, document why:

```python
tracker.mark_skipped(
    "Lib Cleanup",
    reason="We use lib/ for vendored dependencies required for offline deployment"
)
```

### 5. Focus on Quick Wins

Start with quick wins for fast progress:

```python
result = engine.run_comparison()
quick_wins = [t for t in result['tasks'] if t.effort_hours < 4]

# Implement quick wins first
for task in quick_wins:
    print(f"Quick win: {task.title} ({task.effort_hours:.1f}h)")
```

### 6. Address High Priority Gaps

Prioritize high-impact items:

```python
gaps = result['gaps']
high_priority = [g for g in gaps if g.priority == "High"]

# Focus on high priority gaps
for gap in high_priority:
    print(f"High priority: {gap.description}")
    print(f"Action: {gap.proposed_action}")
```

## Integration

### CI/CD Integration

Run comparisons in CI/CD to track progress:

```yaml
# .github/workflows/v2-comparison.yml
name: V2 Structure Comparison

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  compare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Run comparison
        run: |
          sdlc-kit compare \
            --status-file .comparison_status.json \
            --output comparison_report.md \
            --verbose
      
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: comparison-report
          path: comparison_report.md
```

### Pre-commit Hook

Run comparison before commits:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run quick comparison
sdlc-kit compare --no-validation --output .comparison_check.md

# Check completion percentage
# (Add logic to fail if completion drops)
```

## Advanced Usage

### Custom Analyzers

Extend the comparison with custom analyzers:

```python
from agentic_sdlc.comparison.analyzer import GapAnalyzer

class CustomGapAnalyzer(GapAnalyzer):
    def identify_gaps(self, comparison):
        gaps = super().identify_gaps(comparison)
        
        # Add custom gap detection logic
        # ...
        
        return gaps

# Use custom analyzer
engine = ComparisonEngine(project_root=".", v2_docs_path="claude_suggestion/v2")
engine.gap_analyzer = CustomGapAnalyzer()
```

### Custom Reports

Create custom report formats:

```python
from agentic_sdlc.comparison.reporter import ComparisonReporter

class CustomReporter(ComparisonReporter):
    def generate_report(self, comparison, gaps, conflicts):
        # Custom report format
        report = "# My Custom Report\n\n"
        
        # Add custom sections
        # ...
        
        return report

# Use custom reporter
engine = ComparisonEngine(project_root=".", v2_docs_path="claude_suggestion/v2")
engine.reporter = CustomReporter()
```

### Filtering Results

Filter results based on custom criteria:

```python
result = engine.run_comparison()

# Filter gaps by category
docs_gaps = [g for g in result['gaps'] if 'documentation' in g.category.lower()]

# Filter tasks by effort
small_tasks = [t for t in result['tasks'] if t.effort_hours < 2]

# Filter conflicts by severity
critical_conflicts = [c for c in result['conflicts'] if c.severity == "High"]
```

## API Reference

See the [API documentation](API.md) for complete reference of all classes and methods.

## Examples

See `examples/v2_structure_comparison_demo.py` for comprehensive examples of:

- Basic comparison
- Generating migration scripts
- Accessing detailed results
- Creating custom reports
- Using status tracking
- Validation checks

Run the demo:

```bash
python examples/v2_structure_comparison_demo.py
```

## Contributing

To contribute improvements to the V2 Structure Comparison feature:

1. Review the design document: `.kiro/specs/v2-structure-comparison/design.md`
2. Check the requirements: `.kiro/specs/v2-structure-comparison/requirements.md`
3. Follow the implementation plan: `.kiro/specs/v2-structure-comparison/tasks.md`
4. Write property-based tests for new features
5. Update this documentation

## License

This feature is part of the agentic-sdlc project and follows the same license.
