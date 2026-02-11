# Implementation Plan: SDK Reorganization

## Overview

This implementation plan transforms the Agentic SDLC Kit from its current structure into a professional SDK following Python best practices. The approach is incremental, maintaining backward compatibility during migration, and focuses on creating a clean separation between SDK core and CLI interface.

The implementation follows a phased approach:
1. **Phase 1**: Create new structure alongside existing code (no breaking changes)
2. **Phase 2**: Migrate code and add deprecation warnings
3. **Phase 3**: Remove old structure and finalize (breaking changes for v3.0.0)

Each task builds on previous work, with checkpoints to ensure stability before proceeding.

## Tasks

- [x] 1. Create new directory structure and build configuration
  - Create `src/agentic_sdlc/` directory structure with core, infrastructure, intelligence, orchestration, plugins, cli, and _internal subdirectories
  - Create `resources/` directory for templates, workflows, and rules
  - Update `pyproject.toml` to use src layout and configure package discovery
  - Add `py.typed` marker file for type hint support
  - _Requirements: 1.1, 1.3, 1.4, 11.1, 11.3_

- [x] 2. Implement core module foundation
  - [x] 2.1 Create exception hierarchy
    - Implement `AgenticSDLCError` base exception with context support
    - Implement specific exception classes: `ConfigurationError`, `ValidationError`, `PluginError`, `WorkflowError`, `AgentError`, `ModelError`
    - Add `__init__.py` exports for core exceptions
    - _Requirements: 15.1_
  
  - [x] 2.2 Write unit tests for exception hierarchy
    - Test exception creation with and without context
    - Test exception string representation
    - Test exception inheritance chain
    - _Requirements: 15.1_
  
  - [x] 2.3 Create logging configuration module
    - Implement `setup_logging()` function with level, file, and format configuration
    - Implement `get_logger()` function for module-specific loggers
    - Add `__init__.py` exports for logging functions
    - _Requirements: 15.3, 15.4_
  
  - [x] 2.4 Create version management
    - Create `_version.py` with version string
    - Implement version reading from VERSION file if present
    - Export `__version__` in core `__init__.py`
    - _Requirements: 12.1, 12.2, 12.3_
  
  - [x] 2.5 Write unit tests for version management
    - Test version string format matches semver
    - Test version is accessible from public API
    - _Requirements: 12.3, 12.6_

- [-] 3. Implement configuration system with validation
  - [x] 3.1 Define configuration data models using Pydantic
    - Create `types.py` module in core with Pydantic models
    - Implement `ModelConfig` with provider, model_name, api_key, temperature, max_tokens, timeout fields
    - Implement `AgentConfig` with name, role, model, system_prompt, tools, max_iterations fields
    - Implement `WorkflowConfig` with name, description, agents, steps, timeout fields
    - Implement `SDKConfig` with project_root, log_level, log_file, models, workflows, plugins, defaults_dir fields
    - Add validation rules and field descriptions for all models
    - _Requirements: 6.1, 6.5_
  
  - [x] 3.2 Implement Config class
    - Create `config.py` module in core
    - Implement `__init__()` to load from file, environment variables, and defaults
    - Implement `get()` method with dot notation support (e.g., "models.openai.temperature")
    - Implement `set()` method with validation using Pydantic
    - Implement `validate()` method to check entire configuration against schema
    - Implement `merge()` method for combining configurations with proper precedence
    - Add `load_config()` and `get_config()` module-level functions
    - _Requirements: 6.1, 6.4, 6.5, 6.6_
  
  - [x] 3.3 Write property test for configuration validation
    - **Property 5: Configuration Validation**
    - **Validates: Requirements 6.5**
    - Test that invalid values (wrong type, out of range, missing required fields) raise ValidationError
    - Test that error messages include the field name and valid values
  
  - [x] 3.4 Write property test for configuration override consistency
    - **Property 4: Configuration Override Consistency**
    - **Validates: Requirements 6.4**
    - Test that setting via environment variables, files, and API calls produces same result
    - Test that Config.get() returns consistent values regardless of how they were set
  
  - [x] 3.5 Write property test for configuration merging
    - **Property 6: Configuration Merging**
    - **Validates: Requirements 6.6**
    - Test that merged config contains all defaults for unspecified keys
    - Test that user-specified keys override defaults
    - Test that merging multiple times is idempotent
  
  - [x] 3.6 Write unit tests for Config class
    - Test loading from YAML/JSON configuration file
    - Test loading from environment variables with prefix
    - Test dot notation access for nested values
    - Test invalid configuration file handling
    - Test missing required fields raise ValidationError
    - _Requirements: 6.1, 6.4, 6.5, 6.6_

