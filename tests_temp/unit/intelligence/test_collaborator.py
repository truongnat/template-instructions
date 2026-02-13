"""Unit tests for Collaborator and TeamCoordinator classes."""

import pytest
from agentic_sdlc.intelligence.collaboration import (
    Collaborator,
    TeamCoordinator,
    MessageType,
    CollaborationMessage,
)


class TestCollaborator:
    """Tests for Collaborator functionality."""

    @pytest.fixture
    def collaborator(self):
        """Create a collaborator instance."""
        return Collaborator("agent_a")

    def test_collaborator_initialization(self, collaborator):
        """Test collaborator initialization."""
        assert collaborator.agent_name == "agent_a"
        assert len(collaborator.messages) == 0
        assert len(collaborator.collaborations) == 0

    def test_send_message(self, collaborator):
        """Test sending a message."""
        message = collaborator.send_message(
            "agent_b", MessageType.REQUEST, "Please help with task X"
        )
        assert message.sender == "agent_a"
        assert message.recipient == "agent_b"
        assert message.message_type == MessageType.REQUEST
        assert len(collaborator.messages) == 1

    def test_send_message_with_metadata(self, collaborator):
        """Test sending a message with metadata."""
        metadata = {"priority": "high", "deadline": "urgent"}
        message = collaborator.send_message(
            "agent_b", MessageType.REQUEST, "Help", metadata=metadata
        )
        assert message.metadata == metadata

    def test_receive_message(self, collaborator):
        """Test receiving a message."""
        other = Collaborator("agent_b")
        message = other.send_message("agent_a", MessageType.RESPONSE, "I can help")
        collaborator.receive_message(message)
        assert len(collaborator.messages) == 1
        assert collaborator.messages[0].sender == "agent_b"

    def test_get_messages(self, collaborator):
        """Test getting all messages."""
        collaborator.send_message("agent_b", MessageType.REQUEST, "msg1")
        collaborator.send_message("agent_c", MessageType.REQUEST, "msg2")
        messages = collaborator.get_messages()
        assert len(messages) == 2

    def test_get_messages_from_sender(self, collaborator):
        """Test getting messages from specific sender."""
        other_a = Collaborator("agent_b")
        other_b = Collaborator("agent_c")
        msg_a = other_a.send_message("agent_a", MessageType.RESPONSE, "from b")
        msg_b = other_b.send_message("agent_a", MessageType.RESPONSE, "from c")
        collaborator.receive_message(msg_a)
        collaborator.receive_message(msg_b)

        messages_from_b = collaborator.get_messages(sender="agent_b")
        assert len(messages_from_b) == 1
        assert messages_from_b[0].sender == "agent_b"

    def test_get_message_history(self, collaborator):
        """Test getting message history."""
        collaborator.send_message("agent_b", MessageType.REQUEST, "msg1")
        collaborator.send_message("agent_b", MessageType.RESPONSE, "msg2")
        history = collaborator.get_message_history()
        assert len(history) == 2

    def test_record_collaboration(self, collaborator):
        """Test recording a collaboration session."""
        collaborator.send_message("agent_b", MessageType.REQUEST, "Help")
        result = collaborator.record_collaboration(
            "task_x", ["agent_a", "agent_b"], "completed successfully"
        )
        assert result.task == "task_x"
        assert len(result.participants) == 2
        assert result.outcome == "completed successfully"
        assert len(collaborator.collaborations) == 1

    def test_get_collaboration_history(self, collaborator):
        """Test getting collaboration history."""
        collaborator.record_collaboration("task_1", ["agent_a", "agent_b"], "success")
        collaborator.record_collaboration("task_2", ["agent_a", "agent_c"], "success")
        history = collaborator.get_collaboration_history()
        assert len(history) == 2


