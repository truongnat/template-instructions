"""
Property-based tests for Health Check Completeness.

These tests use Hypothesis to verify that health check executions include
status reports for all critical system components.

Feature: sdlc-kit-improvements
Property 6: Health Check Completeness
Requirements: 5.7
"""

import pytest
from hypothesis import given, strategies as st, settings
from typing import List, Optional

from monitoring.health import HealthChecker, HealthCheck, HealthStatus


# Strategy for generating database URLs
database_urls = st.one_of(
    st.none(),
    st.just("sqlite:///test.db"),
    st.just("sqlite:///data/test.db"),
)

# Strategy for generating API endpoints
api_endpoints = st.one_of(
    st.none(),
    st.lists(
        st.sampled_from([
            "https://api.example.com/health",
            "https://api.test.com/status",
            "https://service.example.org/ping"
        ]),
        min_size=0,
        max_size=3
    )
)

# Strategy for generating threshold percentages
threshold_percentages = st.floats(min_value=70.0, max_value=95.0)


# Feature: sdlc-kit-improvements, Property 6: Health Check Completeness
@given(
    database_url=database_urls,
    api_endpoints_list=api_endpoints,
    disk_threshold=threshold_percentages,
    memory_threshold=threshold_percentages,
)
@settings(max_examples=10, deadline=None)
def test_health_check_includes_all_critical_components(
    database_url: Optional[str],
    api_endpoints_list: Optional[List[str]],
    disk_threshold: float,
    memory_threshold: float
):
    """
    Property: For any health check execution, the results should include status
    reports for all critical system components (database, API connectivity,
    disk space, memory).
    
    This property ensures that health checks are comprehensive and don't skip
    any critical components regardless of configuration.
    
    **Validates: Requirements 5.7**
    """
    # Create health checker with various configurations
    health_checker = HealthChecker(
        database_url=database_url,
        api_endpoints=api_endpoints_list,
        disk_threshold_percent=disk_threshold,
        memory_threshold_percent=memory_threshold
    )
    
    # Run all health checks
    results = health_checker.check_all()
    
    # Property: Results should be a non-empty list
    assert isinstance(results, list), "Health check results should be a list"
    assert len(results) > 0, "Health check results should not be empty"
    
    # Property: All results should be HealthCheck instances
    for result in results:
        assert isinstance(result, HealthCheck), (
            f"Each result should be a HealthCheck instance, got {type(result)}"
        )
    
    # Extract component names from results
    component_names = {result.component for result in results}
    
    # Property: Disk space check should always be included
    assert "disk_space" in component_names, (
        "Health check results must include disk_space component"
    )
    
    # Property: Memory check should always be included
    assert "memory" in component_names, (
        "Health check results must include memory component"
    )
    
    # Property: Database check should be included if database is configured
    if database_url:
        assert "database" in component_names, (
            "Health check results must include database component when database_url is configured"
        )
    
    # Property: API connectivity check should be included if endpoints are configured
    if api_endpoints_list and len(api_endpoints_list) > 0:
        assert "api_connectivity" in component_names, (
            "Health check results must include api_connectivity component when api_endpoints are configured"
        )
    
    # Property: Each component should have required fields
    for result in results:
        assert hasattr(result, 'component'), "Result should have component field"
        assert hasattr(result, 'status'), "Result should have status field"
        assert hasattr(result, 'message'), "Result should have message field"
        assert hasattr(result, 'details'), "Result should have details field"
        
        # Property: Component name should be non-empty
        assert result.component, "Component name should not be empty"
        
        # Property: Status should be a valid HealthStatus enum value
        assert isinstance(result.status, HealthStatus), (
            f"Status should be HealthStatus enum, got {type(result.status)}"
        )
        
        # Property: Message should be non-empty
        assert result.message, "Message should not be empty"


# Feature: sdlc-kit-improvements, Property 6: Health Check Completeness
@given(
    database_url=database_urls,
    api_endpoints_list=api_endpoints,
)
@settings(max_examples=10, deadline=None)
def test_health_check_results_have_consistent_structure(
    database_url: Optional[str],
    api_endpoints_list: Optional[List[str]]
):
    """
    Property: For any health check execution, all component results should
    have a consistent structure with component name, status, message, and details.
    
    This property ensures that health check results are uniformly structured
    for easy consumption by monitoring systems.
    
    **Validates: Requirements 5.7**
    """
    health_checker = HealthChecker(
        database_url=database_url,
        api_endpoints=api_endpoints_list
    )
    
    results = health_checker.check_all()
    
    # Property: All results should have the same structure
    for result in results:
        # Check that to_dict() method works
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict), "to_dict() should return a dictionary"
        
        # Property: Dictionary should contain all required keys
        required_keys = {'component', 'status', 'message', 'details'}
        assert required_keys.issubset(result_dict.keys()), (
            f"Result dictionary should contain keys {required_keys}, got {result_dict.keys()}"
        )
        
        # Property: Status should be serialized as string
        assert isinstance(result_dict['status'], str), (
            "Status in dictionary should be a string"
        )
        
        # Property: Component should be a string
        assert isinstance(result_dict['component'], str), (
            "Component should be a string"
        )
        
        # Property: Message should be a string
        assert isinstance(result_dict['message'], str), (
            "Message should be a string"
        )


