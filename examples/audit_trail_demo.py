#!/usr/bin/env python3
"""
Audit Trail Demo - Demonstrates the enhanced request logging and audit trail functionality

This demo shows how the MainAgent now logs comprehensive audit trails for all
user requests, processing decisions, and workflow executions with proper
timestamps, user context, and persistence capabilities.
"""

import sys
import tempfile
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import from the orchestration package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_sdlc.orchestration.agents.main_agent import MainAgent
from agentic_sdlc.orchestration.models import UserRequest, ConversationContext
from agentic_sdlc.orchestration.utils.audit_trail import setup_audit_trail


def demo_basic_request_logging():
    """Demonstrate basic request logging with audit trail"""
    print("=" * 60)
    print("DEMO: Basic Request Logging with Audit Trail")
    print("=" * 60)
    
    # Create temporary storage for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup audit trail with temporary storage
        audit_trail = setup_audit_trail(Path(temp_dir))
        
        # Create MainAgent
        agent = MainAgent()
        
        # Create a sample request
        request = UserRequest(
            user_id="demo_user_001",
            content="Create a new Python web application with user authentication and a REST API",
            metadata={"source": "demo", "priority": "high"}
        )
        
        print(f"Processing request: {request.content}")
        print(f"User ID: {request.user_id}")
        print(f"Request ID: {request.id}")
        print()
        
        # Process the request
        result = agent.process_request(request)
        
        print(f"Processing Result:")
        print(f"  Should Proceed: {result.should_proceed}")
        print(f"  Workflow Type: {result.workflow_type}")
        print(f"  Estimated Complexity: {result.estimated_complexity}")
        print(f"  Required Clarifications: {len(result.required_clarifications)}")
        print(f"  Suggested Next Steps: {len(result.suggested_next_steps)}")
        print()
        
        # Show audit trail entries
        print("Audit Trail Entries:")
        print("-" * 40)
        
        trail_entries = agent.get_request_audit_trail(request.id)
        for i, entry in enumerate(trail_entries, 1):
            timestamp = entry['timestamp']
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%H:%M:%S.%f')[:-3]
                except:
                    pass
            
            print(f"{i}. [{timestamp}] {entry['action']}")
            print(f"   Category: {entry['category']}")
            print(f"   Severity: {entry['severity']}")
            if entry.get('processing_duration_ms'):
                print(f"   Duration: {entry['processing_duration_ms']}ms")
            if entry.get('request_intent'):
                print(f"   Intent: {entry['request_intent']} (confidence: {entry.get('request_confidence', 0):.2f})")
            if entry.get('workflow_decision'):
                print(f"   Decision: {entry['workflow_decision']}")
            print()


def demo_error_logging():
    """Demonstrate error logging with audit trail"""
    print("=" * 60)
    print("DEMO: Error Logging with Audit Trail")
    print("=" * 60)
    
    # Create temporary storage for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup audit trail with temporary storage
        audit_trail = setup_audit_trail(Path(temp_dir))
        
        # Create MainAgent
        agent = MainAgent()
        
        # Create a request that will cause clarification (not an error, but shows the flow)
        request = UserRequest(
            user_id="demo_user_002",
            content="do something",  # Very vague request
            metadata={"source": "demo"}
        )
        
        print(f"Processing vague request: '{request.content}'")
        print(f"User ID: {request.user_id}")
        print(f"Request ID: {request.id}")
        print()
        
        # Process the request
        result = agent.process_request(request)
        
        print(f"Processing Result:")
        print(f"  Should Proceed: {result.should_proceed}")
        print(f"  Required Clarifications: {result.required_clarifications}")
        print()
        
        # Show audit trail entries
        print("Audit Trail Entries:")
        print("-" * 40)
        
        trail_entries = agent.get_request_audit_trail(request.id)
        for i, entry in enumerate(trail_entries, 1):
            timestamp = entry['timestamp']
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%H:%M:%S.%f')[:-3]
                except:
                    pass
            
            print(f"{i}. [{timestamp}] {entry['action']}")
            print(f"   Category: {entry['category']}")
            if entry.get('request_confidence'):
                print(f"   Confidence: {entry['request_confidence']:.2f}")
            if entry.get('clarifications_requested'):
                print(f"   Clarifications: {entry['clarifications_requested']}")
            print()


