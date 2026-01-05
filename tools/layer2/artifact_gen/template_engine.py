"""
Template Engine - Template processing for artifacts.

Part of Layer 2: Intelligence Layer.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class TemplateEngine:
    """
    Template processing engine with variable substitution.
    
    Features:
    - Variable substitution {{variable}}
    - Conditional blocks {{#if condition}}...{{/if}}
    - Loops {{#each items}}...{{/each}}
    - Filters {{variable|filter}}
    """

    BUILTIN_FILTERS = {
        "upper": lambda x: str(x).upper(),
        "lower": lambda x: str(x).lower(),
        "title": lambda x: str(x).title(),
        "strip": lambda x: str(x).strip(),
        "date": lambda x: datetime.now().strftime("%Y-%m-%d") if x == "now" else x,
    }

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(".agent/templates")
        self.template_cache: Dict[str, str] = {}
        self.custom_filters: Dict[str, Callable] = {}

    def add_filter(self, name: str, func: Callable):
        """Add a custom filter."""
        self.custom_filters[name] = func

    def get_filter(self, name: str) -> Optional[Callable]:
        """Get a filter by name."""
        return self.custom_filters.get(name) or self.BUILTIN_FILTERS.get(name)

    def load_template(self, name: str) -> Optional[str]:
        """Load a template from file or cache."""
        if name in self.template_cache:
            return self.template_cache[name]
        
        # Try with .md extension
        for ext in ["", ".md", ".txt", ".template"]:
            template_path = self.templates_dir / f"{name}{ext}"
            if template_path.exists():
                content = template_path.read_text(encoding='utf-8')
                self.template_cache[name] = content
                return content
        
        return None

    def render(self, template: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template: Template string
            context: Dictionary of variables
            
        Returns:
            Rendered string
        """
        result = template
        
        # Process conditionals first
        result = self._process_conditionals(result, context)
        
        # Process loops
        result = self._process_loops(result, context)
        
        # Process variables with filters
        result = self._process_variables(result, context)
        
        return result

    def render_file(self, template_name: str, context: Dict[str, Any]) -> Optional[str]:
        """Load and render a template file."""
        template = self.load_template(template_name)
        if template:
            return self.render(template, context)
        return None

    def _process_variables(self, template: str, context: Dict) -> str:
        """Process {{variable}} and {{variable|filter}} patterns."""
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace(match):
            expr = match.group(1).strip()
            
            # Check for filter
            if '|' in expr:
                var_name, filter_name = expr.split('|', 1)
                var_name = var_name.strip()
                filter_name = filter_name.strip()
                
                value = self._get_value(var_name, context)
                filter_func = self.get_filter(filter_name)
                
                if filter_func:
                    return str(filter_func(value))
                return str(value)
            else:
                return str(self._get_value(expr, context))
        
        return re.sub(pattern, replace, template)

    def _process_conditionals(self, template: str, context: Dict) -> str:
        """Process {{#if condition}}...{{/if}} blocks."""
        pattern = r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{/if\}\}'
        
        def replace(match):
            condition = match.group(1).strip()
            content = match.group(2)
            
            value = self._get_value(condition, context)
            if value:
                return content
            return ""
        
        return re.sub(pattern, replace, template, flags=re.DOTALL)

    def _process_loops(self, template: str, context: Dict) -> str:
        """Process {{#each items}}...{{/each}} blocks."""
        pattern = r'\{\{#each\s+([^}]+)\}\}(.*?)\{\{/each\}\}'
        
        def replace(match):
            var_name = match.group(1).strip()
            content = match.group(2)
            
            items = self._get_value(var_name, context)
            if not items or not isinstance(items, (list, tuple)):
                return ""
            
            result = []
            for item in items:
                item_context = {**context, "item": item, "this": item}
                rendered = self._process_variables(content, item_context)
                result.append(rendered)
            
            return "".join(result)
        
        return re.sub(pattern, replace, template, flags=re.DOTALL)

    def _get_value(self, path: str, context: Dict) -> Any:
        """Get a value from context using dot notation."""
        parts = path.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part, "")
            else:
                return ""
        
        return value

    def list_templates(self) -> List[str]:
        """List available templates."""
        if not self.templates_dir.exists():
            return []
        
        templates = []
        for ext in ["*.md", "*.txt", "*.template"]:
            templates.extend(f.stem for f in self.templates_dir.glob(ext))
        
        return sorted(set(templates))

    def create_template(self, name: str, content: str) -> Path:
        """Create a new template file."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        template_path = self.templates_dir / f"{name}.md"
        template_path.write_text(content, encoding='utf-8')
        self.template_cache[name] = content
        return template_path


def main():
    """CLI entry point."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Template Engine")
    parser.add_argument("--render", type=str, help="Template name to render")
    parser.add_argument("--context", type=str, help="JSON context for rendering")
    parser.add_argument("--list", action="store_true", help="List templates")
    
    args = parser.parse_args()
    engine = TemplateEngine()
    
    if args.render:
        context = json.loads(args.context) if args.context else {}
        result = engine.render_file(args.render, context)
        if result:
            print(result)
        else:
            print(f"Template not found: {args.render}")
    
    elif args.list:
        for template in engine.list_templates():
            print(f"- {template}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
