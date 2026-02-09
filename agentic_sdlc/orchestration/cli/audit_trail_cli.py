#!/usr/bin/env python3
"""
Audit Trail CLI - Command-line interface for managing and querying audit trails

This utility provides commands for viewing, searching, and managing
audit trail data for the Multi-Agent Orchestration System.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Add the parent directory to the path so we can import from the orchestration package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_sdlc.orchestration.utils.audit_trail import get_audit_trail, setup_audit_trail


def format_entry(entry_dict: dict) -> str:
    """Format an audit entry for display"""
    timestamp = entry_dict.get('timestamp', 'Unknown')
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    severity = entry_dict.get('severity', 'info').upper()
    action = entry_dict.get('action', 'Unknown action')
    category = entry_dict.get('category', 'unknown')
    
    # Color coding for severity
    color_codes = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m'  # Magenta
    }
    reset_code = '\033[0m'
    
    color = color_codes.get(severity, '')
    
    line = f"[{timestamp}] {color}[{severity}]{reset_code} [{category}] {action}"
    
    # Add additional context if available
    if entry_dict.get('user_id'):
        line += f" (user: {entry_dict['user_id']})"
    
    if entry_dict.get('request_id'):
        line += f" (request: {entry_dict['request_id'][:8]}...)"
    
    if entry_dict.get('processing_duration_ms'):
        line += f" ({entry_dict['processing_duration_ms']}ms)"
    
    return line


def cmd_list(args):
    """List recent audit entries"""
    audit_trail = get_audit_trail(Path(args.storage_path) if args.storage_path else None)
    
    # Build filters
    filters = {}
    if args.user_id:
        filters['user_id'] = args.user_id
    if args.request_id:
        filters['request_id'] = args.request_id
    if args.workflow_id:
        filters['workflow_id'] = args.workflow_id
    if args.entry_type:
        filters['entry_type'] = args.entry_type
    if args.category:
        filters['category'] = args.category
    if args.severity:
        filters['severity'] = args.severity
    
    # Time filters
    if args.since:
        try:
            if args.since.isdigit():
                # Assume hours
                filters['start_time'] = datetime.now() - timedelta(hours=int(args.since))
            else:
                # Try to parse as ISO date
                filters['start_time'] = datetime.fromisoformat(args.since)
        except ValueError:
            print(f"Error: Invalid date format for --since: {args.since}")
            return 1
    
    filters['limit'] = args.limit
    
    try:
        entries = audit_trail.get_entries(**filters)
        
        if not entries:
            print("No audit entries found matching the criteria.")
            return 0
        
        print(f"Found {len(entries)} audit entries:")
        print("-" * 80)
        
        for entry in entries:
            entry_dict = entry.to_dict()
            print(format_entry(entry_dict))
            
            # Show additional details if verbose
            if args.verbose:
                if entry_dict.get('error_message'):
                    print(f"    Error: {entry_dict['error_message']}")
                if entry_dict.get('metadata'):
                    print(f"    Metadata: {json.dumps(entry_dict['metadata'], indent=2)}")
                print()
        
        return 0
        
    except Exception as e:
        print(f"Error retrieving audit entries: {e}")
        return 1


def cmd_search(args):
    """Search audit entries"""
    audit_trail = get_audit_trail(Path(args.storage_path) if args.storage_path else None)
    
    try:
        # Get all entries and filter by search term
        entries = audit_trail.get_entries(limit=args.limit)
        
        search_term = args.query.lower()
        matching_entries = []
        
        for entry in entries:
            entry_dict = entry.to_dict()
            # Search in action, error_message, and metadata
            searchable_text = " ".join([
                entry_dict.get('action', ''),
                entry_dict.get('error_message', ''),
                json.dumps(entry_dict.get('metadata', {}))
            ]).lower()
            
            if search_term in searchable_text:
                matching_entries.append(entry)
        
        if not matching_entries:
            print(f"No audit entries found matching '{args.query}'.")
            return 0
        
        print(f"Found {len(matching_entries)} entries matching '{args.query}':")
        print("-" * 80)
        
        for entry in matching_entries:
            entry_dict = entry.to_dict()
            print(format_entry(entry_dict))
            
            if args.verbose:
                if entry_dict.get('error_message'):
                    print(f"    Error: {entry_dict['error_message']}")
                if entry_dict.get('metadata'):
                    print(f"    Metadata: {json.dumps(entry_dict['metadata'], indent=2)}")
                print()
        
        return 0
        
    except Exception as e:
        print(f"Error searching audit entries: {e}")
        return 1


def cmd_request_trail(args):
    """Show complete audit trail for a specific request"""
    audit_trail = get_audit_trail(Path(args.storage_path) if args.storage_path else None)
    
    try:
        entries = audit_trail.get_request_trail(args.request_id)
        
        if not entries:
            print(f"No audit entries found for request ID: {args.request_id}")
            return 0
        
        print(f"Complete audit trail for request {args.request_id}:")
        print("=" * 80)
        
        for entry in entries:
            entry_dict = entry.to_dict()
            print(format_entry(entry_dict))
            
            # Always show details for request trails
            if entry_dict.get('request_content'):
                print(f"    Content: {entry_dict['request_content'][:100]}...")
            if entry_dict.get('request_intent'):
                print(f"    Intent: {entry_dict['request_intent']}")
            if entry_dict.get('request_confidence'):
                print(f"    Confidence: {entry_dict['request_confidence']:.2f}")
            if entry_dict.get('workflow_type'):
                print(f"    Workflow: {entry_dict['workflow_type']}")
            if entry_dict.get('error_message'):
                print(f"    Error: {entry_dict['error_message']}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"Error retrieving request trail: {e}")
        return 1


def cmd_errors(args):
    """Show error summary"""
    audit_trail = get_audit_trail(Path(args.storage_path) if args.storage_path else None)
    
    try:
        error_summary = audit_trail.get_error_summary(args.days)
        
        print(f"Error Summary (last {args.days} days):")
        print("=" * 50)
        print(f"Total Errors: {error_summary['total_errors']}")
        print()
        
        if error_summary['error_types']:
            print("Error Types:")
            for error_type, count in error_summary['error_types'].items():
                print(f"  {error_type}: {count}")
            print()
        
        if error_summary['error_operations']:
            print("Error Operations:")
            for operation, count in error_summary['error_operations'].items():
                print(f"  {operation}: {count}")
            print()
        
        if error_summary['recent_errors']:
            print("Recent Errors:")
            for error in error_summary['recent_errors']:
                timestamp = error['timestamp']
                if isinstance(timestamp, str):
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                print(f"  [{timestamp}] {error['error_type']}: {error['error_message']}")
                if error.get('operation'):
                    print(f"    Operation: {error['operation']}")
        
        return 0
        
    except Exception as e:
        print(f"Error retrieving error summary: {e}")
        return 1


def cmd_cleanup(args):
    """Clean up old audit entries"""
    audit_trail = get_audit_trail(Path(args.storage_path) if args.storage_path else None)
    
    try:
        if not args.force:
            response = input(f"This will delete audit entries older than {args.days} days. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Cleanup cancelled.")
                return 0
        
        deleted_count = audit_trail.cleanup_old_entries(args.days)
        print(f"Cleaned up {deleted_count} old audit entries.")
        return 0
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Audit Trail CLI - Manage and query orchestration audit trails",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--storage-path',
        help='Path to audit trail storage directory'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent audit entries')
    list_parser.add_argument('--user-id', help='Filter by user ID')
    list_parser.add_argument('--request-id', help='Filter by request ID')
    list_parser.add_argument('--workflow-id', help='Filter by workflow ID')
    list_parser.add_argument('--entry-type', help='Filter by entry type')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--severity', help='Filter by severity')
    list_parser.add_argument('--since', help='Show entries since (hours ago or ISO date)')
    list_parser.add_argument('--limit', type=int, default=50, help='Maximum number of entries')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search audit entries')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=100, help='Maximum number of entries to search')
    search_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    # Request trail command
    trail_parser = subparsers.add_parser('request-trail', help='Show complete trail for a request')
    trail_parser.add_argument('request_id', help='Request ID to show trail for')
    
    # Errors command
    errors_parser = subparsers.add_parser('errors', help='Show error summary')
    errors_parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old audit entries')
    cleanup_parser.add_argument('--days', type=int, default=365, help='Delete entries older than this many days')
    cleanup_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate command handler
    command_handlers = {
        'list': cmd_list,
        'search': cmd_search,
        'request-trail': cmd_request_trail,
        'errors': cmd_errors,
        'cleanup': cmd_cleanup
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())