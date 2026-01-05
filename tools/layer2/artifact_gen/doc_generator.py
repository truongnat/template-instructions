"""
Document Generator - Automated documentation creation.

Part of Layer 2: Intelligence Layer.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DocGenerator:
    """
    Generates documentation from code and context.
    
    Features:
    - Auto-generate README files
    - Create API documentation
    - Generate usage guides
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("docs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_readme(
        self,
        title: str,
        description: str,
        sections: Optional[Dict[str, str]] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a README.md file.
        
        Args:
            title: Document title
            description: Project/module description
            sections: Additional sections {name: content}
            output_file: Optional output filename
            
        Returns:
            Generated markdown content
        """
        content = f"# {title}\n\n{description}\n\n"
        
        if sections:
            for section_name, section_content in sections.items():
                content += f"## {section_name}\n\n{section_content}\n\n"
        
        content += f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        
        if output_file:
            output_path = self.output_dir / output_file
            output_path.write_text(content, encoding='utf-8')
        
        return content

    def generate_api_doc(
        self,
        module_name: str,
        functions: List[Dict],
        classes: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate API documentation.
        
        Args:
            module_name: Name of the module
            functions: List of function definitions
            classes: Optional list of class definitions
            
        Returns:
            Generated markdown content
        """
        content = f"# {module_name} API Reference\n\n"
        
        if functions:
            content += "## Functions\n\n"
            for func in functions:
                content += f"### `{func['name']}`\n\n"
                content += f"{func.get('description', 'No description')}\n\n"
                
                if func.get('params'):
                    content += "**Parameters:**\n"
                    for param in func['params']:
                        content += f"- `{param['name']}`: {param.get('type', 'any')} - {param.get('description', '')}\n"
                    content += "\n"
                
                if func.get('returns'):
                    content += f"**Returns:** {func['returns']}\n\n"
        
        if classes:
            content += "## Classes\n\n"
            for cls in classes:
                content += f"### `{cls['name']}`\n\n"
                content += f"{cls.get('description', 'No description')}\n\n"
        
        return content

    def generate_from_file(self, source_file: Path) -> str:
        """
        Generate documentation from a Python file.
        """
        if not source_file.exists():
            return ""
        
        content = source_file.read_text(encoding='utf-8')
        
        # Extract docstring
        doc_start = content.find('"""')
        if doc_start != -1:
            doc_end = content.find('"""', doc_start + 3)
            if doc_end != -1:
                docstring = content[doc_start+3:doc_end].strip()
                return self.generate_readme(
                    title=source_file.stem,
                    description=docstring
                )
        
        return self.generate_readme(
            title=source_file.stem,
            description=f"Documentation for {source_file.name}"
        )


class ReportGenerator:
    """
    Generates various report types.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("docs/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_summary_report(
        self,
        title: str,
        sections: Dict[str, any],
        output_file: Optional[str] = None
    ) -> str:
        """Generate a summary report."""
        content = f"# {title}\n\n"
        content += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        for section_name, section_data in sections.items():
            content += f"## {section_name}\n\n"
            
            if isinstance(section_data, str):
                content += f"{section_data}\n\n"
            elif isinstance(section_data, list):
                for item in section_data:
                    content += f"- {item}\n"
                content += "\n"
            elif isinstance(section_data, dict):
                for key, value in section_data.items():
                    content += f"- **{key}**: {value}\n"
                content += "\n"
        
        if output_file:
            output_path = self.output_dir / output_file
            output_path.write_text(content, encoding='utf-8')
        
        return content

    def generate_status_report(
        self,
        project_name: str,
        status: str,
        metrics: Dict,
        issues: Optional[List[str]] = None
    ) -> str:
        """Generate a status report."""
        sections = {
            "Status": status,
            "Metrics": metrics
        }
        
        if issues:
            sections["Issues"] = issues
        
        return self.generate_summary_report(
            title=f"{project_name} Status Report",
            sections=sections
        )


class TemplateEngine:
    """
    Template processing engine.
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(".agent/templates")
        self.template_cache: Dict[str, str] = {}

    def load_template(self, template_name: str) -> Optional[str]:
        """Load a template by name."""
        if template_name in self.template_cache:
            return self.template_cache[template_name]
        
        template_path = self.templates_dir / template_name
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            self.template_cache[template_name] = content
            return content
        
        return None

    def render(self, template: str, variables: Dict) -> str:
        """
        Render a template with variables.
        
        Uses simple {{variable}} syntax.
        """
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    def render_template(self, template_name: str, variables: Dict) -> Optional[str]:
        """Load and render a template."""
        template = self.load_template(template_name)
        if template:
            return self.render(template, variables)
        return None

    def list_templates(self) -> List[str]:
        """List available templates."""
        if self.templates_dir.exists():
            return [f.name for f in self.templates_dir.glob("*.md")]
        return []


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Artifact Generator - Layer 2 Intelligence")
    parser.add_argument("--generate-readme", type=str, help="Generate README with title")
    parser.add_argument("--description", type=str, help="Description for README")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    
    args = parser.parse_args()
    
    if args.generate_readme:
        doc_gen = DocGenerator()
        content = doc_gen.generate_readme(
            title=args.generate_readme,
            description=args.description or "Auto-generated documentation"
        )
        print(content)
    
    elif args.list_templates:
        engine = TemplateEngine()
        for template in engine.list_templates():
            print(f"- {template}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
