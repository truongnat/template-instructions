"""
Unit tests for the MarkdownParser utility class.

Tests cover the three main methods:
- extract_sections(): Parse markdown headers and extract section content
- extract_code_blocks(): Extract fenced code blocks
- parse_checklist_items(): Parse checkbox lists
"""

import pytest
from agentic_sdlc.comparison.parser import MarkdownParser


class TestMarkdownParser:
    """Test suite for MarkdownParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create a MarkdownParser instance for testing."""
        return MarkdownParser()
    
    # Tests for extract_sections()
    
    def test_extract_sections_single_section(self, parser):
        """Test extracting a single section."""
        content = "# Section 1\nThis is content for section 1."
        sections = parser.extract_sections(content)
        
        assert len(sections) == 1
        assert "Section 1" in sections
        assert sections["Section 1"] == "This is content for section 1."
    
    def test_extract_sections_multiple_sections(self, parser):
        """Test extracting multiple sections at the same level."""
        content = """# Section 1
Content 1

# Section 2
Content 2

# Section 3
Content 3"""
        sections = parser.extract_sections(content)
        
        assert len(sections) == 3
        assert sections["Section 1"] == "Content 1"
        assert sections["Section 2"] == "Content 2"
        assert sections["Section 3"] == "Content 3"
    
    def test_extract_sections_nested_headers(self, parser):
        """Test that all headers are extracted as separate sections."""
        content = """# Main Section
Main content

## Subsection
Subsection content

### Sub-subsection
Deep content

# Another Section
Other content"""
        sections = parser.extract_sections(content)
        
        assert len(sections) == 4
        assert "Main Section" in sections
        assert "Subsection" in sections
        assert "Sub-subsection" in sections
        assert "Another Section" in sections
        
        # Each section has its own content
        assert sections["Main Section"] == "Main content"
        assert sections["Subsection"] == "Subsection content"
        assert sections["Sub-subsection"] == "Deep content"
        assert sections["Another Section"] == "Other content"
    
    def test_extract_sections_empty_content(self, parser):
        """Test extracting sections from empty content."""
        content = ""
        sections = parser.extract_sections(content)
        
        assert len(sections) == 0
    
    def test_extract_sections_no_headers(self, parser):
        """Test content without any headers."""
        content = "Just some text\nwithout any headers\nat all."
        sections = parser.extract_sections(content)
        
        assert len(sections) == 0
    
    def test_extract_sections_header_with_special_chars(self, parser):
        """Test headers containing special characters."""
        content = """# Section: With Colon
Content 1

# Section (With Parentheses)
Content 2

# Section - With Dash
Content 3"""
        sections = parser.extract_sections(content)
        
        assert len(sections) == 3
        assert "Section: With Colon" in sections
        assert "Section (With Parentheses)" in sections
        assert "Section - With Dash" in sections
    
    def test_extract_sections_preserves_whitespace(self, parser):
        """Test that content whitespace is preserved."""
        content = """# Section
Line 1
    Indented line
        More indented

Another paragraph"""
        sections = parser.extract_sections(content)
        
        assert "    Indented line" in sections["Section"]
        assert "        More indented" in sections["Section"]
    
    # Tests for extract_code_blocks()
    
    def test_extract_code_blocks_single_block(self, parser):
        """Test extracting a single code block."""
        content = """Some text
```
code here
```
More text"""
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 1
        assert blocks[0] == "code here"
    
    def test_extract_code_blocks_with_language_tag(self, parser):
        """Test extracting code blocks with language tags."""
        content = """```python
print('hello')
```

```javascript
console.log('world');
```"""
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 2
        assert blocks[0] == "print('hello')"
        assert blocks[1] == "console.log('world');"
    
    def test_extract_code_blocks_multiple_blocks(self, parser):
        """Test extracting multiple code blocks."""
        content = """Text before

```
block 1
```

Text between

```
block 2
```

Text after"""
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 2
        assert blocks[0] == "block 1"
        assert blocks[1] == "block 2"
    
    def test_extract_code_blocks_multiline(self, parser):
        """Test extracting multiline code blocks."""
        content = """```python
def hello():
    print('Hello')
    return True
```"""
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 1
        assert "def hello():" in blocks[0]
        assert "    print('Hello')" in blocks[0]
        assert "    return True" in blocks[0]
    
    def test_extract_code_blocks_empty_content(self, parser):
        """Test extracting code blocks from empty content."""
        content = ""
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 0
    
    def test_extract_code_blocks_no_blocks(self, parser):
        """Test content without any code blocks."""
        content = "Just regular text\nwithout any code blocks."
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 0
    
    def test_extract_code_blocks_empty_block(self, parser):
        """Test extracting an empty code block."""
        content = """```
```"""
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 1
        assert blocks[0] == ""
    
    def test_extract_code_blocks_with_special_chars(self, parser):
        """Test code blocks containing special characters."""
        content = """```
Special chars: !@#$%^&*()
Quotes: "double" 'single'
Backslashes: \\ \\n \\t
```"""
        blocks = parser.extract_code_blocks(content)
        
        assert len(blocks) == 1
        assert "!@#$%^&*()" in blocks[0]
        assert '"double"' in blocks[0]
        assert "\\" in blocks[0]  # Single backslash in the extracted content
    
    # Tests for parse_checklist_items()
    
    def test_parse_checklist_items_unchecked(self, parser):
        """Test parsing unchecked checklist items."""
        content = "- [ ] Task 1\n- [ ] Task 2"
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 2
        assert items[0]['text'] == "Task 1"
        assert items[0]['checked'] is False
        assert items[0]['line_number'] == 1
        assert items[1]['text'] == "Task 2"
        assert items[1]['checked'] is False
        assert items[1]['line_number'] == 2
    
    def test_parse_checklist_items_checked_lowercase(self, parser):
        """Test parsing checked items with lowercase x."""
        content = "- [x] Completed task"
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 1
        assert items[0]['text'] == "Completed task"
        assert items[0]['checked'] is True
    
    def test_parse_checklist_items_checked_uppercase(self, parser):
        """Test parsing checked items with uppercase X."""
        content = "- [X] Completed task"
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 1
        assert items[0]['text'] == "Completed task"
        assert items[0]['checked'] is True
    
    def test_parse_checklist_items_mixed(self, parser):
        """Test parsing a mix of checked and unchecked items."""
        content = """- [ ] Todo 1
- [x] Done 1
- [ ] Todo 2
- [X] Done 2
- [ ] Todo 3"""
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 5
        assert items[0]['checked'] is False
        assert items[1]['checked'] is True
        assert items[2]['checked'] is False
        assert items[3]['checked'] is True
        assert items[4]['checked'] is False
    
    def test_parse_checklist_items_with_indentation(self, parser):
        """Test parsing indented checklist items."""
        content = """  - [ ] Indented task 1
    - [x] More indented task 2"""
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 2
        assert items[0]['text'] == "Indented task 1"
        assert items[1]['text'] == "More indented task 2"
    
    def test_parse_checklist_items_empty_content(self, parser):
        """Test parsing empty content."""
        content = ""
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 0
    
    def test_parse_checklist_items_no_items(self, parser):
        """Test content without checklist items."""
        content = "Just regular text\nwithout any checklist items."
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 0
    
    def test_parse_checklist_items_with_special_chars(self, parser):
        """Test checklist items containing special characters."""
        content = """- [ ] Task with: colon
- [x] Task (with parentheses)
- [ ] Task - with dash
- [ ] Task with "quotes"
- [ ] Task with 'apostrophes'"""
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 5
        assert items[0]['text'] == "Task with: colon"
        assert items[1]['text'] == "Task (with parentheses)"
        assert items[2]['text'] == "Task - with dash"
        assert items[3]['text'] == 'Task with "quotes"'
        assert items[4]['text'] == "Task with 'apostrophes'"
    
    def test_parse_checklist_items_line_numbers(self, parser):
        """Test that line numbers are correctly tracked."""
        content = """Some text before
- [ ] Task 1
More text
- [x] Task 2
Even more text
- [ ] Task 3"""
        items = parser.parse_checklist_items(content)
        
        assert len(items) == 3
        assert items[0]['line_number'] == 2
        assert items[1]['line_number'] == 4
        assert items[2]['line_number'] == 6
    
    def test_parse_checklist_items_multiline_text(self, parser):
        """Test that only the first line of item is captured."""
        content = """- [ ] Task 1
  This is continuation but not part of checkbox
- [x] Task 2"""
        items = parser.parse_checklist_items(content)
        
        # Should only capture the checkbox lines, not continuations
        assert len(items) == 2
        assert items[0]['text'] == "Task 1"
        assert items[1]['text'] == "Task 2"
    
    # Integration tests combining multiple methods
    
    def test_extract_sections_with_code_blocks(self, parser):
        """Test extracting sections that contain code blocks."""
        content = """# Section 1
Some text

```python
code here
```

# Section 2
More text"""
        sections = parser.extract_sections(content)
        code_blocks = parser.extract_code_blocks(content)
        
        assert len(sections) == 2
        assert len(code_blocks) == 1
        assert "```python" in sections["Section 1"]
    
    def test_extract_sections_with_checklists(self, parser):
        """Test extracting sections that contain checklists."""
        content = """# Tasks
- [ ] Task 1
- [x] Task 2

# Notes
Some notes here"""
        sections = parser.extract_sections(content)
        items = parser.parse_checklist_items(content)
        
        assert len(sections) == 2
        assert len(items) == 2
        assert "- [ ] Task 1" in sections["Tasks"]



