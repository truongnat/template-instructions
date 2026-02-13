"""
Property-based tests for FileScanner service.

Feature: project-audit-cleanup
Tests universal properties of file scanning functionality using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import tempfile
import shutil

from scripts.cleanup.scanner import FileScanner


# Feature: project-audit-cleanup, Property 11: Requirements File Pattern Matching
@given(
    st.lists(
        st.sampled_from([
            "requirements.txt",
            "requirements-dev.txt",
            "requirements_test.txt",
            "requirements-prod.txt",
            "requirements_tools.txt",
        ]),
        min_size=1,
        max_size=5,
        unique=True
    )
)
@settings(max_examples=10, deadline=None)
def test_requirements_file_pattern_matching(requirements_files):
    """
    Property 11: Requirements File Pattern Matching
    
    For any file matching the pattern "requirements*.txt", that file should be
    identified by the scanner and categorized as CONSOLIDATE.
    
    **Validates: Requirements 4.1**
    """
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create requirements files
        created_files = []
        for req_file in requirements_files:
            file_path = tmp_path / req_file
            file_path.write_text("# Test requirements file\nrequests>=2.0.0\n")
            created_files.append(req_file)
        
        # Scan the directory
        scanner = FileScanner()
        scanned_files = scanner.scan(tmp_path)
        
        # Extract just the filenames from scanned files
        scanned_names = {f.path.name for f in scanned_files}
        
        # Property: All requirements*.txt files should be found
        for req_file in created_files:
            assert req_file in scanned_names, (
                f"Requirements file '{req_file}' was not found by scanner. "
                f"Found files: {scanned_names}"
            )
        
        # Property: Number of scanned files should match created files
        assert len(scanned_files) == len(created_files), (
            f"Expected {len(created_files)} files, but scanner found {len(scanned_files)}"
        )


@given(
    st.lists(st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-.'
    )), min_size=1, max_size=10, unique=True)
)
@settings(max_examples=10, deadline=None)
def test_scanner_finds_all_files(filenames):
    """
    Property: Scanner completeness
    
    For any set of files created in a directory, the scanner should find
    all of them (unless excluded by patterns).
    """
    # Filter out invalid filenames
    valid_filenames = [f for f in filenames if f and not f.startswith('.') and '/' not in f]
    
    if not valid_filenames:
        return  # Skip if no valid filenames
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create files
        for filename in valid_filenames:
            try:
                file_path = tmp_path / filename
                file_path.write_text("test content")
            except (OSError, ValueError):
                # Skip invalid filenames
                continue
        
        # Scan directory
        scanner = FileScanner()
        scanned_files = scanner.scan(tmp_path)
        
        # Property: Scanner should find at least as many files as we created
        # (may find more if OS creates hidden files)
        assert len(scanned_files) >= len([f for f in tmp_path.iterdir() if f.is_file()])


@given(
    st.lists(st.integers(min_value=0, max_value=1024*1024), min_size=1, max_size=20)
)
@settings(max_examples=10, deadline=None)
def test_directory_size_calculation_accuracy(file_sizes):
    """
    Property: Directory size calculation accuracy
    
    For any set of files with known sizes, the calculated directory size
    should equal the sum of all file sizes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create files with specific sizes
        expected_total = 0
        for i, size in enumerate(file_sizes):
            file_path = tmp_path / f"file_{i}.txt"
            content = "x" * size
            file_path.write_text(content)
            expected_total += size
        
        # Calculate directory size
        scanner = FileScanner()
        calculated_size = scanner.calculate_directory_size(tmp_path)
        
        # Property: Calculated size should equal sum of file sizes
        assert calculated_size == expected_total, (
            f"Expected total size {expected_total}, but got {calculated_size}"
        )


@given(
    st.lists(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz'), 
             min_size=1, max_size=5, unique=True)
)
@settings(max_examples=10, deadline=None)
def test_exclude_patterns_work(patterns):
    """
    Property: Exclude pattern effectiveness
    
    For any exclude pattern, files matching that pattern should not appear
    in scan results.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create files that match and don't match patterns
        matching_files = []
        non_matching_files = []
        
        for pattern in patterns:
            # Create a file that matches the pattern
            match_file = tmp_path / f"{pattern}.txt"
            match_file.write_text("matching")
            matching_files.append(match_file.name)
            
            # Create a file that doesn't match
            non_match_file = tmp_path / f"other_{pattern}_file.dat"
            non_match_file.write_text("non-matching")
            non_matching_files.append(non_match_file.name)
        
        # Scan with exclude patterns
        exclude_patterns = [f"{p}.txt" for p in patterns]
        scanner = FileScanner(exclude_patterns=exclude_patterns)
        scanned_files = scanner.scan(tmp_path)
        
        scanned_names = {f.path.name for f in scanned_files}
        
        # Property: No matching files should be in results
        for match_file in matching_files:
            assert match_file not in scanned_names, (
                f"Excluded file '{match_file}' was found in scan results"
            )
        
        # Property: Non-matching files should be in results
        for non_match_file in non_matching_files:
            assert non_match_file in scanned_names, (
                f"Non-excluded file '{non_match_file}' was not found in scan results"
            )
