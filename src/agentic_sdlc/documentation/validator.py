"""Document validator for checking documentation quality and consistency.

This module provides the DocumentValidator class for validating documentation
structure, content, code examples, and cross-references.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass

from .models import (
    Document,
    GuideDocument,
    UseCaseDocument,
    APIReferenceDocument,
    DocumentType,
    Section,
    CodeBlock,
)


@dataclass
class ValidationError:
    """Represents a validation error in a document."""
    file_path: str
    error_type: str
    message: str
    line_number: Optional[int] = None
    severity: str = "error"  # "error", "warning", "info"


class DocumentValidator:
    """Validate documentation content for quality and consistency.
    
    This class provides methods to validate document structure, content completeness,
    code example syntax, and cross-references between documents.
    """
    
    def __init__(self, docs_root: str):
        """Initialize DocumentValidator.
        
        Args:
            docs_root: Root directory of documentation
        """
        self.docs_root = Path(docs_root)
        self.all_doc_files: Set[Path] = set()
        self._scan_documents()
    
    def _scan_documents(self) -> None:
        """Scan documentation directory to find all markdown files."""
        if self.docs_root.exists():
            self.all_doc_files = set(self.docs_root.rglob("*.md"))
    
    def validate_document(self, doc_path: Path) -> List[ValidationError]:
        """Validate a complete document.
        
        Args:
            doc_path: Path to the document file
            
        Returns:
            List of validation errors found
        """
        errors = []
        
        if not doc_path.exists():
            errors.append(ValidationError(
                file_path=str(doc_path),
                error_type="file_not_found",
                message=f"Document file not found: {doc_path}",
                severity="error"
            ))
            return errors
        
        # Read document content
        try:
            content = doc_path.read_text(encoding='utf-8')
        except Exception as e:
            errors.append(ValidationError(
                file_path=str(doc_path),
                error_type="read_error",
                message=f"Failed to read document: {e}",
                severity="error"
            ))
            return errors
        
        # Run all validation checks
        errors.extend(self.validate_structure(doc_path, content))
        errors.extend(self.validate_content(doc_path, content))
        errors.extend(self.validate_code_examples(doc_path, content))
        errors.extend(self.validate_cross_references(doc_path, content))
        
        return errors
    
    def validate_structure(self, doc_path: Path, content: str) -> List[ValidationError]:
        """Validate document structure matches template requirements.
        
        Args:
            doc_path: Path to the document file
            content: Document content
            
        Returns:
            List of validation errors
        """
        errors = []
        relative_path = str(doc_path.relative_to(self.docs_root))
        
        # Check for title (H1 heading)
        if not re.search(r'^#\s+.+', content, re.MULTILINE):
            errors.append(ValidationError(
                file_path=relative_path,
                error_type="missing_title",
                message="Document missing H1 title",
                severity="error"
            ))
        
        # Check for metadata (version and last updated)
        has_version = re.search(r'\*\*Phiên bản\*\*:', content) or \
                     re.search(r'\*\*Version\*\*:', content)
        has_updated = re.search(r'\*\*Cập nhật lần cuối\*\*:', content) or \
                     re.search(r'\*\*Last Updated\*\*:', content)
        
        if not has_version:
            errors.append(ValidationError(
                file_path=relative_path,
                error_type="missing_metadata",
                message="Document missing version information",
                severity="warning"
            ))
        
        if not has_updated:
            errors.append(ValidationError(
                file_path=relative_path,
                error_type="missing_metadata",
                message="Document missing last updated date",
                severity="warning"
            ))
        
        # Check for proper heading hierarchy
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        if headings:
            prev_level = 0
            for i, (hashes, title) in enumerate(headings):
                level = len(hashes)
                if level > prev_level + 1 and prev_level > 0:
                    errors.append(ValidationError(
                        file_path=relative_path,
                        error_type="heading_hierarchy",
                        message=f"Heading hierarchy skip detected: '{title}' (level {level} after level {prev_level})",
                        severity="warning"
                    ))
                prev_level = level
        
        # Validate specific document types
        if 'use-cases' in str(doc_path):
            errors.extend(self._validate_use_case_structure(relative_path, content))
        elif 'api-reference' in str(doc_path):
            errors.extend(self._validate_api_reference_structure(relative_path, content))
        elif 'guides' in str(doc_path):
            errors.extend(self._validate_guide_structure(relative_path, content))
        
        return errors
    
    def _validate_use_case_structure(self, file_path: str, content: str) -> List[ValidationError]:
        """Validate use case document structure."""
        errors = []
        required_sections = [
            r'##\s+Tổng Quan',
            r'##\s+Kịch Bản',
            r'##\s+Triển Khai',
        ]
        
        for section_pattern in required_sections:
            if not re.search(section_pattern, content):
                section_name = section_pattern.replace(r'##\s+', '')
                errors.append(ValidationError(
                    file_path=file_path,
                    error_type="missing_section",
                    message=f"Use case missing required section: {section_name}",
                    severity="error"
                ))
        
        return errors
    
    def _validate_api_reference_structure(self, file_path: str, content: str) -> List[ValidationError]:
        """Validate API reference document structure."""
        errors = []
        
        # Check for module path
        if not re.search(r'\*\*Module\*\*:\s*`[^`]+`', content):
            errors.append(ValidationError(
                file_path=file_path,
                error_type="missing_module_path",
                message="API reference missing module path",
                severity="error"
            ))
        
        return errors
    
    def _validate_guide_structure(self, file_path: str, content: str) -> List[ValidationError]:
        """Validate guide document structure."""
        errors = []
        
        # Check for introduction section
        if not re.search(r'##\s+Giới Thiệu', content):
            errors.append(ValidationError(
                file_path=file_path,
                error_type="missing_section",
                message="Guide missing 'Giới Thiệu' (Introduction) section",
                severity="warning"
            ))
        
        return errors
    
    def validate_content(self, doc_path: Path, content: str) -> List[ValidationError]:
        """Validate content completeness and quality.
        
        Args:
            doc_path: Path to the document file
            content: Document content
            
        Returns:
            List of validation errors
        """
        errors = []
        relative_path = str(doc_path.relative_to(self.docs_root))
        
        # Check for minimum content length
        if len(content.strip()) < 100:
            errors.append(ValidationError(
                file_path=relative_path,
                error_type="insufficient_content",
                message="Document content is too short (< 100 characters)",
                severity="warning"
            ))
        
        # Check for empty sections
        sections = re.findall(r'^##\s+(.+)$\n\n(.*?)(?=^##|\Z)', content, 
                             re.MULTILINE | re.DOTALL)
        for section_title, section_content in sections:
            if len(section_content.strip()) < 10:
                errors.append(ValidationError(
                    file_path=relative_path,
                    error_type="empty_section",
                    message=f"Section '{section_title}' has insufficient content",
                    severity="warning"
                ))
        
        # Check for Vietnamese language usage
        if 'vi/' in str(doc_path):
            # Check if document has substantial Vietnamese content
            vietnamese_chars = len(re.findall(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', 
                                             content, re.IGNORECASE))
            total_alpha = len(re.findall(r'[a-zA-Zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', 
                                        content, re.IGNORECASE))
            
            if total_alpha > 100 and vietnamese_chars < total_alpha * 0.1:
                errors.append(ValidationError(
                    file_path=relative_path,
                    error_type="language_consistency",
                    message="Document in vi/ directory should contain Vietnamese content",
                    severity="warning"
                ))
        
        # Check for technical terms with English in parentheses
        # Look for common technical terms that should have translations
        technical_terms = ['Agent', 'Workflow', 'Plugin', 'CLI', 'API', 'SDK']
        for term in technical_terms:
            # Check if term appears without Vietnamese explanation
            pattern = rf'\b{term}\b(?!\s*\([^)]*\))'
            matches = re.finditer(pattern, content)
            count = sum(1 for _ in matches)
            if count > 3:  # Allow a few occurrences without translation
                errors.append(ValidationError(
                    file_path=relative_path,
                    error_type="missing_translation",
                    message=f"Technical term '{term}' appears frequently without Vietnamese explanation",
                    severity="info"
                ))
        
        return errors
    
    def validate_code_examples(self, doc_path: Path, content: str) -> List[ValidationError]:
        """Validate all code examples are syntactically correct.
        
        Args:
            doc_path: Path to the document file
            content: Document content
            
        Returns:
            List of validation errors
        """
        errors = []
        relative_path = str(doc_path.relative_to(self.docs_root))
        
        # Find all code blocks
        code_blocks = re.finditer(r'```(\w+)\n(.*?)```', content, re.DOTALL)
        
        for match in code_blocks:
            language = match.group(1)
            code = match.group(2)
            line_number = content[:match.start()].count('\n') + 1
            
            # Validate Python code
            if language.lower() in ['python', 'py']:
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    errors.append(ValidationError(
                        file_path=relative_path,
                        error_type="syntax_error",
                        message=f"Python syntax error in code block: {e.msg}",
                        line_number=line_number + (e.lineno or 0),
                        severity="error"
                    ))
                except Exception as e:
                    errors.append(ValidationError(
                        file_path=relative_path,
                        error_type="parse_error",
                        message=f"Failed to parse Python code: {str(e)}",
                        line_number=line_number,
                        severity="warning"
                    ))
            
            # Check for empty code blocks
            if len(code.strip()) == 0:
                errors.append(ValidationError(
                    file_path=relative_path,
                    error_type="empty_code_block",
                    message=f"Empty {language} code block found",
                    line_number=line_number,
                    severity="warning"
                ))
        
        # Check for code blocks without language specification
        unspecified_blocks = re.finditer(r'```\n(.*?)```', content, re.DOTALL)
        for match in unspecified_blocks:
            line_number = content[:match.start()].count('\n') + 1
            errors.append(ValidationError(
                file_path=relative_path,
                error_type="missing_language",
                message="Code block missing language specification",
                line_number=line_number,
                severity="warning"
            ))
        
        return errors
    
    def validate_cross_references(self, doc_path: Path, content: str) -> List[ValidationError]:
        """Validate all links point to existing documents.
        
        Args:
            doc_path: Path to the document file
            content: Document content
            
        Returns:
            List of validation errors
        """
        errors = []
        relative_path = str(doc_path.relative_to(self.docs_root))
        
        # Find all markdown links
        links = re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content)
        
        for match in links:
            link_text = match.group(1)
            link_url = match.group(2)
            line_number = content[:match.start()].count('\n') + 1
            
            # Skip external URLs
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            
            # Resolve relative path
            link_path = (doc_path.parent / link_url).resolve()
            
            # Check if linked file exists
            if not link_path.exists():
                errors.append(ValidationError(
                    file_path=relative_path,
                    error_type="broken_link",
                    message=f"Broken link to '{link_url}' (text: '{link_text}')",
                    line_number=line_number,
                    severity="error"
                ))
        
        # Find all reference-style links
        ref_links = re.finditer(r'\[([^\]]+)\]:\s*(.+)$', content, re.MULTILINE)
        for match in ref_links:
            link_id = match.group(1)
            link_url = match.group(2).strip()
            line_number = content[:match.start()].count('\n') + 1
            
            # Skip external URLs
            if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            
            # Resolve relative path
            link_path = (doc_path.parent / link_url).resolve()
            
            # Check if linked file exists
            if not link_path.exists():
                errors.append(ValidationError(
                    file_path=relative_path,
                    error_type="broken_reference",
                    message=f"Broken reference link '{link_id}' to '{link_url}'",
                    line_number=line_number,
                    severity="error"
                ))
        
        return errors
    
    def validate_all_documents(self) -> Dict[str, List[ValidationError]]:
        """Validate all documents in the documentation directory.
        
        Returns:
            Dictionary mapping file paths to their validation errors
        """
        results = {}
        
        for doc_file in self.all_doc_files:
            errors = self.validate_document(doc_file)
            if errors:
                results[str(doc_file.relative_to(self.docs_root))] = errors
        
        return results
    
    def generate_report(self, validation_results: Dict[str, List[ValidationError]]) -> str:
        """Generate a human-readable validation report.
        
        Args:
            validation_results: Dictionary of validation errors by file
            
        Returns:
            Formatted validation report
        """
        if not validation_results:
            return "✓ All documents passed validation!"
        
        report_lines = ["# Documentation Validation Report\n"]
        
        # Count errors by severity
        error_count = 0
        warning_count = 0
        info_count = 0
        
        for errors in validation_results.values():
            for error in errors:
                if error.severity == "error":
                    error_count += 1
                elif error.severity == "warning":
                    warning_count += 1
                else:
                    info_count += 1
        
        report_lines.append(f"## Summary\n")
        report_lines.append(f"- Files with issues: {len(validation_results)}")
        report_lines.append(f"- Errors: {error_count}")
        report_lines.append(f"- Warnings: {warning_count}")
        report_lines.append(f"- Info: {info_count}\n")
        
        # List issues by file
        report_lines.append("## Issues by File\n")
        
        for file_path, errors in sorted(validation_results.items()):
            report_lines.append(f"### {file_path}\n")
            
            for error in errors:
                severity_icon = {
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(error.severity, "•")
                
                line_info = f" (line {error.line_number})" if error.line_number else ""
                report_lines.append(
                    f"{severity_icon} **{error.error_type}**{line_info}: {error.message}"
                )
            
            report_lines.append("")
        
        return "\n".join(report_lines)
