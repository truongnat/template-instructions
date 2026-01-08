"""
Artifact Generator - automated document creation.

Part of Layer 2: Intelligence Layer.
Consolidates DocGenerator, ReportGenerator, and TemplateEngine.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TemplateEngine:
    """
    Template processing engine.
    """

    def __init__(self, templates_dir: Optional[Path] = None):
        # Allow default to be overridden, but default to .agent/templates relative to project root
        if templates_dir:
            self.templates_dir = templates_dir
        else:
            # Assuming we are in tools/intelligence/artifact_gen/
            self.templates_dir = Path(__file__).resolve().parent.parent.parent.parent / ".agent" / "templates"
            
        self.template_cache: Dict[str, str] = {}

    def load_template(self, template_name: str) -> Optional[str]:
        """Load a template by name (with or without .md extension)."""
        if not template_name.endswith(".md"):
             template_name += ".md"
             
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
            # Handle list values for simple bullet points
            if isinstance(value, list):
                list_str = "\n".join([f"- {item}" for item in value])
                result = result.replace(placeholder, list_str)
            else:
                result = result.replace(placeholder, str(value))
        return result


class ArtifactGenerator:
    """
    Generates artifacts from templates and context.
    
    Features:
    - Generate documents from templates
    - Auto-fill from context
    - Validate against rules
    - Version control artifacts
    """

    def __init__(self, output_dir: Optional[Path] = None, templates_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("docs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_engine = TemplateEngine(templates_dir)

    def generate_from_template(
        self, 
        template_name: str, 
        context: Dict, 
        output_subpath: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate a document from a template.
        
        Args:
            template_name: Name of template (e.g., 'project-plan')
            context: Variables to fill in template
            output_subpath: Subdirectory in docs/ (e.g., 'planning')
            output_filename: Optional filename (defaults to generated name)
            
        Returns:
            Path to generated file
        """
        template_content = self.template_engine.load_template(template_name)
        if not template_content:
            raise ValueError(f"Template not found: {template_name}")
            
        content = self.template_engine.render(template_content, context)
        
        # Determine output path
        target_dir = self.output_dir
        if output_subpath:
            target_dir = target_dir / output_subpath
        target_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        if not output_filename:
            # Try to generate filename from context or template
            name_slug = template_name.replace(".md", "")
            output_filename = f"{timestamp}-{name_slug}.md"
            
        output_path = target_dir / output_filename
        output_path.write_text(content, encoding='utf-8')
        
        return str(output_path)

    def generate_readme(
        self,
        title: str,
        description: str,
        sections: Optional[Dict[str, str]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Generate a generic README."""
        content = f"# {title}\n\n{description}\n\n"
        
        if sections:
            for section_name, section_content in sections.items():
                content += f"## {section_name}\n\n{section_content}\n\n"
        
        content += f"\n---\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"
        
        if output_path:
            Path(output_path).write_text(content, encoding='utf-8')
            return output_path
            
        return content


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Artifact Generator - Layer 2 Intelligence")
    parser.add_argument("--template", type=str, help="Template to use")
    parser.add_argument("--context", type=str, help="JSON context string")
    parser.add_argument("--output", type=str, help="Output filename")
    parser.add_argument("--list-templates", action="store_true", help="List available templates")
    
    args = parser.parse_args()
    generator = ArtifactGenerator()
    
    if args.template and args.context:
        try:
            context = json.loads(args.context)
            path = generator.generate_from_template(args.template, context, output_filename=args.output)
            print(f"✅ Generated artifact: {path}")
        except json.JSONDecodeError:
            print("❌ Error: Valid JSON context required")
    
    elif args.list_templates:
        # Simple listing
        print("Available templates:")
        # We'd need to expose list_templates from engine
        # For now, just placeholder
        print(" (Template listing not implemented in CLI yet)")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
