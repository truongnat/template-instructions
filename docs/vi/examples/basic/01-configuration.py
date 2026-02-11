"""
Ví Dụ 1: Cấu Hình Hệ Thống (System Configuration)

Ví dụ này minh họa cách cấu hình Agentic SDLC với các LLM providers khác nhau.

Setup Instructions:
1. Cài đặt: pip install agentic-sdlc
2. Tạo file .env với API keys
3. Chạy: python 01-configuration.py

Dependencies:
- agentic-sdlc>=3.0.0
- python-dotenv

Expected Output:
- Hiển thị cấu hình đã load
- Xác nhận kết nối với LLM provider
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def example_basic_configuration():
    """Ví dụ cấu hình cơ bản với OpenAI."""
    from agentic_sdlc.core.config import Config, ModelConfig
    
    # Tạo cấu hình cơ bản
    config = Config(
        project_name="my-project",
        log_level="INFO",
        models={
            "default": ModelConfig(
                provider="openai",
                model_name="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.7,
                max_tokens=2000
            )
        }
    )
    
    print("✓ Cấu hình cơ bản đã được tạo")
    print(f"  Project: {config.project_name}")
    print(f"  Log Level: {config.log_level}")
    print(f"  Default Model: {config.models['default'].model_name}")
    
    return config


def example_multiple_providers():
    """Ví dụ cấu hình nhiều LLM providers."""
    from agentic_sdlc.core.config import Config, ModelConfig
    
    config = Config(
        project_name="multi-provider-project",
        models={
            "openai": ModelConfig(
                provider="openai",
                model_name="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            "anthropic": ModelConfig(
                provider="anthropic",
                model_name="claude-3-opus-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            ),
            "ollama": ModelConfig(
                provider="ollama",
                model_name="llama2",
                base_url="http://localhost:11434"
            )
        }
    )
    
    print("\n✓ Cấu hình multi-provider đã được tạo")
    for name, model_config in config.models.items():
        print(f"  {name}: {model_config.provider}/{model_config.model_name}")
    
    return config


def example_load_from_file():
    """Ví dụ load cấu hình từ file YAML."""
    from agentic_sdlc.core.config import Config
    
    # Tạo file config mẫu
    config_content = """
project_name: example-project
log_level: DEBUG

models:
  default:
    provider: openai
    model_name: gpt-4
    temperature: 0.7
    max_tokens: 2000
  
  fast:
    provider: openai
    model_name: gpt-3.5-turbo
    temperature: 0.5
    max_tokens: 1000
"""
    
    config_path = Path("config.yaml")
    config_path.write_text(config_content)
    
    # Load từ file
    config = Config.from_yaml(str(config_path))
    
    print("\n✓ Cấu hình đã được load từ file")
    print(f"  File: {config_path}")
    print(f"  Project: {config.project_name}")
    print(f"  Models: {list(config.models.keys())}")
    
    # Cleanup
    config_path.unlink()
    
    return config


def example_environment_variables():
    """Ví dụ cấu hình từ environment variables."""
    from agentic_sdlc.core.config import Config, ModelConfig
    
    # Set environment variables
    os.environ["AGENTIC_PROJECT_NAME"] = "env-project"
    os.environ["AGENTIC_LOG_LEVEL"] = "WARNING"
    
    config = Config(
        project_name=os.getenv("AGENTIC_PROJECT_NAME", "default-project"),
        log_level=os.getenv("AGENTIC_LOG_LEVEL", "INFO"),
        models={
            "default": ModelConfig(
                provider="openai",
                model_name=os.getenv("AGENTIC_MODEL_NAME", "gpt-4"),
                api_key=os.getenv("OPENAI_API_KEY")
            )
        }
    )
    
    print("\n✓ Cấu hình từ environment variables")
    print(f"  Project: {config.project_name}")
    print(f"  Log Level: {config.log_level}")
    
    return config


if __name__ == "__main__":
    print("=" * 60)
    print("VÍ DỤ: CẤU HÌNH HỆ THỐNG AGENTIC SDLC")
    print("=" * 60)
    
    # Chạy các ví dụ
    example_basic_configuration()
    example_multiple_providers()
    example_load_from_file()
    example_environment_variables()
    
    print("\n" + "=" * 60)
    print("✓ Tất cả ví dụ cấu hình đã hoàn thành!")
    print("=" * 60)
