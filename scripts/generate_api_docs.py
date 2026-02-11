#!/usr/bin/env python3
"""Script to generate API reference documentation.

This script scans the agentic_sdlc source code and generates comprehensive
API reference documentation in Vietnamese for all public modules.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_sdlc.documentation.api_reference import APIReferenceGenerator
from agentic_sdlc.documentation.models import (
    APIReferenceDocument,
    ClassReference,
    FunctionReference,
    ConstantReference,
    MethodReference,
    PropertyReference,
    Parameter,
    CodeBlock
)


def format_parameter(param: Parameter) -> str:
    """Format a parameter for markdown."""
    param_str = f"- `{param.name}` ({param.type})"
    if not param.required and param.default is not None:
        param_str += f", mặc định: `{param.default}`"
    param_str += f": {param.description}"
    return param_str


def format_method(method: MethodReference, level: int = 3) -> str:
    """Format a method for markdown."""
    heading = "#" * level
    lines = [
        f"{heading} `{method.name}`",
        "",
        f"**Chữ ký (Signature):**",
        "",
        f"```python",
        method.signature,
        "```",
        "",
        f"**Mô tả:**",
        "",
        method.description or f"Method {method.name}",
        ""
    ]
    
    if method.parameters:
        lines.extend([
            "**Tham số (Parameters):**",
            ""
        ])
        for param in method.parameters:
            lines.append(format_parameter(param))
        lines.append("")
    
    lines.extend([
        "**Giá trị trả về (Returns):**",
        "",
        f"- `{method.returns.type}`: {method.returns.description}",
        ""
    ])
    
    if method.raises:
        lines.extend([
            "**Ngoại lệ (Raises):**",
            ""
        ])
        for exc in method.raises:
            lines.append(f"- `{exc}`")
        lines.append("")
    
    if method.examples:
        lines.extend([
            "**Ví dụ:**",
            ""
        ])
        for example in method.examples:
            lines.extend([
                f"```{example.language}",
                example.code.strip(),
                "```",
                ""
            ])
    
    return "\n".join(lines)


def format_property(prop: PropertyReference) -> str:
    """Format a property for markdown."""
    readonly_str = " (chỉ đọc)" if prop.readonly else ""
    return f"- `{prop.name}` ({prop.type}){readonly_str}: {prop.description}"


def format_class(cls: ClassReference) -> str:
    """Format a class for markdown."""
    lines = [
        f"## Class `{cls.name}`",
        "",
        "**Mô tả:**",
        "",
        cls.description or f"Class {cls.name}",
        ""
    ]
    
    # Constructor
    lines.extend([
        "### Constructor",
        "",
        format_method(cls.constructor, level=4)
    ])
    
    # Properties
    if cls.properties:
        lines.extend([
            "### Properties",
            ""
        ])
        for prop in cls.properties:
            lines.append(format_property(prop))
        lines.append("")
    
    # Methods
    if cls.methods:
        lines.extend([
            "### Methods",
            ""
        ])
        for method in cls.methods:
            lines.append(format_method(method, level=4))
    
    # Examples
    if cls.examples:
        lines.extend([
            "### Ví dụ sử dụng",
            ""
        ])
        for example in cls.examples:
            if example.caption:
                lines.append(f"**{example.caption}**")
                lines.append("")
            lines.extend([
                f"```{example.language}",
                example.code.strip(),
                "```",
                ""
            ])
    
    return "\n".join(lines)


def format_function(func: FunctionReference) -> str:
    """Format a function for markdown."""
    lines = [
        f"## Function `{func.name}`",
        "",
        f"**Chữ ký (Signature):**",
        "",
        f"```python",
        func.signature,
        "```",
        "",
        f"**Mô tả:**",
        "",
        func.description or f"Function {func.name}",
        ""
    ]
    
    if func.parameters:
        lines.extend([
            "**Tham số (Parameters):**",
            ""
        ])
        for param in func.parameters:
            lines.append(format_parameter(param))
        lines.append("")
    
    lines.extend([
        "**Giá trị trả về (Returns):**",
        "",
        f"- `{func.returns.type}`: {func.returns.description}",
        ""
    ])
    
    if func.raises:
        lines.extend([
            "**Ngoại lệ (Raises):**",
            ""
        ])
        for exc in func.raises:
            lines.append(f"- `{exc}`")
        lines.append("")
    
    if func.examples:
        lines.extend([
            "**Ví dụ:**",
            ""
        ])
        for example in func.examples:
            lines.extend([
                f"```{example.language}",
                example.code.strip(),
                "```",
                ""
            ])
    
    return "\n".join(lines)


def format_constant(const: ConstantReference) -> str:
    """Format a constant for markdown."""
    return f"- `{const.name}` ({const.type}): {const.description}\n  - Giá trị: `{const.value}`"


def generate_api_doc_markdown(doc: APIReferenceDocument) -> str:
    """Generate markdown content from APIReferenceDocument."""
    lines = [
        f"# {doc.title}",
        "",
        f"**Module:** `{doc.module_path}`",
        "",
        f"**Phiên bản:** {doc.version}",
        "",
        f"**Cập nhật lần cuối:** {doc.last_updated}",
        "",
        "---",
        ""
    ]
    
    # Module overview
    if doc.sections:
        for section in doc.sections:
            if section.title == "Tổng Quan Module":
                lines.extend([
                    "## Tổng Quan",
                    "",
                    section.content,
                    "",
                    "---",
                    ""
                ])
    
    # Classes
    if doc.classes:
        lines.extend([
            "## Classes",
            ""
        ])
        for cls in doc.classes:
            lines.append(format_class(cls))
            lines.append("---")
            lines.append("")
    
    # Functions
    if doc.functions:
        lines.extend([
            "## Functions",
            ""
        ])
        for func in doc.functions:
            lines.append(format_function(func))
            lines.append("---")
            lines.append("")
    
    # Constants
    if doc.constants:
        lines.extend([
            "## Constants",
            ""
        ])
        for const in doc.constants:
            lines.append(format_constant(const))
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Generate all API reference documentation."""
    # Initialize generator
    generator = APIReferenceGenerator(
        source_dir="src/agentic_sdlc",
        glossary_file="docs/vi/glossary.yaml"
    )
    
    # Define modules to document
    modules_to_document = {
        "core": [
            "agentic_sdlc.core.config",
            "agentic_sdlc.core.exceptions",
            "agentic_sdlc.core.logging",
        ],
        "infrastructure": [
            "agentic_sdlc.infrastructure.engine.execution_engine",
            "agentic_sdlc.infrastructure.lifecycle.lifecycle",
        ],
        "intelligence": [
            "agentic_sdlc.intelligence.learning.learner",
            "agentic_sdlc.intelligence.monitoring.monitor",
            "agentic_sdlc.intelligence.reasoning.reasoner",
            "agentic_sdlc.intelligence.collaboration.collaborator",
        ],
        "orchestration": [
            "agentic_sdlc.orchestration.agents.agent",
            "agentic_sdlc.orchestration.workflows.workflow",
            "agentic_sdlc.orchestration.models.client",
        ],
        "plugins": [
            "agentic_sdlc.plugins.base",
            "agentic_sdlc.plugins.registry",
        ]
    }
    
    # Create output directory
    output_dir = Path("docs/vi/api-reference")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate documentation for each category
    for category, modules in modules_to_document.items():
        category_dir = output_dir / category
        category_dir.mkdir(exist_ok=True)
        
        print(f"\nGenerating {category} documentation...")
        
        for module_path in modules:
            try:
                print(f"  - {module_path}")
                
                # Generate API reference document
                api_doc = generator.generate_module_docs(module_path)
                
                # Convert to markdown
                markdown_content = generate_api_doc_markdown(api_doc)
                
                # Determine output filename
                module_name = module_path.split(".")[-1]
                output_file = category_dir / f"{module_name}.md"
                
                # Write to file
                output_file.write_text(markdown_content, encoding="utf-8")
                
                print(f"    ✓ Generated {output_file}")
                
            except Exception as e:
                print(f"    ✗ Error generating {module_path}: {e}")
                import traceback
                traceback.print_exc()
    
    # Generate README for api-reference
    readme_content = """# API Reference

Tài liệu tham khảo API đầy đủ cho Agentic SDLC v3.0.0.

## Cấu Trúc

### Core
Các module cốt lõi của hệ thống:
- [config.md](core/config.md) - Quản lý cấu hình
- [exceptions.md](core/exceptions.md) - Các exception types
- [logging.md](core/logging.md) - Hệ thống logging

### Infrastructure
Các module hạ tầng:
- [execution_engine.md](infrastructure/execution_engine.md) - Task execution engine
- [lifecycle.md](infrastructure/lifecycle.md) - Lifecycle management

### Intelligence
Các module trí tuệ nhân tạo:
- [learner.md](intelligence/learner.md) - Learning và knowledge management
- [monitor.md](intelligence/monitor.md) - Monitoring và metrics
- [reasoner.md](intelligence/reasoner.md) - Reasoning và decision making
- [collaborator.md](intelligence/collaborator.md) - Team collaboration

### Orchestration
Các module điều phối:
- [agent.md](orchestration/agent.md) - Agent management
- [workflow.md](orchestration/workflow.md) - Workflow definition
- [client.md](orchestration/client.md) - Model client integration

### Plugins
Hệ thống plugin:
- [base.md](plugins/base.md) - Plugin base class
- [registry.md](plugins/registry.md) - Plugin registry

## Quy Ước

### Type Hints
Tất cả các API đều có type hints đầy đủ để hỗ trợ IDE autocomplete và type checking.

### Docstrings
Mỗi class, method, và function đều có docstring mô tả chức năng, parameters, và return values.

### Examples
Mỗi API reference đều bao gồm ví dụ sử dụng cơ bản.

## Xem Thêm

- [Hướng dẫn cài đặt](../getting-started/installation.md)
- [Hướng dẫn cấu hình](../getting-started/configuration.md)
- [Use Cases](../use-cases/README.md)
- [Examples](../examples/README.md)
"""
    
    readme_file = output_dir / "README.md"
    readme_file.write_text(readme_content, encoding="utf-8")
    print(f"\n✓ Generated {readme_file}")
    
    print("\n✅ API reference documentation generation complete!")


if __name__ == "__main__":
    main()
