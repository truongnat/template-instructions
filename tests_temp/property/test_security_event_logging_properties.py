"""
Property-based tests for Security Event Logging.

These tests use Hypothesis to verify that all security events are properly
logged to the audit trail across many randomly generated inputs.

Feature: sdlc-kit-improvements
Property 13: Security Event Logging
Requirements: 14.6
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any

from security.audit_logger import AuditLogger, SecurityEventType


# Strategy for generating usernames
usernames = st.text(
    alphabet=st.characters(min_codepoint=65, max_codepoint=122),
    min_size=3,
    max_size=30
).filter(lambda x: x.strip() and x.isalnum())

# Strategy for generating resource names
resource_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
    min_size=3,
    max_size=50
).filter(lambda x: x and x[0].isalpha())

# Strategy for generating action names
action_names = st.sampled_from(['read', 'write', 'delete', 'update', 'execute', 'create'])

# Strategy for generating authentication methods
auth_methods = st.sampled_from(['password', 'token', 'oauth', 'api_key', 'certificate'])

# Strategy for generating IP addresses
ip_addresses = st.from_regex(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', fullmatch=True)

# Strategy for generating permission names
permission_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
    min_size=5,
    max_size=40
).filter(lambda x: x and x[0].isalpha() and ':' not in x)


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
    success=st.booleans(),
    method=auth_methods,
    ip_address=ip_addresses,
)
@settings(max_examples=10, deadline=None)
def test_authentication_events_are_logged(user, success, method, ip_address):
    """
    Property: For any authentication event (success or failure), when the event
    occurs, an entry should be created in the security audit log with the
    appropriate event type, user, and details.
    
    This property ensures that all authentication attempts are tracked.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log authentication event
        audit_logger.log_authentication(
            user=user,
            success=success,
            method=method,
            ip_address=ip_address
        )
        
        # Read the audit log
        assert log_path.exists(), "Audit log file should be created"
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Property: Log should contain an entry
        assert log_content.strip(), "Audit log should contain an entry"
        
        # Parse the log entry
        log_entry = json.loads(log_content.strip())
        
        # Property: Log entry should have required fields
        assert "timestamp" in log_entry, "Log entry should have timestamp"
        assert "event_type" in log_entry, "Log entry should have event_type"
        assert "user" in log_entry, "Log entry should have user"
        assert "details" in log_entry, "Log entry should have details"
        
        # Property: Event type should match authentication result
        expected_event_type = (
            SecurityEventType.AUTHENTICATION_SUCCESS.value if success
            else SecurityEventType.AUTHENTICATION_FAILURE.value
        )
        assert log_entry["event_type"] == expected_event_type, (
            f"Event type should be {expected_event_type}"
        )
        
        # Property: User should match
        assert log_entry["user"] == user, "User should match"
        
        # Property: Details should contain method and IP address
        assert log_entry["details"]["method"] == method, "Method should be logged"
        assert log_entry["details"]["ip_address"] == ip_address, "IP address should be logged"


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
)
@settings(max_examples=10, deadline=None)
def test_logout_events_are_logged(user):
    """
    Property: For any logout event, when the event occurs, an entry should be
    created in the security audit log with the logout event type and user.
    
    This property ensures that all logout events are tracked.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log logout event
        audit_logger.log_logout(user=user)
        
        # Read the audit log
        assert log_path.exists(), "Audit log file should be created"
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse the log entry
        log_entry = json.loads(log_content.strip())
        
        # Property: Event type should be logout
        assert log_entry["event_type"] == SecurityEventType.LOGOUT.value, (
            "Event type should be logout"
        )
        
        # Property: User should match
        assert log_entry["user"] == user, "User should match"


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
    resource=resource_names,
    action=action_names,
    granted=st.booleans(),
)
@settings(max_examples=10, deadline=None)
def test_authorization_events_are_logged(user, resource, action, granted):
    """
    Property: For any authorization event (granted or denied), when the event
    occurs, an entry should be created in the security audit log with the
    appropriate event type, user, resource, and action.
    
    This property ensures that all authorization checks are tracked.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log authorization event
        audit_logger.log_authorization(
            user=user,
            resource=resource,
            action=action,
            granted=granted
        )
        
        # Read the audit log
        assert log_path.exists(), "Audit log file should be created"
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse the log entry
        log_entry = json.loads(log_content.strip())
        
        # Property: Event type should match authorization result
        expected_event_type = (
            SecurityEventType.AUTHORIZATION_GRANTED.value if granted
            else SecurityEventType.AUTHORIZATION_DENIED.value
        )
        assert log_entry["event_type"] == expected_event_type, (
            f"Event type should be {expected_event_type}"
        )
        
        # Property: User should match
        assert log_entry["user"] == user, "User should match"
        
        # Property: Details should contain resource and action
        assert log_entry["details"]["resource"] == resource, "Resource should be logged"
        assert log_entry["details"]["action"] == action, "Action should be logged"


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
    secret_key=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=65, max_codepoint=122),
        min_size=5,
        max_size=30
    ).filter(lambda x: x and x[0].isalpha()),
    action=st.sampled_from(['accessed', 'created', 'deleted']),
)
@settings(max_examples=10, deadline=None)
def test_secret_access_events_are_logged(user, secret_key, action):
    """
    Property: For any secret access event (accessed, created, or deleted),
    when the event occurs, an entry should be created in the security audit
    log with the appropriate event type, user, and secret key.
    
    This property ensures that all secret operations are tracked.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log secret access event
        audit_logger.log_secret_access(
            user=user,
            secret_key=secret_key,
            action=action
        )
        
        # Read the audit log
        assert log_path.exists(), "Audit log file should be created"
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse the log entry
        log_entry = json.loads(log_content.strip())
        
        # Property: Event type should match action
        event_type_map = {
            "accessed": SecurityEventType.SECRET_ACCESSED.value,
            "created": SecurityEventType.SECRET_CREATED.value,
            "deleted": SecurityEventType.SECRET_DELETED.value,
        }
        expected_event_type = event_type_map[action]
        assert log_entry["event_type"] == expected_event_type, (
            f"Event type should be {expected_event_type}"
        )
        
        # Property: User should match
        assert log_entry["user"] == user, "User should match"
        
        # Property: Details should contain secret key
        assert log_entry["details"]["secret_key"] == secret_key, (
            "Secret key should be logged"
        )


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
    permission=permission_names,
    result=st.booleans(),
)
@settings(max_examples=10, deadline=None)
def test_permission_check_events_are_logged(user, permission, result):
    """
    Property: For any permission check event, when the event occurs, an entry
    should be created in the security audit log with the permission check
    event type, user, permission, and result.
    
    This property ensures that all permission checks are tracked.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log permission check event
        audit_logger.log_permission_check(
            user=user,
            permission=permission,
            result=result
        )
        
        # Read the audit log
        assert log_path.exists(), "Audit log file should be created"
        
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse the log entry
        log_entry = json.loads(log_content.strip())
        
        # Property: Event type should be permission check
        assert log_entry["event_type"] == SecurityEventType.PERMISSION_CHECK.value, (
            "Event type should be permission_check"
        )
        
        # Property: User should match
        assert log_entry["user"] == user, "User should match"
        
        # Property: Details should contain permission and result
        assert log_entry["details"]["permission"] == permission, (
            "Permission should be logged"
        )
        assert log_entry["details"]["result"] == result, "Result should be logged"


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    events=st.lists(
        st.tuples(
            usernames,  # user
            st.sampled_from(['auth', 'logout', 'authz', 'secret', 'permission']),  # event_type
        ),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=10, deadline=None)
