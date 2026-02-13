"""Document generator for creating markdown documentation files.

This module provides the DocumentGenerator class for generating various types
of documentation including guides, use cases, and API references using Jinja2 templates.
"""

from pathlib import Path
from typing import Dict, Any, List, Type, Callable, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from .models import (
    Document,
    GuideDocument,
    UseCaseDocument,
    APIReferenceDocument,
    DocumentType,
    Category,
    Section,
    CodeBlock,
    Diagram,
    ClassReference,
    FunctionReference,
)
from .translation import TranslationManager


class DocumentGenerator:
    """Generate markdown documentation files.
    
    This class handles the generation of various documentation types using
    Jinja2 templates for consistent formatting and structure.
    """
    
    def __init__(self, output_dir: str, language: str = "vi", 
                 templates_dir: Optional[str] = None):
        """Initialize DocumentGenerator.
        
        Args:
            output_dir: Directory where generated documents will be saved
            language: Language code for documentation (default: "vi")
            templates_dir: Directory containing Jinja2 templates (optional)
        """
        self.output_dir = Path(output_dir)
        self.language = language
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.has_template_loader = templates_dir and Path(templates_dir).exists()
        if self.has_template_loader:
            self.env = Environment(
                loader=FileSystemLoader(templates_dir),
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
        else:
            # Use string templates if no template directory
            self.env = Environment(
                trim_blocks=True,
                lstrip_blocks=True,
                keep_trailing_newline=True
            )
        
        # Add custom filters
        self.env.filters['format_date'] = self._format_date
        self.env.filters['indent_code'] = self._indent_code
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display.
        
        Args:
            date_str: Date string in ISO format
            
        Returns:
            Formatted date string
        """
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%d/%m/%Y")
        except (ValueError, AttributeError):
            return date_str
    
    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """Indent code block.
        
        Args:
            code: Code string to indent
            spaces: Number of spaces for indentation
            
        Returns:
            Indented code string
        """
        indent = " " * spaces
        return "\n".join(indent + line if line.strip() else line 
                        for line in code.split("\n"))
    
    def _get_default_guide_template(self) -> str:
        """Get default guide template string."""
        return """# {{ title }}

**Phiên bản**: {{ version }}  
**Cập nhật lần cuối**: {{ last_updated }}

## Giới Thiệu

{{ description }}

{% if prerequisites %}
## Yêu Cầu Tiên Quyết

{% for prereq in prerequisites %}
- {{ prereq }}
{% endfor %}
{% endif %}

{% if learning_objectives %}
## Mục Tiêu Học Tập

{% for objective in learning_objectives %}
- {{ objective }}
{% endfor %}
{% endif %}

{% for section in sections %}
## {{ section.title }}

{{ section.content }}

{% if section.code_blocks %}
{% for code_block in section.code_blocks %}
{% if code_block.caption %}
**{{ code_block.caption }}**
{% endif %}
```{{ code_block.language }}
{{ code_block.code }}
```
{% endfor %}
{% endif %}

{% if section.diagrams %}
{% for diagram in section.diagrams %}
**{{ diagram.caption }}**

```mermaid
{{ diagram.mermaid_code }}
```
{% endfor %}
{% endif %}

{% if section.subsections %}
{% for subsection in section.subsections %}
### {{ subsection.title }}

{{ subsection.content }}

{% if subsection.code_blocks %}
{% for code_block in subsection.code_blocks %}
{% if code_block.caption %}
**{{ code_block.caption }}**
{% endif %}
```{{ code_block.language }}
{{ code_block.code }}
```
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}

{% if related_guides %}
## Tài Liệu Liên Quan

{% for guide in related_guides %}
- [{{ guide }}]({{ guide }}.md)
{% endfor %}
{% endif %}
"""
    
    def _get_default_use_case_template(self) -> str:
        """Get default use case template string."""
        return """# {{ title }}

**Phiên bản**: {{ version }}  
**Cập nhật lần cuối**: {{ last_updated }}

## Tổng Quan

{{ description }}

## Kịch Bản

{{ scenario }}

## Vấn Đề

{{ problem }}

## Giải Pháp

{{ solution }}

{% if architecture %}
## Kiến Trúc

**{{ architecture.caption }}**

```mermaid
{{ architecture.mermaid_code }}
```
{% endif %}

## Triển Khai

