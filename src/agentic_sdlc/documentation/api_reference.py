"""API reference documentation generator.

This module provides the APIReferenceGenerator class for automatically
generating API reference documentation from Python source code.
"""

import inspect
import importlib
import pkgutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Type, Callable, get_type_hints
import ast
import re

from .models import (
    APIReferenceDocument,
    ClassReference,
    FunctionReference,
    MethodReference,
    PropertyReference,
    Parameter,
    ReturnValue,
    ConstantReference,
    CodeBlock,
    Section,
    DocumentType,
    Category
)
from .translation import TranslationManager


class APIReferenceGenerator:
    """Generate API reference documentation from source code.
    
    This class scans Python modules, extracts class and function information
    using the inspect module, and generates comprehensive API documentation
    in Vietnamese.
    """
    
    def __init__(self, source_dir: str, glossary_file: str = "docs/vi/glossary.yaml"):
        """Initialize APIReferenceGenerator.
        
        Args:
            source_dir: Path to source directory to scan
            glossary_file: Path to glossary file for translations
        """
        self.source_dir = Path(source_dir)
        self.translator = TranslationManager(glossary_file)
    
    def generate_module_docs(self, module_path: str) -> APIReferenceDocument:
        """Generate documentation for a Python module.
        
        Scans the module and extracts all public classes, functions, and constants.
        
        Args:
            module_path: Python module path (e.g., "agentic_sdlc.core.config")
            
        Returns:
            APIReferenceDocument with complete module documentation
        """
        # Import the module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Cannot import module {module_path}: {e}")
        
        # Extract module docstring
        module_doc = inspect.getdoc(module) or ""
        translated_doc = self._translate_docstring(module_doc)
        
        # Extract classes
        classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Only document classes defined in this module
            if obj.__module__ == module_path and not name.startswith('_'):
                class_ref = self.generate_class_docs(obj)
                classes.append(class_ref)
        
        # Extract functions
        functions = []
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            # Only document functions defined in this module
            if obj.__module__ == module_path and not name.startswith('_'):
                func_ref = self.generate_function_docs(obj)
                functions.append(func_ref)
        
        # Extract constants (module-level variables)
        constants = []
        for name in dir(module):
            if not name.startswith('_') and name.isupper():
                obj = getattr(module, name)
                if not inspect.isclass(obj) and not inspect.isfunction(obj):
                    const_ref = self._generate_constant_docs(name, obj, module)
                    constants.append(const_ref)
        
        # Create sections
        sections = [
            Section(
                title="Tổng Quan Module",
                content=translated_doc,
                subsections=None,
                code_blocks=None,
                diagrams=None
            )
        ]
        
        # Create API reference document
        doc = APIReferenceDocument(
            title=f"API Reference: {module_path}",
            type=DocumentType.API_REFERENCE,
            category=Category.ADVANCED,
            description=f"Tài liệu API cho module {module_path}",
            sections=sections,
            metadata={
                "module": module_path,
                "public_classes": len(classes),
                "public_functions": len(functions),
                "constants": len(constants)
            },
            last_updated="2024-01-01",
            version="3.0.0",
            module_path=module_path,
            classes=classes,
            functions=functions,
            constants=constants
        )
        
        return doc
    
    def generate_class_docs(self, cls: Type) -> ClassReference:
        """Generate documentation for a class.
        
        Extracts class information using inspect module including:
        - Class description (Vietnamese)
        - Constructor parameters
        - Methods with signatures
        - Properties
        - Usage examples
        
        Args:
            cls: Class object to document
            
        Returns:
            ClassReference with complete class documentation
        """
        # Extract class docstring
        class_doc = inspect.getdoc(cls) or ""
        translated_doc = self._translate_docstring(class_doc)
        
        # Extract constructor
        try:
            init_method = cls.__init__
            constructor = self._generate_method_docs(init_method, is_constructor=True)
        except AttributeError:
            # No custom __init__, create default
            constructor = MethodReference(
                name="__init__",
                signature="__init__(self)",
                description="Khởi tạo instance của class",
                parameters=[],
                returns=ReturnValue(type="None", description=""),
                raises=[],
                examples=[]
            )
        
        # Extract methods
        methods = []
        for name, method in inspect.getmembers(cls, inspect.isfunction):
            # Skip private methods and __init__
            if not name.startswith('_') or name in ['__str__', '__repr__']:
                method_ref = self._generate_method_docs(method)
                methods.append(method_ref)
        
        # Extract properties
        properties = []
        for name, obj in inspect.getmembers(cls):
            if isinstance(obj, property) and not name.startswith('_'):
                prop_ref = self._generate_property_docs(name, obj)
                properties.append(prop_ref)
        
        # Generate usage example
        examples = [
            CodeBlock(
                language="python",
                code=f"# Ví dụ sử dụng {cls.__name__}\nfrom {cls.__module__} import {cls.__name__}\n\n# Tạo instance\nobj = {cls.__name__}()\n",
                caption=f"Ví dụ cơ bản sử dụng {cls.__name__}",
                line_numbers=True
            )
        ]
        
        return ClassReference(
            name=cls.__name__,
            description=translated_doc,
            constructor=constructor,
            methods=methods,
            properties=properties,
            examples=examples
        )
    
    def generate_function_docs(self, func: Callable) -> FunctionReference:
        """Generate documentation for a function.
        
        Extracts function signature, parameters, return type, and docstring.
        
        Args:
            func: Function object to document
            
        Returns:
            FunctionReference with complete function documentation
        """
        # Get function signature
        try:
            sig = inspect.signature(func)
            signature_str = f"{func.__name__}{sig}"
        except (ValueError, TypeError):
            signature_str = f"{func.__name__}(...)"
        
        # Extract docstring
        func_doc = inspect.getdoc(func) or ""
        translated_doc = self._translate_docstring(func_doc)
        
        # Extract parameters
        parameters = []
        try:
            sig = inspect.signature(func)
            try:
                type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
            except (NameError, AttributeError):
                type_hints = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_type = type_hints.get(param_name, param.annotation)
                if param_type == inspect.Parameter.empty:
                    param_type_str = "Any"
                else:
                    param_type_str = self._format_type(param_type)
                
                param_default = param.default
                has_default = param_default != inspect.Parameter.empty
                
                parameters.append(Parameter(
                    name=param_name,
                    type=param_type_str,
                    description=f"Tham số {param_name}",
                    default=param_default if has_default else None,
                    required=not has_default
                ))
        except (ValueError, TypeError):
            pass
        
        # Extract return type
        try:
            try:
                type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
            except (NameError, AttributeError):
                type_hints = {}
            return_type = type_hints.get('return', inspect.signature(func).return_annotation)
            if return_type == inspect.Signature.empty:
                return_type_str = "Any"
            else:
                return_type_str = self._format_type(return_type)
        except (ValueError, TypeError):
            return_type_str = "Any"
        
        returns = ReturnValue(
            type=return_type_str,
            description="Giá trị trả về"
        )
        
        # Extract exceptions from docstring
        raises = self._extract_exceptions_from_docstring(func_doc)
        
        # Generate usage example
        examples = [
            CodeBlock(
                language="python",
                code=f"# Ví dụ sử dụng {func.__name__}\nfrom {func.__module__} import {func.__name__}\n\nresult = {func.__name__}()\n",
                caption=f"Ví dụ sử dụng {func.__name__}",
                line_numbers=True
            )
        ]
        
        return FunctionReference(
            name=func.__name__,
            signature=signature_str,
            description=translated_doc,
            parameters=parameters,
            returns=returns,
            raises=raises,
            examples=examples
        )
    
    def extract_docstring(self, obj: Any) -> str:
        """Extract and translate docstring to Vietnamese.
        
        Args:
            obj: Python object (class, function, method, module)
            
        Returns:
            Translated docstring in Vietnamese
        """
        docstring = inspect.getdoc(obj) or ""
        return self._translate_docstring(docstring)
    
    def _generate_method_docs(self, method: Callable, is_constructor: bool = False) -> MethodReference:
        """Generate documentation for a method.
        
        Args:
            method: Method object to document
            is_constructor: Whether this is a constructor method
            
        Returns:
            MethodReference with complete method documentation
        """
        # Get method signature
        try:
            sig = inspect.signature(method)
            signature_str = f"{method.__name__}{sig}"
        except (ValueError, TypeError):
            signature_str = f"{method.__name__}(...)"
        
        # Extract docstring
        method_doc = inspect.getdoc(method) or ""
        translated_doc = self._translate_docstring(method_doc)
        
        # Extract parameters
        parameters = []
        try:
            sig = inspect.signature(method)
            try:
                type_hints = get_type_hints(method) if hasattr(method, '__annotations__') else {}
            except (NameError, AttributeError):
                type_hints = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_type = type_hints.get(param_name, param.annotation)
                if param_type == inspect.Parameter.empty:
                    param_type_str = "Any"
                else:
                    param_type_str = self._format_type(param_type)
                
                param_default = param.default
                has_default = param_default != inspect.Parameter.empty
                
                parameters.append(Parameter(
                    name=param_name,
                    type=param_type_str,
                    description=f"Tham số {param_name}",
                    default=param_default if has_default else None,
                    required=not has_default
                ))
        except (ValueError, TypeError):
            pass
        
        # Extract return type
        try:
            try:
                type_hints = get_type_hints(method) if hasattr(method, '__annotations__') else {}
            except (NameError, AttributeError):
                type_hints = {}
            return_type = type_hints.get('return', inspect.signature(method).return_annotation)
            if return_type == inspect.Signature.empty:
                return_type_str = "None" if is_constructor else "Any"
            else:
                return_type_str = self._format_type(return_type)
        except (ValueError, TypeError):
            return_type_str = "None" if is_constructor else "Any"
        
        returns = ReturnValue(
            type=return_type_str,
            description="Giá trị trả về"
        )
        
        # Extract exceptions from docstring
        raises = self._extract_exceptions_from_docstring(method_doc)
        
        return MethodReference(
            name=method.__name__,
            signature=signature_str,
            description=translated_doc,
            parameters=parameters,
            returns=returns,
            raises=raises,
            examples=[]
        )
    
    def _generate_property_docs(self, name: str, prop: property) -> PropertyReference:
        """Generate documentation for a property.
        
        Args:
            name: Property name
            prop: Property object
            
        Returns:
            PropertyReference with property documentation
        """
        # Extract docstring from property getter
        prop_doc = inspect.getdoc(prop.fget) if prop.fget else ""
        translated_doc = self._translate_docstring(prop_doc)
        
        # Determine if readonly
        readonly = prop.fset is None
        
        # Try to get type hint
        try:
            if prop.fget:
                try:
                    type_hints = get_type_hints(prop.fget)
                except (NameError, AttributeError):
                    type_hints = {}
                prop_type = type_hints.get('return', 'Any')
                prop_type_str = self._format_type(prop_type)
            else:
                prop_type_str = "Any"
        except (ValueError, TypeError, NameError):
            prop_type_str = "Any"
        
        return PropertyReference(
            name=name,
            type=prop_type_str,
            description=translated_doc or f"Property {name}",
            readonly=readonly
        )
    
    def _generate_constant_docs(self, name: str, value: Any, module: Any) -> ConstantReference:
        """Generate documentation for a module constant.
        
        Args:
            name: Constant name
            value: Constant value
            module: Module containing the constant
            
        Returns:
            ConstantReference with constant documentation
        """
        # Get type
        value_type = type(value).__name__
        
        # Get string representation
        value_str = repr(value)
        if len(value_str) > 100:
            value_str = value_str[:97] + "..."
        
        return ConstantReference(
            name=name,
            type=value_type,
            value=value_str,
            description=f"Hằng số {name}"
        )
    
    def _translate_docstring(self, docstring: str) -> str:
        """Translate docstring to Vietnamese.
        
        This is a simple implementation that keeps the docstring as-is
        but could be enhanced with actual translation logic.
        
        Args:
            docstring: Original docstring
            
        Returns:
            Translated docstring
        """
        if not docstring:
            return ""
        
        # For now, keep English docstrings but add Vietnamese prefix
        # In a real implementation, this would use translation service
        return docstring
    
    def _format_type(self, type_hint: Any) -> str:
        """Format type hint as string.
        
        Args:
            type_hint: Type hint object
            
        Returns:
            String representation of type
        """
        if type_hint is None or type_hint == type(None):
            return "None"
        
        if hasattr(type_hint, '__name__'):
            return type_hint.__name__
        
        # Handle typing module types
        type_str = str(type_hint)
        
        # Clean up typing module prefix
        type_str = type_str.replace('typing.', '')
        
        return type_str
    
    def _extract_exceptions_from_docstring(self, docstring: str) -> List[str]:
        """Extract exception types from docstring.
        
        Looks for "Raises:" section in docstring.
        
        Args:
            docstring: Function/method docstring
            
        Returns:
            List of exception type names
        """
        if not docstring:
            return []
        
        exceptions = []
        
        # Look for "Raises:" section
        raises_pattern = re.compile(r'Raises:\s*\n\s*(\w+(?:Error|Exception))', re.MULTILINE)
        matches = raises_pattern.findall(docstring)
        
        exceptions.extend(matches)
        
        return exceptions