- [x] 4. Implement plugin system
  - [x] 4.1 Create plugin base class and interface
    - Create `base.py` module in plugins with abstract `Plugin` class
    - Define abstract properties: `name`, `version`
    - Define abstract methods: `initialize(config)`, `shutdown()`
    - Create `PluginMetadata` Pydantic model with name, version, author, description, dependencies, entry_point, config_schema
    - Add comprehensive docstrings documenting plugin interface
    - _Requirements: 10.1, 10.3_
  
  - [x] 4.2 Implement plugin registry
    - Create `registry.py` module in plugins with `PluginRegistry` class
    - Implement `register(plugin)` method with interface validation
    - Implement `unregister(name)` method
    - Implement `get(name)` method returning Optional[Plugin]
    - Implement `load_from_entry_points()` to load plugins from setuptools entry points
    - Add error isolation with try-except blocks to prevent plugin failures from crashing SDK
    - Create singleton `get_plugin_registry()` function
    - _Requirements: 10.2, 10.4, 10.5, 10.6_
  
  - [x] 4.3 Write property test for plugin registration round-trip
    - **Property 7: Plugin Registration Round-Trip**
    - **Validates: Requirements 10.2**
    - Test that for any registered plugin, retrieving it by name returns the same instance
    - Test that plugin metadata is preserved through registration
  
  - [x] 4.4 Write property test for plugin failure isolation
    - **Property 8: Plugin Failure Isolation**
    - **Validates: Requirements 10.5**
    - Test that when a plugin raises an exception during initialization, SDK catches it and continues
    - Test that other plugins can still be loaded after one fails
    - Test that failure is logged with context
  
  - [x] 4.5 Write property test for plugin interface validation
    - **Property 9: Plugin Interface Validation**
    - **Validates: Requirements 10.6**
    - Test that objects without required methods are rejected during registration
    - Test that error message lists missing methods
    - Test that valid plugins pass validation
  
  - [x] 4.6 Write unit tests for plugin system
    - Test plugin registration and retrieval
    - Test loading from entry points
    - Test error handling for invalid plugins (missing methods, wrong types)
    - Test plugin lifecycle (initialize called on load, shutdown called on unload)
    - Test plugin metadata validation
    - _Requirements: 10.2, 10.4, 10.5, 10.6_

- [x] 5. Checkpoint - Core foundation complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Migrate and reorganize infrastructure module
  - [x] 6.1 Create infrastructure module structure
    - Create subdirectories: automation, bridge, engine, lifecycle
    - Move existing infrastructure code to new locations
    - Update internal imports to use new structure
    - _Requirements: 5.2_
  
  - [x] 6.2 Define infrastructure public API
    - Create `__init__.py` with explicit exports
    - Export: `WorkflowEngine`, `WorkflowRunner`, `Bridge`, `BridgeRegistry`, `ExecutionEngine`, `TaskExecutor`, `LifecycleManager`, `Phase`
    - Add type hints to all exported functions and classes
    - _Requirements: 3.1, 3.4, 5.2_
  
  - [x] 6.3 Write unit tests for infrastructure components
    - Test workflow engine execution
    - Test bridge registry
    - Test task executor
    - Test lifecycle manager
    - _Requirements: 5.2_

- [x] 7. Migrate and reorganize intelligence module
  - [x] 7.1 Create intelligence module structure
    - Create subdirectories: learning, monitoring, reasoning, collaboration
    - Move existing intelligence code to new locations
    - Update internal imports to use new structure
    - _Requirements: 5.3_
  
  - [x] 7.2 Define intelligence public API
    - Create `__init__.py` with explicit exports
    - Export: `Learner`, `LearningStrategy`, `Monitor`, `MetricsCollector`, `Reasoner`, `DecisionEngine`, `Collaborator`, `TeamCoordinator`
    - Add type hints to all exported functions and classes
    - _Requirements: 3.1, 3.4, 5.3_
  
  - [x] 7.3 Write unit tests for intelligence components
    - Test learner functionality
    - Test monitoring and metrics collection
    - Test reasoning engine
    - Test collaboration coordinator
    - _Requirements: 5.3_

