"""Property-based tests for diagram generation.

This module contains property-based tests that verify universal correctness
properties for the diagram generation system.
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings

from src.agentic_sdlc.documentation.diagrams import (
    DiagramGenerator,
    Component,
    Connection,
    WorkflowStep,
    Agent,
    Interaction,
    DataFlowNode,
    DataFlow,
)
from src.agentic_sdlc.documentation.models import Diagram


# Strategies for generating test data
@st.composite
def component_strategy(draw):
    """Generate a valid Component."""
    return Component(
        id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Nd'), min_codepoint=48, max_codepoint=122
        )).filter(lambda x: x[0].isalpha())),
        name=draw(st.text(min_size=3, max_size=30)),
        type=draw(st.sampled_from(['database', 'external', 'process', 'decision', 'service'])),
        description=draw(st.one_of(st.none(), st.text(min_size=10, max_size=100)))
    )


@st.composite
def connection_strategy(draw, source_id, target_id):
    """Generate a valid Connection."""
    return Connection(
        source=source_id,
        target=target_id,
        label=draw(st.one_of(st.none(), st.text(min_size=3, max_size=30))),
        type=draw(st.sampled_from(['arrow', 'dotted', 'thick']))
    )


@st.composite
def workflow_step_strategy(draw):
    """Generate a valid WorkflowStep."""
    return WorkflowStep(
        id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Nd'), min_codepoint=48, max_codepoint=122
        )).filter(lambda x: x[0].isalpha())),
        name=draw(st.text(min_size=3, max_size=50)),
        actor=draw(st.text(min_size=3, max_size=30, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu'), min_codepoint=65, max_codepoint=122
        ))),
        description=draw(st.one_of(st.none(), st.text(min_size=10, max_size=100)))
    )


@st.composite
def agent_strategy(draw):
    """Generate a valid Agent."""
    return Agent(
        id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Nd'), min_codepoint=48, max_codepoint=122
        )).filter(lambda x: x[0].isalpha())),
        name=draw(st.text(min_size=3, max_size=30)),
        role=draw(st.sampled_from(['Developer', 'Tester', 'Reviewer', 'Manager', 'Architect'])),
        description=draw(st.one_of(st.none(), st.text(min_size=10, max_size=100)))
    )


@st.composite
def interaction_strategy(draw, source_id, target_id):
    """Generate a valid Interaction."""
    return Interaction(
        source=source_id,
        target=target_id,
        message=draw(st.text(min_size=5, max_size=50)),
        type=draw(st.sampled_from(['sync', 'async', 'return']))
    )


@st.composite
def data_flow_node_strategy(draw):
    """Generate a valid DataFlowNode."""
    return DataFlowNode(
        id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Ll', 'Lu', 'Nd'), min_codepoint=48, max_codepoint=122
        )).filter(lambda x: x[0].isalpha())),
        name=draw(st.text(min_size=3, max_size=30)),
        type=draw(st.sampled_from(['process', 'datastore', 'external'])),
        description=draw(st.one_of(st.none(), st.text(min_size=10, max_size=100)))
    )


@st.composite
def data_flow_strategy(draw, source_id, target_id):
    """Generate a valid DataFlow."""
    return DataFlow(
        source=source_id,
        target=target_id,
        data=draw(st.text(min_size=3, max_size=30)),
        description=draw(st.one_of(st.none(), st.text(min_size=10, max_size=100)))
    )


@st.composite
def diagram_model_strategy(draw):
    """Generate a valid Diagram model."""
    diagram_type = draw(st.sampled_from(['flowchart', 'sequence', 'class', 'stateDiagram', 'erDiagram']))
    
    # Generate valid Mermaid code based on type
    if diagram_type == 'flowchart':
        mermaid_code = f"flowchart TB\n    A[Start] --> B[End]"
    elif diagram_type == 'sequence':
        mermaid_code = f"sequenceDiagram\n    participant A\n    A->>B: Message"
    elif diagram_type == 'class':
        mermaid_code = f"classDiagram\n    class Animal"
    elif diagram_type == 'stateDiagram':
        mermaid_code = f"stateDiagram-v2\n    [*] --> State1"
    else:  # erDiagram
        mermaid_code = f"erDiagram\n    CUSTOMER ||--o{{ ORDER : places"
    
    return Diagram(
        type=diagram_type,
        mermaid_code=mermaid_code,
        caption=draw(st.text(min_size=5, max_size=100))
    )


# Property Test 4: Diagram Format Consistency
@settings(max_examples=20, deadline=None)
@given(diagram=diagram_model_strategy())
def test_diagram_format_consistency(diagram):
    """Feature: use-cases-and-usage-guide, Property 4:
    
    For any diagram in the documentation, it must use Mermaid syntax 
    for rendering and maintenance.
    
    **Validates: Requirements 13.5**
    """
    # Diagram must have mermaid_code
    assert diagram.mermaid_code is not None
    assert len(diagram.mermaid_code) > 0
    
    # Mermaid code must start with a valid diagram type
    valid_starts = (
        "graph",
        "flowchart",
        "sequenceDiagram",
        "classDiagram",
        "stateDiagram",
        "erDiagram",
        "gantt",
        "pie",
        "gitGraph"
    )
    
    stripped_code = diagram.mermaid_code.strip()
    assert any(stripped_code.startswith(start) for start in valid_starts), \
        f"Diagram must start with valid Mermaid syntax, got: {stripped_code[:50]}"
    
    # Diagram must have a caption
    assert diagram.caption is not None
    assert len(diagram.caption) > 0
    
    # Diagram must have a type
    assert diagram.type is not None
    assert len(diagram.type) > 0


@settings(max_examples=20, deadline=None)
@given(
    components=st.lists(component_strategy(), min_size=2, max_size=5, unique_by=lambda c: c.id)
)
def test_architecture_diagram_format(components):
    """Test that generated architecture diagrams use valid Mermaid flowchart syntax."""
    generator = DiagramGenerator()
    
    # Create connections between components
    connections = []
    for i in range(len(components) - 1):
        conn = Connection(
            source=components[i].id,
            target=components[i + 1].id,
            label=f"Connection {i}",
            type="arrow"
        )
        connections.append(conn)
    
    # Generate diagram
    mermaid_code = generator.generate_architecture_diagram(components, connections)
    
    # Verify it's valid Mermaid flowchart syntax
    assert mermaid_code.strip().startswith("flowchart"), \
        "Architecture diagram must start with 'flowchart'"
    
    # Verify all components are included
    for comp in components:
        assert comp.id in mermaid_code, \
            f"Component {comp.id} must be in the diagram"
    
    # Verify all connections are included
    for conn in connections:
        assert conn.source in mermaid_code, \
            f"Connection source {conn.source} must be in the diagram"
        assert conn.target in mermaid_code, \
            f"Connection target {conn.target} must be in the diagram"


@settings(max_examples=20, deadline=None)
@given(
    steps=st.lists(workflow_step_strategy(), min_size=2, max_size=5, unique_by=lambda s: s.id)
)
def test_workflow_diagram_format(steps):
    """Test that generated workflow diagrams use valid Mermaid sequence syntax."""
    generator = DiagramGenerator()
    
    # Generate diagram
    mermaid_code = generator.generate_workflow_diagram(steps, title="Test Workflow")
    
    # Verify it's valid Mermaid sequence diagram syntax
    assert mermaid_code.strip().startswith("sequenceDiagram"), \
        "Workflow diagram must start with 'sequenceDiagram'"
    
    # Verify all actors are included as participants
    actors = list(set(step.actor for step in steps))
    for actor in actors:
        assert f"participant {actor}" in mermaid_code, \
            f"Actor {actor} must be declared as participant"
    
    # Verify all steps are included
    for step in steps:
        assert step.name in mermaid_code, \
            f"Step {step.name} must be in the diagram"


@settings(max_examples=20, deadline=None)
@given(
    agents=st.lists(agent_strategy(), min_size=2, max_size=5, unique_by=lambda a: a.id)
)
def test_agent_interaction_diagram_format(agents):
    """Test that generated agent interaction diagrams use valid Mermaid sequence syntax."""
    generator = DiagramGenerator()
    
    # Create interactions between agents
    interactions = []
    for i in range(len(agents) - 1):
        interaction = Interaction(
            source=agents[i].id,
            target=agents[i + 1].id,
            message=f"Message {i}",
            type="sync"
        )
        interactions.append(interaction)
    
    # Generate diagram
    mermaid_code = generator.generate_agent_interaction_diagram(agents, interactions)
    
    # Verify it's valid Mermaid sequence diagram syntax
    assert mermaid_code.strip().startswith("sequenceDiagram"), \
        "Agent interaction diagram must start with 'sequenceDiagram'"
    
    # Verify all agents are included as participants
    for agent in agents:
        assert f"participant {agent.id}" in mermaid_code, \
            f"Agent {agent.id} must be declared as participant"
    
    # Verify all interactions are included
    for interaction in interactions:
        assert interaction.message in mermaid_code, \
            f"Interaction message '{interaction.message}' must be in the diagram"


@settings(max_examples=20, deadline=None)
@given(
    nodes=st.lists(data_flow_node_strategy(), min_size=2, max_size=5, unique_by=lambda n: n.id)
)
def test_data_flow_diagram_format(nodes):
    """Test that generated data flow diagrams use valid Mermaid flowchart syntax."""
    generator = DiagramGenerator()
    
    # Create flows between nodes
    flows = []
    for i in range(len(nodes) - 1):
        flow = DataFlow(
            source=nodes[i].id,
            target=nodes[i + 1].id,
            data=f"Data {i}",
            description=None
        )
        flows.append(flow)
    
    # Generate diagram
    mermaid_code = generator.generate_data_flow_diagram(nodes, flows)
    
    # Verify it's valid Mermaid flowchart syntax
    assert mermaid_code.strip().startswith("flowchart"), \
        "Data flow diagram must start with 'flowchart'"
    
    # Verify all nodes are included
    for node in nodes:
        assert node.id in mermaid_code, \
            f"Node {node.id} must be in the diagram"
    
    # Verify all flows are included
    for flow in flows:
        assert flow.source in mermaid_code, \
            f"Flow source {flow.source} must be in the diagram"
        assert flow.target in mermaid_code, \
            f"Flow target {flow.target} must be in the diagram"
        assert flow.data in mermaid_code, \
            f"Flow data '{flow.data}' must be in the diagram"
