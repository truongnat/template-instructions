"""
Table formatting utilities for CLI output.

Provides functions for creating formatted tables in terminal output.
"""

from typing import List, Dict, Any, Optional
from cli.output.colors import Colors, bold


def format_table(
    headers: List[str],
    rows: List[List[Any]],
    column_widths: Optional[List[int]] = None
) -> str:
    """
    Format data as a table.
    
    Args:
        headers: Column headers
        rows: Data rows
        column_widths: Optional fixed column widths
        
    Returns:
        Formatted table string
    """
    if not rows:
        return "No data to display"
    
    # Calculate column widths if not provided
    if column_widths is None:
        column_widths = []
        for i, header in enumerate(headers):
            max_width = len(str(header))
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            column_widths.append(max_width + 2)  # Add padding
    
    # Build separator line
    separator = "+" + "+".join(["-" * width for width in column_widths]) + "+"
    
    # Build header row
    header_cells = []
    for i, header in enumerate(headers):
        width = column_widths[i]
        cell = f" {str(header).ljust(width - 1)}"
        header_cells.append(cell)
    header_row = "|" + "|".join(header_cells) + "|"
    
    # Build data rows
    data_rows = []
    for row in rows:
        cells = []
        for i, value in enumerate(row):
            width = column_widths[i] if i < len(column_widths) else 20
            cell = f" {str(value).ljust(width - 1)}"
            cells.append(cell)
        data_rows.append("|" + "|".join(cells) + "|")
    
    # Combine all parts
    table_parts = [
        separator,
        bold(header_row),
        separator,
        *data_rows,
        separator
    ]
    
    return "\n".join(table_parts)


def format_key_value_table(data: Dict[str, Any]) -> str:
    """
    Format dictionary as a key-value table.
    
    Args:
        data: Dictionary to format
        
    Returns:
        Formatted table string
    """
    if not data:
        return "No data to display"
    
    rows = [[key, str(value)] for key, value in data.items()]
    return format_table(["Key", "Value"], rows)


def format_list_table(items: List[str], title: str = "Items") -> str:
    """
    Format list as a single-column table.
    
    Args:
        items: List of items
        title: Column title
        
    Returns:
        Formatted table string
    """
    if not items:
        return "No items to display"
    
    rows = [[item] for item in items]
    return format_table([title], rows)