# Feature: sdlc-kit-improvements, Property 6: Health Check Completeness
@given(
    disk_threshold=threshold_percentages,
    memory_threshold=threshold_percentages,
)
@settings(max_examples=10, deadline=None)
def test_health_check_always_includes_mandatory_components(
    disk_threshold: float,
    memory_threshold: float
):
    """
    Property: For any health check execution, regardless of optional configuration,
    the mandatory components (disk_space and memory) should always be checked.
    
    This property ensures that critical system resources are always monitored.
    
    **Validates: Requirements 5.7**
    """
    # Create health checker with minimal configuration (no database, no API endpoints)
    health_checker = HealthChecker(
        database_url=None,
        api_endpoints=None,
        disk_threshold_percent=disk_threshold,
        memory_threshold_percent=memory_threshold
    )
    
    results = health_checker.check_all()
    component_names = {result.component for result in results}
    
    # Property: Mandatory components should always be present
    mandatory_components = {'disk_space', 'memory'}
    assert mandatory_components.issubset(component_names), (
        f"Health check must always include mandatory components {mandatory_components}, "
        f"got {component_names}"
    )
    
    # Property: At minimum, we should have 2 components (disk and memory)
    assert len(results) >= 2, (
        f"Health check should have at least 2 components (disk_space, memory), got {len(results)}"
    )


# Feature: sdlc-kit-improvements, Property 6: Health Check Completeness
@given(
    database_url=st.just("sqlite:///test.db"),
    api_endpoints_list=st.just(["https://api.example.com/health"]),
)
@settings(max_examples=5, deadline=None)
def test_health_check_includes_all_configured_components(
    database_url: str,
    api_endpoints_list: List[str]
):
    """
    Property: For any health check execution with all components configured,
    the results should include all four critical components: database,
    API connectivity, disk space, and memory.
    
    This property ensures complete coverage when all components are configured.
    
    **Validates: Requirements 5.7**
    """
    health_checker = HealthChecker(
        database_url=database_url,
        api_endpoints=api_endpoints_list
    )
    
    results = health_checker.check_all()
    component_names = {result.component for result in results}
    
    # Property: All four critical components should be present
    expected_components = {'database', 'api_connectivity', 'disk_space', 'memory'}
    assert expected_components == component_names, (
        f"Health check with full configuration should include all components {expected_components}, "
        f"got {component_names}"
    )
    
    # Property: Should have exactly 4 components
    assert len(results) == 4, (
        f"Health check with full configuration should have exactly 4 components, got {len(results)}"
    )


# Feature: sdlc-kit-improvements, Property 6: Health Check Completeness
@given(
    database_url=database_urls,
    api_endpoints_list=api_endpoints,
)
@settings(max_examples=10, deadline=None)
def test_health_check_components_have_valid_status(
    database_url: Optional[str],
    api_endpoints_list: Optional[List[str]]
):
    """
    Property: For any health check execution, every component result should
    have a valid status (HEALTHY, DEGRADED, or UNHEALTHY).
    
    This property ensures that health status is always properly categorized.
    
    **Validates: Requirements 5.7**
    """
    health_checker = HealthChecker(
        database_url=database_url,
        api_endpoints=api_endpoints_list
    )
    
    results = health_checker.check_all()
    
    valid_statuses = {HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY}
    
    # Property: Every component should have a valid status
    for result in results:
        assert result.status in valid_statuses, (
            f"Component '{result.component}' has invalid status: {result.status}. "
            f"Valid statuses are: {valid_statuses}"
        )
        
        # Property: is_healthy() method should work correctly
        if result.status == HealthStatus.HEALTHY:
            assert result.is_healthy() is True, (
                f"Component '{result.component}' with HEALTHY status should return True from is_healthy()"
            )
        else:
            assert result.is_healthy() is False, (
                f"Component '{result.component}' with non-HEALTHY status should return False from is_healthy()"
            )
