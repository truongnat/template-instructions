"""Project Scanner - Auto-detect project type and generate context.

Scans a project directory to identify:
- Language (Python, Dart, TypeScript, JavaScript, etc.)
- Framework (Flutter, NestJS, Next.js, FastAPI, Django, etc.)
- Dependencies
- Directory structure

Used by `asdlc init` to generate project-aware GEMINI.md and CONTEXT.md.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class ProjectProfile:
    """Result of scanning a project directory."""
    name: str
    language: str = "unknown"
    framework: str = "generic"
    dependencies: List[str] = field(default_factory=list)
    has_tests: bool = False
    has_docker: bool = False
    has_ci: bool = False
    entry_points: List[str] = field(default_factory=list)
    key_directories: List[str] = field(default_factory=list)
    description: str = ""


class ProjectScanner:
    """Scans a project directory to detect type, language, and framework."""

    def scan(self, project_dir: Path) -> ProjectProfile:
        """Scan a project and return its profile.
        
        Args:
            project_dir: Path to the project root.
            
        Returns:
            ProjectProfile with detected characteristics.
        """
        project_dir = project_dir.resolve()
        profile = ProjectProfile(name=project_dir.name)

        # Detect by marker files (order matters — first match wins for framework)
        detectors = [
            self._detect_flutter,
            self._detect_nestjs,
            self._detect_nextjs,
            self._detect_react,
            self._detect_fastapi,
            self._detect_django,
            self._detect_python,
            self._detect_node,
        ]

        for detector in detectors:
            if detector(project_dir, profile):
                break

        # Common detections
        self._detect_common(project_dir, profile)
        self._detect_directories(project_dir, profile)

        logger.info(f"Scanned project: {profile.name} → {profile.language}/{profile.framework}")
        return profile

    def _detect_flutter(self, path: Path, profile: ProjectProfile) -> bool:
        pubspec = path / "pubspec.yaml"
        if not pubspec.exists():
            return False
        profile.language = "dart"
        profile.framework = "flutter"
        profile.entry_points = ["lib/main.dart"]
        # Parse basic deps
        try:
            content = pubspec.read_text()
            if "flutter:" in content:
                profile.description = "Flutter mobile/web application"
        except Exception:
            pass
        return True

    def _detect_nestjs(self, path: Path, profile: ProjectProfile) -> bool:
        nest_cli = path / "nest-cli.json"
        pkg = path / "package.json"
        if nest_cli.exists():
            profile.language = "typescript"
            profile.framework = "nestjs"
            profile.entry_points = ["src/main.ts"]
            profile.description = "NestJS backend application"
            self._parse_package_json(pkg, profile)
            return True
        if pkg.exists():
            try:
                data = json.loads(pkg.read_text())
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "@nestjs/core" in deps:
                    profile.language = "typescript"
                    profile.framework = "nestjs"
                    profile.entry_points = ["src/main.ts"]
                    profile.description = "NestJS backend application"
                    self._parse_package_json(pkg, profile)
                    return True
            except Exception:
                pass
        return False

    def _detect_nextjs(self, path: Path, profile: ProjectProfile) -> bool:
        for name in ["next.config.js", "next.config.mjs", "next.config.ts"]:
            if (path / name).exists():
                profile.language = "typescript"
                profile.framework = "nextjs"
                profile.entry_points = ["app/page.tsx", "pages/index.tsx"]
                profile.description = "Next.js web application"
                self._parse_package_json(path / "package.json", profile)
                return True
        return False

    def _detect_react(self, path: Path, profile: ProjectProfile) -> bool:
        pkg = path / "package.json"
        if not pkg.exists():
            return False
        try:
            data = json.loads(pkg.read_text())
            deps = data.get("dependencies", {})
            if "react" in deps and "next" not in deps:
                profile.language = "typescript" if (path / "tsconfig.json").exists() else "javascript"
                profile.framework = "react"
                profile.entry_points = ["src/App.tsx", "src/index.tsx"]
                profile.description = "React web application"
                self._parse_package_json(pkg, profile)
                return True
        except Exception:
            pass
        return False

    def _detect_fastapi(self, path: Path, profile: ProjectProfile) -> bool:
        for req_file in ["requirements.txt", "pyproject.toml", "setup.py"]:
            f = path / req_file
            if f.exists():
                try:
                    content = f.read_text().lower()
                    if "fastapi" in content:
                        profile.language = "python"
                        profile.framework = "fastapi"
                        profile.entry_points = ["main.py", "app/main.py"]
                        profile.description = "FastAPI backend application"
                        return True
                except Exception:
                    pass
        return False

    def _detect_django(self, path: Path, profile: ProjectProfile) -> bool:
        if (path / "manage.py").exists():
            profile.language = "python"
            profile.framework = "django"
            profile.entry_points = ["manage.py"]
            profile.description = "Django web application"
            return True
        return False

    def _detect_python(self, path: Path, profile: ProjectProfile) -> bool:
        markers = ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"]
        for marker in markers:
            if (path / marker).exists():
                profile.language = "python"
                profile.framework = "python"
                profile.description = "Python project"
                # Try to find entry points
                for ep in ["main.py", "app.py", "src/main.py"]:
                    if (path / ep).exists():
                        profile.entry_points.append(ep)
                return True
        return False

    def _detect_node(self, path: Path, profile: ProjectProfile) -> bool:
        pkg = path / "package.json"
        if pkg.exists():
            profile.language = "typescript" if (path / "tsconfig.json").exists() else "javascript"
            profile.framework = "node"
            profile.description = "Node.js project"
            self._parse_package_json(pkg, profile)
            return True
        return False

    def _detect_common(self, path: Path, profile: ProjectProfile) -> None:
        """Detect common project features."""
        # Tests
        test_dirs = ["tests", "test", "__tests__", "spec"]
        profile.has_tests = any((path / d).is_dir() for d in test_dirs)

        # Docker
        profile.has_docker = (path / "Dockerfile").exists() or (path / "docker-compose.yml").exists()

        # CI
        ci_markers = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci"]
        profile.has_ci = any((path / m).exists() for m in ci_markers)

    def _detect_directories(self, path: Path, profile: ProjectProfile) -> None:
        """List key top-level directories."""
        skip = {"node_modules", ".git", "__pycache__", ".venv", "venv", "build", ".dart_tool"}
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir() and item.name not in skip and not item.name.startswith("."):
                    profile.key_directories.append(item.name)
        except Exception:
            pass

    def _parse_package_json(self, pkg_path: Path, profile: ProjectProfile) -> None:
        """Extract dependencies from package.json."""
        if not pkg_path.exists():
            return
        try:
            data = json.loads(pkg_path.read_text())
            deps = list(data.get("dependencies", {}).keys())[:10]
            profile.dependencies = deps
        except Exception:
            pass


def generate_gemini_md(profile: ProjectProfile) -> str:
    """Generate a project-specific GEMINI.md from a ProjectProfile."""
    return f"""# {profile.name} — AI Agent Configuration

