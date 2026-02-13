"""
Property-based tests for status tracking functionality.

Feature: v2-structure-comparison
Tests Properties 22 and 23 related to status persistence and completion date recording.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from agentic_sdlc.comparison.status import (
    StatusTracker,
    StatusEntry,
    StatusFile,
    ImprovementStatus,
)


# Hypothesis strategies for generating test data
@st.composite
def status_entry_strategy(draw):
    """Generate a valid StatusEntry."""
    improvement_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )))
    category = draw(st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
        "Testing",
        "CLI",
    ]))
    status = draw(st.sampled_from([
        ImprovementStatus.IMPLEMENTED,
        ImprovementStatus.PARTIAL,
        ImprovementStatus.NOT_YET_IMPLEMENTED,
        ImprovementStatus.INTENTIONALLY_SKIPPED,
    ]))
    
    # Generate completion date only if status is IMPLEMENTED
    completion_date = None
    if status == ImprovementStatus.IMPLEMENTED:
        completion_date = draw(st.one_of(
            st.none(),
            st.just(datetime.utcnow().isoformat() + 'Z')
        ))
    
    # Generate skip reason only if status is INTENTIONALLY_SKIPPED
    skip_reason = None
    if status == ImprovementStatus.INTENTIONALLY_SKIPPED:
        skip_reason = draw(st.text(min_size=10, max_size=200))
    
    last_updated = draw(st.one_of(
        st.none(),
        st.just(datetime.utcnow().isoformat() + 'Z')
    ))
    
    return StatusEntry(
        improvement_id=improvement_id,
        category=category,
        status=status,
        completion_date=completion_date,
        skip_reason=skip_reason,
        last_updated=last_updated,
    )


@st.composite
def status_file_strategy(draw):
    """Generate a valid StatusFile."""
    version = draw(st.just("1.0"))
    last_comparison_date = draw(st.one_of(
        st.none(),
        st.just(datetime.utcnow().isoformat() + 'Z')
    ))
    
    # Generate 0-10 status entries
    num_entries = draw(st.integers(min_value=0, max_value=10))
    entries = {}
    for _ in range(num_entries):
        entry = draw(status_entry_strategy())
        entries[entry.improvement_id] = entry
    
    return StatusFile(
        version=version,
        last_comparison_date=last_comparison_date,
        entries=entries,
    )


# Feature: v2-structure-comparison, Property 22: Status tracking persistence
@given(status_file=status_file_strategy())
def test_status_persistence_roundtrip(status_file):
    """
    Property 22: Status tracking persistence
    
    For any status update operation, writing to the status file and then
    reading it back should return the same status information.
    
    This property ensures that:
    1. All status data can be serialized to JSON
    2. All status data can be deserialized from JSON
    3. The round-trip preserves all information
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        
        # Create tracker and set status data
        tracker = StatusTracker(str(status_path))
        tracker.status_data = status_file
        
        # Save to file
        tracker.save_status()
        
        # Create new tracker and load from file
        tracker2 = StatusTracker(str(status_path))
        loaded_status = tracker2.load_status()
        
        # Verify all fields match
        assert loaded_status.version == status_file.version
        assert loaded_status.last_comparison_date == status_file.last_comparison_date
        assert len(loaded_status.entries) == len(status_file.entries)
        
        # Verify each entry matches
        for improvement_id, original_entry in status_file.entries.items():
            assert improvement_id in loaded_status.entries
            loaded_entry = loaded_status.entries[improvement_id]
            
            assert loaded_entry.improvement_id == original_entry.improvement_id
            assert loaded_entry.category == original_entry.category
            assert loaded_entry.status == original_entry.status
            assert loaded_entry.completion_date == original_entry.completion_date
            assert loaded_entry.skip_reason == original_entry.skip_reason
            assert loaded_entry.last_updated == original_entry.last_updated


