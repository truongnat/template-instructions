"""
Property-based tests for the Parser module (MarkdownParser and V2SuggestionParser).

These tests use Hypothesis to verify universal properties that should hold
for all valid markdown inputs and v2 suggestion parsing.

Feature: v2-structure-comparison
Property 5: Markdown parsing completeness - For any valid markdown document 
with code blocks and sections, the parser should extract all sections and 
code blocks without loss.

Property 6: Improvement classification - For any improvement from v2 suggestions,
the system should correctly classify whether it involves directory changes, 
file changes, or both.
"""

import pytest
import tempfile
import os
from hypothesis import given, strategies as st, assume
from agentic_sdlc.comparison.parser import MarkdownParser, V2SuggestionParser


# Custom strategies for generating markdown content

@st.composite
def markdown_header(draw, level=None):
    """Generate a markdown header."""
    if level is None:
        level = draw(st.integers(min_value=1, max_value=6))
    else:
        level = draw(st.just(level))
    
    # Generate header text (avoid newlines and special chars that break headers)
    header_text = draw(st.text(
        alphabet=st.characters(
            blacklist_categories=('Cc', 'Cs'),  # Control chars
            blacklist_characters='\n\r'
        ),
        min_size=1,
        max_size=50
    ))
    
    return '#' * level + ' ' + header_text


@st.composite
def markdown_section(draw):
    """Generate a markdown section with header and content."""
    header = draw(markdown_header())
    # Generate content (can be multiline)
    content = draw(st.text(
        alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
        max_size=200
    ))
    return header + '\n' + content


@st.composite
def markdown_code_block(draw, with_language=None):
    """Generate a markdown code block."""
    if with_language is None:
        with_language = draw(st.booleans())
    
    language = ''
    if with_language:
        language = draw(st.sampled_from(['python', 'javascript', 'bash', 'java', 'cpp']))
    
    # Generate code content (avoid triple backticks inside)
    code_content = draw(st.text(
        alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
        max_size=200
    ).filter(lambda x: '```' not in x))
    
    return f'```{language}\n{code_content}\n```'


@st.composite
def markdown_checklist_item(draw, checked=None):
    """Generate a markdown checklist item."""
    if checked is None:
        checked = draw(st.booleans())
    
    checkbox = '[x]' if checked else '[ ]'
    
    # Generate item text (single line)
    item_text = draw(st.text(
        alphabet=st.characters(
            blacklist_categories=('Cc', 'Cs'),
            blacklist_characters='\n\r'
        ),
        min_size=1,
        max_size=100
    ))
    
    return f'- {checkbox} {item_text}'


@st.composite
def markdown_document_with_sections(draw):
    """Generate a markdown document with multiple sections."""
    num_sections = draw(st.integers(min_value=1, max_value=5))
    sections = [draw(markdown_section()) for _ in range(num_sections)]
    return '\n\n'.join(sections)


@st.composite
def markdown_document_with_code_blocks(draw):
    """Generate a markdown document with code blocks."""
    num_blocks = draw(st.integers(min_value=1, max_value=5))
    
    parts = []
    for _ in range(num_blocks):
        # Add some text before the code block
        text = draw(st.text(max_size=50))
        code_block = draw(markdown_code_block())
        parts.append(text)
        parts.append(code_block)
    
    return '\n\n'.join(parts)


@st.composite
def markdown_document_with_checklists(draw):
    """Generate a markdown document with checklist items."""
    num_items = draw(st.integers(min_value=1, max_value=10))
    items = [draw(markdown_checklist_item()) for _ in range(num_items)]
    return '\n'.join(items)


