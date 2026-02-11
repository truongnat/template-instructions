"""Use case documentation builder for documentation system.

This module provides the UseCaseBuilder class for creating comprehensive
use case documentation with code examples, diagrams, and structured sections.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from .models import (
    UseCaseDocument,
    DocumentType,
    Category,
    Section,
    CodeBlock,
    Diagram
)
from .code_examples import CodeExampleManager
from .diagrams import DiagramGenerator


@dataclass
class Scenario:
    """A use case scenario description."""
    context: str
    actors: List[str]
    goals: List[str]
    constraints: Optional[List[str]] = None


@dataclass
class Implementation:
    """Implementation details for a use case."""
    overview: str
    steps: List[str]
    code_sections: List[Dict[str, str]] = field(default_factory=list)
    diagrams: List[Diagram] = field(default_factory=list)


@dataclass
class Results:
    """Results and outcomes of a use case."""
    outcomes: List[str]
    metrics: Optional[Dict[str, Any]] = None
    screenshots: Optional[List[str]] = None


class UseCaseBuilder:
    """Build comprehensive use case documentation."""
    
    def __init__(self, examples_dir: str = "examples/"):
        """Initialize UseCaseBuilder.
        
        Args:
            examples_dir: Directory for storing code examples
        """
        self.code_manager = CodeExampleManager(examples_dir)
        self.diagram_gen = DiagramGenerator()
    
    def build_use_case(
        self,
        title: str,
        description: str,
        scenario: Scenario,
        implementation: Implementation,
        results: Results,
        category: Category = Category.INTERMEDIATE,
        lessons_learned: Optional[List[str]] = None
    ) -> UseCaseDocument:
        """Build a complete use case document.
        
        Structure:
        1. Giới thiệu (Introduction)
        2. Kịch bản (Scenario)
        3. Kiến trúc (Architecture)
        4. Triển khai (Implementation)
        5. Kết quả (Results)
        6. Bài học (Lessons Learned)
        
        Args:
            title: Use case title in Vietnamese
            description: Brief description of the use case
            scenario: Scenario object with context, actors, goals
            implementation: Implementation object with steps and code
            results: Results object with outcomes and metrics
            category: Category level (basic, intermediate, advanced)
            lessons_learned: List of lessons learned from the use case
            
        Returns:
            UseCaseDocument object with complete structure
        """
        sections = []
        
        # 1. Giới thiệu (Introduction)
        intro_content = f"{description}\n\n"
        intro_content += "## Mục Tiêu\n\n"
        intro_content += "Use case này minh họa cách sử dụng Agentic SDLC để giải quyết "
        intro_content += "các vấn đề thực tế trong phát triển phần mềm.\n"
        
        intro_section = Section(
            title="Giới Thiệu",
            content=intro_content
        )
        sections.append(intro_section)
        
        # 2. Kịch bản (Scenario)
        scenario_content = f"## Bối Cảnh\n\n{scenario.context}\n\n"
        scenario_content += "## Các Tác Nhân\n\n"
        for actor in scenario.actors:
            scenario_content += f"- {actor}\n"
        scenario_content += "\n## Mục Tiêu\n\n"
        for goal in scenario.goals:
            scenario_content += f"- {goal}\n"
        
        if scenario.constraints:
            scenario_content += "\n## Ràng Buộc\n\n"
            for constraint in scenario.constraints:
                scenario_content += f"- {constraint}\n"
        
        scenario_section = Section(
            title="Kịch Bản",
            content=scenario_content
        )
        sections.append(scenario_section)
        
        # 3. Kiến trúc (Architecture)
        arch_content = "Sơ đồ kiến trúc của giải pháp:\n\n"
        
        arch_section = Section(
            title="Kiến Trúc",
            content=arch_content,
            diagrams=implementation.diagrams if implementation.diagrams else []
        )
        sections.append(arch_section)
        
        # 4. Triển khai (Implementation)
        impl_content = f"{implementation.overview}\n\n"
        impl_content += "## Các Bước Triển Khai\n\n"
        for i, step in enumerate(implementation.steps, 1):
            impl_content += f"{i}. {step}\n"
        
        # Convert code sections to CodeBlock objects
        code_blocks = []
        for code_section in implementation.code_sections:
            code_block = CodeBlock(
                language=code_section.get('language', 'python'),
                code=code_section.get('code', ''),
                caption=code_section.get('caption')
            )
            code_blocks.append(code_block)
        
        impl_section = Section(
            title="Triển Khai",
            content=impl_content,
            code_blocks=code_blocks
        )
        sections.append(impl_section)
        
        # 5. Kết quả (Results)
        results_content = "## Kết Quả Đạt Được\n\n"
        for outcome in results.outcomes:
            results_content += f"- {outcome}\n"
        
        if results.metrics:
            results_content += "\n## Các Chỉ Số\n\n"
            for metric_name, metric_value in results.metrics.items():
                results_content += f"- **{metric_name}**: {metric_value}\n"
        
        results_section = Section(
            title="Kết Quả",
            content=results_content
        )
        sections.append(results_section)
        
        # 6. Bài học (Lessons Learned)
        if lessons_learned:
            lessons_content = "Những bài học rút ra từ use case này:\n\n"
            for lesson in lessons_learned:
                lessons_content += f"- {lesson}\n"
            
            lessons_section = Section(
                title="Bài Học Kinh Nghiệm",
                content=lessons_content
            )
            sections.append(lessons_section)
        
        # Create the UseCaseDocument
        use_case_doc = UseCaseDocument(
            title=title,
            type=DocumentType.USE_CASE,
            category=category,
            description=description,
            sections=sections,
            metadata={
                "actors": scenario.actors,
                "goals": scenario.goals,
                "version": "1.0.0"
            },
            last_updated=datetime.now().strftime("%Y-%m-%d"),
            version="1.0.0",
            scenario=scenario.context,
            problem="",  # Will be set separately if needed
            solution=implementation.overview,
            architecture=implementation.diagrams[0] if implementation.diagrams else None,
            implementation=code_blocks,
            results=results_content,
            lessons_learned=lessons_learned if lessons_learned else []
        )
        
        return use_case_doc
    
    def add_code_section(
        self,
        use_case: UseCaseDocument,
        title: str,
        code: str,
        explanation: str,
        language: str = "python"
    ) -> None:
        """Add code section to use case.
        
        Args:
            use_case: UseCaseDocument to add code to
            title: Title/caption for the code section
            code: The code content
            explanation: Vietnamese explanation of the code
            language: Programming language (default: python)
        """
        # Create a new code block
        code_block = CodeBlock(
            language=language,
            code=code,
            caption=title
        )
        
        # Add to implementation list
        use_case.implementation.append(code_block)
        
        # Find the Implementation section and add the code block
        for section in use_case.sections:
            if section.title == "Triển Khai":
                if section.code_blocks is None:
                    section.code_blocks = []
                section.code_blocks.append(code_block)
                
                # Add explanation to section content
                section.content += f"\n\n### {title}\n\n{explanation}\n\n"
                break
    
    def add_diagram(
        self,
        use_case: UseCaseDocument,
        diagram_type: str,
        diagram: str,
        caption: str = "",
        section_title: str = "Kiến Trúc"
    ) -> None:
        """Add diagram to use case.
        
        Args:
            use_case: UseCaseDocument to add diagram to
            diagram_type: Type of diagram (flowchart, sequence, etc.)
            diagram: Mermaid diagram code
            caption: Caption for the diagram
            section_title: Section to add diagram to (default: "Kiến Trúc")
        """
        # Create a new Diagram object
        diagram_obj = Diagram(
            type=diagram_type,
            mermaid_code=diagram,
            caption=caption
        )
        
        # Update architecture if adding to architecture section
        if section_title == "Kiến Trúc" and use_case.architecture is None:
            use_case.architecture = diagram_obj
        
        # Find the target section and add the diagram
        for section in use_case.sections:
            if section.title == section_title:
                if section.diagrams is None:
                    section.diagrams = []
                section.diagrams.append(diagram_obj)
                break
