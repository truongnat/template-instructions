"""Diagram generation for documentation system.

This module provides the DiagramGenerator class for creating Mermaid diagrams
including architecture diagrams, workflow diagrams, agent interaction diagrams,
and data flow diagrams.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Component:
    """A component in an architecture diagram."""
    id: str
    name: str
    type: str
    description: Optional[str] = None


@dataclass
class Connection:
    """A connection between components."""
    source: str
    target: str
    label: Optional[str] = None
    type: str = "arrow"  # arrow, dotted, thick


@dataclass
class WorkflowStep:
    """A step in a workflow."""
    id: str
    name: str
    actor: str
    description: Optional[str] = None


@dataclass
class Agent:
    """An agent in the system."""
    id: str
    name: str
    role: str
    description: Optional[str] = None


@dataclass
class Interaction:
    """An interaction between agents."""
    source: str
    target: str
    message: str
    type: str = "sync"  # sync, async, return


@dataclass
class DataFlowNode:
    """A node in a data flow diagram."""
    id: str
    name: str
    type: str  # process, datastore, external
    description: Optional[str] = None


@dataclass
class DataFlow:
    """A data flow between nodes."""
    source: str
    target: str
    data: str
    description: Optional[str] = None


class DiagramGenerator:
    """Generate Mermaid diagrams for documentation."""
    
    def __init__(self):
        """Initialize the diagram generator."""
        pass
    
    def generate_architecture_diagram(
        self,
        components: List[Component],
        connections: List[Connection]
    ) -> str:
        """Generate architecture diagram in Mermaid flowchart format.
        
        Args:
            components: List of system components
            connections: List of connections between components
            
        Returns:
            Mermaid flowchart syntax as string
        """
        lines = ["flowchart TB"]
        
        # Add components
        for comp in components:
            # Determine shape based on component type
            if comp.type == "database":
                shape_start, shape_end = "[(", ")]"
            elif comp.type == "external":
                shape_start, shape_end = "{{", "}}"
            elif comp.type == "process":
                shape_start, shape_end = "[", "]"
            elif comp.type == "decision":
                shape_start, shape_end = "{", "}"
            else:
                shape_start, shape_end = "[", "]"
            
            node_def = f"    {comp.id}{shape_start}\"{comp.name}\"{shape_end}"
            lines.append(node_def)
        
        # Add connections
        for conn in connections:
            if conn.type == "dotted":
                arrow = "-.->"
            elif conn.type == "thick":
                arrow = "==>"
            else:
                arrow = "-->"
            
            if conn.label:
                conn_def = f"    {conn.source} {arrow}|{conn.label}| {conn.target}"
            else:
                conn_def = f"    {conn.source} {arrow} {conn.target}"
            lines.append(conn_def)
        
        return "\n".join(lines)
    
    def generate_workflow_diagram(
        self,
        steps: List[WorkflowStep],
        title: Optional[str] = None
    ) -> str:
        """Generate workflow sequence diagram in Mermaid format.
        
        Args:
            steps: List of workflow steps
            title: Optional diagram title
            
        Returns:
            Mermaid sequence diagram syntax as string
        """
        lines = ["sequenceDiagram"]
        
        if title:
            lines.append(f"    title {title}")
        
        # Get unique actors
        actors = list(set(step.actor for step in steps))
        
        # Add participants
        for actor in actors:
            lines.append(f"    participant {actor}")
        
        # Add steps
        for i, step in enumerate(steps):
            # Determine target (next step's actor or self)
            if i < len(steps) - 1:
                target = steps[i + 1].actor
            else:
                target = step.actor
            
            lines.append(f"    {step.actor}->>+{target}: {step.name}")
            
            if step.description:
                lines.append(f"    Note over {step.actor},{target}: {step.description}")
        
        return "\n".join(lines)
    
    def generate_agent_interaction_diagram(
        self,
        agents: List[Agent],
        interactions: List[Interaction]
    ) -> str:
        """Generate agent interaction sequence diagram in Mermaid format.
        
        Args:
            agents: List of agents in the system
            interactions: List of interactions between agents
            
        Returns:
            Mermaid sequence diagram syntax as string
        """
        lines = ["sequenceDiagram"]
        
        # Add participants
        for agent in agents:
            lines.append(f"    participant {agent.id} as {agent.name}")
        
        # Add interactions
        for interaction in interactions:
            if interaction.type == "async":
                arrow = "->>"
            elif interaction.type == "return":
                arrow = "-->>"
            else:
                arrow = "->>"
            
            lines.append(f"    {interaction.source}{arrow}{interaction.target}: {interaction.message}")
        
        return "\n".join(lines)
    
    def generate_data_flow_diagram(
        self,
        nodes: List[DataFlowNode],
        flows: List[DataFlow]
    ) -> str:
        """Generate data flow diagram in Mermaid flowchart format.
        
        Args:
            nodes: List of data flow nodes
            flows: List of data flows between nodes
            
        Returns:
            Mermaid flowchart syntax as string
        """
        lines = ["flowchart LR"]
        
        # Add nodes
        for node in nodes:
            # Determine shape based on node type
            if node.type == "datastore":
                shape_start, shape_end = "[(", ")]"
            elif node.type == "external":
                shape_start, shape_end = "([", "])"
            elif node.type == "process":
                shape_start, shape_end = "[", "]"
            else:
                shape_start, shape_end = "[", "]"
            
            node_def = f"    {node.id}{shape_start}\"{node.name}\"{shape_end}"
            lines.append(node_def)
        
        # Add flows
        for flow in flows:
            if flow.description:
                flow_def = f"    {flow.source} -->|{flow.data}| {flow.target}"
                lines.append(flow_def)
                lines.append(f"    Note right of {flow.target}: {flow.description}")
            else:
                flow_def = f"    {flow.source} -->|{flow.data}| {flow.target}"
                lines.append(flow_def)
        
        return "\n".join(lines)
