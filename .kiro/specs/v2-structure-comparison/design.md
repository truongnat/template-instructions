# Design Document: V2 Structure Comparison

## Overview

The V2 Structure Comparison feature provides a comprehensive analysis tool that compares the current agentic-sdlc project structure against the proposed v2 improvements. The system will scan the existing codebase, parse the v2 suggestion documents, perform gap analysis, and generate actionable recommendations with prioritization.

The design follows a modular architecture with clear separation between data collection (scanning), analysis (comparison), and output generation (reporting). This allows each component to be tested independently and enables future extensions such as continuous monitoring or automated implementation.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Comparison Engine                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scanner    │  │   Parser     │  │   Analyzer   │     │
│  │   Module     │  │   Module     │  │   Module     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                       │
│                    │  Data Models   │                       │
│                    └───────┬────────┘                       │
│                            │                                 │
│         ┌──────────────────┴──────────────────┐             │
│         │                                      │             │
│  ┌──────▼───────┐                    ┌────────▼────────┐   │
│  │   Reporter   │                    │   Task          │   │
│  │   Module     │                    │   Generator     │   │
│  └──────────────┘                    └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

1. **Scanner Module**: Traverses the file system and collects information about the current project structure
2. **Parser Module**: Reads and extracts structured data from v2 suggestion markdown files
3. **Analyzer Module**: Compares current state against proposed state and identifies gaps
4. **Data Models**: Represents directories, files, improvements, and comparison results
5. **Reporter Module**: Generates human-readable comparison reports in markdown format
6. **Task Generator**: Creates actionable task lists with priorities and estimates

## Components and Interfaces

### 1. Scanner Module

**Purpose**: Scan the current project structure and collect metadata about directories and files.

**Key Classes**:

```python
class DirectoryScanner:
    """Scans project directory structure"""
    
    def scan_project(self, root_path: str, max_depth: int = 3) -> ProjectStructure:
        """
        Scan project starting from root_path
        
        Args:
            root_path: Root directory to scan
            max_depth: Maximum depth to traverse
            
        Returns:
            ProjectStructure object containing all discovered directories and files
        """
        pass
    
    def check_directory_exists(self, path: str) -> bool:
        """Check if a directory exists"""
        pass
    
    def get_subdirectories(self, path: str) -> List[str]:
        """Get immediate subdirectories of a path"""
        pass
    
    def find_config_files(self, root_path: str) -> Dict[str, bool]:
        """
        Find key configuration files
        
        Returns:
            Dict mapping config file names to existence boolean
        """
        pass

class LibraryAnalyzer:
    """Analyzes the lib/ directory for bundled dependencies"""
    
    def analyze_lib_directory(self, lib_path: str) -> LibraryInfo:
        """
        Analyze lib/ directory contents
        
        Returns:
            LibraryInfo with package count, size, and dependency list
        """
        pass
    
    def extract_dependencies(self, lib_path: str) -> List[str]:
        """Extract list of bundled packages from lib/"""
        pass
```

**Interfaces**:
- Input: Project root path
- Output: `ProjectStructure` object containing directory tree and file metadata

### 2. Parser Module

**Purpose**: Parse v2 suggestion documents and extract structured improvement data.

**Key Classes**:

```python
class V2SuggestionParser:
    """Parses v2 improvement suggestion documents"""
    
    def parse_improvement_suggestions(self, file_path: str) -> List[Improvement]:
        """
        Parse SDLC_Improvement_Suggestions.md
        
        Returns:
            List of Improvement objects with categories and recommendations
        """
        pass
    
    def parse_proposed_structure(self, file_path: str) -> ProposedStructure:
        """
        Parse Proposed_Structure.md
        
        Returns:
            ProposedStructure object representing the directory tree
        """
        pass
    
    def parse_checklist(self, file_path: str) -> List[ChecklistItem]:
        """
        Parse Quick_Action_Checklist.md
        
        Returns:
            List of ChecklistItem objects with priorities and estimates
        """
        pass
    
    def extract_directory_tree(self, markdown_content: str) -> DirectoryTree:
        """Extract directory tree from markdown code block"""
        pass

class MarkdownParser:
    """Utility for parsing markdown documents"""
    
    def extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections by headers"""
        pass
    
    def extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks from markdown"""
        pass
    
    def parse_checklist_items(self, content: str) -> List[Dict]:
        """Parse markdown checklist items"""
        pass
```

**Interfaces**:
- Input: File paths to v2 suggestion documents
- Output: Structured objects representing improvements, proposed structure, and checklists