class TestV2SuggestionParser:
    """Test suite for V2SuggestionParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create a V2SuggestionParser instance for testing."""
        from agentic_sdlc.comparison.parser import V2SuggestionParser
        return V2SuggestionParser()
    
    # Tests for parse_improvement_suggestions()
    
    def test_parse_improvement_suggestions_returns_15_categories(self, parser):
        """Test that parsing SDLC_Improvement_Suggestions.md returns exactly 15 categories."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        # Should have exactly 15 improvement categories
        assert len(improvements) == 15
    
    def test_parse_improvement_suggestions_first_category(self, parser):
        """Test that the first category is parsed correctly."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        # First category should be about lib directory cleanup
        first = improvements[0]
        assert 'lib' in first.category.lower() or 'clean' in first.category.lower()
        assert first.priority in ['High', 'Medium', 'Low']
        assert first.estimated_hours > 0
        assert isinstance(first.description, str)
        assert len(first.description) > 0
    
    def test_parse_improvement_suggestions_all_have_required_fields(self, parser):
        """Test that all improvements have required fields."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        for improvement in improvements:
            assert isinstance(improvement.category, str)
            assert len(improvement.category) > 0
            assert isinstance(improvement.title, str)
            assert len(improvement.title) > 0
            assert isinstance(improvement.description, str)
            assert len(improvement.description) > 0
            assert improvement.priority in ['High', 'Medium', 'Low']
            assert improvement.estimated_hours > 0
            assert isinstance(improvement.related_directories, list)
    
    def test_parse_improvement_suggestions_categories_are_unique(self, parser):
        """Test that all category names are unique."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        categories = [imp.category for imp in improvements]
        assert len(categories) == len(set(categories))
    
    def test_parse_improvement_suggestions_extracts_directories(self, parser):
        """Test that related directories are extracted from content."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        # At least some improvements should have related directories
        has_directories = any(len(imp.related_directories) > 0 for imp in improvements)
        assert has_directories
    
    # Tests for parse_proposed_structure()
    
    def test_parse_proposed_structure_extracts_directories(self, parser):
        """Test that proposed structure extracts directory tree."""
        file_path = 'claude_suggestion/v2/Proposed_Structure.md'
        
        structure = parser.parse_proposed_structure(file_path)
        
        # Should have multiple directories
        assert len(structure.directories) > 0
    
    def test_parse_proposed_structure_has_key_directories(self, parser):
        """Test that key directories are present in proposed structure."""
        file_path = 'claude_suggestion/v2/Proposed_Structure.md'
        
        structure = parser.parse_proposed_structure(file_path)
        
        # Check for some key directories that should be in the proposed structure
        dir_paths = list(structure.directories.keys())
        
        # Should have docs/ directory
        has_docs = any('docs' in path.lower() for path in dir_paths)
        assert has_docs, f"docs/ not found in: {dir_paths}"
    
    def test_parse_proposed_structure_directories_have_required_fields(self, parser):
        """Test that all proposed directories have required fields."""
        file_path = 'claude_suggestion/v2/Proposed_Structure.md'
        
        structure = parser.parse_proposed_structure(file_path)
        
        for dir_path, proposed_dir in structure.directories.items():
            assert isinstance(proposed_dir.path, str)
            assert len(proposed_dir.path) > 0
            assert isinstance(proposed_dir.purpose, str)
            assert isinstance(proposed_dir.subdirectories, list)
            assert isinstance(proposed_dir.required_files, list)
            assert isinstance(proposed_dir.is_new, bool)
    
    def test_parse_proposed_structure_identifies_new_directories(self, parser):
        """Test that new directories are correctly identified."""
        file_path = 'claude_suggestion/v2/Proposed_Structure.md'
        
        structure = parser.parse_proposed_structure(file_path)
        
        # At least some directories should be marked as new
        new_dirs = [d for d in structure.directories.values() if d.is_new]
        assert len(new_dirs) > 0
    
    # Tests for parse_checklist()
    
    def test_parse_checklist_extracts_items(self, parser):
        """Test that checklist items are extracted."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        # Should have multiple checklist items
        assert len(items) > 0
    
    def test_parse_checklist_items_have_required_fields(self, parser):
        """Test that all checklist items have required fields."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        for item in items:
            assert 'text' in item
            assert 'checked' in item
            assert 'priority' in item
            assert 'category' in item
            assert 'estimated_hours' in item
            
            assert isinstance(item['text'], str)
            assert len(item['text']) > 0
            assert isinstance(item['checked'], bool)
            assert isinstance(item['priority'], str)
            assert isinstance(item['category'], str)
            assert isinstance(item['estimated_hours'], (int, float))
            assert item['estimated_hours'] > 0
    
    def test_parse_checklist_has_priority_levels(self, parser):
        """Test that checklist items have different priority levels."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        priorities = set(item['priority'] for item in items)
        
        # Should have multiple priority levels
        assert len(priorities) > 1
    
    def test_parse_checklist_has_categories(self, parser):
        """Test that checklist items are categorized."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        categories = set(item['category'] for item in items)
        
        # Should have multiple categories
        assert len(categories) > 1
    
    # Tests for extract_directory_tree()
    
    def test_extract_directory_tree_simple(self, parser):
        """Test extracting a simple directory tree."""
        tree_text = """
