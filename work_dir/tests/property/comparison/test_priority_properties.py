"""
Property-based tests for priority matrix and task generation.

Tests Properties 13-15 from the design document.
"""

import pytest
from hypothesis import given, strategies as st, assume

from agentic_sdlc.comparison.models import Gap, Task
from agentic_sdlc.comparison.priority import PriorityMatrix, TaskGenerator


# Strategies for generating test data
@st.composite
def gap_strategy(draw):
    """Generate a random Gap object."""
    categories = ["Directory Structure", "Configuration", "Documentation", 
                  "Testing", "Security", "Critical Infrastructure"]
    priorities = ["High", "Medium", "Low"]
    efforts = ["Quick Win", "Medium", "Large"]
    
    category = draw(st.sampled_from(categories))
    description = draw(st.text(min_size=10, max_size=200))
    priority = draw(st.sampled_from(priorities))
    effort = draw(st.sampled_from(efforts))
    related_req = draw(st.text(min_size=1, max_size=10))
    proposed_action = draw(st.text(min_size=10, max_size=200))
    
    return Gap(
        category=category,
        description=description,
        priority=priority,
        effort=effort,
        related_requirement=related_req,
        proposed_action=proposed_action
    )


@st.composite
def task_with_dependencies_strategy(draw):
    """Generate a Task with potential dependencies."""
    task_id = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))))
    title = draw(st.text(min_size=5, max_size=100))
    description = draw(st.text(min_size=10, max_size=200))
    priority = draw(st.sampled_from(["High", "Medium", "Low"]))
    effort_hours = draw(st.floats(min_value=0.5, max_value=40.0))
    category = draw(st.text(min_size=3, max_size=50))
    
    # Generate dependencies (list of task IDs)
    num_deps = draw(st.integers(min_value=0, max_value=3))
    dependencies = [
        draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))))
        for _ in range(num_deps)
    ]
    
    return Task(
        id=task_id,
        title=title,
        description=description,
        priority=priority,
        effort_hours=effort_hours,
        category=category,
        files_to_create=[],
        files_to_modify=[],
        dependencies=dependencies,
        reference=""
    )


# Feature: v2-structure-comparison, Property 13: Priority categorization
@given(gap=gap_strategy())
def test_priority_categorization_assigns_exactly_one_level(gap):
    """
    For any identified gap, the priority matrix should assign exactly one 
    priority level and exactly one effort level.
    
    **Validates: Requirements 6.1, 6.2**
    """
    matrix = PriorityMatrix()
    
    # Categorize priority
    priority = matrix.categorize_priority(gap)
    
    # Verify exactly one priority level is assigned
    assert priority in ["High", "Medium", "Low"], \
        f"Priority must be one of High/Medium/Low, got: {priority}"
    
    # Estimate effort
    effort = matrix.estimate_effort(gap)
    
    # Verify exactly one effort level is assigned
    assert effort in ["Quick Win", "Medium", "Large"], \
        f"Effort must be one of Quick Win/Medium/Large, got: {effort}"
    
    # Verify the values are strings (not None, not empty)
    assert isinstance(priority, str) and len(priority) > 0
    assert isinstance(effort, str) and len(effort) > 0


# Feature: v2-structure-comparison, Property 14: Task dependency ordering
@given(tasks=st.lists(task_with_dependencies_strategy(), min_size=1, max_size=20))
def test_task_dependency_ordering_respects_dependencies(tasks):
    """
    For any list of tasks with dependencies, the generated implementation order 
    should ensure no task appears before any of its dependencies.
    
    **Validates: Requirements 6.3, 6.4**
    """
    # Filter out tasks with dependencies that don't exist in the task list
    task_ids = {task.id for task in tasks}
    for task in tasks:
        task.dependencies = [dep for dep in task.dependencies if dep in task_ids]
    
    # Check for cycles - if there's a cycle, we can't have valid ordering
    has_cycle = _has_cycle(tasks)
    
    if has_cycle:
        # If there's a cycle, skip this test case
        assume(False)
    
    generator = TaskGenerator()
    
    # Prioritize tasks (which includes topological sort)
    sorted_tasks = generator.prioritize_tasks(tasks)
    
    # Verify ordering: for each task, all its dependencies should appear before it
    task_positions = {task.id: i for i, task in enumerate(sorted_tasks)}
    
    for task in sorted_tasks:
        task_pos = task_positions[task.id]
        
        for dep_id in task.dependencies:
            if dep_id in task_positions:
                dep_pos = task_positions[dep_id]
                assert dep_pos < task_pos, \
                    f"Task {task.id} at position {task_pos} depends on {dep_id} " \
                    f"at position {dep_pos}, but dependency should come first"