class TestMarkdownParserProperties:
    """Property-based tests for MarkdownParser."""
    
    # Property 5: Markdown parsing completeness - Sections
    
    @given(document=markdown_document_with_sections())
    def test_property_extract_sections_count(self, document):
        """
        Property: The number of extracted sections should equal the number of headers.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        
        # Count headers in the document
        header_count = document.count('\n#')
        # Add 1 if document starts with a header
        if document.startswith('#'):
            header_count += 1
        
        sections = parser.extract_sections(document)
        
        # Number of sections should match number of headers
        assert len(sections) == header_count
    
    @given(header=markdown_header(), content=st.text(max_size=100))
    def test_property_extract_sections_preserves_content(self, header, content):
        """
        Property: Extracted section content should be preserved exactly.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        
        # Avoid content that looks like a header
        assume('\n#' not in content)
        
        document = f"{header}\n{content}"
        sections = parser.extract_sections(document)
        
        # Should have exactly one section
        assert len(sections) == 1
        
        # Content should be preserved (stripped of leading/trailing whitespace)
        section_content = list(sections.values())[0]
        assert section_content == content.strip()
    
    @given(document=markdown_document_with_sections())
    def test_property_extract_sections_no_duplicates(self, document):
        """
        Property: Section titles should be unique keys in the result.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        sections = parser.extract_sections(document)
        
        # All keys should be unique (this is guaranteed by dict, but we verify)
        assert len(sections) == len(set(sections.keys()))
    
    # Property 5: Markdown parsing completeness - Code blocks
    
    @given(document=markdown_document_with_code_blocks())
    def test_property_extract_code_blocks_count(self, document):
        """
        Property: The number of extracted code blocks should equal the number of 
        code fence pairs.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        
        # Count code fence pairs (opening ```)
        fence_count = document.count('```') // 2
        
        code_blocks = parser.extract_code_blocks(document)
        
        # Number of code blocks should match number of fence pairs
        assert len(code_blocks) == fence_count
    
    @given(code_content=st.text(max_size=200).filter(lambda x: '```' not in x))
    def test_property_extract_code_blocks_preserves_content(self, code_content):
        """
        Property: Extracted code block content should be preserved exactly.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        document = f"```\n{code_content}\n```"
        code_blocks = parser.extract_code_blocks(document)
        
        # Should have exactly one code block
        assert len(code_blocks) == 1
        
        # Content should be preserved (stripped of leading/trailing whitespace)
        assert code_blocks[0] == code_content.strip()
    
    @given(
        code_content=st.text(max_size=100).filter(lambda x: '```' not in x),
        language=st.sampled_from(['python', 'javascript', 'bash', 'java', 'cpp', ''])
    )
    def test_property_extract_code_blocks_ignores_language_tag(self, code_content, language):
        """
        Property: Language tags should not affect extracted code content.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        document = f"```{language}\n{code_content}\n```"
        code_blocks = parser.extract_code_blocks(document)
        
        # Should have exactly one code block
        assert len(code_blocks) == 1
        
        # Content should be the same regardless of language tag
        assert code_blocks[0] == code_content.strip()
    
    @given(num_blocks=st.integers(min_value=0, max_value=10))
    def test_property_extract_code_blocks_empty_document(self, num_blocks):
        """
        Property: Extracting from a document with no code blocks returns empty list.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        # Create document with text but no code blocks
        document = "Just some text\n" * num_blocks
        code_blocks = parser.extract_code_blocks(document)
        
        assert len(code_blocks) == 0
    
    # Property 5: Markdown parsing completeness - Checklist items
    
    @given(document=markdown_document_with_checklists())
    def test_property_parse_checklist_items_count(self, document):
        """
        Property: The number of parsed checklist items should equal the number of 
        checkbox patterns.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        
        # Count checkbox patterns
        checkbox_count = document.count('- [ ]') + document.count('- [x]') + document.count('- [X]')
        
        items = parser.parse_checklist_items(document)
        
        # Number of items should match number of checkboxes
        assert len(items) == checkbox_count
    
    @given(
        item_text=st.text(
            alphabet=st.characters(
                blacklist_categories=('Cc', 'Cs'),
                blacklist_characters='\n\r'
            ),
            min_size=1,
            max_size=100
        ),
        checked=st.booleans()
    )
    def test_property_parse_checklist_items_preserves_text(self, item_text, checked):
        """
        Property: Parsed checklist item text should be preserved exactly.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        checkbox = '[x]' if checked else '[ ]'
        document = f"- {checkbox} {item_text}"
        
        items = parser.parse_checklist_items(document)
        
        # Should have exactly one item
        assert len(items) == 1
        
        # Text should be preserved
        assert items[0]['text'] == item_text.strip()
        assert items[0]['checked'] == checked
    
    @given(
        num_checked=st.integers(min_value=0, max_value=10),
        num_unchecked=st.integers(min_value=0, max_value=10)
    )
    def test_property_parse_checklist_items_checked_count(self, num_checked, num_unchecked):
        """
        Property: The number of checked items should match the input.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        
        # Create document with specific number of checked/unchecked items
        checked_items = ['- [x] Checked item' for _ in range(num_checked)]
        unchecked_items = ['- [ ] Unchecked item' for _ in range(num_unchecked)]
        document = '\n'.join(checked_items + unchecked_items)
        
        items = parser.parse_checklist_items(document)
        
        # Count checked items
        checked_count = sum(1 for item in items if item['checked'])
        unchecked_count = sum(1 for item in items if not item['checked'])
        
        assert checked_count == num_checked
        assert unchecked_count == num_unchecked
    
    @given(document=markdown_document_with_checklists())
    def test_property_parse_checklist_items_line_numbers_ascending(self, document):
        """
        Property: Line numbers should be in ascending order.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        items = parser.parse_checklist_items(document)
        
        if len(items) > 1:
            line_numbers = [item['line_number'] for item in items]
            # Line numbers should be strictly increasing
            assert all(line_numbers[i] < line_numbers[i+1] for i in range(len(line_numbers)-1))
    
    @given(document=markdown_document_with_checklists())
    def test_property_parse_checklist_items_all_have_required_fields(self, document):
        """
        Property: All parsed checklist items should have required fields.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        items = parser.parse_checklist_items(document)
        
        for item in items:
            # Each item must have these fields
            assert 'text' in item
            assert 'checked' in item
            assert 'line_number' in item
            
            # Fields should have correct types
            assert isinstance(item['text'], str)
            assert isinstance(item['checked'], bool)
            assert isinstance(item['line_number'], int)
            assert item['line_number'] >= 1
    
    # Combined properties
    
    @given(
        sections=st.lists(markdown_section(), min_size=1, max_size=5),
        code_blocks=st.lists(markdown_code_block(), min_size=1, max_size=5)
    )
    def test_property_sections_and_code_blocks_independent(self, sections, code_blocks):
        """
        Property: Extracting sections and code blocks should be independent operations.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        
        # Interleave sections and code blocks
        parts = []
        for i in range(max(len(sections), len(code_blocks))):
            if i < len(sections):
                parts.append(sections[i])
            if i < len(code_blocks):
                parts.append(code_blocks[i])
        
        document = '\n\n'.join(parts)
        
        extracted_sections = parser.extract_sections(document)
        extracted_code_blocks = parser.extract_code_blocks(document)
        
        # Should extract all sections
        assert len(extracted_sections) >= len(sections)
        
        # Should extract all code blocks
        assert len(extracted_code_blocks) == len(code_blocks)
    
    @given(text=st.text(max_size=500))
    def test_property_no_false_positives(self, text):
        """
        Property: Parser should not extract sections/code blocks from plain text.
        
        Feature: v2-structure-comparison, Property 5
        """
        parser = MarkdownParser()
        
        # Ensure text doesn't contain markdown patterns
        assume('#' not in text or '\n#' not in text)
        assume('```' not in text)
        assume('- [ ]' not in text and '- [x]' not in text and '- [X]' not in text)
        
        sections = parser.extract_sections(text)
        code_blocks = parser.extract_code_blocks(text)
        checklist_items = parser.parse_checklist_items(text)
        
        # Should not extract anything from plain text
        assert len(sections) == 0
        assert len(code_blocks) == 0
        assert len(checklist_items) == 0



# ============================================================================
# Property 6: Improvement classification
# ============================================================================

# Custom strategies for generating improvement suggestions

@st.composite
def directory_name(draw):
    """Generate a valid directory name (ASCII only, as real directories typically use ASCII)."""
    # Use ASCII letters, digits, underscore, and hyphen
    # Start with a letter
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    rest_chars = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-',
        min_size=2,
        max_size=19
    ))
    name = first_char + rest_chars
    return name + '/'


@st.composite
def file_name(draw):
    """Generate a valid file name with extension (ASCII only)."""
    # Use ASCII letters, digits, underscore, and hyphen
    # Start with a letter
    first_char = draw(st.sampled_from('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    rest_chars = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-',
        min_size=2,
        max_size=19
    ))
    name = first_char + rest_chars
    
    extension = draw(st.sampled_from(['py', 'md', 'txt', 'yaml', 'json', 'sh']))
    return f"{name}.{extension}"


@st.composite
def improvement_category(draw):
    """Generate an improvement category."""
    categories = [
        'Clean Up & Organize lib Directory',
        'Improve Documentation Structure',
        'Centralize Configuration Management',
        'Enhance Test Organization',
        'Standardize Logging',
        'Version Management',
        'CLI Structure',
        'Data Models',
        'Examples',
        'Scripts Organization'
    ]
    return draw(st.sampled_from(categories))


@st.composite
def improvement_with_directories(draw):
    """Generate an improvement suggestion that mentions directories."""
    category = draw(improvement_category())
    num_dirs = draw(st.integers(min_value=1, max_value=5))
    directories = [draw(directory_name()) for _ in range(num_dirs)]
    
    # Create description that mentions directories
    dir_mentions = ', '.join([f'`{d}`' for d in directories])
    description = f"""