project/
├── docs/
├── src/
└── tests/
"""
        
        tree = parser.extract_directory_tree(tree_text)
        
        # 'project/' is stripped because it's the only root
        assert 'project/' not in tree
        assert 'docs/' in tree
        assert 'src/' in tree
        assert 'tests/' in tree
    
    def test_extract_directory_tree_nested(self, parser):
        """Test extracting a nested directory tree."""
        tree_text = """
project/
├── docs/
│   ├── api/
│   └── guides/
└── src/
    ├── core/
    └── utils/
"""
        
        tree = parser.extract_directory_tree(tree_text)
        
        # 'project/' is stripped because it's the only root
        assert 'project/' not in tree
        assert 'docs/' in tree
        assert 'src/' in tree
        
        # Check nested structure
        assert 'api/' in tree['docs/']
        assert 'guides/' in tree['docs/']
        assert 'core/' in tree['src/']
        assert 'utils/' in tree['src/']
    
    def test_extract_directory_tree_ignores_files(self, parser):
        """Test that files (not ending with /) are not added to directory tree."""
        tree_text = """
project/
├── README.md
├── setup.py
└── src/
    └── main.py
"""
        
        tree = parser.extract_directory_tree(tree_text)
        
        # Should only have directories
        assert 'project/' in tree
        assert 'src/' in tree['project/']
        
        # Files should not be in the tree keys
        assert 'README.md' not in tree
        assert 'setup.py' not in tree
    
    def test_extract_directory_tree_empty(self, parser):
        """Test extracting from empty content."""
        tree_text = ""
        
        tree = parser.extract_directory_tree(tree_text)
        
        assert isinstance(tree, dict)
        assert len(tree) == 0
    
    def test_extract_directory_tree_with_comments(self, parser):
        """Test extracting directory tree with comments."""
        tree_text = """