# Feature: v2-structure-comparison, Property 22: Status tracking persistence (update operations)
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
    status=st.sampled_from([
        ImprovementStatus.IMPLEMENTED,
        ImprovementStatus.PARTIAL,
        ImprovementStatus.NOT_YET_IMPLEMENTED,
    ]),
)
def test_update_improvement_status_persistence(improvement_id, category, status):
    """
    Property 22: Status tracking persistence (update variant)
    
    For any status update operation, the updated status should persist
    correctly when saved and loaded.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        
        # Create tracker and update status
        tracker = StatusTracker(str(status_path))
        tracker.update_improvement_status(improvement_id, category, status)
        tracker.save_status()
        
        # Load in new tracker
        tracker2 = StatusTracker(str(status_path))
        tracker2.load_status()
        
        # Verify the update persisted
        entry = tracker2.get_status(improvement_id)
        assert entry is not None
        assert entry.improvement_id == improvement_id
        assert entry.category == category
        assert entry.status == status


# Feature: v2-structure-comparison, Property 23: Completion date recording
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
)
def test_completion_date_recorded_when_implemented(improvement_id, category):
    """
    Property 23: Completion date recording
    
    For any improvement marked as complete, the status file should contain
    a completion date field with a valid ISO 8601 timestamp.
    
    This property ensures that:
    1. Completion date is set when status is IMPLEMENTED
    2. Completion date is in ISO 8601 format
    3. Completion date is persisted correctly
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        
        # Create tracker and mark as implemented
        tracker = StatusTracker(str(status_path))
        tracker.update_improvement_status(
            improvement_id,
            category,
            ImprovementStatus.IMPLEMENTED
        )
        
        # Get the entry
        entry = tracker.get_status(improvement_id)
        
        # Verify completion date is set
        assert entry is not None
        assert entry.completion_date is not None
        
        # Verify it's a valid ISO 8601 timestamp
        # Should be parseable and end with 'Z' for UTC
        assert entry.completion_date.endswith('Z')
        parsed_date = datetime.fromisoformat(entry.completion_date.rstrip('Z'))
        assert isinstance(parsed_date, datetime)
        
        # Save and reload to verify persistence
        tracker.save_status()
        
        tracker2 = StatusTracker(str(status_path))
        tracker2.load_status()
        entry2 = tracker2.get_status(improvement_id)
        
        assert entry2 is not None
        assert entry2.completion_date == entry.completion_date


# Feature: v2-structure-comparison, Property 23: Completion date not set for non-implemented
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
    status=st.sampled_from([
        ImprovementStatus.PARTIAL,
        ImprovementStatus.NOT_YET_IMPLEMENTED,
    ]),
)
def test_completion_date_not_set_for_non_implemented(improvement_id, category, status):
    """
    Property 23: Completion date recording (negative case)
    
    For any improvement not marked as complete, the completion date should be None.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        
        # Create tracker and set non-implemented status
        tracker = StatusTracker(str(status_path))
        tracker.update_improvement_status(improvement_id, category, status)
        
        # Get the entry
        entry = tracker.get_status(improvement_id)
        
        # Verify completion date is NOT set
        assert entry is not None
        assert entry.completion_date is None


# Feature: v2-structure-comparison, Property 23: Completion date cleared when status changes
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
    new_status=st.sampled_from([
        ImprovementStatus.PARTIAL,
        ImprovementStatus.NOT_YET_IMPLEMENTED,
    ]),
)
def test_completion_date_cleared_when_unmarked(improvement_id, category, new_status):
    """
    Property 23: Completion date recording (state transition)
    
    When an improvement is marked as implemented and then changed to a different status,
    the completion date should be cleared.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        
        tracker = StatusTracker(str(status_path))
        
        # First mark as implemented
        tracker.update_improvement_status(
            improvement_id,
            category,
            ImprovementStatus.IMPLEMENTED
        )
        
        entry = tracker.get_status(improvement_id)
        assert entry.completion_date is not None
        
        # Then change to different status
        tracker.update_improvement_status(improvement_id, category, new_status)
        
        entry = tracker.get_status(improvement_id)
        assert entry.completion_date is None


# Feature: v2-structure-comparison, Property 31: Skip status validation
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
)
def test_skip_status_requires_reason(improvement_id, category):
    """
    Property 31: Skip status validation
    
    For any attempt to mark a suggestion as "Intentionally Skipped",
    the operation should fail if no reason is provided.
    
    This property ensures that:
    1. Marking as skipped without reason raises ValueError
    2. Marking as skipped with empty reason raises ValueError
    3. The error message is informative
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        tracker = StatusTracker(str(status_path))
        
        # Test 1: No reason provided via update_improvement_status
        with pytest.raises(ValueError) as exc_info:
            tracker.update_improvement_status(
                improvement_id,
                category,
                ImprovementStatus.INTENTIONALLY_SKIPPED,
                skip_reason=None
            )
        assert "skip_reason is required" in str(exc_info.value).lower()
        
        # Test 2: Empty reason via mark_as_skipped
        with pytest.raises(ValueError) as exc_info:
            tracker.mark_as_skipped(improvement_id, category, "")
        assert "reason must be provided" in str(exc_info.value).lower()
        
        # Test 3: Whitespace-only reason via mark_as_skipped
        with pytest.raises(ValueError) as exc_info:
            tracker.mark_as_skipped(improvement_id, category, "   ")
        assert "reason must be provided" in str(exc_info.value).lower()


# Feature: v2-structure-comparison, Property 31: Skip status validation (positive case)
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
    reason=st.text(min_size=10, max_size=200),
)
def test_skip_status_succeeds_with_reason(improvement_id, category, reason):
    """
    Property 31: Skip status validation (positive case)
    
    For any attempt to mark a suggestion as "Intentionally Skipped" with a valid reason,
    the operation should succeed.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        tracker = StatusTracker(str(status_path))
        
        # Should succeed with valid reason
        tracker.mark_as_skipped(improvement_id, category, reason)
        
        entry = tracker.get_status(improvement_id)
        assert entry is not None
        assert entry.status == ImprovementStatus.INTENTIONALLY_SKIPPED
        assert entry.skip_reason == reason.strip()


