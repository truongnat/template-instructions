"""Translation management for Vietnamese documentation.

This module provides the TranslationManager class for managing Vietnamese
translations and technical terminology consistency across documentation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import re


class TranslationManager:
    """Manage Vietnamese translations and terminology.
    
    This class handles loading glossary terms, translating technical terms,
    adding new terms, and validating terminology consistency in documents.
    """
    
    def __init__(self, glossary_file: str):
        """Initialize TranslationManager with a glossary file.
        
        Args:
            glossary_file: Path to the YAML glossary file
        """
        self.glossary_file = Path(glossary_file)
        self.glossary: Dict[str, Dict[str, Any]] = {}
        self.technical_terms: Dict[str, str] = {}
        self.load_glossary()
    
    def load_glossary(self) -> None:
        """Load glossary from YAML file.
        
        Reads the glossary file and populates the internal glossary
        and technical_terms dictionaries for quick lookup.
        
        Raises:
            FileNotFoundError: If glossary file doesn't exist
            yaml.YAMLError: If glossary file is not valid YAML
        """
        if not self.glossary_file.exists():
            raise FileNotFoundError(f"Glossary file not found: {self.glossary_file}")
        
        with open(self.glossary_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'terms' not in data:
            raise ValueError("Invalid glossary format: missing 'terms' key")
        
        # Build lookup dictionaries
        for term in data['terms']:
            english = term.get('english', '')
            vietnamese = term.get('vietnamese', '')
            
            if english and vietnamese:
                self.glossary[english.lower()] = term
                self.technical_terms[english.lower()] = vietnamese
    
    def translate_term(self, english_term: str) -> str:
        """Translate technical term to Vietnamese.
        
        Returns Vietnamese translation with English term in parentheses.
        If term is not in glossary, returns the original term.
        
        Args:
            english_term: English technical term to translate
            
        Returns:
            Translated term in format "Vietnamese (English)" or original term
            
        Examples:
            >>> tm = TranslationManager("glossary.yaml")
            >>> tm.translate_term("Agent")
            "Tác nhân (Agent)"
            >>> tm.translate_term("Unknown")
            "Unknown"
        """
        term_lower = english_term.lower()
        
        if term_lower in self.technical_terms:
            vietnamese = self.technical_terms[term_lower]
            return f"{vietnamese} ({english_term})"
        
        return english_term
    
    def add_term(self, english: str, vietnamese: str, 
                 description: str = "", 
                 usage_examples: Optional[List[str]] = None,
                 related_terms: Optional[List[str]] = None) -> None:
        """Add new term to glossary.
        
        Adds a new technical term to the in-memory glossary and updates
        the glossary file.
        
        Args:
            english: English term
            vietnamese: Vietnamese translation
            description: Description of the term
            usage_examples: List of usage examples
            related_terms: List of related terms
        """
        term_entry = {
            'english': english,
            'vietnamese': vietnamese,
            'description': description,
            'usage_examples': usage_examples or [],
            'related_terms': related_terms or []
        }
        
        # Add to in-memory glossary
        self.glossary[english.lower()] = term_entry
        self.technical_terms[english.lower()] = vietnamese
        
        # Update the glossary file
        self._save_glossary()
    
    def _save_glossary(self) -> None:
        """Save glossary to YAML file.
        
        Internal method to persist glossary changes to disk.
        """
        # Convert glossary dict back to list format
        terms_list = list(self.glossary.values())
        
        data = {'terms': terms_list}
        
        with open(self.glossary_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, 
                     default_flow_style=False)
    
    def validate_consistency(self, document: str) -> List[Dict[str, Any]]:
        """Check terminology consistency in document.
        
        Validates that technical terms in the document follow the glossary
        and identifies potential issues like:
        - Terms that should be translated but aren't
        - Inconsistent usage of terms
        - Terms not in glossary
        
        Args:
            document: Document content as string
            
        Returns:
            List of issues found, each as a dict with:
                - type: Issue type (missing_translation, inconsistent, unknown_term)
                - term: The term in question
                - line: Line number where issue was found
                - suggestion: Suggested fix
        """
        issues: List[Dict[str, Any]] = []
        lines = document.split('\n')
        
        # Pattern to find potential technical terms (capitalized words)
        term_pattern = re.compile(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b')
        
        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith('```') or line.strip().startswith('    '):
                continue
            
            # Find potential technical terms
            matches = term_pattern.findall(line)
            
            for match in matches:
                term_lower = match.lower()
                
                # Check if term is in glossary
                if term_lower in self.glossary:
                    # Check if it's used with Vietnamese translation
                    expected_format = self.translate_term(match)
                    
                    # If term appears alone without Vietnamese, flag it
                    if match in line and expected_format not in line:
                        # Check if Vietnamese translation appears nearby
                        vietnamese = self.technical_terms[term_lower]
                        if vietnamese not in line:
                            issues.append({
                                'type': 'missing_translation',
                                'term': match,
                                'line': line_num,
                                'suggestion': f'Use "{expected_format}" instead of "{match}"'
                            })
        
        return issues
    
    def get_term_info(self, english_term: str) -> Optional[Dict[str, Any]]:
        """Get full information about a term from glossary.
        
        Args:
            english_term: English term to look up
            
        Returns:
            Dictionary with term information or None if not found
        """
        return self.glossary.get(english_term.lower())
    
    def search_terms(self, query: str) -> List[Dict[str, Any]]:
        """Search for terms matching a query.
        
        Searches both English and Vietnamese terms for matches.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching term entries
        """
        query_lower = query.lower()
        results = []
        
        for term_entry in self.glossary.values():
            english = term_entry.get('english', '').lower()
            vietnamese = term_entry.get('vietnamese', '').lower()
            description = term_entry.get('description', '').lower()
            
            if (query_lower in english or 
                query_lower in vietnamese or 
                query_lower in description):
                results.append(term_entry)
        
        return results
    
    def get_all_terms(self) -> List[Dict[str, Any]]:
        """Get all terms in the glossary.
        
        Returns:
            List of all term entries
        """
        return list(self.glossary.values())
