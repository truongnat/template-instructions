"""
Ví Dụ 3: Workflow Cơ Bản (Basic Workflow)

Ví dụ này minh họa cách tạo và thực thi một workflow đơn giản.

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Cấu hình API key trong .env
3. Chạy: python 03-basic-workflow.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Workflow được tạo với các steps
- Workflow thực thi tuần tự
- Kết quả từ mỗi step
"""

import os
from dotenv import load_dotenv

load_dotenv()


def create_sequential_workflow():
    """Tạo workflow tuần tự đơn giản."""
    from agentic_sdlc.orchestration.workflow import Workflow, WorkflowStep, WorkflowBuilder
    
    # Tạo workflow builder
    builder = WorkflowBuilder(name="simple-workflow")
    
    # Thêm các steps tuần tự
    builder.add_step(
        WorkflowStep(
            name="step1",
            action="analyze",
            description="Phân tích requirements",
            parameters={"input": "User story: Tạo API endpoint"}
        )
    )
    
    builder.add_step(
        WorkflowStep(
            name="step2",
            action="design",
            description="Thiết kế solution",
            parameters={"requirements": "{{step1.output}}"},
            dependencies=["step1"]
        )
    )
    
    builder.add_step(
        WorkflowStep(
            name="step3",
            action="implement",
            description="Implement code",
            parameters={"design": "{{step2.output}}"},
            dependencies=["step2"]
        )
    )
    
    # Build workflow
    workflow = builder.build()
    
    print("✓ Sequential workflow đã được tạo")
    print(f"  Name: {workflow.name}")
    print(f"  Steps: {len(workflow.steps)}")
    for step in workflow.steps:
        print(f"    - {step.name}: {step.description}")
    
    return workflow


def create_parallel_workflow():
    """Tạo workflow với các steps song song."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="parallel-workflow")
    
    # Step đầu tiên
    builder.add_step(
        WorkflowStep(
            name="prepare",
            action="prepare",
            description="Chuẩn bị dữ liệu",
            parameters={"source": "database"}
        )
    )
    
    # Các steps song song (không có dependencies lẫn nhau)
    builder.add_step(
        WorkflowStep(
            name="process_a",
            action="process",
            description="Xử lý dữ liệu A",
            parameters={"data": "{{prepare.output}}", "type": "A"},
            dependencies=["prepare"]
        )
    )
    
    builder.add_step(
        WorkflowStep(
            name="process_b",
            action="process",
            description="Xử lý dữ liệu B",
            parameters={"data": "{{prepare.output}}", "type": "B"},
            dependencies=["prepare"]
        )
    )
    
    builder.add_step(
        WorkflowStep(
            name="process_c",
            action="process",
            description="Xử lý dữ liệu C",
            parameters={"data": "{{prepare.output}}", "type": "C"},
            dependencies=["prepare"]
        )
    )
    
    # Step cuối cùng merge kết quả
    builder.add_step(
        WorkflowStep(
            name="merge",
            action="merge",
            description="Merge kết quả",
            parameters={
                "results": [
                    "{{process_a.output}}",
                    "{{process_b.output}}",
                    "{{process_c.output}}"
                ]
            },
            dependencies=["process_a", "process_b", "process_c"]
        )
    )
    
    workflow = builder.build()
    
    print("\n✓ Parallel workflow đã được tạo")
    print(f"  Name: {workflow.name}")
    print(f"  Steps: {len(workflow.steps)}")
    print("  Execution plan:")
    print("    1. prepare")
    print("    2. process_a, process_b, process_c (parallel)")
    print("    3. merge")
    
    return workflow


def execute_workflow():
    """Thực thi workflow."""
    from agentic_sdlc.orchestration.workflow import WorkflowRunner, WorkflowBuilder, WorkflowStep
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig
    from agentic_sdlc.core.config import ModelConfig
    
    # Tạo workflow đơn giản
    builder = WorkflowBuilder(name="execution-example")
    
    builder.add_step(
        WorkflowStep(
            name="greet",
            action="greet",
            description="Chào mừng",
            parameters={"message": "Hello from workflow!"}
        )
    )
    
    builder.add_step(
        WorkflowStep(
            name="process",
            action="process",
            description="Xử lý",
            parameters={"input": "{{greet.output}}"},
            dependencies=["greet"]
        )
    )
    
    workflow = builder.build()
    
    # Tạo agent để thực thi workflow
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    agent_config = AgentConfig(
        name="workflow-agent",
        role="orchestrator",
        description="Agent thực thi workflow",
        model_config=model_config
    )
    
    agent = Agent(config=agent_config)
    
    # Tạo runner và thực thi
    runner = WorkflowRunner(workflow=workflow, agent=agent)
    
    print("\n✓ Đang thực thi workflow...")
    result = runner.run()
    
    print("\n✓ Workflow hoàn thành!")
    print(f"  Status: {result.status}")
    print(f"  Steps executed: {len(result.step_results)}")
    
    return result


def workflow_with_conditions():
    """Tạo workflow với conditional execution."""
    from agentic_sdlc.orchestration.workflow import WorkflowBuilder, WorkflowStep
    
    builder = WorkflowBuilder(name="conditional-workflow")
    
    # Step kiểm tra điều kiện
    builder.add_step(
        WorkflowStep(
            name="check",
            action="check",
            description="Kiểm tra điều kiện",
            parameters={"condition": "value > 10"}
        )
    )
    
    # Step thực thi nếu điều kiện đúng
    builder.add_step(
        WorkflowStep(
            name="process_if_true",
            action="process",
            description="Xử lý khi điều kiện đúng",
            parameters={"data": "{{check.output}}"},
            dependencies=["check"],
            condition="{{check.result}} == true"
        )
    )
    
    # Step thực thi nếu điều kiện sai
    builder.add_step(
        WorkflowStep(
            name="process_if_false",
            action="process",
            description="Xử lý khi điều kiện sai",
            parameters={"data": "{{check.output}}"},
            dependencies=["check"],
            condition="{{check.result}} == false"
        )
    )
    
    workflow = builder.build()
    
    print("\n✓ Conditional workflow đã được tạo")
    print(f"  Name: {workflow.name}")
    print("  Logic: if-then-else based on check result")
    
    return workflow


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: WORKFLOW CƠ BẢN")
    print("=" * 60)
    
    # Tạo sequential workflow
    create_sequential_workflow()
    
    # Tạo parallel workflow
    create_parallel_workflow()
    
    # Thực thi workflow
    execute_workflow()
    
    # Workflow với conditions
    workflow_with_conditions()
    
    print("\n" + "=" * 60)
    print("✓ Tất cả ví dụ workflow đã hoàn thành!")
    print("=" * 60)
