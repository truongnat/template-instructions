"""
Property-based tests for Public API Type Hints (SDK Reorganization).

These tests use Hypothesis and AST analysis to verify that all functions
in the public API have complete type hints for parameters and return values.

Feature: sdk-reorganization
Property 3: Public API Type Hints
Requirements: 3.4
"""

import ast
import inspect
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple

import pytest
from hypothesis import given, strategies as st, settings

import agentic_sdlc


def get_public_api_symbols() -> List[Tuple[str, Any]]:
    """Get all symbols exported in the public API.
    
    Returns:
        List of (name, object) tuples for all symbols in __all__
    """
    symbols = []
    for name in agentic_sdlc.__all__:
        try:
            obj = getattr(agentic_sdlc, name)
            symbols.append((name, obj))
        except AttributeError:
            pass
    return symbols


def is_function_or_method(obj: Any) -> bool:
    """Check if object is a function or method."""
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def is_class(obj: Any) -> bool:
    """Check if object is a class."""
    return inspect.isclass(obj)


def get_function_signature(func: Any) -> Optional[inspect.Signature]:
    """Get function signature, handling edge cases."""
    try:
        return inspect.signature(func)
    except (ValueError, TypeError):
        return None


def has_return_type_hint(func: Any) -> bool:
    """Check if function has a return type hint.
    
    Args:
        func: Function to check
        
    Returns:
        True if function has return type hint, False otherwise
    """
    sig = get_function_signature(func)
    if sig is None:
        return False
    
    return sig.return_annotation != inspect.Signature.empty


def has_parameter_type_hints(func: Any) -> Tuple[bool, List[str]]:
    """Check if all parameters have type hints (except self, cls).
    
    Args:
        func: Function to check
        
    Returns:
        Tuple of (all_have_hints, missing_hints_params)
    """
    sig = get_function_signature(func)
    if sig is None:
        return False, []
    
    missing_hints = []
    for param_name, param in sig.parameters.items():
        # Skip self and cls parameters
        if param_name in ("self", "cls"):
            continue
        
        # Skip *args and **kwargs
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        
        # Check if parameter has type hint
        if param.annotation == inspect.Parameter.empty:
            missing_hints.append(param_name)
    
    return len(missing_hints) == 0, missing_hints


def is_type_hint_valid(annotation: Any) -> bool:
    """Check if a type hint is valid and importable.
    
    Args:
        annotation: Type annotation to check
        
    Returns:
        True if annotation is valid, False otherwise
    """
    if annotation == inspect.Signature.empty:
        return False
    
    if annotation is None:
        return True
    
    # Check if it's a string annotation (forward reference)
    if isinstance(annotation, str):
        return True
    
    # Check if it's a type
    try:
        # Try to get the module of the annotation
        if hasattr(annotation, "__module__"):
            return True
        # For generic types like List, Dict, etc.
        if hasattr(annotation, "__origin__"):
            return True
        # For basic types
        if isinstance(annotation, type):
            return True
    except Exception:
        pass
    
    return False


# Feature: sdk-reorganization, Property 3: Public API Type Hints
def test_all_public_functions_have_return_type_hints():
    """
    Property: For any function in the public API, it SHALL have a return type hint.
    
    This property ensures that all public functions declare what they return,
    making the API more discoverable and enabling better IDE support.
    
    **Validates: Requirements 3.4**
    """
    symbols = get_public_api_symbols()
    
    functions_without_return_hints = []
    for name, obj in symbols:
        if is_function_or_method(obj):
            if not has_return_type_hint(obj):
                functions_without_return_hints.append(name)
    
    assert len(functions_without_return_hints) == 0, (
        f"Functions in public API should have return type hints. "
        f"Missing return hints: {functions_without_return_hints}"
    )


# Feature: sdk-reorganization, Property 3: Public API Type Hints
def test_all_public_function_parameters_have_type_hints():
    """
    Property: For any function in the public API, all parameters (except self, cls)
    SHALL have type hints.
    
    This property ensures that all public function parameters are typed,
    making the API contract clear and enabling better IDE support.
    
    **Validates: Requirements 3.4**
    """
    symbols = get_public_api_symbols()
    
    functions_with_missing_hints = []
    for name, obj in symbols:
        if is_function_or_method(obj):
            all_have_hints, missing_hints = has_parameter_type_hints(obj)
            if not all_have_hints:
                functions_with_missing_hints.append((name, missing_hints))
    
    assert len(functions_with_missing_hints) == 0, (
        f"All parameters in public API functions should have type hints. "
        f"Functions with missing parameter hints: {functions_with_missing_hints}"
    )


# Feature: sdk-reorganization, Property 3: Public API Type Hints
def test_all_public_class_methods_have_type_hints():
    """
    Property: For any method in a public class, it SHALL have complete type hints
    for parameters and return values (except self, cls).
    
    This property ensures that all public class methods are properly typed.
    
    **Validates: Requirements 3.4**
    """
    symbols = get_public_api_symbols()
    
    methods_with_missing_hints = []
    for name, obj in symbols:
        if is_class(obj):
            # Check all public methods
            for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                # Skip private methods
                if method_name.startswith("_"):
                    continue
                
                # Check return type hint
                if not has_return_type_hint(method):
                    methods_with_missing_hints.append(
                        (f"{name}.{method_name}", "missing return hint")
                    )
                
                # Check parameter type hints
                all_have_hints, missing_hints = has_parameter_type_hints(method)
                if not all_have_hints:
                    methods_with_missing_hints.append(
                        (f"{name}.{method_name}", f"missing parameter hints: {missing_hints}")
                    )
    
    assert len(methods_with_missing_hints) == 0, (
        f"All methods in public classes should have type hints. "
        f"Methods with missing hints: {methods_with_missing_hints}"
    )


