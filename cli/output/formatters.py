"""
General output formatting utilities for CLI.

Provides functions for formatting various types of output.
"""

from typing import Any, Dict, List, Optional
import json
from cli.output.colors import success, error, warning, info, highlight, bold, dim
from cli.output.tables import format_table, format_key_value_table


def format_success(message: str) -> str:
    """Format a success message."""
    return f"{success('✓')} {message}"


def format_error(message: str) -> str:
    """Format an error message."""
    return f"{error('✗')} {message}"


def format_warning(message: str) -> str:
    """Format a warning message."""
    return f"{warning('⚠')} {message}"


def format_info(message: str) -> str:
    """Format an info message."""
    return f"{info('ℹ')} {message}"


def format_header(text: str) -> str:
    """Format a section header."""
    line = "=" * len(text)
    return f"\n{bold(text)}\n{line}\n"


def format_subheader(text: str) -> str:
    """Format a subsection header."""
    return f"\n{highlight(text)}\n{'-' * len(text)}\n"


def format_list(items: List[str], bullet: str = "•") -> str:
    """
    Format a list of items.
    
    Args:
        items: List of items
        bullet: Bullet character
        
    Returns:
        Formatted list string
    """
    if not items:
        return dim("(none)")
    
    return "\n".join([f"  {bullet} {item}" for item in items])


def format_dict(data: Dict[str, Any], indent: int = 0) -> str:
    """
    Format a dictionary for display.
    
    Args:
        data: Dictionary to format
        indent: Indentation level
        
    Returns:
        Formatted dictionary string
    """
    if not data:
        return dim("(empty)")
    
    lines = []
    prefix = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{bold(key)}:")
            lines.append(format_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{bold(key)}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(format_dict(item, indent + 1))
                else:
                    lines.append(f"{prefix}  • {item}")
        else:
            lines.append(f"{prefix}{bold(key)}: {value}")
    
    return "\n".join(lines)


def format_json(data: Any, pretty: bool = True) -> str:
    """
    Format data as JSON.
    
    Args:
        data: Data to format
        pretty: Whether to pretty-print
        
    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, default=str)
    return json.dumps(data, default=str)


def format_workflow_output(workflow_data: Dict[str, Any]) -> str:
    """
    Format workflow data for display.
    
    Args:
        workflow_data: Workflow data dictionary
        
    Returns:
        Formatted workflow output
    """
    output = []
    
    # Header
    output.append(format_header(f"Workflow: {workflow_data.get('name', 'Unknown')}"))
    
    # Basic info
    info_data = {
        "Version": workflow_data.get("version", "N/A"),
        "Status": workflow_data.get("status", "N/A"),
        "Description": workflow_data.get("description", "N/A")
    }
    output.append(format_dict(info_data))
    
    # Agents
    if "agents" in workflow_data and workflow_data["agents"]:
        output.append(format_subheader("Agents"))
        output.append(format_list(workflow_data["agents"]))
    
    # Tasks
    if "tasks" in workflow_data and workflow_data["tasks"]:
        output.append(format_subheader("Tasks"))
        task_rows = []
        for task in workflow_data["tasks"]:
            task_rows.append([
                task.get("id", "N/A"),
                task.get("type", "N/A"),
                task.get("status", "N/A")
            ])
        output.append(format_table(["ID", "Type", "Status"], task_rows))
    
    return "\n".join(output)


def format_agent_output(agent_data: Dict[str, Any]) -> str:
    """
    Format agent data for display.
    
    Args:
        agent_data: Agent data dictionary
        
    Returns:
        Formatted agent output
    """
    output = []
    
    # Header
    output.append(format_header(f"Agent: {agent_data.get('id', 'Unknown')}"))
    
    # Basic info
    info_data = {
        "Type": agent_data.get("type", "N/A"),
        "Model": agent_data.get("model", "N/A"),
        "Status": agent_data.get("status", "N/A")
    }
    output.append(format_dict(info_data))
    
    # Capabilities
    if "capabilities" in agent_data and agent_data["capabilities"]:
        output.append(format_subheader("Capabilities"))
        output.append(format_list(agent_data["capabilities"]))
    
    # Configuration
    if "config" in agent_data and agent_data["config"]:
        output.append(format_subheader("Configuration"))
        output.append(format_dict(agent_data["config"]))
    
    return "\n".join(output)


def format_validation_output(validation_result: Dict[str, Any]) -> str:
    """
    Format validation result for display.
    
    Args:
        validation_result: Validation result dictionary
        
    Returns:
        Formatted validation output
    """
    output = []
    
    is_valid = validation_result.get("is_valid", False)
    
    if is_valid:
        output.append(format_success("Validation passed"))
    else:
        output.append(format_error("Validation failed"))
    
    # Errors
    if "errors" in validation_result and validation_result["errors"]:
        output.append(format_subheader("Errors"))
        for error_item in validation_result["errors"]:
            if isinstance(error_item, dict):
                field = error_item.get("field", "unknown")
                message = error_item.get("message", "unknown error")
                output.append(f"  {error('✗')} {bold(field)}: {message}")
            else:
                output.append(f"  {error('✗')} {error_item}")
    
    # Warnings
    if "warnings" in validation_result and validation_result["warnings"]:
        output.append(format_subheader("Warnings"))
        for warning_item in validation_result["warnings"]:
            output.append(f"  {warning('⚠')} {warning_item}")
    
    return "\n".join(output)


def format_health_check_output(health_checks: List[Dict[str, Any]]) -> str:
    """
    Format health check results for display.
    
    Args:
        health_checks: List of health check results
        
    Returns:
        Formatted health check output
    """
    output = []
    output.append(format_header("System Health Check"))
    
    if not health_checks:
        output.append(dim("No health checks available"))
        return "\n".join(output)
    
    # Create table
    rows = []
    for check in health_checks:
        component = check.get("component", "Unknown")
        status = check.get("status", "unknown")
        message = check.get("message", "")
        
        # Colorize status
        if status == "healthy":
            status_display = success(status)
        elif status == "degraded":
            status_display = warning(status)
        else:
            status_display = error(status)
        
        rows.append([component, status_display, message])
    
    output.append(format_table(["Component", "Status", "Message"], rows))
    
    return "\n".join(output)
