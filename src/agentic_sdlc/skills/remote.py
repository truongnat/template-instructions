"""Remote Skill Registry - Pull and install skills from remote sources.

Supports pulling skills from:
- GitHub repositories
- NPX-style skill packages (npx skills)
- Custom API endpoints

Includes mandatory security scanning before installation.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logging import get_logger
from .loader import SkillLoader
from .skill import Skill

logger = get_logger(__name__)

# Patterns considered unsafe in skill YAML/markdown
UNSAFE_PATTERNS = [
    r"subprocess\.\w+",
    r"os\.system\s*\(",
    r"exec\s*\(",
    r"eval\s*\(",
    r"__import__\s*\(",
    r"import\s+os",
    r"import\s+subprocess",
    r"rm\s+-rf",
    r"curl\s+.*\|\s*(sh|bash)",
    r"wget\s+.*\|\s*(sh|bash)",
    r"<script",
    r"javascript:",
    r"\bsudo\b",
    r"chmod\s+777",
    r"\.env\b",
    r"API_KEY|SECRET|PASSWORD|TOKEN",
]


class SecurityScanResult:
    """Result of security scanning a skill."""

    def __init__(self) -> None:
        self.safe: bool = True
        self.warnings: List[str] = []
        self.blocked_patterns: List[str] = []
        self.scanned_files: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "safe": self.safe,
            "warnings": self.warnings,
            "blocked_patterns": self.blocked_patterns,
            "scanned_files": self.scanned_files,
        }


class RemoteSkillRegistry:
    """Pull and install skills from remote sources with security scanning.

    All remote skills are security-scanned before installation.
    Unsafe patterns (shell injection, exec, env access) are blocked.

    Example:
        >>> remote = RemoteSkillRegistry(install_dir=Path(".agentic_sdlc/skills/remote"))
        >>> result = remote.pull_from_github("user/repo", "skills/my-skill")
        >>> if result["safe"]:
        ...     skills = result["skills"]
    """

    def __init__(self, install_dir: Path) -> None:
        """Initialize the remote registry.

        Args:
            install_dir: Directory to install remote skills into.
        """
        self._install_dir = install_dir
        self._loader = SkillLoader()
        self._install_dir.mkdir(parents=True, exist_ok=True)

    def pull_from_github(
        self,
        repo: str,
        skill_path: str = "skills",
        branch: str = "main",
    ) -> Dict[str, Any]:
        """Pull skills from a GitHub repository.

        Clones the repo (sparse checkout), scans for security,
        and copies approved skills to the install directory.

        Args:
            repo: GitHub repo in "user/repo" format.
            skill_path: Path within the repo to skills directory.
            branch: Git branch to pull from.

        Returns:
            Dictionary with 'safe', 'skills', 'scan_result' keys.
        """
        logger.info("Pulling skills from GitHub: %s/%s", repo, skill_path)

        # Create temp directory for clone
        temp_dir = self._install_dir / ".tmp_clone"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Sparse clone
            url = f"https://github.com/{repo}.git"
            clone_target = temp_dir / repo.replace("/", "_")

            if clone_target.exists():
                import shutil
                shutil.rmtree(clone_target)

            subprocess.run(
                [
                    "git", "clone", "--depth=1", "--single-branch",
                    f"--branch={branch}", url, str(clone_target),
                ],
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )

            # Scan and install
            skills_source = clone_target / skill_path
            if not skills_source.exists():
                return {
                    "safe": False,
                    "skills": [],
                    "error": f"Path not found in repo: {skill_path}",
                }

            # Security scan
            scan = self.scan_directory(skills_source)
            if not scan.safe:
                logger.warning(
                    "Security scan FAILED for %s: %s",
                    repo,
                    scan.blocked_patterns,
                )
                return {
                    "safe": False,
                    "skills": [],
                    "scan_result": scan.to_dict(),
                }

            # Copy approved skills
            return self._install_from_directory(skills_source, repo)

        except subprocess.CalledProcessError as e:
            logger.error("Git clone failed: %s", e.stderr)
            return {"safe": False, "skills": [], "error": f"Clone failed: {e.stderr}"}
        except Exception as e:
            logger.error("Pull failed: %s", e)
            return {"safe": False, "skills": [], "error": str(e)}
        finally:
            # Cleanup temp
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

    def pull_from_npx(self, package_name: str) -> Dict[str, Any]:
        """Pull skills via npx-style package.

        Runs `npx <package>` and scans the output directory.

        Args:
            package_name: NPX package name (e.g. "@agentic-sdlc/skills").

        Returns:
            Dictionary with results.
        """
        logger.info("Pulling skills via npx: %s", package_name)

        temp_dir = self._install_dir / ".tmp_npx"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # First, security-check the package name
            if not re.match(r"^[@a-zA-Z0-9._/-]+$", package_name):
                return {
                    "safe": False,
                    "skills": [],
                    "error": f"Invalid package name: {package_name}",
                }

            # Run npx to install to temp dir
            result = subprocess.run(
                ["npx", "-y", package_name, "--output", str(temp_dir)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(temp_dir),
            )

            if result.returncode != 0:
                return {
                    "safe": False,
                    "skills": [],
                    "error": f"npx failed: {result.stderr}",
                }

            # Scan output
            scan = self.scan_directory(temp_dir)
            if not scan.safe:
                return {
                    "safe": False,
                    "skills": [],
                    "scan_result": scan.to_dict(),
                }

            return self._install_from_directory(temp_dir, f"npx:{package_name}")

        except Exception as e:
            return {"safe": False, "skills": [], "error": str(e)}
        finally:
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)

    def scan_directory(self, directory: Path) -> SecurityScanResult:
        """Security scan all files in a directory.

        Checks for unsafe patterns like shell injection, exec calls,
        env variable access, and other dangerous operations.

        Args:
            directory: Directory to scan.

        Returns:
            SecurityScanResult with findings.
        """
        result = SecurityScanResult()

        # Scan YAML and MD files
        patterns_to_scan = list(directory.rglob("*.yaml")) + \
                          list(directory.rglob("*.yml")) + \
                          list(directory.rglob("*.md"))

        for filepath in patterns_to_scan:
            result.scanned_files += 1
            try:
                content = filepath.read_text(encoding="utf-8")
                self._scan_content(content, str(filepath), result)
            except Exception as e:
                result.warnings.append(f"Could not read {filepath}: {e}")

        return result

    def scan_skill(self, skill: Skill) -> SecurityScanResult:
        """Security scan a single skill definition.

        Args:
            skill: Skill to scan.

        Returns:
            SecurityScanResult.
        """
        result = SecurityScanResult()
        result.scanned_files = 1

        # Scan all text content
        content = skill.to_skill_md() + "\n" + str(skill.to_yaml_dict())
        self._scan_content(content, skill.name, result)

        return result

    def _scan_content(
        self,
        content: str,
        source: str,
        result: SecurityScanResult,
    ) -> None:
        """Scan content for unsafe patterns."""
        for pattern in UNSAFE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result.safe = False
                result.blocked_patterns.append(
                    f"[{source}] Blocked pattern '{pattern}': {matches[:3]}"
                )

    def _install_from_directory(
        self,
        source_dir: Path,
        origin: str,
    ) -> Dict[str, Any]:
        """Install scanned skills from a directory."""
        skills = self._loader.load_directory(source_dir)

        # Copy skill files to install dir
        installed = []
        for skill in skills:
            from .skill import SkillSource
            skill.source = SkillSource.REMOTE

            # Save as YAML
            import yaml
            dest = self._install_dir / f"{skill.name}.yaml"
            with open(dest, "w", encoding="utf-8") as f:
                yaml.safe_dump(skill.to_yaml_dict(), f, default_flow_style=False)

            installed.append(skill)
            logger.info("Installed remote skill: %s (from %s)", skill.name, origin)

        return {
            "safe": True,
            "skills": installed,
            "installed_count": len(installed),
        }