## Issue
The current structure needs reorganization.

## Recommendation
Create the following directories: {dir_mentions}

## Priority
High priority task.
"""
    
    return category, description, directories


@st.composite
def improvement_with_files(draw):
    """Generate an improvement suggestion that mentions files."""
    category = draw(improvement_category())
    num_files = draw(st.integers(min_value=1, max_value=5))
    files = [draw(file_name()) for _ in range(num_files)]
    
    # Create description that mentions files
    file_mentions = ', '.join([f'`{f}`' for f in files])
    description = f"""
## Issue
Missing important files.

## Recommendation
Create the following files: {file_mentions}

## Priority
Medium priority task.
"""
    
    return category, description, files


@st.composite
def improvement_with_both(draw):
    """Generate an improvement suggestion that mentions both directories and files."""
    category = draw(improvement_category())
    num_dirs = draw(st.integers(min_value=1, max_value=3))
    num_files = draw(st.integers(min_value=1, max_value=3))
    
    directories = [draw(directory_name()) for _ in range(num_dirs)]
    files = [draw(file_name()) for _ in range(num_files)]
    
    # Create description that mentions both
    dir_mentions = ', '.join([f'`{d}`' for d in directories])
    file_mentions = ', '.join([f'`{f}`' for f in files])
    description = f"""
