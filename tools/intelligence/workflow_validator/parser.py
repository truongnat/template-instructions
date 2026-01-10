"""
Workflow Parser - Parse workflow .md files into structured definitions
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    number: int
    description: str
    commands: List[str] = field(default_factory=list)
    is_turbo: bool = False
    is_critical: bool = False
    substeps: List['WorkflowStep'] = field(default_factory=list)

    @property
    def command(self) -> Optional[str]:
        """Backward compatibility for single command access"""
        return self.commands[0] if self.commands else None


@dataclass
class WorkflowDefinition:
    """Structured representation of a workflow"""
    name: str
    filepath: Path
    description: str
    steps: List[WorkflowStep]
    turbo_all: bool = False
    enforcement_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowParser:
    """Parse workflow markdown files into structured WorkflowDefinition"""
    
    def __init__(self):
        self.step_pattern = re.compile(r'^(\d+)\.\s+(.+)$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```(?:bash|python)?\n(.*?)\n```', re.DOTALL)
        self.turbo_pattern = re.compile(r'//\s*turbo(?:-all)?')
        
    def parse(self, workflow_path: Path) -> WorkflowDefinition:
        """
        Parse a workflow .md file into a WorkflowDefinition
        
        Args:
            workflow_path: Path to the workflow .md file
            
        Returns:
            WorkflowDefinition object
            
        Raises:
            FileNotFoundError: If workflow file doesn't exist
            ValueError: If workflow format is invalid
        """
        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")
            
        content = workflow_path.read_text(encoding='utf-8')
        
        # Extract workflow name from filename
        workflow_name = workflow_path.stem
        
        # Extract description from YAML frontmatter or first heading
        description = self._extract_description(content)
        
        # Check for turbo-all flag
        turbo_all = '// turbo-all' in content
        
        # Extract steps
        steps = self._extract_steps(content)
        
        # Extract enforcement notes
        enforcement_notes = self._extract_enforcement_notes(content)
        
        # Extract metadata
        metadata = self._extract_metadata(content)
        
        return WorkflowDefinition(
            name=workflow_name,
            filepath=workflow_path,
            description=description,
            steps=steps,
            turbo_all=turbo_all,
            enforcement_notes=enforcement_notes,
            metadata=metadata
        )
    
    def _extract_description(self, content: str) -> str:
        """Extract workflow description from YAML frontmatter or content"""
        # Try YAML frontmatter first
        yaml_match = re.search(r'^---\s*\ndescription:\s*(.+?)\n---', content, re.MULTILINE)
        if yaml_match:
            return yaml_match.group(1).strip()
        
        # Fallback to first heading
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()
        
        return "No description available"
    
    def _extract_steps(self, content: str) -> List[WorkflowStep]:
        """Extract numbered steps from workflow content"""
        steps = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for step number (handle direct "1. " or markdown "### 1. ")
            step_match = re.match(r'^(?:#+\s*)?(\d+)\.\s+(.+)$', line)
            if step_match:
                step_num = int(step_match.group(1))
                step_desc = step_match.group(2)
                
                # Check if previous line has // turbo annotation
                is_turbo = False
                if i > 0 and '// turbo' in lines[i-1]:
                    is_turbo = True
                
                # Look ahead for code blocks
                commands = []
                j = i + 1
                while j < len(lines) and not re.match(r'^(?:#+\s*)?\d+\.', lines[j].strip()):
                    line_j = lines[j].strip()
                    if line_j.startswith('```'):
                        # Extract fenced code block
                        code_start = j + 1
                        code_end = code_start
                        while code_end < len(lines) and not lines[code_end].strip().startswith('```'):
                            code_end += 1
                        if code_end < len(lines):
                            cmd = '\n'.join(lines[code_start:code_end]).strip()
                            if cmd:
                                commands.append(cmd)
                            j = code_end
                    else:
                        # Check for inline backtick commands in list items or standalone
                        inline_matches = re.findall(r'`([^`\n]+)`', line_j)
                        for cmd in inline_matches:
                            # Only count as a command if it looks like a shell command
                            # (simple heuristic: starts with common tools)
                            cmd_base = cmd.split()[0] if cmd.split() else ""
                            if cmd_base in ['git', 'python', 'npm', 'bun', 'pytest', 'ls', 'rm']:
                                commands.append(cmd.strip())
                                
                    j += 1
                
                steps.append(WorkflowStep(
                    number=step_num,
                    description=step_desc,
                    commands=commands,
                    is_turbo=is_turbo
                ))
            
            i += 1
        
        return steps
    
    def _extract_enforcement_notes(self, content: str) -> List[str]:
        """Extract enforcement reminder notes"""
        notes = []
        
        # Look for "ENFORCEMENT REMINDER" sections
        enforcement_section = re.search(
            r'##\s*ENFORCEMENT REMINDER\s*\n(.+?)(?=##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if enforcement_section:
            text = enforcement_section.group(1).strip()
            # Split by lines and filter
            notes = [line.strip() for line in text.split('\n') if line.strip()]
        
        return notes
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract additional metadata from workflow"""
        metadata = {}
        
        # Extract "When to Use" section
        when_section = re.search(
            r'##\s*When to Use\s*\n(.+?)(?=##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if when_section:
            metadata['when_to_use'] = when_section.group(1).strip()
        
        # Extract "Next Steps" section
        next_section = re.search(
            r'##\s*.*Next Steps\s*\n(.+?)(?=##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if next_section:
            metadata['next_steps'] = next_section.group(1).strip()
        
        return metadata


def parse_workflow(workflow_name: str, workflows_dir: Optional[Path] = None) -> WorkflowDefinition:
    """
    Convenience function to parse a workflow by name
    
    Args:
        workflow_name: Name of the workflow (without .md extension)
        workflows_dir: Optional custom workflows directory (defaults to .agent/workflows)
        
    Returns:
        WorkflowDefinition object
    """
    if workflows_dir is None:
        # Default to .agent/workflows relative to project root
        workflows_dir = Path(__file__).parent.parent.parent.parent / '.agent' / 'workflows'
    
    workflow_path = workflows_dir / f"{workflow_name}.md"
    parser = WorkflowParser()
    return parser.parse(workflow_path)


if __name__ == "__main__":
    # Test parsing
    import sys
    
    if len(sys.argv) > 1:
        workflow_name = sys.argv[1]
        try:
            definition = parse_workflow(workflow_name)
            print(f"Workflow: {definition.name}")
            print(f"Description: {definition.description}")
            print(f"Turbo All: {definition.turbo_all}")
            print(f"\nSteps ({len(definition.steps)}):")
            for step in definition.steps:
                turbo_flag = " [TURBO]" if step.is_turbo else ""
                print(f"  {step.number}. {step.description}{turbo_flag}")
                if step.command:
                    print(f"     Command: {step.command[:50]}...")
        except Exception as e:
            print(f"Error parsing workflow: {e}")
            sys.exit(1)
    else:
        print("Usage: python parser.py <workflow_name>")
        print("Example: python parser.py commit")
