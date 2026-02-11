# API Reference: agentic_sdlc.intelligence.collaboration.collaborator

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.intelligence.collaboration.collaborator`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Multi-agent collaboration and coordination.

---

## Classes

## Class `CollaborationMessage`

**Mô tả:**

A message in agent collaboration.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, sender: str, recipient: str, message_type: agentic_sdlc.intelligence.collaboration.collaborator.MessageType, content: str, timestamp: str = <factory>, metadata: Dict[str, Any] = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `sender` (str): Tham số sender
- `recipient` (str): Tham số recipient
- `message_type` (MessageType): Tham số message_type
- `content` (str): Tham số content
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp
- `metadata` (Dict), mặc định: `<factory>`: Tham số metadata

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng CollaborationMessage**

```python
# Ví dụ sử dụng CollaborationMessage
from agentic_sdlc.intelligence.collaboration.collaborator import CollaborationMessage

# Tạo instance
obj = CollaborationMessage()
```text

---

## Class `CollaborationResult`

**Mô tả:**

Result of a collaboration session.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, task: str, participants: List[str], messages: List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage], outcome: str, timestamp: str = <factory>) -> None
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `task` (str): Tham số task
- `participants` (List): Tham số participants
- `messages` (List): Tham số messages
- `outcome` (str): Tham số outcome
- `timestamp` (str), mặc định: `<factory>`: Tham số timestamp

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self)
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `Any`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng CollaborationResult**

```python
# Ví dụ sử dụng CollaborationResult
from agentic_sdlc.intelligence.collaboration.collaborator import CollaborationResult

# Tạo instance
obj = CollaborationResult()
```text

---

## Class `Collaborator`

**Mô tả:**

Manages collaboration between agents.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, agent_name: str)
```text

**Mô tả:**

Initialize a collaborator.

Args:
    agent_name: Name of the agent

**Tham số (Parameters):**

- `agent_name` (str): Tham số agent_name

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `get_collaboration_history`

**Chữ ký (Signature):**

```python
get_collaboration_history(self) -> List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationResult]
```text

**Mô tả:**

Get collaboration history.

Returns:
    List of past collaborations

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_message_history`

**Chữ ký (Signature):**

```python
get_message_history(self) -> List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage]
```text

**Mô tả:**

Get full message history.

Returns:
    List of all messages

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_messages`

**Chữ ký (Signature):**

```python
get_messages(self, sender: Optional[str] = None) -> List[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage]
```text

**Mô tả:**

Get messages, optionally filtered by sender.

Args:
    sender: Optional sender to filter by

Returns:
    List of messages

**Tham số (Parameters):**

- `sender` (Optional): Tham số sender

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `receive_message`

**Chữ ký (Signature):**

```python
receive_message(self, message: agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage) -> None
```text

**Mô tả:**

Receive a message from another agent.

Args:
    message: CollaborationMessage to receive

**Tham số (Parameters):**

- `message` (CollaborationMessage): Tham số message

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

#### `record_collaboration`

**Chữ ký (Signature):**

```python
record_collaboration(self, task: str, participants: List[str], outcome: str) -> agentic_sdlc.intelligence.collaboration.collaborator.CollaborationResult
```text

**Mô tả:**

Record a collaboration session.

Args:
    task: Task description
    participants: List of participant agent names
    outcome: Outcome of collaboration

Returns:
    CollaborationResult object

**Tham số (Parameters):**

- `task` (str): Tham số task
- `participants` (List): Tham số participants
- `outcome` (str): Tham số outcome

**Giá trị trả về (Returns):**

- `CollaborationResult`: Giá trị trả về

#### `send_message`

**Chữ ký (Signature):**

```python
send_message(self, recipient: str, message_type: agentic_sdlc.intelligence.collaboration.collaborator.MessageType, content: str, metadata: Optional[Dict] = None) -> agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage
```text

**Mô tả:**

Send a message to another agent.

Args:
    recipient: Recipient agent name
    message_type: Type of message
    content: Message content
    metadata: Optional metadata

Returns:
    CollaborationMessage object

**Tham số (Parameters):**

- `recipient` (str): Tham số recipient
- `message_type` (MessageType): Tham số message_type
- `content` (str): Tham số content
- `metadata` (Optional): Tham số metadata

**Giá trị trả về (Returns):**

- `CollaborationMessage`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Collaborator**

