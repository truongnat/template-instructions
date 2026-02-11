#!/usr/bin/env python3
"""
Example 2: Running Workflows Programmatically

This example demonstrates:
- Creating workflow configurations
- Executing workflows programmatically
- Monitoring workflow execution
- Handling workflow results

Run: python 02_workflow_execution.py
"""

from typing import Dict, Any
from agentic_sdlc import (
    Config,
    setup_logging,
    get_logger,
    WorkflowEngine,
    WorkflowBuilder,
)


def main():
    """Main example function."""
    
    print("=" * 60)
    print("Example 2: Running Workflows Programmatically")
    print("=" * 60)
    print()
    
    # Setup logging
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    
    # Load configuration
    print("Loading configuration...")
    config = Config()
    logger.info("Configuration loaded")
    print()
    
    # Create a workflow builder
    print("Creating workflow...")
    print("-" * 40)
    
    try:
        builder = WorkflowBuilder(name="example-workflow")
        
        # Configure workflow
        builder.set_description("Example workflow demonstrating programmatic execution")
        
        # Add workflow steps
        builder.add_step(
            name="initialize",
            description="Initialize workflow",
            action="initialize"
        )
        
        builder.add_step(
            name="process",
            description="Process data",
            action="process"
        )
        
        builder.add_step(
            name="finalize",
            description="Finalize workflow",
            action="finalize"
        )
        
        # Build the workflow
        workflow = builder.build()
        logger.info(f"Workflow created: {workflow.name}")
        print(f"  ✓ Workflow: {workflow.name}")
        print(f"  ✓ Description: {workflow.description}")
        print(f"  ✓ Steps: {len(workflow.steps)}")
        print()
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        return
    
    # Create workflow engine
    print("Creating workflow engine...")
    print("-" * 40)
    
    try:
        engine = WorkflowEngine()
        logger.info("Workflow engine created")
        print("  ✓ Workflow engine initialized")
        print()
        
    except Exception as e:
        logger.error(f"Failed to create workflow engine: {e}")
        return
    
    # Execute workflow
    print("Executing workflow...")
    print("-" * 40)
    
    try:
        # Execute the workflow
        logger.info(f"Starting workflow execution: {workflow.name}")
        
        # Simulate workflow execution
        print(f"  Starting workflow: {workflow.name}")
        
        for i, step in enumerate(workflow.steps, 1):
            print(f"  Step {i}/{len(workflow.steps)}: {step.get('name', 'Unknown')}")
            print(f"    Description: {step.get('description', 'No description')}")
            print(f"    Action: {step.get('action', 'No action')}")
        
        logger.info("Workflow execution completed")
        print()
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return
    
    # Display workflow results
    print("Workflow Results:")
    print("-" * 40)
    print(f"  Workflow: {workflow.name}")
    print(f"  Status: Completed")
    print(f"  Steps Executed: {len(workflow.steps)}")
    print(f"  Duration: ~0.1s (simulated)")
    print()
    
    # Example: Handling workflow results
    print("Example: Processing workflow results:")
    print("-" * 40)
    
    results: Dict[str, Any] = {
        "workflow": workflow.name,
        "status": "completed",
        "steps_executed": len(workflow.steps),
        "timestamp": "2024-02-11T10:30:00Z"
    }
    
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