# Feature: v2-structure-comparison, Property 15: Quick wins identification
@given(gaps=st.lists(gap_strategy(), min_size=1, max_size=30))
def test_quick_wins_identification(gaps):
    """
    For any set of gaps, the quick wins should be exactly those gaps with 
    effort level "Quick Win" and priority "High" or "Medium".
    
    **Validates: Requirements 6.5**
    """
    matrix = PriorityMatrix()
    
    # Categorize all gaps
    categorized_gaps = []
    for gap in gaps:
        priority = matrix.categorize_priority(gap)
        effort = matrix.estimate_effort(gap)
        categorized_gaps.append((gap, priority, effort))
    
    # Identify quick wins: effort = "Quick Win" AND priority in ["High", "Medium"]
    expected_quick_wins = [
        gap for gap, priority, effort in categorized_gaps
        if effort == "Quick Win" and priority in ["High", "Medium"]
    ]
    
    # Generate tasks from gaps
    generator = TaskGenerator()
    tasks = generator.generate_tasks(gaps)
    
    # Filter tasks that are quick wins
    actual_quick_wins = [
        task for task in tasks
        if task.effort_hours <= 4.0 and task.priority in ["High", "Medium"]
    ]
    
    # Verify the count matches
    # Note: Quick Win effort level maps to ~2 hours in our implementation
    quick_win_tasks = [
        task for task in tasks
        if task.effort_hours <= 4.0  # Quick Win threshold
    ]
    
    high_medium_priority_quick_wins = [
        task for task in quick_win_tasks
        if task.priority in ["High", "Medium"]
    ]
    
    # The number of quick wins should match expected
    assert len(high_medium_priority_quick_wins) == len(expected_quick_wins), \
        f"Expected {len(expected_quick_wins)} quick wins, got {len(high_medium_priority_quick_wins)}"


def _has_cycle(tasks: list) -> bool:
    """
    Check if task dependencies contain a cycle.
    
    Args:
        tasks: List of Task objects
        
    Returns:
        True if there's a cycle, False otherwise
    """
    task_map = {task.id: task for task in tasks}
    visited = set()
    rec_stack = set()
    
    def visit(task_id: str) -> bool:
        if task_id in rec_stack:
            return True  # Cycle detected
        if task_id in visited:
            return False
        
        visited.add(task_id)
        rec_stack.add(task_id)
        
        if task_id in task_map:
            task = task_map[task_id]
            for dep_id in task.dependencies:
                if dep_id in task_map and visit(dep_id):
                    return True
        
        rec_stack.remove(task_id)
        return False
    
    for task in tasks:
        if task.id not in visited:
            if visit(task.id):
                return True
    
    return False


# Feature: v2-structure-comparison, Property 16: Task generation completeness
@given(gap=gap_strategy())
def test_task_generation_completeness(gap):
    """
    For any identified gap, the task generator should create a task that 
    includes all required fields.
    
    **Validates: Requirements 7.1, 7.2, 7.3, 7.5**
    """
    generator = TaskGenerator()
    
    # Generate tasks from a single gap
    tasks = generator.generate_tasks([gap])
    
    # Should generate exactly one task
    assert len(tasks) == 1, f"Expected 1 task, got {len(tasks)}"
    
    task = tasks[0]
    
    # Verify all required fields are present and non-empty
    assert task.id is not None and len(task.id) > 0, "Task ID must be present"
    assert task.title is not None and len(task.title) > 0, "Task title must be present"
    assert task.description is not None and len(task.description) > 0, "Task description must be present"
    assert task.priority in ["High", "Medium", "Low"], f"Task priority must be valid, got: {task.priority}"
    assert task.effort_hours > 0, f"Task effort_hours must be positive, got: {task.effort_hours}"
    assert task.category is not None and len(task.category) > 0, "Task category must be present"
    
    # Verify files_to_create and files_to_modify are lists (can be empty)
    assert isinstance(task.files_to_create, list), "files_to_create must be a list"
    assert isinstance(task.files_to_modify, list), "files_to_modify must be a list"
    
    # Verify dependencies is a list (can be empty)
    assert isinstance(task.dependencies, list), "dependencies must be a list"
    
    # Verify reference is present (can be empty string)
    assert isinstance(task.reference, str), "reference must be a string"


# Feature: v2-structure-comparison, Property 17: Task grouping coherence
@given(gaps=st.lists(gap_strategy(), min_size=2, max_size=20))
def test_task_grouping_coherence(gaps):
    """
    For any set of related tasks, the grouping function should place them 
    in the same work package.
    
    **Validates: Requirements 7.4**
    """
    generator = TaskGenerator()
    
    # Generate tasks from gaps
    tasks = generator.generate_tasks(gaps)
    
    # Group tasks
    packages = generator.group_related_tasks(tasks)
    
    # Verify that tasks with the same category are in the same package
    for category, tasks_in_package in packages.items():
        # All tasks in this package should have the same category
        for task in tasks_in_package:
            assert task.category == category, \
                f"Task {task.id} has category {task.category} but is in package {category}"
    
    # Verify that all tasks are in exactly one package
    all_tasks_in_packages = []
    for tasks_in_package in packages.values():
        all_tasks_in_packages.extend(tasks_in_package)
    
    assert len(all_tasks_in_packages) == len(tasks), \
        f"Expected {len(tasks)} tasks in packages, got {len(all_tasks_in_packages)}"
    
    # Verify no duplicate tasks in packages
    task_ids_in_packages = [task.id for task in all_tasks_in_packages]
    assert len(task_ids_in_packages) == len(set(task_ids_in_packages)), \
        "Tasks should not appear in multiple packages"