project/
├── docs/          # Documentation
├── src/           # Source code
└── tests/         # Test files
"""
        
        tree = parser.extract_directory_tree(tree_text)
        
        # Should extract directories regardless of comments
        assert 'project/' in tree
        assert 'docs/' in tree['project/']
        assert 'src/' in tree['project/']
        assert 'tests/' in tree['project/']
    
    # Additional comprehensive tests for actual v2 documents
    
    def test_parse_improvement_suggestions_specific_categories(self, parser):
        """Test that specific expected categories are present in SDLC_Improvement_Suggestions.md."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        # Extract category names
        categories = [imp.category for imp in improvements]
        
        # Check for specific expected categories
        expected_keywords = [
            'lib',  # Category 1: Clean Up & Organize lib Directory
            'Documentation',  # Category 2: Add Documentation Layer
            'Configuration',  # Category 3: Improve Configuration Management
            'Tests',  # Category 4: Add Tests Properly Structured
            'Logging',  # Category 5: Add Logging & Monitoring Structure
        ]
        
        for keyword in expected_keywords:
            assert any(keyword.lower() in cat.lower() for cat in categories), \
                f"Expected keyword '{keyword}' not found in categories: {categories}"
    
    def test_parse_improvement_suggestions_priority_distribution(self, parser):
        """Test that improvements have a reasonable priority distribution."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        # Count priorities
        priorities = [imp.priority for imp in improvements]
        priority_counts = {
            'High': priorities.count('High'),
            'Medium': priorities.count('Medium'),
            'Low': priorities.count('Low')
        }
        
        # Should have at least some high priority items
        assert priority_counts['High'] > 0, "Should have at least one high priority item"
        
        # All priorities should be valid
        for priority in priorities:
            assert priority in ['High', 'Medium', 'Low'], f"Invalid priority: {priority}"
    
    def test_parse_improvement_suggestions_estimated_hours_reasonable(self, parser):
        """Test that estimated hours are reasonable values."""
        file_path = 'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        
        improvements = parser.parse_improvement_suggestions(file_path)
        
        for improvement in improvements:
            # Hours should be positive and reasonable (between 1 and 20 hours)
            assert 0 < improvement.estimated_hours <= 20, \
                f"Unreasonable hours estimate for {improvement.category}: {improvement.estimated_hours}"
    
    def test_parse_proposed_structure_complete_tree(self, parser):
        """Test that Proposed_Structure.md extracts a complete directory tree."""
        file_path = 'claude_suggestion/v2/Proposed_Structure.md'
        
        structure = parser.parse_proposed_structure(file_path)
        
        # Should have a substantial number of directories
        assert len(structure.directories) >= 10, \
            f"Expected at least 10 directories, got {len(structure.directories)}"
        
        # Check for specific key directories that should be in the proposed structure
        expected_dirs = ['docs/', 'config/', 'tests/', 'cli/', 'models/']
        
        for expected_dir in expected_dirs:
            # Check if the directory exists in any path
            found = any(expected_dir in path for path in structure.directories.keys())
            assert found, f"Expected directory '{expected_dir}' not found in structure"
    
    def test_parse_proposed_structure_subdirectories(self, parser):
        """Test that proposed directories have subdirectories extracted."""
        file_path = 'claude_suggestion/v2/Proposed_Structure.md'
        
        structure = parser.parse_proposed_structure(file_path)
        
        # At least some directories should have subdirectories
        dirs_with_subdirs = [d for d in structure.directories.values() if len(d.subdirectories) > 0]
        assert len(dirs_with_subdirs) > 0, "Expected some directories to have subdirectories"
    
    def test_parse_proposed_structure_new_directories_marked(self, parser):
        """Test that new directories are properly marked in Proposed_Structure.md."""
        file_path = 'claude_suggestion/v2/Proposed_Structure.md'
        
        structure = parser.parse_proposed_structure(file_path)
        
        # Count new vs existing directories
        new_dirs = [d for d in structure.directories.values() if d.is_new]
        existing_dirs = [d for d in structure.directories.values() if not d.is_new]
        
        # Should have both new and existing directories
        assert len(new_dirs) > 0, "Expected some directories to be marked as new"
        assert len(existing_dirs) > 0, "Expected some directories to be marked as existing"
    
    def test_parse_checklist_all_items_extracted(self, parser):
        """Test that Quick_Action_Checklist.md extracts all checklist items."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        # Should have a substantial number of checklist items
        assert len(items) >= 10, \
            f"Expected at least 10 checklist items, got {len(items)}"
    
    def test_parse_checklist_priority_1_items(self, parser):
        """Test that Priority 1 items are correctly identified."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        # Filter Priority 1 items
        priority_1_items = [item for item in items if 'Priority 1' in item['priority']]
        
        # Should have Priority 1 items
        assert len(priority_1_items) > 0, "Expected some Priority 1 items"
        
        # Check that Priority 1 items have reasonable hour estimates
        for item in priority_1_items:
            assert item['estimated_hours'] > 0, \
                f"Priority 1 item should have positive hours: {item['text']}"
    
    def test_parse_checklist_categories_extracted(self, parser):
        """Test that checklist items are properly categorized."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        # Extract unique categories
        categories = set(item['category'] for item in items)
        
        # Should have multiple categories
        assert len(categories) >= 3, \
            f"Expected at least 3 categories, got {len(categories)}: {categories}"
        
        # Categories should not be empty
        for category in categories:
            assert len(category) > 0, "Category should not be empty"
    
    def test_parse_checklist_specific_items(self, parser):
        """Test that specific expected checklist items are present."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        # Extract item texts
        item_texts = [item['text'].lower() for item in items]
        
        # Check for specific expected items (based on the document structure)
        expected_keywords = [
            'requirements.txt',  # Should have item about creating requirements.txt
            'docs',  # Should have items about documentation
            'tests',  # Should have items about tests
        ]
        
        for keyword in expected_keywords:
            found = any(keyword in text for text in item_texts)
            assert found, f"Expected keyword '{keyword}' not found in checklist items"
    
    def test_parse_checklist_checked_status(self, parser):
        """Test that checklist items have checked status."""
        file_path = 'claude_suggestion/v2/Quick_Action_Checklist.md'
        
        items = parser.parse_checklist(file_path)
        
        # All items should have a checked field
        for item in items:
            assert 'checked' in item, f"Item missing 'checked' field: {item}"
            assert isinstance(item['checked'], bool), \
                f"'checked' should be boolean: {item['checked']}"
    
    def test_parse_all_documents_integration(self, parser):
        """Integration test: Parse all three v2 documents successfully."""
        # Parse all three documents
        improvements = parser.parse_improvement_suggestions(
            'claude_suggestion/v2/SDLC_Improvement_Suggestions.md'
        )
        structure = parser.parse_proposed_structure(
            'claude_suggestion/v2/Proposed_Structure.md'
        )
        checklist = parser.parse_checklist(
            'claude_suggestion/v2/Quick_Action_Checklist.md'
        )
        
        # All should return data
        assert len(improvements) == 15, "Should have 15 improvement categories"
        assert len(structure.directories) > 0, "Should have directories in structure"
        assert len(checklist) > 0, "Should have checklist items"
        
        # Verify data quality
        assert all(imp.category for imp in improvements), "All improvements should have categories"
        assert all(d.path for d in structure.directories.values()), "All directories should have paths"
        assert all(item['text'] for item in checklist), "All checklist items should have text"