{% for code_block in implementation %}
{% if code_block.caption %}
**{{ code_block.caption }}**
{% endif %}
```{{ code_block.language }}
{{ code_block.code }}
```

{% endfor %}

{% for section in sections %}
## {{ section.title }}

{{ section.content }}

{% if section.code_blocks %}
{% for code_block in section.code_blocks %}
{% if code_block.caption %}
**{{ code_block.caption }}**
{% endif %}
```{{ code_block.language }}
{{ code_block.code }}
```
{% endfor %}
{% endif %}
{% endfor %}

{% if results %}
## Kết Quả

{{ results }}
{% endif %}

{% if lessons_learned %}
## Bài Học Kinh Nghiệm

{% for lesson in lessons_learned %}
- {{ lesson }}
{% endfor %}
{% endif %}
"""
    
    def _get_default_api_reference_template(self) -> str:
        """Get default API reference template string."""
        return """# {{ title }}

**Phiên bản**: {{ version }}  
**Cập nhật lần cuối**: {{ last_updated }}

## Tổng Quan Module

**Module**: `{{ module_path }}`

{{ description }}

{% if classes %}
## Classes

{% for class_ref in classes %}
### {{ class_ref.name }}

{{ class_ref.description }}

#### Constructor

**Signature**: `{{ class_ref.constructor.signature }}`

{{ class_ref.constructor.description }}

{% if class_ref.constructor.parameters %}
**Parameters**:
{% for param in class_ref.constructor.parameters %}
- `{{ param.name }}` ({{ param.type }}{% if not param.required %}, optional{% endif %}): {{ param.description }}{% if param.default is not none %} (default: {{ param.default }}){% endif %}
{% endfor %}
{% endif %}

{% if class_ref.methods %}
#### Methods

{% for method in class_ref.methods %}
##### {{ method.name }}

**Signature**: `{{ method.signature }}`

{{ method.description }}

{% if method.parameters %}
**Parameters**:
{% for param in method.parameters %}
- `{{ param.name }}` ({{ param.type }}{% if not param.required %}, optional{% endif %}): {{ param.description }}{% if param.default is not none %} (default: {{ param.default }}){% endif %}
{% endfor %}
{% endif %}

**Returns**: {{ method.returns.type }} - {{ method.returns.description }}

{% if method.raises %}
**Raises**:
{% for exception in method.raises %}
- {{ exception }}
{% endfor %}
{% endif %}

{% if method.examples %}
**Examples**:
{% for example in method.examples %}
```{{ example.language }}
{{ example.code }}
```
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}

{% if class_ref.properties %}
#### Properties

{% for prop in class_ref.properties %}
- `{{ prop.name }}` ({{ prop.type }}{% if prop.readonly %}, read-only{% endif %}): {{ prop.description }}
{% endfor %}
{% endif %}

{% if class_ref.examples %}
#### Usage Examples

{% for example in class_ref.examples %}
{% if example.caption %}
**{{ example.caption }}**
{% endif %}
```{{ example.language }}
{{ example.code }}
```
{% endfor %}
{% endif %}

---
{% endfor %}
{% endif %}

{% if functions %}
## Functions

{% for func in functions %}
### {{ func.name }}

**Signature**: `{{ func.signature }}`

{{ func.description }}

{% if func.parameters %}
**Parameters**:
{% for param in func.parameters %}
- `{{ param.name }}` ({{ param.type }}{% if not param.required %}, optional{% endif %}): {{ param.description }}{% if param.default is not none %} (default: {{ param.default }}){% endif %}
{% endfor %}
{% endif %}

**Returns**: {{ func.returns.type }} - {{ func.returns.description }}

{% if func.raises %}
**Raises**:
{% for exception in func.raises %}
- {{ exception }}
{% endfor %}
{% endif %}

{% if func.examples %}
**Examples**:
{% for example in func.examples %}
```{{ example.language }}
{{ example.code }}
```
{% endfor %}
{% endif %}

---
{% endfor %}
{% endif %}

{% if constants %}
## Constants