> [!IMPORTANT]
> This file is for **Gemini CLI** and **Antigravity IDE**. Read `CONTEXT.md` for full project context.

## Project Overview

- **Language**: {profile.language}
- **Framework**: {profile.framework}
- **Description**: {profile.description}
{f"- **Entry Points**: {', '.join(profile.entry_points)}" if profile.entry_points else ""}
{f"- **Key Dependencies**: {', '.join(profile.dependencies[:8])}" if profile.dependencies else ""}

## Directory Structure

```
{profile.name}/
{chr(10).join(f"├── {d}/" for d in profile.key_directories[:10])}
```

## Agentic SDLC Integration

This project is managed by [Agentic SDLC](https://github.com/truongnat/agentic-sdlc).

### CLI Commands
```bash
asdlc run "your task"     # Process a task through the AI pipeline
asdlc status              # View SDLC board
asdlc task next           # Get next task
```

### Workflows (Antigravity)
- `/asdlc-run` — Process a task request
- `/asdlc-status` — Check board status
- `/asdlc-task-next` — Get and execute next task

## Rules for AI Agents

> [!CAUTION]
> **ALWAYS** read `CONTEXT.md` before making changes.

> [!TIP]
> This is a **{profile.framework}** project. Use {profile.language}-idiomatic patterns.
"""


def generate_context_md(profile: ProjectProfile) -> str:
    """Generate a project-specific CONTEXT.md from a ProjectProfile."""
    return f"""# {profile.name} — Project Context

> This document helps AI agents understand this project's architecture.

## Overview

| Property | Value |
|----------|-------|
| Language | {profile.language} |
| Framework | {profile.framework} |
| Tests | {"✅ Yes" if profile.has_tests else "❌ No"} |
| Docker | {"✅ Yes" if profile.has_docker else "❌ No"} |
| CI/CD | {"✅ Yes" if profile.has_ci else "❌ No"} |

## Directory Structure

```
{chr(10).join(f"├── {d}/" for d in profile.key_directories[:10])}
```

{f"## Key Dependencies" + chr(10) + chr(10).join(f"- {d}" for d in profile.dependencies[:10]) if profile.dependencies else ""}

## Agentic SDLC

This project uses `asdlc` for AI-assisted development. See `GEMINI.md` for commands and workflows.
"""