```python
# Ví dụ sử dụng Collaborator
from agentic_sdlc.intelligence.collaboration.collaborator import Collaborator

# Tạo instance
obj = Collaborator()
```text

---

## Class `MessageType`

**Mô tả:**

Types of messages in collaboration.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, *args, **kwds)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwds` (Any): Tham số kwds

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng MessageType**

```python
# Ví dụ sử dụng MessageType
from agentic_sdlc.intelligence.collaboration.collaborator import MessageType

# Tạo instance
obj = MessageType()
```text

---

## Class `TeamCoordinator`

**Mô tả:**

Coordinates collaboration between multiple agents.

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self)
```text

**Mô tả:**

Initialize the team coordinator.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Methods

#### `end_session`

**Chữ ký (Signature):**

```python
end_session(self, session_index: int, outcome: str) -> Optional[Dict]
```text

**Mô tả:**

End a collaboration session.

Args:
    session_index: Index of the session
    outcome: Outcome of the session

Returns:
    Updated session dictionary or None

**Tham số (Parameters):**

- `session_index` (int): Tham số session_index
- `outcome` (str): Tham số outcome

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `get_agent`

**Chữ ký (Signature):**

```python
get_agent(self, agent_name: str) -> Optional[agentic_sdlc.intelligence.collaboration.collaborator.Collaborator]
```text

**Mô tả:**

Get a registered agent.

Args:
    agent_name: Name of the agent

Returns:
    Collaborator instance or None

**Tham số (Parameters):**

- `agent_name` (str): Tham số agent_name

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `get_all_agents`

**Chữ ký (Signature):**

```python
get_all_agents(self) -> Dict[str, agentic_sdlc.intelligence.collaboration.collaborator.Collaborator]
```text

**Mô tả:**

Get all registered agents.

Returns:
    Dictionary of agent names to Collaborator instances

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `get_sessions`

**Chữ ký (Signature):**

```python
get_sessions(self) -> List[Dict]
```text

**Mô tả:**

Get all collaboration sessions.

Returns:
    List of sessions

**Giá trị trả về (Returns):**

- `List`: Giá trị trả về

#### `get_team_stats`

**Chữ ký (Signature):**

```python
get_team_stats(self) -> Dict[str, Any]
```text

**Mô tả:**

Get statistics about the team.

Returns:
    Dictionary with team statistics

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `register_agent`

**Chữ ký (Signature):**

```python
register_agent(self, agent_name: str) -> agentic_sdlc.intelligence.collaboration.collaborator.Collaborator
```text

**Mô tả:**

Register an agent with the coordinator.

Args:
    agent_name: Name of the agent

Returns:
    Collaborator instance for the agent

**Tham số (Parameters):**

- `agent_name` (str): Tham số agent_name

**Giá trị trả về (Returns):**

- `Collaborator`: Giá trị trả về

#### `send_message`

**Chữ ký (Signature):**

```python
send_message(self, sender: str, recipient: str, message_type: agentic_sdlc.intelligence.collaboration.collaborator.MessageType, content: str, metadata: Optional[Dict] = None) -> Optional[agentic_sdlc.intelligence.collaboration.collaborator.CollaborationMessage]
```text

**Mô tả:**

Send a message between agents.

Args:
    sender: Sender agent name
    recipient: Recipient agent name
    message_type: Type of message
    content: Message content
    metadata: Optional metadata

Returns:
    CollaborationMessage or None if agents not found

**Tham số (Parameters):**

- `sender` (str): Tham số sender
- `recipient` (str): Tham số recipient
- `message_type` (MessageType): Tham số message_type
- `content` (str): Tham số content
- `metadata` (Optional): Tham số metadata

**Giá trị trả về (Returns):**

- `Optional`: Giá trị trả về

#### `start_session`

**Chữ ký (Signature):**

```python
start_session(self, task: str, participants: List[str]) -> Dict
```text

**Mô tả:**

Start a collaboration session.

Args:
    task: Task description
    participants: List of participant agent names

Returns:
    Session dictionary

**Tham số (Parameters):**

- `task` (str): Tham số task
- `participants` (List): Tham số participants

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng TeamCoordinator**

```python
# Ví dụ sử dụng TeamCoordinator
from agentic_sdlc.intelligence.collaboration.collaborator import TeamCoordinator

# Tạo instance
obj = TeamCoordinator()
```

---
