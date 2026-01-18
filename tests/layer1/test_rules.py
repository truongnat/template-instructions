
import pytest
from pathlib import Path

RULES_DIR = Path("agentic_sdlc/defaults/rules")
GEMINI_FILE = Path("agentic_sdlc/defaults/GEMINI.md")

def test_rules_directory_exists():
    assert RULES_DIR.exists()
    assert RULES_DIR.is_dir()

def test_gemini_rules():
    assert GEMINI_FILE.exists()
    content = GEMINI_FILE.read_text(encoding="utf-8")
    assert "MANDATORY COMPLIANCE" in content
    assert "Pre-Flight Checklist" in content
    assert "Gate 1: PRE-TASK" in content

def test_global_rules():
    global_rule = RULES_DIR / "global.md"
    if global_rule.exists():
        content = global_rule.read_text(encoding="utf-8")
        assert "Rules" in content or "Protocol" in content