class TestTeamCoordinator:
    """Tests for TeamCoordinator functionality."""

    @pytest.fixture
    def coordinator(self):
        """Create a team coordinator instance."""
        return TeamCoordinator()

    def test_coordinator_initialization(self, coordinator):
        """Test coordinator initialization."""
        assert coordinator is not None
        assert len(coordinator.agents) == 0
        assert len(coordinator.sessions) == 0

    def test_register_agent(self, coordinator):
        """Test registering an agent."""
        agent = coordinator.register_agent("agent_a")
        assert agent is not None
        assert agent.agent_name == "agent_a"
        assert len(coordinator.agents) == 1

    def test_register_multiple_agents(self, coordinator):
        """Test registering multiple agents."""
        coordinator.register_agent("agent_a")
        coordinator.register_agent("agent_b")
        coordinator.register_agent("agent_c")
        assert len(coordinator.agents) == 3

    def test_get_agent(self, coordinator):
        """Test getting a registered agent."""
        coordinator.register_agent("agent_a")
        agent = coordinator.get_agent("agent_a")
        assert agent is not None
        assert agent.agent_name == "agent_a"

    def test_get_nonexistent_agent(self, coordinator):
        """Test getting an agent that doesn't exist."""
        agent = coordinator.get_agent("nonexistent")
        assert agent is None

    def test_get_all_agents(self, coordinator):
        """Test getting all agents."""
        coordinator.register_agent("agent_a")
        coordinator.register_agent("agent_b")
        agents = coordinator.get_all_agents()
        assert len(agents) == 2

    def test_send_message_between_agents(self, coordinator):
        """Test sending a message between agents."""
        coordinator.register_agent("agent_a")
        coordinator.register_agent("agent_b")
        message = coordinator.send_message(
            "agent_a", "agent_b", MessageType.REQUEST, "Help with task"
        )
        assert message is not None
        assert message.sender == "agent_a"
        assert message.recipient == "agent_b"

    def test_send_message_nonexistent_agent(self, coordinator):
        """Test sending message to nonexistent agent."""
        coordinator.register_agent("agent_a")
        message = coordinator.send_message(
            "agent_a", "nonexistent", MessageType.REQUEST, "Help"
        )
        assert message is None

    def test_start_session(self, coordinator):
        """Test starting a collaboration session."""
        coordinator.register_agent("agent_a")
        coordinator.register_agent("agent_b")
        session = coordinator.start_session("task_x", ["agent_a", "agent_b"])
        assert session["task"] == "task_x"
        assert len(session["participants"]) == 2
        assert len(coordinator.sessions) == 1

    def test_end_session(self, coordinator):
        """Test ending a collaboration session."""
        coordinator.register_agent("agent_a")
        coordinator.register_agent("agent_b")
        coordinator.start_session("task_x", ["agent_a", "agent_b"])
        result = coordinator.end_session(0, "completed")
        assert result is not None
        assert result["outcome"] == "completed"
        assert "end_time" in result

    def test_end_nonexistent_session(self, coordinator):
        """Test ending a session that doesn't exist."""
        result = coordinator.end_session(0, "completed")
        assert result is None

    def test_get_sessions(self, coordinator):
        """Test getting all sessions."""
        coordinator.register_agent("agent_a")
        coordinator.register_agent("agent_b")
        coordinator.start_session("task_1", ["agent_a", "agent_b"])
        coordinator.start_session("task_2", ["agent_a", "agent_b"])
        sessions = coordinator.get_sessions()
        assert len(sessions) == 2

    def test_get_team_stats(self, coordinator):
        """Test getting team statistics."""
        coordinator.register_agent("agent_a")
        coordinator.register_agent("agent_b")
        coordinator.send_message("agent_a", "agent_b", MessageType.REQUEST, "Help")
        coordinator.start_session("task_x", ["agent_a", "agent_b"])

        stats = coordinator.get_team_stats()
        assert stats["total_agents"] == 2
        assert stats["total_messages"] >= 1
        assert stats["total_sessions"] == 1
        assert "agent_a" in stats["agents"]
        assert "agent_b" in stats["agents"]