### 3. Analyzer Module

**Purpose**: Compare current structure against proposed structure and perform gap analysis.

**Key Classes**:

```python
class StructureComparator:
    """Compares current and proposed structures"""
    
    def compare_structures(
        self, 
        current: ProjectStructure, 
        proposed: ProposedStructure
    ) -> ComparisonResult:
        """
        Compare current vs proposed structures
        
        Returns:
            ComparisonResult with implementation status for each component
        """
        pass
    
    def check_directory_status(
        self, 
        dir_path: str, 
        current: ProjectStructure, 
        proposed: ProposedStructure
    ) -> DirectoryStatus:
        """
        Check status of a specific directory
        
        Returns:
            DirectoryStatus: IMPLEMENTED, PARTIAL, or MISSING
        """
        pass
    
    def verify_subdirectories(
        self, 
        parent_path: str, 
        expected_subdirs: List[str], 
        current: ProjectStructure
    ) -> Dict[str, bool]:
        """Verify if expected subdirectories exist"""
        pass

class GapAnalyzer:
    """Analyzes gaps between current and proposed state"""
    
    def identify_gaps(self, comparison: ComparisonResult) -> List[Gap]:
        """
        Identify all gaps in implementation
        
        Returns:
            List of Gap objects describing missing or incomplete items
        """
        pass
    
    def categorize_gaps(self, gaps: List[Gap]) -> Dict[str, List[Gap]]:
        """Categorize gaps by improvement category"""
        pass
    
    def calculate_completion_percentage(
        self, 
        comparison: ComparisonResult
    ) -> float:
        """Calculate overall completion percentage"""
        pass

class ConflictDetector:
    """Detects potential conflicts in proposed changes"""
    
    def detect_conflicts(
        self, 
        current: ProjectStructure, 
        proposed: ProposedStructure
    ) -> List[Conflict]:
        """
        Detect potential conflicts
        
        Returns:
            List of Conflict objects describing issues
        """
        pass
    
    def check_import_impacts(self, file_moves: List[FileMove]) -> List[ImportImpact]:
        """Check if file moves will break imports"""
        pass
```

**Interfaces**:
- Input: `ProjectStructure` (current) and `ProposedStructure` (proposed)
- Output: `ComparisonResult`, `List[Gap]`, `List[Conflict]`

### 4. Data Models

**Purpose**: Define data structures for representing project state and analysis results.

**Key Models**:

```python
@dataclass
class ProjectStructure:
    """Represents current project structure"""
    root_path: str
    directories: Dict[str, DirectoryInfo]
    config_files: Dict[str, bool]
    lib_info: Optional[LibraryInfo]

@dataclass
class DirectoryInfo:
    """Information about a directory"""
    path: str
    exists: bool
    subdirectories: List[str]
    file_count: int
    
@dataclass
class LibraryInfo:
    """Information about lib/ directory"""
    exists: bool
    package_count: int
    total_size_mb: float
    packages: List[str]

@dataclass
class ProposedStructure:
    """Represents proposed v2 structure"""
    directories: Dict[str, ProposedDirectory]
    improvements: List[Improvement]

@dataclass
class ProposedDirectory:
    """A proposed directory in v2 structure"""
    path: str
    purpose: str
    subdirectories: List[str]
    required_files: List[str]
    is_new: bool  # True if this is a new directory

@dataclass
class Improvement:
    """An improvement from v2 suggestions"""
    category: str
    title: str
    description: str
    priority: str  # "High", "Medium", "Low"
    estimated_hours: float
    related_directories: List[str]

@dataclass
class ComparisonResult:
    """Result of comparing current vs proposed"""
    directory_statuses: Dict[str, DirectoryStatus]
    completion_percentage: float
    implemented_count: int
    partial_count: int
    missing_count: int

@dataclass
class Gap:
    """A gap in implementation"""
    category: str
    description: str
    priority: str
    effort: str  # "Quick Win", "Medium", "Large"
    related_requirement: str
    proposed_action: str

@dataclass
class Conflict:
    """A potential conflict"""
    type: str  # "directory_exists", "import_break", "config_conflict"
    description: str
    affected_paths: List[str]
    severity: str  # "High", "Medium", "Low"
    mitigation: str

class DirectoryStatus(Enum):
    """Status of a directory implementation"""
    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    MISSING = "missing"
    CONFLICT = "conflict"
```

### 5. Reporter Module