def demo_user_activity_summary():
    """Demonstrate user activity summary generation"""
    print("=" * 60)
    print("DEMO: User Activity Summary")
    print("=" * 60)
    
    # Create temporary storage for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup audit trail with temporary storage
        audit_trail = setup_audit_trail(Path(temp_dir))
        
        # Create MainAgent
        agent = MainAgent()
        
        user_id = "demo_user_003"
        
        # Process multiple requests for the same user
        requests = [
            "Create a Python web application",
            "Design a database schema for user management",
            "Implement user authentication",
            "Add REST API endpoints",
            "Write unit tests"
        ]
        
        print(f"Processing {len(requests)} requests for user: {user_id}")
        print()
        
        for i, content in enumerate(requests, 1):
            request = UserRequest(
                user_id=user_id,
                content=content,
                metadata={"source": "demo", "batch": i}
            )
            
            print(f"{i}. Processing: {content}")
            result = agent.process_request(request)
            print(f"   Result: {'Proceed' if result.should_proceed else 'Clarification needed'}")
        
        print()
        
        # Get user activity summary
        summary = agent.get_user_activity_summary(user_id, days=1)
        
        print("User Activity Summary:")
        print("-" * 30)
        print(f"User ID: {summary['user_id']}")
        print(f"Period: {summary['period_days']} days")
        print(f"Total Entries: {summary['total_entries']}")
        print(f"Requests: {summary['request_count']}")
        print(f"Processing Events: {summary['processing_count']}")
        print(f"Workflow Events: {summary['workflow_count']}")
        print(f"Errors: {summary['error_count']}")
        print(f"Average Processing Time: {summary['average_processing_time_ms']:.1f}ms")
        print()
        
        print("Recent Activity:")
        for activity in summary['recent_activity'][:5]:  # Show last 5
            timestamp = activity['timestamp']
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%H:%M:%S')
                except:
                    pass
            print(f"  [{timestamp}] {activity['action']} ({activity['category']})")


def demo_audit_trail_persistence():
    """Demonstrate audit trail persistence across sessions"""
    print("=" * 60)
    print("DEMO: Audit Trail Persistence")
    print("=" * 60)
    
    # Create temporary storage for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)
        
        # First session
        print("Session 1: Creating audit entries...")
        audit_trail1 = setup_audit_trail(storage_path)
        agent1 = MainAgent()
        
        request1 = UserRequest(
            user_id="persistent_user",
            content="Create a microservices architecture",
            metadata={"session": 1}
        )
        
        result1 = agent1.process_request(request1)
        print(f"  Processed request: {request1.content}")
        print(f"  Request ID: {request1.id}")
        
        # Second session (new instances)
        print("\nSession 2: Loading from persistent storage...")
        audit_trail2 = setup_audit_trail(storage_path)
        agent2 = MainAgent()
        
        # Retrieve entries from first session
        trail_entries = audit_trail2.get_request_trail(request1.id)
        print(f"  Retrieved {len(trail_entries)} entries from previous session")
        
        # Process another request in second session
        request2 = UserRequest(
            user_id="persistent_user",
            content="Add monitoring and logging",
            metadata={"session": 2}
        )
        
        result2 = agent2.process_request(request2)
        print(f"  Processed new request: {request2.content}")
        
        # Show combined activity
        user_summary = agent2.get_user_activity_summary("persistent_user", days=1)
        print(f"\nCombined User Activity:")
        print(f"  Total Entries: {user_summary['total_entries']}")
        print(f"  Requests: {user_summary['request_count']}")
        print(f"  Processing Events: {user_summary['processing_count']}")
        
        # Verify database file exists
        db_path = storage_path / "audit_trail.db"
        print(f"\nDatabase file exists: {db_path.exists()}")
        if db_path.exists():
            print(f"Database size: {db_path.stat().st_size} bytes")


def main():
    """Run all audit trail demos"""
    print("Multi-Agent Orchestration System")
    print("Enhanced Request Logging and Audit Trail Demo")
    print("=" * 60)
    print()
    
    try:
        demo_basic_request_logging()
        print("\n" + "=" * 60 + "\n")
        
        demo_error_logging()
        print("\n" + "=" * 60 + "\n")
        
        demo_user_activity_summary()
        print("\n" + "=" * 60 + "\n")
        
        demo_audit_trail_persistence()
        
        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())