def test_multiple_events_are_logged_sequentially(events):
    """
    Property: For any sequence of security events, when the events occur,
    each event should be logged as a separate entry in the audit log in
    the order they occurred.
    
    This property ensures that the audit log maintains a complete and
    ordered history of security events.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log multiple events
        for user, event_type in events:
            if event_type == 'auth':
                audit_logger.log_authentication(user=user, success=True, method='password')
            elif event_type == 'logout':
                audit_logger.log_logout(user=user)
            elif event_type == 'authz':
                audit_logger.log_authorization(
                    user=user, resource='resource', action='read', granted=True
                )
            elif event_type == 'secret':
                audit_logger.log_secret_access(user=user, secret_key='key', action='accessed')
            elif event_type == 'permission':
                audit_logger.log_permission_check(user=user, permission='perm', result=True)
        
        # Read the audit log
        assert log_path.exists(), "Audit log file should be created"
        
        with open(log_path, 'r') as f:
            log_lines = f.readlines()
        
        # Property: Number of log entries should match number of events
        assert len(log_lines) == len(events), (
            f"Should have {len(events)} log entries, found {len(log_lines)}"
        )
        
        # Property: Each log entry should be valid JSON
        for i, line in enumerate(log_lines):
            try:
                log_entry = json.loads(line.strip())
                assert "timestamp" in log_entry, f"Entry {i} should have timestamp"
                assert "event_type" in log_entry, f"Entry {i} should have event_type"
                assert "user" in log_entry, f"Entry {i} should have user"
            except json.JSONDecodeError:
                pytest.fail(f"Log entry {i} is not valid JSON: {line}")


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
    success=st.booleans(),
)
@settings(max_examples=10, deadline=None)
def test_log_entries_have_valid_timestamps(user, success):
    """
    Property: For any security event, when the event is logged, the log entry
    should contain a valid ISO format timestamp that can be parsed.
    
    This property ensures that all log entries have parseable timestamps
    for querying and analysis.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log an event
        audit_logger.log_authentication(user=user, success=success, method='password')
        
        # Read the audit log
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse the log entry
        log_entry = json.loads(log_content.strip())
        
        # Property: Timestamp should be present
        assert "timestamp" in log_entry, "Log entry should have timestamp"
        
        # Property: Timestamp should be parseable as ISO format
        try:
            timestamp = datetime.fromisoformat(log_entry["timestamp"])
            assert isinstance(timestamp, datetime), "Timestamp should be a datetime object"
        except (ValueError, TypeError) as e:
            pytest.fail(f"Timestamp should be valid ISO format: {e}")


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
    resource=resource_names,
    action=action_names,
    granted=st.booleans(),
    extra_details=st.dictionaries(
        keys=st.text(min_size=1, max_size=20).filter(lambda x: x.isalnum()),
        values=st.one_of(st.text(max_size=50), st.integers(), st.booleans()),
        max_size=5
    )
)
@settings(max_examples=10, deadline=None)
def test_log_entries_preserve_additional_details(user, resource, action, granted, extra_details):
    """
    Property: For any security event with additional details, when the event
    is logged, the log entry should preserve all the additional details
    provided.
    
    This property ensures that contextual information is not lost during
    logging.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log authorization event with extra details
        audit_logger.log_authorization(
            user=user,
            resource=resource,
            action=action,
            granted=granted,
            details=extra_details
        )
        
        # Read the audit log
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # Parse the log entry
        log_entry = json.loads(log_content.strip())
        
        # Property: All extra details should be present in the log entry
        for key, value in extra_details.items():
            assert key in log_entry["details"], (
                f"Extra detail '{key}' should be in log entry"
            )
            assert log_entry["details"][key] == value, (
                f"Extra detail '{key}' should have value '{value}'"
            )


# Feature: sdlc-kit-improvements, Property 13: Security Event Logging
@given(
    user=usernames,
    event_type=st.sampled_from(['auth', 'logout', 'authz', 'secret', 'permission']),
)
@settings(max_examples=10, deadline=None)
def test_log_entries_are_queryable(user, event_type):
    """
    Property: For any security event that is logged, when querying the audit
    log by user or event type, the event should be retrievable.
    
    This property ensures that the audit log supports querying for analysis
    and investigation.
    
    **Validates: Requirements 14.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "audit.log"
        
        # Create audit logger
        audit_logger = AuditLogger(log_path=str(log_path))
        
        # Log an event based on type
        if event_type == 'auth':
            audit_logger.log_authentication(user=user, success=True, method='password')
            expected_event_type = SecurityEventType.AUTHENTICATION_SUCCESS
        elif event_type == 'logout':
            audit_logger.log_logout(user=user)
            expected_event_type = SecurityEventType.LOGOUT
        elif event_type == 'authz':
            audit_logger.log_authorization(
                user=user, resource='resource', action='read', granted=True
            )
            expected_event_type = SecurityEventType.AUTHORIZATION_GRANTED
        elif event_type == 'secret':
            audit_logger.log_secret_access(user=user, secret_key='key', action='accessed')
            expected_event_type = SecurityEventType.SECRET_ACCESSED
        elif event_type == 'permission':
            audit_logger.log_permission_check(user=user, permission='perm', result=True)
            expected_event_type = SecurityEventType.PERMISSION_CHECK
        
        # Query by user
        events_by_user = audit_logger.query_events(user=user)
        
        # Property: Should find at least one event for this user
        assert len(events_by_user) >= 1, (
            f"Should find at least one event for user '{user}'"
        )
        
        # Property: All returned events should match the user
        for event in events_by_user:
            assert event["user"] == user, "All events should match the queried user"
        
        # Query by event type
        events_by_type = audit_logger.query_events(event_type=expected_event_type)
        
        # Property: Should find at least one event of this type
        assert len(events_by_type) >= 1, (
            f"Should find at least one event of type '{expected_event_type.value}'"
        )
        
        # Property: All returned events should match the event type
        for event in events_by_type:
            assert event["event_type"] == expected_event_type.value, (
                "All events should match the queried event type"
            )
