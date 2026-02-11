"""
Ví Dụ 9: Complex Workflow (Workflow Phức Tạp)

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Cấu hình API keys
3. Chạy: python 09-complex-workflow.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Workflow phức tạp với conditional logic
- Error handling và retry
- Parallel execution
- Dynamic routing
"""

import os
from dotenv import load_dotenv

load_dotenv()


def create_ci_cd_workflow():
    """Tạo CI/CD workflow phức tạp."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="ci-cd-pipeline")
    
    # Stage 1: Code checkout
    builder.add_step(WorkflowStep(
        name="checkout",
        action="git_checkout",
        description="Checkout code from repository",
        parameters={"branch": "main", "repo": "https://github.com/user/repo"}
    ))
    
    # Stage 2: Parallel build and test
    builder.add_step(WorkflowStep(
        name="build",
        action="build",
        description="Build application",
        parameters={"target": "production"},
        dependencies=["checkout"]
    ))
    
    builder.add_step(WorkflowStep(
        name="unit_tests",
        action="test",
        description="Run unit tests",
        parameters={"test_type": "unit"},
        dependencies=["checkout"]
    ))
    
    builder.add_step(WorkflowStep(
        name="integration_tests",
        action="test",
        description="Run integration tests",
        parameters={"test_type": "integration"},
        dependencies=["checkout"]
    ))
    
    # Stage 3: Quality checks (after tests pass)
    builder.add_step(WorkflowStep(
        name="code_quality",
        action="analyze",
        description="Check code quality",
        parameters={"tools": ["pylint", "mypy", "black"]},
        dependencies=["unit_tests", "integration_tests"]
    ))
    
    # Stage 4: Security scan
    builder.add_step(WorkflowStep(
        name="security_scan",
        action="security_scan",
        description="Run security scan",
        parameters={"scanner": "bandit"},
        dependencies=["build"]
    ))
    
    # Stage 5: Deploy (conditional on all checks passing)
    builder.add_step(WorkflowStep(
        name="deploy_staging",
        action="deploy",
        description="Deploy to staging",
        parameters={"environment": "staging"},
        dependencies=["build", "code_quality", "security_scan"],
        condition="{{all_checks_passed}}"
    ))
    
    # Stage 6: Smoke tests on staging
    builder.add_step(WorkflowStep(
        name="smoke_tests",
        action="test",
        description="Run smoke tests",
        parameters={"environment": "staging"},
        dependencies=["deploy_staging"]
    ))
    
    # Stage 7: Deploy to production (manual approval)
    builder.add_step(WorkflowStep(
        name="deploy_production",
        action="deploy",
        description="Deploy to production",
        parameters={"environment": "production"},
        dependencies=["smoke_tests"],
        condition="{{manual_approval}}"
    ))
    
    workflow = builder.build()
    
    print("✓ CI/CD workflow created")
    print(f"  Total steps: {len(workflow.steps)}")
    print("  Stages:")
    print("    1. Checkout")
    print("    2. Build + Tests (parallel)")
    print("    3. Quality & Security checks")
    print("    4. Deploy staging")
    print("    5. Smoke tests")
    print("    6. Deploy production (with approval)")
    
    return workflow


def workflow_with_error_handling():
    """Workflow với error handling và retry logic."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="resilient-workflow")
    
    # Step với retry logic
    builder.add_step(WorkflowStep(
        name="fetch_data",
        action="fetch",
        description="Fetch data from API",
        parameters={
            "url": "https://api.example.com/data",
            "retry_count": 3,
            "retry_delay": 5,
            "timeout": 30
        }
    ))
    
    # Step với fallback
    builder.add_step(WorkflowStep(
        name="process_data",
        action="process",
        description="Process data",
        parameters={
            "data": "{{fetch_data.output}}",
            "fallback_strategy": "use_cache"
        },
        dependencies=["fetch_data"]
    ))
    
    # Error handling step
    builder.add_step(WorkflowStep(
        name="handle_errors",
        action="error_handler",
        description="Handle any errors",
        parameters={
            "errors": "{{workflow.errors}}",
            "notify": True
        },
        condition="{{workflow.has_errors}}"
    ))
    
    workflow = builder.build()
    
    print("\n✓ Resilient workflow created")
    print("  Features:")
    print("    - Automatic retry on failure")
    print("    - Fallback strategies")
    print("    - Error notification")
    
    return workflow


def dynamic_workflow():
    """Workflow với dynamic routing."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="dynamic-routing")
    
    # Analyze input
    builder.add_step(WorkflowStep(
        name="analyze_input",
        action="analyze",
        description="Analyze input type",
        parameters={"input": "{{workflow.input}}"}
    ))
    
    # Route to different processors based on input type
    builder.add_step(WorkflowStep(
        name="process_text",
        action="process_text",
        description="Process text input",
        parameters={"data": "{{analyze_input.output}}"},
        dependencies=["analyze_input"],
        condition="{{analyze_input.type}} == 'text'"
    ))
    
    builder.add_step(WorkflowStep(
        name="process_image",
        action="process_image",
        description="Process image input",
        parameters={"data": "{{analyze_input.output}}"},
        dependencies=["analyze_input"],
        condition="{{analyze_input.type}} == 'image'"
    ))
    
    builder.add_step(WorkflowStep(
        name="process_video",
        action="process_video",
        description="Process video input",
        parameters={"data": "{{analyze_input.output}}"},
        dependencies=["analyze_input"],
        condition="{{analyze_input.type}} == 'video'"
    ))
    
    # Merge results
    builder.add_step(WorkflowStep(
        name="merge_results",
        action="merge",
        description="Merge processing results",
        parameters={
            "results": [
                "{{process_text.output}}",
                "{{process_image.output}}",
                "{{process_video.output}}"
            ]
        },
        dependencies=["process_text", "process_image", "process_video"]
    ))
    
    workflow = builder.build()
    
    print("\n✓ Dynamic workflow created")
    print("  Features:")
    print("    - Input type detection")
    print("    - Dynamic routing")
    print("    - Conditional execution")
    
    return workflow


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: COMPLEX WORKFLOW")
    print("=" * 60)
    
    create_ci_cd_workflow()
    workflow_with_error_handling()
    dynamic_workflow()
    
    print("\n" + "=" * 60)
    print("✓ Hoàn thành!")
    print("=" * 60)