**Purpose**: Generate human-readable comparison reports.

**Key Classes**:

```python
class ComparisonReporter:
    """Generates comparison reports"""
    
    def generate_report(
        self, 
        comparison: ComparisonResult, 
        gaps: List[Gap], 
        conflicts: List[Conflict]
    ) -> str:
        """
        Generate complete comparison report in markdown
        
        Returns:
            Markdown-formatted report string
        """
        pass
    
    def generate_summary_section(self, comparison: ComparisonResult) -> str:
        """Generate summary section with completion percentage"""
        pass
    
    def generate_category_breakdown(
        self, 
        comparison: ComparisonResult
    ) -> str:
        """Generate breakdown by improvement category"""
        pass
    
    def generate_gaps_section(self, gaps: List[Gap]) -> str:
        """Generate section listing all gaps"""
        pass
    
    def generate_conflicts_section(self, conflicts: List[Conflict]) -> str:
        """Generate section listing conflicts"""
        pass
    
    def generate_quick_wins_section(self, gaps: List[Gap]) -> str:
        """Generate section highlighting quick wins"""
        pass

class ProgressVisualizer:
    """Creates visual representations of progress"""
    
    def create_progress_bar(self, percentage: float) -> str:
        """Create ASCII progress bar"""
        pass
    
    def create_category_chart(
        self, 
        categories: Dict[str, DirectoryStatus]
    ) -> str:
        """Create ASCII chart showing category statuses"""
        pass
```

**Interfaces**:
- Input: `ComparisonResult`, `List[Gap]`, `List[Conflict]`
- Output: Markdown-formatted report string

### 6. Task Generator Module

**Purpose**: Generate actionable tasks from identified gaps.

**Key Classes**:

```python
class TaskGenerator:
    """Generates actionable tasks from gaps"""
    
    def generate_tasks(self, gaps: List[Gap]) -> List[Task]:
        """
        Generate tasks from gaps
        
        Returns:
            List of Task objects with descriptions and metadata
        """
        pass
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority and dependencies"""
        pass
    
    def group_related_tasks(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        """Group related tasks into work packages"""
        pass
    
    def estimate_task_effort(self, task: Task) -> float:
        """Estimate hours required for a task"""
        pass

class MigrationScriptGenerator:
    """Generates migration scripts for structural changes"""
    
    def generate_lib_cleanup_script(self, lib_info: LibraryInfo) -> str:
        """Generate script to cleanup lib/ and create requirements.txt"""
        pass
    
    def generate_directory_move_script(
        self, 
        moves: List[DirectoryMove]
    ) -> str:
        """Generate git mv commands for directory reorganization"""
        pass
    
    def generate_import_update_script(
        self, 
        file_moves: List[FileMove]
    ) -> str:
        """Generate script to update import statements"""
        pass
    
    def generate_backup_script(self) -> str:
        """Generate backup commands before migrations"""
        pass

@dataclass
class Task:
    """An actionable task"""
    id: str
    title: str
    description: str
    priority: str
    effort_hours: float
    category: str
    files_to_create: List[str]
    files_to_modify: List[str]
    dependencies: List[str]  # IDs of tasks that must complete first
    reference: str  # Reference to v2 suggestion section
```

**Interfaces**:
- Input: `List[Gap]`, `LibraryInfo`, `List[DirectoryMove]`
- Output: `List[Task]`, migration scripts as strings

## Data Models

### Core Data Flow

```
File System → Scanner → ProjectStructure
                              ↓
V2 Docs → Parser → ProposedStructure
                              ↓
                        Analyzer
                              ↓
                    ComparisonResult + Gaps + Conflicts
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
                Reporter            TaskGenerator
                    ↓                   ↓
            Markdown Report         Task List
```

### Key Relationships

- `ProjectStructure` contains multiple `DirectoryInfo` objects
- `ProposedStructure` contains multiple `ProposedDirectory` and `Improvement` objects
- `ComparisonResult` maps directory paths to `DirectoryStatus` enums
- `Gap` objects reference `Improvement` categories
- `Task` objects are generated from `Gap` objects
- `Conflict` objects reference paths in both `ProjectStructure` and `ProposedStructure`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, I've identified several areas where properties can be consolidated:

