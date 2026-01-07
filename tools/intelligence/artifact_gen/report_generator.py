"""
Report Generator - Automated report creation.

Part of Layer 2: Intelligence Layer.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ReportGenerator:
    """
    Generates various report types.
    
    Features:
    - Summary reports
    - Status reports  
    - Analytics reports
    - Custom reports from templates
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("docs/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated_reports: List[Dict] = []

    def generate(
        self,
        report_type: str,
        title: str,
        data: Dict[str, Any],
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a report.
        
        Args:
            report_type: Type of report (summary, status, analytics)
            title: Report title
            data: Report data
            output_file: Optional output filename
            
        Returns:
            Generated markdown content
        """
        if report_type == "summary":
            content = self._generate_summary(title, data)
        elif report_type == "status":
            content = self._generate_status(title, data)
        elif report_type == "analytics":
            content = self._generate_analytics(title, data)
        else:
            content = self._generate_generic(title, data)
        
        if output_file:
            output_path = self.output_dir / output_file
            output_path.write_text(content, encoding='utf-8')
            self.generated_reports.append({
                "type": report_type,
                "title": title,
                "file": str(output_path),
                "timestamp": datetime.now().isoformat()
            })
        
        return content

    def _generate_summary(self, title: str, data: Dict) -> str:
        """Generate summary report."""
        content = f"# {title}\n\n"
        content += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        content += "---\n\n"
        
        for section, section_data in data.items():
            content += f"## {section}\n\n"
            content += self._format_data(section_data)
            content += "\n"
        
        return content

    def _generate_status(self, title: str, data: Dict) -> str:
        """Generate status report."""
        content = f"# 📊 {title}\n\n"
        content += f"*Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        # Status overview
        if "status" in data:
            status = data["status"]
            emoji = "✅" if status.lower() in ["complete", "healthy", "ok"] else "⚠️"
            content += f"**Status:** {emoji} {status}\n\n"
        
        # Metrics
        if "metrics" in data:
            content += "## Metrics\n\n"
            content += "| Metric | Value |\n|--------|-------|\n"
            for metric, value in data["metrics"].items():
                content += f"| {metric} | {value} |\n"
            content += "\n"
        
        # Issues
        if "issues" in data:
            content += "## Issues\n\n"
            for issue in data["issues"]:
                content += f"- ⚠️ {issue}\n"
            content += "\n"
        
        # Actions
        if "actions" in data:
            content += "## Recommended Actions\n\n"
            for action in data["actions"]:
                content += f"- [ ] {action}\n"
            content += "\n"
        
        return content

    def _generate_analytics(self, title: str, data: Dict) -> str:
        """Generate analytics report."""
        content = f"# 📈 {title}\n\n"
        content += f"*Analysis Period: {data.get('period', 'N/A')}*\n\n"
        
        # Summary statistics
        if "stats" in data:
            content += "## Summary Statistics\n\n"
            content += "| Statistic | Value |\n|-----------|-------|\n"
            for stat, value in data["stats"].items():
                content += f"| {stat} | {value} |\n"
            content += "\n"
        
        # Trends
        if "trends" in data:
            content += "## Trends\n\n"
            for trend in data["trends"]:
                direction = "📈" if trend.get("direction") == "up" else "📉"
                content += f"- {direction} {trend.get('metric', 'Unknown')}: {trend.get('change', 'N/A')}\n"
            content += "\n"
        
        # Insights
        if "insights" in data:
            content += "## Key Insights\n\n"
            for insight in data["insights"]:
                content += f"- 💡 {insight}\n"
            content += "\n"
        
        return content

    def _generate_generic(self, title: str, data: Dict) -> str:
        """Generate generic report."""
        content = f"# {title}\n\n"
        content += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        for key, value in data.items():
            content += f"## {key}\n\n"
            content += self._format_data(value)
            content += "\n"
        
        return content

    def _format_data(self, data: Any) -> str:
        """Format data for markdown."""
        if isinstance(data, str):
            return f"{data}\n"
        elif isinstance(data, list):
            return "\n".join(f"- {item}" for item in data) + "\n"
        elif isinstance(data, dict):
            lines = [f"- **{k}**: {v}" for k, v in data.items()]
            return "\n".join(lines) + "\n"
        else:
            return f"{data}\n"

    def get_recent_reports(self, limit: int = 10) -> List[Dict]:
        """Get recently generated reports."""
        return self.generated_reports[-limit:]


class TemplateEngine:
    """
    Template processing for artifact generation.
    """

    DEFAULT_TEMPLATES = {
        "walkthrough": """# {{title}}

*Date: {{date}}*

## Summary
{{summary}}

## What Was Done
{{changes}}

## Verification
{{verification}}

---
*Generated by Agentic SDLC*
""",
        "plan": """# {{title}}

## Objective
{{objective}}

## Proposed Changes
{{changes}}

## Verification Plan
{{verification}}
""",
    }

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(".agent/templates")
        self.custom_templates: Dict[str, str] = {}

    def get_template(self, name: str) -> Optional[str]:
        """Get a template by name."""
        # Check custom templates first
        if name in self.custom_templates:
            return self.custom_templates[name]
        
        # Check default templates
        if name in self.DEFAULT_TEMPLATES:
            return self.DEFAULT_TEMPLATES[name]
        
        # Check file system
        template_file = self.templates_dir / f"{name}.md"
        if template_file.exists():
            return template_file.read_text(encoding='utf-8')
        
        return None

    def render(self, template_name: str, variables: Dict[str, str]) -> Optional[str]:
        """Render a template with variables."""
        template = self.get_template(template_name)
        if not template:
            return None
        
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        
        return result

    def add_template(self, name: str, content: str):
        """Add a custom template."""
        self.custom_templates[name] = content


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Report Generator")
    parser.add_argument("--type", choices=["summary", "status", "analytics"], help="Report type")
    parser.add_argument("--title", type=str, help="Report title")
    parser.add_argument("--data", type=str, help="JSON data for report")
    parser.add_argument("--output", type=str, help="Output filename")
    
    args = parser.parse_args()
    
    if args.type and args.title:
        generator = ReportGenerator()
        data = json.loads(args.data) if args.data else {}
        content = generator.generate(args.type, args.title, data, args.output)
        print(content)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