# Feature: v2-structure-comparison, Property 32: Deviation reporting
@given(
    num_skipped=st.integers(min_value=1, max_value=5),
    num_other=st.integers(min_value=0, max_value=5),
)
def test_deviation_reporting_lists_all_skipped(num_skipped, num_other):
    """
    Property 32: Deviation reporting
    
    For any comparison report, the deviations section should list all suggestions
    marked as "Intentionally Skipped" with their reasons.
    
    This property ensures that:
    1. All skipped improvements are retrievable
    2. Each skipped improvement has a reason
    3. Non-skipped improvements are not included
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        tracker = StatusTracker(str(status_path))
        
        skipped_ids = []
        
        # Add skipped improvements
        for i in range(num_skipped):
            improvement_id = f"skipped-{i}"
            reason = f"Reason for skipping improvement {i}"
            tracker.mark_as_skipped(improvement_id, "Test Category", reason)
            skipped_ids.append(improvement_id)
        
        # Add non-skipped improvements
        for i in range(num_other):
            improvement_id = f"other-{i}"
            status = [
                ImprovementStatus.IMPLEMENTED,
                ImprovementStatus.PARTIAL,
                ImprovementStatus.NOT_YET_IMPLEMENTED,
            ][i % 3]
            tracker.update_improvement_status(improvement_id, "Test Category", status)
        
        # Get skipped improvements
        skipped = tracker.get_skipped_improvements()
        
        # Verify count matches
        assert len(skipped) == num_skipped
        
        # Verify all skipped improvements are present
        skipped_ids_found = [entry.improvement_id for entry in skipped]
        assert set(skipped_ids_found) == set(skipped_ids)
        
        # Verify each has a reason
        for entry in skipped:
            assert entry.skip_reason is not None
            assert len(entry.skip_reason) > 0
            assert entry.status == ImprovementStatus.INTENTIONALLY_SKIPPED


# Feature: v2-structure-comparison, Property 34: Deviation reason updates
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
    initial_reason=st.text(min_size=10, max_size=100),
    new_reason=st.text(min_size=10, max_size=100),
)
def test_deviation_reason_update_preserves_status(
    improvement_id, category, initial_reason, new_reason
):
    """
    Property 34: Deviation reason updates
    
    For any suggestion marked as "Intentionally Skipped", updating its reason
    should preserve the skip status while changing only the reason text.
    
    This property ensures that:
    1. Status remains INTENTIONALLY_SKIPPED after update
    2. Reason is updated to new value
    3. Other fields are preserved
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        tracker = StatusTracker(str(status_path))
        
        # Mark as skipped with initial reason
        tracker.mark_as_skipped(improvement_id, category, initial_reason)
        
        entry_before = tracker.get_status(improvement_id)
        assert entry_before.status == ImprovementStatus.INTENTIONALLY_SKIPPED
        assert entry_before.skip_reason == initial_reason.strip()
        
        # Update the reason
        tracker.update_skip_reason(improvement_id, new_reason)
        
        entry_after = tracker.get_status(improvement_id)
        
        # Verify status is preserved
        assert entry_after.status == ImprovementStatus.INTENTIONALLY_SKIPPED
        
        # Verify reason is updated to the new value
        assert entry_after.skip_reason == new_reason.strip()
        
        # Verify other fields are preserved
        assert entry_after.improvement_id == entry_before.improvement_id
        assert entry_after.category == entry_before.category


# Feature: v2-structure-comparison, Property 34: Deviation reason updates (validation)
@given(
    improvement_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'
    )),
    category=st.sampled_from([
        "Directory Structure",
        "Configuration",
        "Documentation",
    ]),
    initial_reason=st.text(min_size=10, max_size=100),
)
def test_deviation_reason_update_validation(improvement_id, category, initial_reason):
    """
    Property 34: Deviation reason updates (validation)
    
    Updating deviation reason should fail if:
    1. The improvement doesn't exist
    2. The improvement is not marked as skipped
    3. The new reason is empty
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        status_path = Path(tmpdir) / "status.json"
        tracker = StatusTracker(str(status_path))
        
        # Test 1: Update non-existent improvement
        with pytest.raises(ValueError) as exc_info:
            tracker.update_skip_reason(improvement_id, "New reason")
        assert "not found" in str(exc_info.value).lower()
        
        # Test 2: Update non-skipped improvement
        tracker.update_improvement_status(
            improvement_id,
            category,
            ImprovementStatus.IMPLEMENTED
        )
        with pytest.raises(ValueError) as exc_info:
            tracker.update_skip_reason(improvement_id, "New reason")
        assert "not marked as" in str(exc_info.value).lower()
        
        # Test 3: Update with empty reason (after marking as skipped)
        tracker.mark_as_skipped(improvement_id, category, initial_reason)
        with pytest.raises(ValueError) as exc_info:
            tracker.update_skip_reason(improvement_id, "")
        assert "reason must be provided" in str(exc_info.value).lower()