## Issue
Need to reorganize structure and add files.

## Recommendation
1. Create directories: {dir_mentions}
2. Add files: {file_mentions}

## Priority
High priority task.
"""
    
    return category, description, directories, files


@st.composite
def improvement_document(draw):
    """Generate a complete improvement suggestions document."""
    num_improvements = draw(st.integers(min_value=1, max_value=5))
    
    sections = []
    for i in range(num_improvements):
        category_num = i + 1
        
        # Randomly choose type of improvement
        improvement_type = draw(st.sampled_from(['directories', 'files', 'both', 'neither']))
        
        if improvement_type == 'directories':
            category, description, _ = draw(improvement_with_directories())
        elif improvement_type == 'files':
            category, description, _ = draw(improvement_with_files())
        elif improvement_type == 'both':
            category, description, _, _ = draw(improvement_with_both())
        else:
            # Neither - just text
            category = draw(improvement_category())
            description = "General improvement without specific directories or files."
        
        section = f"## {category_num}. **{category}**\n\n{description}"
        sections.append(section)
    
    return '\n\n'.join(sections)


class TestV2SuggestionParserProperties:
    """Property-based tests for V2SuggestionParser."""
    
    # Property 6: Improvement classification - Directory changes
    
    @given(improvement_data=improvement_with_directories())
    def test_property_improvement_identifies_directory_changes(self, improvement_data):
        """
        Property: For any improvement that mentions directories, the parser should
        identify and extract those directory references.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.4
        """
        category, description, expected_directories = improvement_data
        
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Should have identified directory changes
            assert len(improvement.related_directories) > 0
            
            # All expected directories should be found
            for expected_dir in expected_directories:
                assert expected_dir in improvement.related_directories, \
                    f"Expected directory {expected_dir} not found in {improvement.related_directories}"
        
        finally:
            os.unlink(temp_file)
    
    @given(improvement_data=improvement_with_files())
    def test_property_improvement_identifies_file_changes(self, improvement_data):
        """
        Property: For any improvement that mentions files, the description should
        contain those file references.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.5
        """
        category, description, expected_files = improvement_data
        
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Description should contain file references
            for expected_file in expected_files:
                assert expected_file in improvement.description, \
                    f"Expected file {expected_file} not found in description"
        
        finally:
            os.unlink(temp_file)
    
    @given(improvement_data=improvement_with_both())
    def test_property_improvement_identifies_both_directory_and_file_changes(self, improvement_data):
        """
        Property: For any improvement that mentions both directories and files,
        the parser should identify both types of changes.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.4, 2.5
        """
        category, description, expected_directories, expected_files = improvement_data
        
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Should have identified directory changes
            assert len(improvement.related_directories) > 0
            
            # All expected directories should be found
            for expected_dir in expected_directories:
                assert expected_dir in improvement.related_directories
            
            # Description should contain file references
            for expected_file in expected_files:
                assert expected_file in improvement.description
        
        finally:
            os.unlink(temp_file)
    
    @given(
        category=improvement_category(),
        description=st.text(max_size=200).filter(lambda x: '`' not in x and '/' not in x)
    )
    def test_property_improvement_without_directories_or_files(self, category, description):
        """
        Property: For any improvement that doesn't mention directories or files,
        the related_directories list should be empty.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.4, 2.5
        """
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Should not have identified any directory changes
            assert len(improvement.related_directories) == 0
        
        finally:
            os.unlink(temp_file)
    
    @given(document=improvement_document())
    def test_property_all_improvements_classified(self, document):
        """
        Property: For any document with multiple improvements, each improvement
        should be classified (either has directories, or doesn't).
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.4, 2.5
        """
        # Create a temporary file with the document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(document)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have parsed all improvements
            assert len(improvements) > 0
            
            # Each improvement should have a classification
            for improvement in improvements:
                # related_directories should be a list (empty or not)
                assert isinstance(improvement.related_directories, list)
                
                # Each directory should end with /
                for dir_name in improvement.related_directories:
                    assert dir_name.endswith('/'), \
                        f"Directory {dir_name} should end with /"
        
        finally:
            os.unlink(temp_file)
    
    @given(
        num_dirs=st.integers(min_value=1, max_value=10),
        category=improvement_category()
    )
    def test_property_directory_count_matches(self, num_dirs, category):
        """
        Property: The number of directories in related_directories should match
        the number of directory mentions in the description.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.4
        """
        # Generate unique directory names
        directories = [f"dir{i}/" for i in range(num_dirs)]
        
        # Create description with directory mentions
        dir_mentions = ', '.join([f'`{d}`' for d in directories])
        description = f"Create directories: {dir_mentions}"
        
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Should have identified all directories
            assert len(improvement.related_directories) == num_dirs
            
            # All directories should be present
            for directory in directories:
                assert directory in improvement.related_directories
        
        finally:
            os.unlink(temp_file)
    
    @given(improvement_data=improvement_with_directories())
    def test_property_no_duplicate_directories(self, improvement_data):
        """
        Property: The related_directories list should not contain duplicates.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.4
        """
        category, description, _ = improvement_data
        
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Should not have duplicates
            assert len(improvement.related_directories) == len(set(improvement.related_directories)), \
                f"Found duplicates in {improvement.related_directories}"
        
        finally:
            os.unlink(temp_file)
    
    @given(
        category=improvement_category(),
        priority_text=st.sampled_from(['high priority', 'medium priority', 'low priority', 'critical'])
    )
    def test_property_improvement_has_priority(self, category, priority_text):
        """
        Property: Every parsed improvement should have a priority assigned.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.1
        """
        description = f"This is a {priority_text} task."
        
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Should have a priority
            assert improvement.priority in ['High', 'Medium', 'Low']
        
        finally:
            os.unlink(temp_file)
    
    @given(
        category=improvement_category(),
        description=st.text(min_size=10, max_size=200)
    )
    def test_property_improvement_has_estimated_hours(self, category, description):
        """
        Property: Every parsed improvement should have estimated hours assigned.
        
        Feature: v2-structure-comparison, Property 6
        Validates: Requirements 2.1
        """
        # Create a temporary file with the improvement
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            content = f"## 1. **{category}**\n\n{description}"
            f.write(content)
            temp_file = f.name
        
        try:
            parser = V2SuggestionParser()
            improvements = parser.parse_improvement_suggestions(temp_file)
            
            # Should have exactly one improvement
            assert len(improvements) == 1
            
            improvement = improvements[0]
            
            # Should have estimated hours
            assert improvement.estimated_hours > 0
            assert isinstance(improvement.estimated_hours, (int, float))
        
        finally:
            os.unlink(temp_file)