- [x] 8. Migrate and reorganize orchestration module
  - [x] 8.1 Create orchestration module structure
    - Create subdirectories: agents, models, workflows, coordination
    - Move existing orchestration code to new locations
    - Update internal imports to use new structure
    - _Requirements: 5.4_
  
  - [x] 8.2 Define orchestration public API
    - Create `__init__.py` with explicit exports
    - Export: `Agent`, `AgentRegistry`, `create_agent`, `ModelClient`, `ModelConfig`, `get_model_client`, `Workflow`, `WorkflowBuilder`, `Coordinator`, `ExecutionPlan`
    - Add type hints to all exported functions and classes
    - _Requirements: 3.1, 3.4, 5.4_
  
  - [x] 8.3 Write unit tests for orchestration components
    - Test agent creation and registry
    - Test model client configuration
    - Test workflow builder
    - Test coordination logic
    - _Requirements: 5.4_

- [x] 9. Checkpoint - Domain modules migrated
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Separate and refactor CLI module
  - [x] 10.1 Create CLI module structure
    - Create `cli/` subdirectory with main.py and commands/
    - Move CLI code from root-level cli.py to new location
    - _Requirements: 4.1_
  
  - [x] 10.2 Refactor CLI to use SDK public API
    - Update all CLI commands to import from `agentic_sdlc` public API
    - Remove any direct imports from internal modules
    - Ensure CLI only uses public API functions and classes
    - _Requirements: 4.1, 4.2, 4.5_
  
  - [x] 10.3 Make CLI dependencies optional
    - Move click and rich to optional-dependencies in pyproject.toml
    - Add [cli] extra: `pip install agentic-sdlc[cli]`
    - Update CLI imports to handle missing dependencies gracefully
    - _Requirements: 4.3, 4.4_
  
  - [x] 10.4 Write integration tests for CLI commands
    - Test CLI commands execute successfully
    - Test CLI uses SDK public API
    - Test CLI works with optional dependencies
    - _Requirements: 4.1, 4.5_

- [x] 11. Create top-level public API
  - [x] 11.1 Implement main `__init__.py` with explicit exports
    - Create comprehensive `agentic_sdlc/__init__.py` with all public exports
    - Import and re-export from core, infrastructure, intelligence, orchestration, plugins
    - Define `__all__` list with all public symbols (50+ items)
    - Add module docstring describing the SDK and its purpose
    - Export `__version__` from _version module
    - Organize imports by domain for clarity
    - _Requirements: 3.1, 3.2, 12.2_
  
  - [x] 11.2 Write property test for internal module privacy
    - **Property 2: Internal Module Privacy**
    - **Validates: Requirements 3.3**
    - Test that modules prefixed with underscore are not in __all__
    - Test that importing from _internal raises AttributeError or DeprecationWarning
    - Test that public API doesn't expose private implementation details
  
  - [x] 11.3 Write property test for public API type hints
    - **Property 3: Public API Type Hints**
    - **Validates: Requirements 3.4**
    - Test that all functions in public API have return type hints
    - Test that all parameters have type hints (except self, cls)
    - Test that type hints are valid and importable
  
  - [x] 11.4 Write unit tests for public API
    - Test all exported symbols are accessible from top-level import
    - Test version is accessible and matches semver format
    - Test imports work correctly without errors
    - Test that importing from public API doesn't import heavy dependencies
    - _Requirements: 3.1, 3.2, 12.2_

- [x] 12. Migrate dependencies from lib/ to pyproject.toml
  - [x] 12.1 Document all vendored dependencies
    - Create comprehensive list of all packages in lib/ directory
    - Identify version of each vendored package (check setup.py, requirements.txt, or package metadata)
    - Document any custom modifications made to vendored packages
    - Create DEPENDENCIES.md documenting migration plan
    - _Requirements: 2.2_
  
  - [x] 12.2 Add dependencies to pyproject.toml
    - Add all identified dependencies to [project.dependencies] section
    - Specify version constraints for each dependency (minimum and maximum versions)
    - Separate development dependencies to [project.optional-dependencies.dev]
    - Add CLI dependencies to [project.optional-dependencies.cli]
    - Verify all constraints are compatible
    - _Requirements: 2.1, 2.3, 2.4_
  
  - [x] 12.3 Write property test for dependency version constraints
    - **Property 1: Dependency Version Constraints**
    - **Validates: Requirements 2.3**
    - Test that all dependencies in pyproject.toml have version constraints
    - Test that version constraints are valid (e.g., ">=1.0.0,<2.0.0")
    - Test that no dependency has unconstrained version (e.g., just "package-name")
  
  - [x] 12.4 Test installation without lib/ directory
    - Create clean virtual environment
    - Install SDK from source: `pip install -e .`
    - Verify all imports work without lib/ directory
    - Test that all core functionality works
    - Test that CLI works with [cli] extra: `pip install -e ".[cli]"`
    - _Requirements: 2.1, 2.5_
  
  - [x] 12.5 Remove lib/ directory
    - Delete agentic_sdlc/lib/ directory completely
    - Update .gitignore if needed
    - Verify no code references lib/ directory
    - _Requirements: 2.2_