{% for const in constants %}
- `{{ const.name }}` ({{ const.type }}): {{ const.description }} = `{{ const.value }}`
{% endfor %}
{% endif %}
"""
    
    def generate_guide(
        self,
        topic: str,
        content: Dict[str, Any],
        template: str = "guide"
    ) -> Path:
        """Generate a guide document.
        
        Args:
            topic: Topic name (e.g., "agents", "workflows")
            content: Content dictionary with document data
            template: Template name to use (default: "guide")
            
        Returns:
            Path to generated document
            
        Raises:
            ValueError: If required content fields are missing
        """
        # Validate required fields
        if 'title' not in content:
            raise ValueError("Content must include 'title' field")
        if 'description' not in content:
            raise ValueError("Content must include 'description' field")
        if 'sections' not in content:
            raise ValueError("Content must include 'sections' field")
        
        # Add metadata
        if 'version' not in content:
            content['version'] = '3.0.0'
        if 'last_updated' not in content:
            content['last_updated'] = datetime.now().isoformat()
        
        # Try to load custom template, fall back to default
        if self.has_template_loader:
            try:
                tmpl = self.env.get_template(f"{template}_template.md.j2")
            except TemplateNotFound:
                tmpl = self.env.from_string(self._get_default_guide_template())
        else:
            tmpl = self.env.from_string(self._get_default_guide_template())
        
        # Render template
        rendered = tmpl.render(**content)
        
        # Write to file
        output_path = self.output_dir / f"{topic}.md"
        output_path.write_text(rendered, encoding='utf-8')
        
        return output_path
    
    def generate_use_case(
        self,
        name: str,
        description: str,
        code_examples: List[CodeBlock],
        diagrams: List[Diagram],
        **kwargs
    ) -> Path:
        """Generate a use case document.
        
        Args:
            name: Use case name
            description: Use case description
            code_examples: List of code examples
            diagrams: List of diagrams
            **kwargs: Additional fields (scenario, problem, solution, etc.)
            
        Returns:
            Path to generated document
        """
        content = {
            'title': name,
            'description': description,
            'version': kwargs.get('version', '3.0.0'),
            'last_updated': kwargs.get('last_updated', datetime.now().isoformat()),
            'scenario': kwargs.get('scenario', ''),
            'problem': kwargs.get('problem', ''),
            'solution': kwargs.get('solution', ''),
            'architecture': diagrams[0] if diagrams else None,
            'implementation': code_examples,
            'results': kwargs.get('results', ''),
            'lessons_learned': kwargs.get('lessons_learned', []),
            'sections': kwargs.get('sections', []),
        }
        
        # Try to load custom template, fall back to default
        if self.has_template_loader:
            try:
                tmpl = self.env.get_template("use_case_template.md.j2")
            except TemplateNotFound:
                tmpl = self.env.from_string(self._get_default_use_case_template())
        else:
            tmpl = self.env.from_string(self._get_default_use_case_template())
        
        # Render template
        rendered = tmpl.render(**content)
        
        # Write to file
        output_path = self.output_dir / f"{name}.md"
        output_path.write_text(rendered, encoding='utf-8')
        
        return output_path
    
    def generate_api_reference(
        self,
        module: str,
        classes: List[ClassReference],
        functions: List[FunctionReference],
        **kwargs
    ) -> Path:
        """Generate API reference documentation.
        
        Args:
            module: Module path (e.g., "agentic_sdlc.core.config")
            classes: List of class references
            functions: List of function references
            **kwargs: Additional fields (constants, description, etc.)
            
        Returns:
            Path to generated document
        """
        # Extract module name for filename
        module_name = module.split('.')[-1]
        
        content = {
            'title': f"API Reference: {module_name}",
            'module_path': module,
            'description': kwargs.get('description', f'API reference for {module}'),
            'version': kwargs.get('version', '3.0.0'),
            'last_updated': kwargs.get('last_updated', datetime.now().isoformat()),
            'classes': classes,
            'functions': functions,
            'constants': kwargs.get('constants', []),
            'sections': kwargs.get('sections', []),
        }
        
        # Try to load custom template, fall back to default
        if self.has_template_loader:
            try:
                tmpl = self.env.get_template("api_reference_template.md.j2")
            except TemplateNotFound:
                tmpl = self.env.from_string(self._get_default_api_reference_template())
        else:
            tmpl = self.env.from_string(self._get_default_api_reference_template())
        
        # Render template
        rendered = tmpl.render(**content)
        
        # Write to file
        output_path = self.output_dir / f"{module_name}.md"
        output_path.write_text(rendered, encoding='utf-8')
        
        return output_path