**Redundancies Identified:**
1. Properties 5.1-5.4 all test subdirectory verification for different directories - these can be combined into one comprehensive property about subdirectory verification
2. Properties 1.3 and 10.1 both test file existence checking - can be combined
3. Properties 2.4 and 2.5 both test improvement classification - can be combined into one property about classification
4. Properties 4.4 and 4.5 both test report section presence - can be combined with 4.1 into a general report structure property
5. Properties 7.2, 7.3, and 7.5 all test task content completeness - can be combined into one property
6. Properties 11.1-11.5 all test script generation - can be combined into fewer properties about script validity

**Consolidated Properties:**
- Subdirectory verification (combines 5.1-5.4, 3.2)
- File detection (combines 1.3, 10.1)
- Improvement classification (combines 2.4, 2.5)
- Report structure completeness (combines 4.1, 4.4, 4.5)
- Task content completeness (combines 7.2, 7.3, 7.5)
- Script generation validity (combines 11.1-11.3)

### Correctness Properties

Property 1: Directory scanning completeness
*For any* directory tree with known structure, scanning should identify all directories up to the specified depth limit and no directories beyond that depth
**Validates: Requirements 1.1, 1.2**

Property 2: Configuration file detection
*For any* project root directory, the scanner should correctly identify the presence or absence of all specified configuration files (pyproject.toml, requirements.txt, Dockerfile, etc.)
**Validates: Requirements 1.3, 10.1**

Property 3: Lib directory analysis
*For any* lib/ directory containing Python packages, the analyzer should correctly determine if it contains bundled dependencies and extract the package list
**Validates: Requirements 1.4**

Property 4: V2 directory checklist completeness
*For any* list of directories mentioned in v2 suggestions, the scanner should check and record the status of every directory in that list
**Validates: Requirements 1.5**

Property 5: Markdown parsing completeness
*For any* valid markdown document with code blocks and sections, the parser should extract all sections and code blocks without loss
**Validates: Requirements 2.2, 2.3**

Property 6: Improvement classification
*For any* improvement from v2 suggestions, the system should correctly classify whether it involves directory changes, file changes, or both
**Validates: Requirements 2.4, 2.5**

Property 7: Directory status assignment
*For any* proposed directory and current project structure, the comparator should assign exactly one status: IMPLEMENTED, PARTIAL, MISSING, or CONFLICT
**Validates: Requirements 3.1**

Property 8: Subdirectory verification
*For any* directory with a list of expected subdirectories, the verifier should correctly identify which expected subdirectories exist and which are missing
**Validates: Requirements 3.2, 5.1, 5.2, 5.3, 5.4**

Property 9: Configuration content verification
*For any* configuration file with expected sections, the analyzer should correctly identify which sections are present and which are missing
**Validates: Requirements 3.3, 10.2**

Property 10: Gap analysis structure
*For any* comparison result, the gap analysis should produce a list where each gap has all required fields (category, description, priority, effort, action)
**Validates: Requirements 3.5**

Property 11: Report structure completeness
*For any* generated comparison report, it should contain all required sections: summary with completion percentage, category breakdown, gaps section, conflicts section, quick wins section, and high priority gaps section
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

Property 12: Directory mismatch detection
*For any* existing directory that doesn't match the proposed organization, the system should flag it as a mismatch with details about the discrepancy
**Validates: Requirements 5.5**

Property 13: Priority categorization
*For any* identified gap, the priority matrix should assign exactly one priority level (High, Medium, or Low) and exactly one effort level (Quick Win, Medium, or Large)
**Validates: Requirements 6.1, 6.2**

Property 14: Task dependency ordering
*For any* list of tasks with dependencies, the generated implementation order should ensure no task appears before any of its dependencies
**Validates: Requirements 6.3, 6.4**

Property 15: Quick wins identification
*For any* set of gaps, the quick wins should be exactly those gaps with effort level "Quick Win" and priority "High" or "Medium"
**Validates: Requirements 6.5**

Property 16: Task generation completeness
*For any* identified gap, the task generator should create a task that includes all required fields: description, files to create/modify, v2 reference, time estimate, and category
**Validates: Requirements 7.1, 7.2, 7.3, 7.5**

Property 17: Task grouping coherence
*For any* set of related tasks (same category or shared dependencies), the grouping function should place them in the same work package
**Validates: Requirements 7.4**

Property 18: Conflict detection
*For any* proposed directory that exists with different contents than proposed, the conflict detector should flag it with severity level and mitigation suggestion
**Validates: Requirements 8.1**

Property 19: Import impact analysis
*For any* file move operation, the analyzer should identify all import statements in the codebase that reference the moved file
**Validates: Requirements 8.3**