- [x] 13. Checkpoint - Dependencies migrated
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Move resources and package data
  - [x] 14.1 Migrate templates, workflows, and rules
    - Move defaults/ content to resources/ directory
    - Update package data configuration in pyproject.toml
    - Update code to load resources from new location
    - _Requirements: 6.2, 11.4_
  
  - [x] 14.2 Write unit tests for resource loading
    - Test templates can be loaded
    - Test workflows can be loaded
    - Test rules can be loaded
    - Test resources are included in package
    - _Requirements: 6.2, 6.3_

- [x] 15. Add deprecation warnings for old imports
  - [x] 15.1 Create compatibility shims for old import paths
    - Add `__getattr__` to old module locations to intercept imports
    - Emit DeprecationWarning with clear migration instructions
    - Point to new import locations with examples
    - Ensure old imports still work but warn users
    - Test that old code continues to function
    - _Requirements: 13.1, 13.2, 13.3, 13.6_
  
  - [x] 15.2 Write property test for deprecation warning emission
    - **Property 10: Deprecation Warning Emission**
    - **Validates: Requirements 13.2**
    - Test that importing from old locations emits DeprecationWarning
    - Test that warning is emitted exactly once per import (not multiple times)
    - Test that warning includes the deprecated path and new path
  
  - [x] 15.3 Write property test for deprecation warning content
    - **Property 11: Deprecation Warning Content**
    - **Validates: Requirements 13.6**
    - Test that warning message includes function/class name
    - Test that warning message includes migration instructions
    - Test that warning message specifies what to use instead
    - Test that warning message is clear and actionable
  
  - [x] 15.4 Write unit tests for backward compatibility
    - Test old imports still work (e.g., from agentic_sdlc.infrastructure.autogen.agents import create_agent_by_role)
    - Test deprecation warnings are emitted with correct stacklevel
    - Test warning messages contain migration instructions
    - Test that new imports work without warnings
    - _Requirements: 13.1, 13.2, 13.6_

- [x] 16. Reorganize test suite
  - [x] 16.1 Create new test directory structure
    - Create tests/unit/ directory for unit tests
    - Create tests/integration/ directory for integration tests
    - Create tests/property/ directory for property-based tests
    - Create tests/fixtures/ directory for shared test data and mock objects
    - Create tests/conftest.py with pytest configuration and shared fixtures
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 16.2 Move existing tests to new structure
    - Migrate unit tests to tests/unit/ mirroring source structure (e.g., tests/unit/core/, tests/unit/infrastructure/)
    - Migrate integration tests to tests/integration/
    - Move all property tests to tests/property/
    - Update all test imports to use new package structure (from agentic_sdlc import ...)
    - Verify all tests still pass after migration
    - _Requirements: 7.1, 7.2_
  
  - [x] 16.3 Configure pytest and coverage
    - Update pytest.ini_options in pyproject.toml with test discovery patterns
    - Configure coverage to measure new source layout (src/agentic_sdlc/)
    - Add test markers for unit, integration, property tests
    - Configure minimum coverage threshold (80% for core)
    - Add coverage exclusions for __init__.py files if needed
    - _Requirements: 7.1, 7.2_
  
  - [x] 16.4 Run full test suite and verify coverage
    - Execute all tests: `pytest`
    - Ensure all tests pass
    - Generate coverage report: `pytest --cov=agentic_sdlc --cov-report=html`
    - Verify minimum 80% coverage for core functionality
    - Verify 100% coverage for public API functions
    - _Requirements: 7.4, 7.5_

