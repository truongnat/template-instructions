"""Domain Engine - Multi-domain support for skills, workflows, and tools.

The Domain Engine enables the framework to scope skills, workflows, and tools
by domain (e.g., frontend, backend, devops, mobile, data). Domains can be
hierarchical (e.g., backend.api, backend.db) and are configurable via YAML.

Usage:
    from agentic_sdlc.core.domain import DomainRegistry, Domain

    registry = DomainRegistry()
    registry.discover_from_config(config_path)

    domain = registry.detect("Build a React login page")
    # => Domain(name="frontend", ...)

    skills = registry.get_scoped_skills("frontend")
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class DomainTool:
    """A tool available within a domain.

    Attributes:
        name: Tool name (e.g., 'npm', 'docker', 'pytest').
        command: CLI command or callable reference.
        description: What the tool does.
        config: Additional tool configuration.
    """

    name: str
    command: str = ""
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Domain:
    """Represents a scoped domain for skills, workflows, and tools.

    Attributes:
        name: Domain identifier (kebab-case, e.g., 'frontend', 'backend-api').
        description: Human-readable description.
        keywords: Keywords that help detect this domain from user input.
        parent: Parent domain name for hierarchical domains.
        skills_dir: Relative directory for domain-specific skills.
        workflows_dir: Relative directory for domain-specific workflows.
        tools: List of tools available in this domain.
        config: Additional domain-specific configuration.
        priority: Priority for routing conflicts (higher = preferred).
    """

    name: str
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    skills_dir: str = ""
    workflows_dir: str = ""
    tools: List[DomainTool] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0

    @property
    def full_name(self) -> str:
        """Get fully qualified domain name (e.g., 'backend.api')."""
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name

    def matches_keywords(self, text: str) -> float:
        """Score how well a text matches this domain's keywords.

        Args:
            text: Input text to match against.

        Returns:
            Float score (0.0 = no match, higher = better match).
        """
        if not self.keywords:
            return 0.0

        text_lower = text.lower()
        text_tokens = set(text_lower.split())
        score = 0.0

        for keyword in self.keywords:
            kw_lower = keyword.lower()
            # Exact token match scores higher
            if kw_lower in text_tokens:
                score += 2.0
            # Substring match scores lower
            elif kw_lower in text_lower:
                score += 1.0

        return score

    def to_dict(self) -> Dict[str, Any]:
        """Serialize domain to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "parent": self.parent,
            "skills_dir": self.skills_dir,
            "workflows_dir": self.workflows_dir,
            "tools": [
                {"name": t.name, "command": t.command, "description": t.description}
                for t in self.tools
            ],
            "config": self.config,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Domain":
        """Deserialize domain from dictionary."""
        tools = [
            DomainTool(
                name=t.get("name", ""),
                command=t.get("command", ""),
                description=t.get("description", ""),
                config=t.get("config", {}),
            )
            for t in data.get("tools", [])
        ]
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            keywords=data.get("keywords", []),
            parent=data.get("parent"),
            skills_dir=data.get("skills_dir", ""),
            workflows_dir=data.get("workflows_dir", ""),
            tools=tools,
            config=data.get("config", {}),
            priority=data.get("priority", 0),
        )


