"""
Ví Dụ 4: Xử Lý Lỗi (Error Handling)

Ví dụ này minh họa các pattern xử lý lỗi trong Agentic SDLC.

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Chạy: python 04-error-handling.py

Dependencies:
- agentic-sdlc>=3.0.0

Expected Output:
- Các exception được catch và xử lý đúng cách
- Retry logic hoạt động
- Graceful degradation
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()


def handle_configuration_errors():
    """Xử lý lỗi cấu hình."""
    from agentic_sdlc.core.config import Config, ModelConfig
    from agentic_sdlc.core.exceptions import ConfigurationError
    
    print("✓ Ví dụ: Xử lý lỗi cấu hình")
    
    try:
        # Cố gắng tạo config không hợp lệ
        config = Config(
            project_name="",  # Tên rỗng - không hợp lệ
            models={}  # Không có model - không hợp lệ
        )
    except ConfigurationError as e:
        print(f"  ✗ Caught ConfigurationError: {e}")
        print("  ✓ Tạo config hợp lệ thay thế...")
        
        # Tạo config hợp lệ
        config = Config(
            project_name="fallback-project",
            models={
                "default": ModelConfig(
                    provider="openai",
                    model_name="gpt-4",
                    api_key=os.getenv("OPENAI_API_KEY", "dummy-key")
                )
            }
        )
        print(f"  ✓ Fallback config created: {config.project_name}")
    
    return config


def handle_validation_errors():
    """Xử lý lỗi validation."""
    from agentic_sdlc.core.exceptions import ValidationError
    from agentic_sdlc.orchestration.workflow import WorkflowStep
    
    print("\n✓ Ví dụ: Xử lý lỗi validation")
    
    try:
        # Tạo step không hợp lệ (thiếu required fields)
        step = WorkflowStep(
            name="",  # Tên rỗng
            action="",  # Action rỗng
            description="Invalid step"
        )
    except ValidationError as e:
        print(f"  ✗ Caught ValidationError: {e}")
        print("  ✓ Tạo step hợp lệ thay thế...")
        
        # Tạo step hợp lệ
        step = WorkflowStep(
            name="valid-step",
            action="process",
            description="Valid step with all required fields",
            parameters={"input": "data"}
        )
        print(f"  ✓ Valid step created: {step.name}")
    
    return step


def retry_with_exponential_backoff():
    """Retry với exponential backoff."""
    from agentic_sdlc.core.exceptions import AgenticSDLCError
    
    print("\n✓ Ví dụ: Retry với exponential backoff")
    
    max_retries = 3
    base_delay = 1
    
    def unreliable_operation():
        """Operation có thể fail."""
        import random
        if random.random() < 0.7:  # 70% chance to fail
            raise AgenticSDLCError("Temporary failure")
        return "Success!"
    
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt + 1}/{max_retries}...")
            result = unreliable_operation()
            print(f"  ✓ Success: {result}")
            return result
        except AgenticSDLCError as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"  ✗ Failed: {e}")
                print(f"  ⏳ Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"  ✗ All retries exhausted: {e}")
                raise


def graceful_degradation():
    """Graceful degradation khi service không available."""
    from agentic_sdlc.core.exceptions import AgenticSDLCError
    
    print("\n✓ Ví dụ: Graceful degradation")
    
    def primary_service():
        """Primary service (có thể fail)."""
        raise AgenticSDLCError("Primary service unavailable")
    
    def fallback_service():
        """Fallback service."""
        return "Result from fallback service"
    
    try:
        print("  Trying primary service...")
        result = primary_service()
    except AgenticSDLCError as e:
        print(f"  ✗ Primary service failed: {e}")
        print("  ✓ Falling back to secondary service...")
        result = fallback_service()
        print(f"  ✓ Fallback result: {result}")
    
    return result


def handle_agent_errors():
    """Xử lý lỗi từ agent execution."""
    from agentic_sdlc.orchestration.agent import Agent, AgentConfig, Task
    from agentic_sdlc.core.config import ModelConfig
    from agentic_sdlc.core.exceptions import AgenticSDLCError
    
    print("\n✓ Ví dụ: Xử lý lỗi agent execution")
    
    # Tạo agent
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY", "invalid-key")
    )
    
    agent_config = AgentConfig(
        name="error-prone-agent",
        role="developer",
        description="Agent for error handling demo",
        model_config=model_config
    )
    
    agent = Agent(config=agent_config)
    
    # Tạo task
    task = Task(
        id="error-task",
        description="Task that might fail",
        context={}
    )
    
    try:
        print("  Executing task...")
        result = agent.execute(task)
        print(f"  ✓ Task completed: {result.status}")
    except AgenticSDLCError as e:
        print(f"  ✗ Task failed: {e}")
        print("  ✓ Logging error and continuing...")
        # Log error và continue với fallback behavior
        result = None
    
    return result


def context_manager_error_handling():
    """Sử dụng context manager cho error handling."""
    from contextlib import contextmanager
    from agentic_sdlc.core.exceptions import AgenticSDLCError
    
    print("\n✓ Ví dụ: Context manager error handling")
    
    @contextmanager
    def error_handler(operation_name: str):
        """Context manager để handle errors."""
        print(f"  Starting: {operation_name}")
        try:
            yield
            print(f"  ✓ Completed: {operation_name}")
        except AgenticSDLCError as e:
            print(f"  ✗ Error in {operation_name}: {e}")
            print(f"  ✓ Cleaned up after error")
            raise
        finally:
            print(f"  Cleanup: {operation_name}")
    
    # Sử dụng context manager
    with error_handler("database_operation"):
        # Simulate operation
        print("    Performing operation...")
        # Operation succeeds
    
    try:
        with error_handler("failing_operation"):
            print("    Performing operation...")
            raise AgenticSDLCError("Operation failed")
    except AgenticSDLCError:
        print("  ✓ Error was handled properly")


def comprehensive_error_handling():
    """Comprehensive error handling strategy."""
    from agentic_sdlc.core.exceptions import (
        AgenticSDLCError,
        ConfigurationError,
        ValidationError,
        PluginError
    )
    
    print("\n✓ Ví dụ: Comprehensive error handling")
    
    def risky_operation(error_type: str = None):
        """Operation có thể raise nhiều loại errors."""
        if error_type == "config":
            raise ConfigurationError("Configuration is invalid")
        elif error_type == "validation":
            raise ValidationError("Validation failed")
        elif error_type == "plugin":
            raise PluginError("Plugin error occurred")
        elif error_type == "generic":
            raise AgenticSDLCError("Generic error")
        return "Success"
    
    # Handle từng loại error khác nhau
    for error_type in [None, "config", "validation", "plugin", "generic"]:
        try:
            result = risky_operation(error_type)
            print(f"  ✓ Operation succeeded: {result}")
        except ConfigurationError as e:
            print(f"  ✗ ConfigurationError: {e} - Reconfigure and retry")
        except ValidationError as e:
            print(f"  ✗ ValidationError: {e} - Fix input and retry")
        except PluginError as e:
            print(f"  ✗ PluginError: {e} - Disable plugin and continue")
        except AgenticSDLCError as e:
            print(f"  ✗ AgenticSDLCError: {e} - Log and continue")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e} - Critical failure")


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: XỬ LÝ LỖI TRONG AGENTIC SDLC")
    print("=" * 60)
    
    # Các ví dụ error handling
    handle_configuration_errors()
    handle_validation_errors()
    retry_with_exponential_backoff()
    graceful_degradation()
    handle_agent_errors()
    context_manager_error_handling()
    comprehensive_error_handling()
    
    print("\n" + "=" * 60)
    print("✓ Tất cả ví dụ error handling đã hoàn thành!")
    print("=" * 60)
