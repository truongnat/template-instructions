"""Skill Generator - Auto-generate skills from task descriptions.

When the registry doesn't find a matching skill, the generator
creates a new skill definition from a task description and context.
The generated skill is validated and saved to the registry.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..core.logging import get_logger
from .skill import (
    ContextSpec,
    Skill,
    SkillRole,
    SkillSource,
    SkillStep,
)

logger = get_logger(__name__)

# Default scoring criteria for generated skills
DEFAULT_SCORE_CRITERIA = {
    "correctness": 0.35,
    "completeness": 0.25,
    "code_quality": 0.20,
    "documentation": 0.10,
    "efficiency": 0.10,
}

# Keyword-to-role mapping for auto-detecting role
ROLE_KEYWORDS: Dict[SkillRole, List[str]] = {
    SkillRole.DEVELOPER: [
        "create", "build", "implement", "develop", "code", "write",
        "add", "make", "setup", "configure", "integrate",
    ],
    SkillRole.REVIEWER: [
        "review", "check", "audit", "inspect", "validate", "verify",
    ],
    SkillRole.TESTER: [
        "test", "qa", "quality", "assert", "spec", "e2e", "unit",
    ],
    SkillRole.ARCHITECT: [
        "design", "architect", "plan", "structure", "schema", "model",
    ],
    SkillRole.DEVOPS: [
        "deploy", "ci", "cd", "pipeline", "docker", "kubernetes", "infra",
    ],
    SkillRole.ANALYST: [
        "analyze", "research", "investigate", "requirement", "spec",
    ],
    SkillRole.DOCUMENTER: [
        "document", "readme", "guide", "tutorial", "api-doc",
    ],
}

# Keyword-to-category mapping for auto-detecting category
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "frontend": [
        "react", "vue", "angular", "svelte", "css", "html", "ui", "ux",
        "webapp", "web", "frontend", "component", "page", "layout",
        "tailwind", "bootstrap", "responsive",
    ],
    "backend": [
        "api", "server", "rest", "graphql", "database", "sql", "orm",
        "backend", "endpoint", "middleware", "auth", "jwt",
    ],
    "fullstack": [
        "fullstack", "full-stack", "todo", "app", "application", "project",
    ],
    "devops": [
        "deploy", "docker", "kubernetes", "ci", "cd", "pipeline",
        "terraform", "ansible", "aws", "gcp", "azure",
    ],
    "testing": [
        "test", "testing", "e2e", "unit", "integration", "cypress",
        "jest", "pytest", "coverage",
    ],
    "documentation": [
        "document", "docs", "readme", "guide", "tutorial",
    ],
    "mobile": [
        "mobile", "ios", "android", "flutter", "react-native", "swift",
        "kotlin",
    ],
}


class SkillGenerator:
    """Generate skill definitions from task descriptions.

    The generator analyzes a natural language task description and
    produces a structured Skill definition with appropriate role,
    category, steps, and validation rules.

    Example:
        >>> gen = SkillGenerator()
        >>> skill = gen.generate("Create a React todo application with auth")
        >>> print(skill.name)
        "create-react-todo-application"
    """

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        """Initialize the generator.

        Args:
            output_dir: Directory to save generated skill YAML files.
                       If None, skills are returned but not persisted.
        """
        self._output_dir = output_dir

    def generate(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        role: Optional[SkillRole] = None,
        category: Optional[str] = None,
    ) -> Skill:
        """Generate a skill from a task description.

        Args:
            description: Natural language task description.
            context: Optional project context.
            role: Optional role override (auto-detected if None).
            category: Optional category override (auto-detected if None).

        Returns:
            Generated Skill instance.
        """
        context = context or {}

        # Auto-detect role and category from description
        detected_role = role or self._detect_role(description)
        detected_category = category or self._detect_category(description)

        # Generate name from description
        name = self._generate_name(description)

        # Generate tags from description
        tags = self._extract_tags(description)

        # Generate steps based on role
        steps = self._generate_steps(description, detected_role, context)

        # Generate validation rules
        validation_rules = self._generate_validation_rules(detected_role)

        # Generate context requirements
        context_spec = self._generate_context_spec(detected_category, context)

        # Build prompt template
        prompt_template = self._generate_prompt_template(description, detected_role)

        skill = Skill(
            name=name,
            description=description,
            role=detected_role,
            category=detected_category,
            tags=tags,
            prompt_template=prompt_template,
            workflow_steps=steps,
            validation_rules=validation_rules,
            context_requirements=context_spec,
            score_criteria=DEFAULT_SCORE_CRITERIA.copy(),
            source=SkillSource.GENERATED,
        )

        # Persist if output directory is set
        if self._output_dir:
            self._save_skill(skill)

        logger.info(
            "Generated skill: %s (role=%s, category=%s, steps=%d)",
            skill.name,
            skill.role.value,
            skill.category,
            len(skill.workflow_steps),
        )

        return skill

    def _detect_role(self, description: str) -> SkillRole:
        """Detect the most appropriate role from description keywords.

        Args:
            description: Task description.

        Returns:
            Detected SkillRole.
        """
        desc_lower = description.lower()
        best_role = SkillRole.DEVELOPER
        best_count = 0

        for role, keywords in ROLE_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in desc_lower)
            if count > best_count:
                best_count = count
                best_role = role

        return best_role

    def _detect_category(self, description: str) -> str:
        """Detect the most appropriate category from description keywords.

        Args:
            description: Task description.

        Returns:
            Detected category string.
        """
        desc_lower = description.lower()
        best_category = "general"
        best_count = 0

        for category, keywords in CATEGORY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in desc_lower)
            if count > best_count:
                best_count = count
                best_category = category

        return best_category

    def _generate_name(self, description: str) -> str:
        """Generate a kebab-case skill name from description.

        Args:
            description: Task description.

        Returns:
            Kebab-case skill name.
        """
        # Take first 6 meaningful words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "with", "for", "and", "or", "but", "in", "on", "at", "to",
            "of", "that", "this", "it", "from", "by", "as",
        }
        words = [
            w.lower().strip(".,!?;:\"'")
            for w in description.split()
            if w.lower().strip(".,!?;:\"'") not in stop_words and len(w) > 1
        ]
        name_words = words[:6]
        return "-".join(name_words) if name_words else "custom-skill"

    def _extract_tags(self, description: str) -> List[str]:
        """Extract searchable tags from description.

        Args:
            description: Task description.

        Returns:
            List of tags.
        """
        desc_lower = description.lower()
        tags = set()

        # Check all category keywords
        for category, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in desc_lower:
                    tags.add(kw)

        return sorted(tags)

    def _generate_steps(
        self,
        description: str,
        role: SkillRole,
        context: Dict[str, Any],
    ) -> List[SkillStep]:
        """Generate workflow steps based on role and description.

        Args:
            description: Task description.
            role: Detected role.
            context: Project context.

        Returns:
            List of SkillStep.
        """
        # Role-based step templates
        step_templates: Dict[SkillRole, List[Dict[str, str]]] = {
            SkillRole.DEVELOPER: [
                {"name": "analyze", "action": "analyze_requirements",
                 "description": "Analyze the task requirements and identify key components"},
                {"name": "design", "action": "design_solution",
                 "description": "Design the solution architecture and component structure"},
                {"name": "implement", "action": "write_code",
                 "description": "Implement the solution following best practices"},
                {"name": "test", "action": "write_tests",
                 "description": "Write tests to verify the implementation"},
                {"name": "document", "action": "document_changes",
                 "description": "Document the implementation and update README"},
            ],
            SkillRole.REVIEWER: [
                {"name": "review-code", "action": "review_code_quality",
                 "description": "Review code for quality, style, and best practices"},
                {"name": "check-security", "action": "security_check",
                 "description": "Check for security vulnerabilities"},
                {"name": "report", "action": "generate_review_report",
                 "description": "Generate a review report with findings"},
            ],
            SkillRole.TESTER: [
                {"name": "plan-tests", "action": "plan_test_strategy",
                 "description": "Plan testing strategy and identify test cases"},
                {"name": "write-tests", "action": "implement_tests",
                 "description": "Write unit, integration, and e2e tests"},
                {"name": "run-tests", "action": "execute_tests",
                 "description": "Run tests and collect results"},
                {"name": "report", "action": "generate_test_report",
                 "description": "Generate test coverage report"},
            ],
            SkillRole.ARCHITECT: [
                {"name": "research", "action": "research_approaches",
                 "description": "Research different architectural approaches"},
                {"name": "design", "action": "create_architecture",
                 "description": "Create architecture design with diagrams"},
                {"name": "document", "action": "write_adr",
                 "description": "Write Architecture Decision Record"},
            ],
            SkillRole.DEVOPS: [
                {"name": "setup-infra", "action": "setup_infrastructure",
                 "description": "Set up infrastructure and configuration"},
                {"name": "configure-ci", "action": "configure_pipeline",
                 "description": "Configure CI/CD pipeline"},
                {"name": "deploy", "action": "deploy_application",
                 "description": "Deploy the application"},
            ],
            SkillRole.ANALYST: [
                {"name": "gather", "action": "gather_requirements",
                 "description": "Gather and analyze requirements"},
                {"name": "document", "action": "write_requirements",
                 "description": "Write requirement specification"},
                {"name": "validate", "action": "validate_requirements",
                 "description": "Validate requirements with stakeholders"},
            ],
            SkillRole.DOCUMENTER: [
                {"name": "outline", "action": "create_outline",
                 "description": "Create documentation outline"},
                {"name": "write", "action": "write_documentation",
                 "description": "Write documentation content"},
                {"name": "review", "action": "review_documentation",
                 "description": "Review and polish documentation"},
            ],
        }

        templates = step_templates.get(role, step_templates[SkillRole.DEVELOPER])
        steps = []
        for i, tmpl in enumerate(templates):
            depends = [templates[i - 1]["name"]] if i > 0 else []
            steps.append(
                SkillStep(
                    name=tmpl["name"],
                    action=tmpl["action"],
                    description=f"{tmpl['description']}\n\nTask: {description}",
                    expected_output=f"Completed {tmpl['action']} step",
                    depends_on=depends,
                )
            )

        return steps

    def _generate_validation_rules(self, role: SkillRole) -> List[str]:
        """Generate validation rules based on role.

        Args:
            role: Skill role.

        Returns:
            List of validation rule strings.
        """
        base_rules = [
            "Output must be non-empty",
            "Must address the original task description",
        ]

        role_rules: Dict[SkillRole, List[str]] = {
            SkillRole.DEVELOPER: [
                "Code must follow language best practices",
                "No placeholder or TODO comments in final output",
                "Must include error handling",
            ],
            SkillRole.REVIEWER: [
                "Review must cover all changed files",
                "Must categorize findings by severity",
            ],
            SkillRole.TESTER: [
                "Tests must cover happy path and edge cases",
                "Test names must be descriptive",
            ],
            SkillRole.ARCHITECT: [
                "Design must include component diagram",
                "Must justify technology choices",
            ],
            SkillRole.DEVOPS: [
                "Infrastructure must be reproducible",
                "Must include rollback strategy",
            ],
            SkillRole.ANALYST: [
                "Requirements must be testable",
                "Must include acceptance criteria",
            ],
            SkillRole.DOCUMENTER: [
                "Documentation must include examples",
                "Must be accessible to target audience",
            ],
        }

        return base_rules + role_rules.get(role, [])

    def _generate_context_spec(
        self,
        category: str,
        context: Dict[str, Any],
    ) -> ContextSpec:
        """Generate context specification based on category.

        Args:
            category: Detected category.
            context: Project context.

        Returns:
            ContextSpec instance.
        """
        category_files: Dict[str, List[str]] = {
            "frontend": ["*.tsx", "*.jsx", "*.ts", "*.js", "*.css", "*.html"],
            "backend": ["*.py", "*.go", "*.java", "*.rs", "*.ts"],
            "fullstack": ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx"],
            "devops": ["Dockerfile", "*.yml", "*.yaml", "*.tf"],
            "testing": ["test_*.py", "*.test.ts", "*.spec.ts"],
            "mobile": ["*.dart", "*.swift", "*.kt"],
        }

        required_files = category_files.get(category, ["*.*"])
        required_context = ["project_structure", "tech_stack"]

        if "dependencies" in context:
            required_context.append("dependencies")

        return ContextSpec(
            required_files=required_files,
            required_context=required_context,
            max_tokens=4000,
        )

    def _generate_prompt_template(self, description: str, role: SkillRole) -> str:
        """Generate a Jinja2 prompt template for the skill.

        Args:
            description: Task description.
            role: Skill role.

        Returns:
            Jinja2 template string.
        """
        return (
            "You are acting as a {{ skill.role.value }}.\n\n"
            "## Task\n\n"
            "{{ skill.description }}\n\n"
            "## Context\n\n"
            "{{ context }}\n\n"
            "## Instructions\n\n"
            "{% for step in skill.workflow_steps %}\n"
            "### Step {{ loop.index }}: {{ step.name }}\n"
            "{{ step.description }}\n\n"
            "{% endfor %}\n"
            "## Validation\n\n"
            "{% for rule in skill.validation_rules %}\n"
            "- {{ rule }}\n"
            "{% endfor %}\n"
        )

    def _save_skill(self, skill: Skill) -> Path:
        """Save a generated skill to YAML file.

        Args:
            skill: Skill to save.

        Returns:
            Path to saved file.
        """
        if not self._output_dir:
            raise ValueError("Output directory not set")

        self._output_dir.mkdir(parents=True, exist_ok=True)
        file_path = self._output_dir / f"{skill.name}.yaml"

        data = skill.to_yaml_dict()
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        logger.info("Saved generated skill to %s", file_path)
        return file_path