class DomainRegistry:
    """Central registry for domain discovery, detection, and management.

    The registry maintains an index of all available domains and supports:
    - Keyword-based domain detection from user input
    - Hierarchical domain resolution
    - Domain-scoped skill/workflow directory lookups
    - YAML-based configuration loading
    """

    def __init__(self) -> None:
        """Initialize the domain registry."""
        self._domains: Dict[str, Domain] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load built-in default domains."""
        defaults = [
            Domain(
                name="frontend",
                description="Frontend web development",
                keywords=[
                    "react", "vue", "angular", "svelte", "css", "html", "ui", "ux",
                    "webapp", "web", "frontend", "component", "page", "layout",
                    "tailwind", "bootstrap", "responsive", "nextjs", "vite",
                    "typescript", "javascript", "dom", "browser",
                ],
                skills_dir="skills/frontend",
                workflows_dir="workflows/frontend",
                tools=[
                    DomainTool(name="npm", command="npm", description="Node package manager"),
                    DomainTool(name="vite", command="npx vite", description="Vite build tool"),
                ],
                priority=5,
            ),
            Domain(
                name="backend",
                description="Backend server development",
                keywords=[
                    "api", "rest", "graphql", "server", "backend", "endpoint",
                    "database", "sql", "nosql", "orm", "migration", "auth",
                    "express", "fastapi", "django", "flask", "nestjs",
                    "microservice", "grpc", "websocket",
                ],
                skills_dir="skills/backend",
                workflows_dir="workflows/backend",
                tools=[
                    DomainTool(name="docker", command="docker", description="Container runtime"),
                ],
                priority=5,
            ),
            Domain(
                name="devops",
                description="DevOps and infrastructure",
                keywords=[
                    "devops", "ci", "cd", "docker", "kubernetes", "k8s",
                    "terraform", "ansible", "aws", "gcp", "azure", "cloud",
                    "deploy", "pipeline", "infrastructure", "monitoring",
                    "nginx", "load-balancer", "ssl", "helm",
                ],
                skills_dir="skills/devops",
                workflows_dir="workflows/devops",
                tools=[
                    DomainTool(name="docker", command="docker", description="Container runtime"),
                    DomainTool(name="kubectl", command="kubectl", description="Kubernetes CLI"),
                ],
                priority=4,
            ),
            Domain(
                name="mobile",
                description="Mobile app development",
                keywords=[
                    "mobile", "ios", "android", "flutter", "react-native",
                    "swift", "kotlin", "dart", "xcode", "gradle",
                    "app-store", "play-store", "responsive",
                ],
                skills_dir="skills/mobile",
                workflows_dir="workflows/mobile",
                priority=4,
            ),
            Domain(
                name="data",
                description="Data engineering and analytics",
                keywords=[
                    "data", "etl", "pipeline", "analytics", "warehouse",
                    "spark", "airflow", "pandas", "numpy", "jupyter",
                    "tableau", "powerbi", "dbt", "bigquery", "redshift",
                ],
                skills_dir="skills/data",
                workflows_dir="workflows/data",
                priority=3,
            ),
            Domain(
                name="testing",
                description="Testing and quality assurance",
                keywords=[
                    "test", "testing", "unit-test", "integration-test", "e2e",
                    "pytest", "jest", "cypress", "selenium", "coverage",
                    "qa", "quality", "assertion", "mock", "fixture",
                ],
                skills_dir="skills/testing",
                workflows_dir="workflows/testing",
                priority=4,
            ),
            Domain(
                name="documentation",
                description="Documentation and technical writing",
                keywords=[
                    "document", "docs", "readme", "guide", "tutorial",
                    "api-doc", "swagger", "openapi", "changelog",
                    "wiki", "markdown", "sphinx", "mkdocs",
                ],
                skills_dir="skills/documentation",
                workflows_dir="workflows/documentation",
                priority=2,
            ),
        ]

        for domain in defaults:
            self.register(domain)

    def register(self, domain: Domain) -> None:
        """Register a domain in the registry.

        Args:
            domain: Domain to register.
        """
        self._domains[domain.name] = domain
        logger.debug(f"Registered domain: {domain.name}")

    def unregister(self, name: str) -> bool:
        """Unregister a domain by name.

        Args:
            name: Domain name.

        Returns:
            True if removed, False if not found.
        """
        if name in self._domains:
            del self._domains[name]
            return True
        return False

    def get(self, name: str) -> Optional[Domain]:
        """Get a domain by exact name.

        Args:
            name: Domain name.

        Returns:
            Domain if found, None otherwise.
        """
        return self._domains.get(name)

    def list_all(self) -> List[Domain]:
        """List all registered domains.

        Returns:
            List of all domains sorted by priority (highest first).
        """
        return sorted(self._domains.values(), key=lambda d: d.priority, reverse=True)

    def detect(self, text: str, top_k: int = 1) -> List[Domain]:
        """Detect the most relevant domain(s) from user input text.

        Uses keyword matching with scoring. Returns top-k domains
        sorted by relevance score.

        Args:
            text: User input text to analyze.
            top_k: Number of top domains to return.

        Returns:
            List of detected domains (best match first).
        """
        if not text or not self._domains:
            return []

        scored: List[tuple[float, Domain]] = []
        for domain in self._domains.values():
            score = domain.matches_keywords(text)
            if score > 0:
                # Apply priority bonus
                score += domain.priority * 0.1
                scored.append((score, domain))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [domain for _, domain in scored[:top_k]]

    def detect_single(self, text: str) -> Optional[Domain]:
        """Detect the single best matching domain.

        Args:
            text: User input text.

        Returns:
            Best matching Domain or None.
        """
        results = self.detect(text, top_k=1)
        return results[0] if results else None

    def get_domain_names(self) -> Set[str]:
        """Get all registered domain names.

        Returns:
            Set of domain names.
        """
        return set(self._domains.keys())

    def load_from_yaml(self, path: Path) -> int:
        """Load domains from a YAML configuration file.

        Expected YAML format:
            domains:
              - name: custom-domain
                description: My custom domain
                keywords: [keyword1, keyword2]
                ...

        Args:
            path: Path to YAML file.

        Returns:
            Number of domains loaded.
        """
        if not path.exists():
            logger.warning(f"Domain config file not found: {path}")
            return 0

        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)

            if not data or "domains" not in data:
                logger.warning(f"No 'domains' key in config: {path}")
                return 0

            count = 0
            for domain_data in data["domains"]:
                try:
                    domain = Domain.from_dict(domain_data)
                    self.register(domain)
                    count += 1
                except (KeyError, TypeError) as e:
                    logger.warning(f"Invalid domain config: {e}")

            logger.info(f"Loaded {count} domains from {path}")
            return count

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse domain YAML: {e}")
            return 0

    def save_to_yaml(self, path: Path) -> None:
        """Save all domains to a YAML file.

        Args:
            path: Path to write YAML file.
        """
        data = {"domains": [d.to_dict() for d in self.list_all()]}
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Saved {len(self._domains)} domains to {path}")

    @property
    def count(self) -> int:
        """Number of registered domains."""
        return len(self._domains)