- [x] 17. Checkpoint - Testing infrastructure complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Create examples and documentation
  - [x] 18.1 Create example directory structure
    - Create examples/programmatic/ for SDK usage examples
    - Create examples/cli/ for CLI usage examples
    - Create examples/plugins/ for plugin development examples
    - Create README.md in each directory explaining the examples
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  
  - [x] 18.2 Write programmatic SDK examples
    - Example 1: Basic configuration and setup (loading config, setting up logging)
    - Example 2: Running a workflow programmatically (creating and executing workflows)
    - Example 3: Creating and using agents (agent creation, configuration, execution)
    - Example 4: Custom plugin development (implementing Plugin interface, registering)
    - Each example should be complete, runnable, and well-commented
    - _Requirements: 9.2, 9.4_
  
  - [x] 18.3 Write CLI usage examples
    - Example 1: Initializing a project (agentic init)
    - Example 2: Running workflows via CLI (agentic run workflow-name)
    - Example 3: Configuration management (setting config values, viewing config)
    - Each example should show command and expected output
    - _Requirements: 9.3_
  
  - [x] 18.4 Test all examples
    - Create automated tests that run each example
    - Verify examples execute without errors
    - Verify examples produce expected output
    - Update examples if SDK API changes
    - _Requirements: 9.5, 9.6_
  
  - [x] 18.5 Create documentation structure
    - Create docs/api/ for API documentation (generated from docstrings)
    - Create docs/guides/ for user guides (getting started, configuration, plugins)
    - Create docs/architecture/ for architecture documentation (design decisions, module overview)
    - Create docs/GETTING_STARTED.md with installation and basic usage
    - Create docs/MIGRATION.md documenting migration from v2.x to v3.x
    - Create docs/PLUGIN_DEVELOPMENT.md for plugin developers
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 19. Clean up repository structure
  - [x] 19.1 Remove backup and temporary directories
    - Delete .cleanup_backup/ directory
    - Delete backups/ directory
    - Delete claude_suggestion/ directory
    - Remove migration_scripts/ if no longer needed
    - Clean up any other temporary directories
    - Verify no important files are lost before deletion
    - _Requirements: 1.5_
  
  - [x] 19.2 Update root-level configuration files
    - Update .gitignore for new structure (remove old paths, add new ones)
    - Update MANIFEST.in if needed to include resources/
    - Update README.md with new structure, installation instructions, and usage examples
    - Update CHANGELOG.md with v3.0.0 changes and breaking changes
    - Add migration guide to README or separate MIGRATION.md
    - _Requirements: 8.5, 13.4_

- [x] 20. Validate package structure and build
  - [x] 20.1 Validate pyproject.toml configuration
    - Verify all required metadata is present (name, version, description, author, license)
    - Verify dependencies are correctly specified with version constraints
    - Verify package data configuration includes resources/ and py.typed
    - Verify entry points are configured correctly
    - Verify optional dependencies are properly defined ([cli], [dev])
    - Run `python -m build --sdist --wheel --outdir /tmp/dist` to validate
    - _Requirements: 11.1, 11.3_
  
  - [x] 20.2 Build source distribution and wheel
    - Run `python -m build` to create distributions
    - Verify sdist (source distribution) is created successfully
    - Verify wheel (binary distribution) is created successfully
    - Verify both distributions contain correct files
    - Check file sizes are reasonable
    - _Requirements: 11.2, 11.5_
  
  - [x] 20.3 Test installation from built package
    - Create clean virtual environment
    - Install from built wheel: `pip install /tmp/dist/agentic_sdlc-3.0.0-py3-none-any.whl`
    - Test imports work correctly: `python -c "from agentic_sdlc import __version__; print(__version__)"`
    - Test CLI works with [cli] extra: `pip install /tmp/dist/agentic_sdlc-3.0.0-py3-none-any.whl[cli]`
    - Test examples run successfully
    - Verify package data (resources/) is accessible
    - _Requirements: 2.5, 11.2_
  
  - [x] 20.4 Write integration tests for package installation
    - Test pip install works from source
    - Test optional dependencies work ([cli], [dev])
    - Test package data is accessible at runtime
    - Test version is accessible from installed package
    - Test all public API symbols are importable
    - _Requirements: 2.5, 4.4, 11.4_

- [x] 21. Final checkpoint - SDK reorganization complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities to address issues
- Property tests validate universal correctness properties across random inputs
- Unit tests validate specific examples, edge cases, and integration points
- The migration maintains backward compatibility until the final cleanup phase
- All property tests should run with minimum 100 iterations as configured in pyproject.toml
- Breaking changes are isolated to Phase 3 (tasks 19-21) and will require major version bump to 3.0.0