Property 20: Gitignore validation
*For any* directory that should be excluded (lib/, venv/, __pycache__/, etc.), the validator should verify that .gitignore contains a pattern matching that directory
**Validates: Requirements 8.4**

Property 21: CI/CD compatibility check
*For any* proposed structural change, the validator should verify it doesn't break paths referenced in CI/CD workflow files
**Validates: Requirements 8.5**

Property 22: Status tracking persistence
*For any* status update operation, writing to the status file and then reading it back should return the same status information
**Validates: Requirements 9.1, 9.5**

Property 23: Completion date recording
*For any* improvement marked as complete, the status file should contain a completion date field with a valid ISO 8601 timestamp
**Validates: Requirements 9.2**

Property 24: Completion percentage calculation
*For any* set of improvements with completion statuses, the calculated percentage should equal (number completed / total number) × 100
**Validates: Requirements 9.3**

Property 25: Progress visualization generation
*For any* completion percentage, the generated visualization should include a progress bar and category breakdown
**Validates: Requirements 9.4**

Property 26: Supersession detection
*For any* v2 suggestion where the actual implementation achieves the same goal through different means, the system should identify it as superseded
**Validates: Requirements 10.4**

Property 27: Applicability checking
*For any* v2 suggestion that conflicts with current project decisions or is outdated, the system should flag it as potentially not applicable
**Validates: Requirements 10.5**

Property 28: Migration script validity
*For any* generated migration script (lib cleanup, directory moves, import updates), the script should be syntactically valid and executable
**Validates: Requirements 11.1, 11.2, 11.3**

Property 29: Backup script generation
*For any* destructive operation in a migration script, a corresponding backup command should be generated before the destructive operation
**Validates: Requirements 11.4**

Property 30: Rollback script generation
*For any* migration script, a corresponding rollback script should be generated that reverses all operations
**Validates: Requirements 11.5**

Property 31: Skip status validation
*For any* attempt to mark a suggestion as "Intentionally Skipped", the operation should fail if no reason is provided
**Validates: Requirements 12.1, 12.2**

Property 32: Deviation reporting
*For any* comparison report, the deviations section should list all suggestions marked as "Intentionally Skipped" with their reasons
**Validates: Requirements 12.3**

Property 33: Status differentiation
*For any* suggestion, the system should assign exactly one status: "Implemented", "Partial", "Not Yet Implemented", or "Intentionally Skipped"
**Validates: Requirements 12.4**

Property 34: Deviation reason updates
*For any* suggestion marked as "Intentionally Skipped", updating its reason should preserve the skip status while changing only the reason text
**Validates: Requirements 12.5**

## Error Handling

### Error Categories

1. **File System Errors**
   - Directory not found
   - Permission denied
   - Disk full
   - Invalid path

2. **Parsing Errors**
   - Malformed markdown
   - Missing required sections
   - Invalid code block format
   - Encoding issues

3. **Analysis Errors**
   - Circular dependencies in tasks
   - Conflicting priorities
   - Invalid status transitions
   - Missing required data

4. **Generation Errors**
   - Template rendering failures
   - Invalid script syntax
   - Missing placeholders
   - Output file write failures

### Error Handling Strategy

**Graceful Degradation**:
- If a single v2 document fails to parse, continue with others and report the failure
- If a directory scan fails for one path, continue scanning other paths
- If conflict detection fails, proceed with comparison but warn about incomplete analysis

**Validation**:
- Validate all input paths before processing
- Validate markdown structure before parsing
- Validate generated scripts for syntax errors before writing
- Validate status transitions before updating status file

**Error Reporting**:
- All errors should include context (file path, line number, operation)
- Errors should be logged with appropriate severity levels
- User-facing error messages should be actionable
- Internal errors should include stack traces for debugging

**Recovery**:
- Provide rollback capability for status file updates
- Generate backup scripts before any destructive operations
- Support partial report generation if some data is unavailable
- Allow resuming interrupted operations

### Example Error Handling

```python
class ComparisonEngine:
    def run_comparison(self) -> ComparisonResult:
        try:
            current = self.scanner.scan_project(self.root_path)
        except PermissionError as e:
            raise ComparisonError(
                f"Cannot access project directory: {e}",
                recovery="Check file permissions and try again"
            )
        
        try:
            proposed = self.parser.parse_all_v2_docs()
        except MarkdownParseError as e:
            # Continue with partial data
            logger.warning(f"Failed to parse some v2 docs: {e}")
            proposed = e.partial_result
        
        try:
            result = self.analyzer.compare(current, proposed)
        except AnalysisError as e:
            raise ComparisonError(
                f"Comparison failed: {e}",
                recovery="Check that v2 documents are up to date"
            )
        
        return result
```

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples from the actual v2 documents
- Edge cases like empty directories, missing files
- Error conditions and exception handling
- Integration between components
- Specific scenarios like "lib/ exists with 200+ packages"

