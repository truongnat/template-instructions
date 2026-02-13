#!/usr/bin/env python3
"""System health check script for SDLC Kit.

This script runs all health checks from monitoring/health.py and reports
the results in a clear format showing the status of each component.

Exit codes:
    0: All components are healthy
    1: One or more components are unhealthy
    2: One or more components are degraded (but none unhealthy)
"""

import sys
from pathlib import Path
from typing import List

# Add parent directory to path to import monitoring module
sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring.health import HealthChecker, HealthCheck, HealthStatus


def print_header() -> None:
    """Print the header for health check output."""
    print("=" * 60)
    print("SDLC Kit System Health Check")
    print("=" * 60)
    print()


def print_check_result(check: HealthCheck) -> None:
    """Print a single health check result.
    
    Args:
        check: HealthCheck result to print
    """
    # Status symbol
    if check.status == HealthStatus.HEALTHY:
        symbol = "✓"
        status_text = "HEALTHY"
    elif check.status == HealthStatus.DEGRADED:
        symbol = "⚠"
        status_text = "DEGRADED"
    else:
        symbol = "✗"
        status_text = "UNHEALTHY"
    
    # Print component status
    print(f"{symbol} {check.component.upper()}: {status_text}")
    print(f"  Message: {check.message}")
    
    # Print details if available
    if check.details:
        print("  Details:")
        for key, value in check.details.items():
            # Format the value nicely
            if isinstance(value, (list, dict)):
                print(f"    {key}: {value}")
            else:
                print(f"    {key}: {value}")
    
    print()


def print_summary(checks: List[HealthCheck]) -> None:
    """Print summary of all health checks.
    
    Args:
        checks: List of all health check results
    """
    healthy_count = sum(1 for c in checks if c.status == HealthStatus.HEALTHY)
    degraded_count = sum(1 for c in checks if c.status == HealthStatus.DEGRADED)
    unhealthy_count = sum(1 for c in checks if c.status == HealthStatus.UNHEALTHY)
    total_count = len(checks)
    
    print("=" * 60)
    print("Health Check Summary")
    print("=" * 60)
    print(f"Total components checked: {total_count}")
    print(f"Healthy: {healthy_count}")
    print(f"Degraded: {degraded_count}")
    print(f"Unhealthy: {unhealthy_count}")
    print()


def determine_exit_code(checks: List[HealthCheck]) -> int:
    """Determine the exit code based on health check results.
    
    Args:
        checks: List of all health check results
        
    Returns:
        Exit code (0=all healthy, 1=any unhealthy, 2=any degraded)
    """
    has_unhealthy = any(c.status == HealthStatus.UNHEALTHY for c in checks)
    has_degraded = any(c.status == HealthStatus.DEGRADED for c in checks)
    
    if has_unhealthy:
        return 1
    elif has_degraded:
        return 2
    else:
        return 0


def main() -> int:
    """Main function to run health checks.
    
    Returns:
        Exit code based on health check results
    """
    print_header()
    
    # Initialize health checker
    # You can configure these via environment variables or config file
    checker = HealthChecker(
        database_url=None,  # Set to your database URL if needed
        api_endpoints=[],   # Add API endpoints to check if needed
        disk_threshold_percent=90.0,
        memory_threshold_percent=90.0
    )
    
    # Run all health checks
    try:
        checks = checker.check_all()
    except Exception as e:
        print(f"✗ Error running health checks: {e}")
        print()
        return 1
    
    # Print individual results
    for check in checks:
        print_check_result(check)
    
    # Print summary
    print_summary(checks)
    
    # Determine exit code
    exit_code = determine_exit_code(checks)
    
    # Print final status
    if exit_code == 0:
        print("✓ All systems healthy!")
    elif exit_code == 2:
        print("⚠ Some systems degraded - please investigate")
    else:
        print("✗ Some systems unhealthy - immediate attention required")
    
    print()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