# Feature: sdk-reorganization, Property 3: Public API Type Hints
def test_type_hints_are_valid_and_importable():
    """
    Property: For any type hint in the public API, it SHALL be valid and importable.
    
    This property ensures that type hints reference valid types that can be
    imported and used by external code.
    
    **Validates: Requirements 3.4**
    """
    symbols = get_public_api_symbols()
    
    invalid_type_hints = []
    for name, obj in symbols:
        if is_function_or_method(obj):
            sig = get_function_signature(obj)
            if sig is None:
                continue
            
            # Check return type hint
            if not is_type_hint_valid(sig.return_annotation):
                invalid_type_hints.append(
                    (name, "return", str(sig.return_annotation))
                )
            
            # Check parameter type hints
            for param_name, param in sig.parameters.items():
                if param_name in ("self", "cls"):
                    continue
                if not is_type_hint_valid(param.annotation):
                    invalid_type_hints.append(
                        (name, param_name, str(param.annotation))
                    )
    
    assert len(invalid_type_hints) == 0, (
        f"All type hints in public API should be valid. "
        f"Invalid type hints: {invalid_type_hints}"
    )


# Feature: sdk-reorganization, Property 3: Public API Type Hints
@given(symbol_name=st.sampled_from([name for name, _ in get_public_api_symbols()]))
@settings(max_examples=100, deadline=None)
def test_each_public_symbol_has_proper_type_hints(symbol_name):
    """
    Property: For any symbol in the public API, if it's a function,
    it SHALL have complete type hints.
    
    This property uses property-based testing to verify type hints
    for each symbol in the public API.
    
    **Validates: Requirements 3.4**
    """
    obj = getattr(agentic_sdlc, symbol_name)
    
    # Skip non-function symbols
    if not is_function_or_method(obj):
        return
    
    # Check return type hint
    assert has_return_type_hint(obj), (
        f"Function {symbol_name} should have return type hint"
    )
    
    # Check parameter type hints
    all_have_hints, missing_hints = has_parameter_type_hints(obj)
    assert all_have_hints, (
        f"Function {symbol_name} should have type hints for all parameters. "
        f"Missing: {missing_hints}"
    )


# Feature: sdk-reorganization, Property 3: Public API Type Hints
def test_exception_classes_have_proper_type_hints():
    """
    Property: For any exception class in the public API, its __init__ method
    SHALL have complete type hints.
    
    This property ensures that exception classes are properly typed.
    
    **Validates: Requirements 3.4**
    """
    symbols = get_public_api_symbols()
    
    exception_classes_with_missing_hints = []
    for name, obj in symbols:
        if is_class(obj) and issubclass(obj, BaseException):
            # Check __init__ method
            init_method = obj.__init__
            
            # Check return type hint (should be None)
            if not has_return_type_hint(init_method):
                exception_classes_with_missing_hints.append(
                    (name, "missing return hint")
                )
            
            # Check parameter type hints
            all_have_hints, missing_hints = has_parameter_type_hints(init_method)
            if not all_have_hints:
                exception_classes_with_missing_hints.append(
                    (name, f"missing parameter hints: {missing_hints}")
                )
    
    assert len(exception_classes_with_missing_hints) == 0, (
        f"Exception classes should have proper type hints. "
        f"Classes with missing hints: {exception_classes_with_missing_hints}"
    )


# Feature: sdk-reorganization, Property 3: Public API Type Hints
def test_public_api_functions_return_type_is_not_empty():
    """
    Property: For any function in the public API, its return type annotation
    SHALL NOT be empty (inspect.Signature.empty).
    
    This property ensures that all public functions explicitly declare their return type.
    
    **Validates: Requirements 3.4**
    """
    symbols = get_public_api_symbols()
    
    functions_with_empty_return = []
    for name, obj in symbols:
        if is_function_or_method(obj):
            sig = get_function_signature(obj)
            if sig is not None and sig.return_annotation == inspect.Signature.empty:
                functions_with_empty_return.append(name)
    
    assert len(functions_with_empty_return) == 0, (
        f"All public functions should have explicit return type hints. "
        f"Functions with empty return type: {functions_with_empty_return}"
    )


# Feature: sdk-reorganization, Property 3: Public API Type Hints
def test_public_api_consistency_of_type_hints():
    """
    Property: For any function in the public API, if it's called multiple times
    with the same arguments, the type hints should remain consistent.
    
    This property ensures that type hints don't change dynamically.
    
    **Validates: Requirements 3.4**
    """
    symbols = get_public_api_symbols()
    
    # Store initial type hints
    initial_hints = {}
    for name, obj in symbols:
        if is_function_or_method(obj):
            sig = get_function_signature(obj)
            if sig is not None:
                initial_hints[name] = (
                    sig.return_annotation,
                    {
                        param_name: param.annotation
                        for param_name, param in sig.parameters.items()
                    },
                )
    
    # Check that type hints remain the same
    for name, obj in symbols:
        if is_function_or_method(obj):
            sig = get_function_signature(obj)
            if sig is not None and name in initial_hints:
                initial_return, initial_params = initial_hints[name]
                
                # Return type should be the same
                assert sig.return_annotation == initial_return, (
                    f"Return type hint for {name} changed"
                )
                
                # Parameter types should be the same
                for param_name, param in sig.parameters.items():
                    if param_name in initial_params:
                        assert param.annotation == initial_params[param_name], (
                            f"Parameter type hint for {name}.{param_name} changed"
                        )
