"""Code example management for documentation system.

This module provides functionality to create, validate, and extract code examples
for documentation purposes.
"""

import ast
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from .models import CodeExample, Category


@dataclass
class ValidationResult:
    """Result of code example validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class CodeValidator:
    """Validates Python code examples."""
    
    def validate_syntax(self, code: str) -> ValidationResult:
        """Validate Python syntax using AST.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with validation status and any errors
        """
        errors = []
        warnings = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        return ValidationResult(is_valid=True, errors=errors, warnings=warnings)


class CodeExampleManager:
    """Manage code examples for documentation."""
    
    def __init__(self, examples_dir: str):
        """Initialize CodeExampleManager.
        
        Args:
            examples_dir: Directory path for storing code examples
        """
        self.examples_dir = Path(examples_dir)
        self.validator = CodeValidator()
        self.examples_dir.mkdir(parents=True, exist_ok=True)
    
    def create_example(
        self,
        name: str,
        code: str,
        description: str,
        category: str = "basic",
        dependencies: Optional[List[str]] = None,
        setup_instructions: Optional[str] = None,
        expected_output: Optional[str] = None,
        notes: Optional[List[str]] = None
    ) -> CodeExample:
        """Create a new code example.
        
        Args:
            name: Example name
            code: Python code
            description: Vietnamese description
            category: Category (basic, intermediate, advanced)
            dependencies: List of required dependencies
            setup_instructions: Setup instructions for running the example
            expected_output: Expected output when running the example
            notes: Additional notes about the example
            
        Returns:
            CodeExample object
        """
        # Convert category string to Category enum
        if isinstance(category, str):
            category_enum = Category[category.upper()]
        else:
            category_enum = category
        
        # Ensure required fields have defaults
        if dependencies is None:
            dependencies = []
        if setup_instructions is None:
            setup_instructions = "No setup required"
        if expected_output is None:
            expected_output = "No output specified"
        if notes is None:
            notes = []
        
        return CodeExample(
            name=name,
            description=description,
            category=category_enum,
            code=code,
            dependencies=dependencies,
            setup_instructions=setup_instructions,
            expected_output=expected_output,
            notes=notes
        )
    
    def validate_example(self, example: CodeExample) -> ValidationResult:
        """Validate that code example runs without errors.
        
        Args:
            example: CodeExample to validate
            
        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Validate code syntax
        syntax_result = self.validator.validate_syntax(example.code)
        if not syntax_result.is_valid:
            errors.extend(syntax_result.errors)
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Validate required fields
        if not example.setup_instructions or len(example.setup_instructions.strip()) == 0:
            errors.append("Missing setup_instructions")
        
        if not example.expected_output or len(example.expected_output.strip()) == 0:
            errors.append("Missing expected_output")
        
        if not example.dependencies or not isinstance(example.dependencies, list):
            warnings.append("No dependencies specified")
        
        if not example.description or len(example.description.strip()) == 0:
            errors.append("Missing description")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
    
    def extract_from_source(self, source_file: Path) -> List[CodeExample]:
        """Extract code examples from existing source files.
        
        This method looks for specially formatted comments in source files
        that mark code examples for documentation.
        
        Args:
            source_file: Path to source file
            
        Returns:
            List of CodeExample objects extracted from the file
        """
        examples = []
        
        if not source_file.exists():
            return examples
        
        content = source_file.read_text(encoding='utf-8')
        
        # Pattern to match example blocks:
        # # EXAMPLE: name
        # # DESCRIPTION: description
        # # CATEGORY: basic|intermediate|advanced
        # # DEPENDENCIES: dep1, dep2
        # # SETUP: setup instructions
        # # OUTPUT: expected output
        # code here
        # # END EXAMPLE
        
        pattern = r'# EXAMPLE: (.+?)\n# DESCRIPTION: (.+?)\n# CATEGORY: (.+?)\n# DEPENDENCIES: (.+?)\n# SETUP: (.+?)\n# OUTPUT: (.+?)\n(.*?)# END EXAMPLE'
        
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            name = match.group(1).strip()
            description = match.group(2).strip()
            category = match.group(3).strip()
            dependencies_str = match.group(4).strip()
            setup = match.group(5).strip()
            output = match.group(6).strip()
            code = match.group(7).strip()
            
            # Parse dependencies
            dependencies = [d.strip() for d in dependencies_str.split(',') if d.strip()]
            
            example = self.create_example(
                name=name,
                code=code,
                description=description,
                category=category,
                dependencies=dependencies,
                setup_instructions=setup,
                expected_output=output
            )
            
            examples.append(example)
        
        return examples