**Property Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must hold regardless of project structure
- Round-trip properties (parse → generate → parse)
- Metamorphic properties (relationships between operations)

### Property-Based Testing Configuration

- **Library**: Use `hypothesis` for Python property-based testing
- **Iterations**: Minimum 100 iterations per property test
- **Tagging**: Each property test must reference its design document property
- **Tag Format**: `# Feature: v2-structure-comparison, Property N: [property text]`

### Test Organization

```
tests/
├── unit/
│   ├── test_scanner.py              # Scanner module unit tests
│   ├── test_parser.py               # Parser module unit tests
│   ├── test_analyzer.py             # Analyzer module unit tests
│   ├── test_reporter.py             # Reporter module unit tests
│   └── test_task_generator.py       # Task generator unit tests
├── integration/
│   ├── test_full_comparison.py      # End-to-end comparison tests
│   └── test_report_generation.py    # Full report generation tests
├── property/
│   ├── test_scanner_properties.py   # Properties 1-4
│   ├── test_parser_properties.py    # Properties 5-6
│   ├── test_analyzer_properties.py  # Properties 7-12
│   ├── test_priority_properties.py  # Properties 13-15
│   ├── test_task_properties.py      # Properties 16-17
│   ├── test_conflict_properties.py  # Properties 18-21
│   ├── test_status_properties.py    # Properties 22-27
│   └── test_script_properties.py    # Properties 28-34
└── fixtures/
    ├── sample_structures.py         # Sample directory structures
    ├── sample_v2_docs.py           # Sample v2 documents
    └── generators.py               # Hypothesis generators
```

### Key Test Scenarios

**Unit Test Examples**:
1. Parse the actual SDLC_Improvement_Suggestions.md and verify 15 categories
2. Scan a test directory with lib/ containing 200+ packages
3. Generate a report for a project with 50% completion
4. Detect conflict when docs/ exists but lacks README.md
5. Generate migration script for lib/ cleanup

**Property Test Examples**:
1. For any directory tree, scanning then rescanning produces identical results
2. For any comparison result, completion percentage is between 0 and 100
3. For any task list with dependencies, topological sort produces valid order
4. For any generated script, parsing it as shell/Python succeeds
5. For any status update, read-after-write returns the written value

### Test Data Generation

Use Hypothesis strategies to generate:
- Random directory structures with varying depths
- Random markdown documents with sections and code blocks
- Random improvement lists with priorities and efforts
- Random task lists with dependencies
- Random file paths and names

### Example Property Test

```python
from hypothesis import given, strategies as st
import pytest

# Feature: v2-structure-comparison, Property 1: Directory scanning completeness
@given(
    depth=st.integers(min_value=1, max_value=5),
    structure=st.recursive(
        st.just([]),
        lambda children: st.lists(
            st.tuples(st.text(min_size=1), children),
            min_size=0,
            max_size=5
        )
    )
)
def test_directory_scanning_respects_depth_limit(tmp_path, depth, structure):
    """
    For any directory tree, scanning with depth limit N should find
    all directories at depth <= N and no directories at depth > N
    """
    # Create directory structure
    create_structure(tmp_path, structure)
    
    # Scan with depth limit
    scanner = DirectoryScanner()
    result = scanner.scan_project(str(tmp_path), max_depth=depth)
    
    # Verify all directories within depth are found
    expected_dirs = get_dirs_up_to_depth(structure, depth)
    actual_dirs = set(result.directories.keys())
    
    assert expected_dirs == actual_dirs
    
    # Verify no directories beyond depth are found
    beyond_depth_dirs = get_dirs_beyond_depth(structure, depth)
    assert beyond_depth_dirs.isdisjoint(actual_dirs)
```

### Coverage Goals

- **Line Coverage**: Minimum 85%
- **Branch Coverage**: Minimum 80%
- **Property Test Coverage**: All 34 properties must have corresponding tests
- **Integration Coverage**: All component interactions must be tested

### Continuous Testing

- Run unit tests on every commit
- Run property tests on every pull request
- Run full integration tests before release
- Monitor test execution time and optimize slow tests
- Track flaky tests and fix root causes
