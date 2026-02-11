"""Unit tests for configuration validator.

Tests the ConfigValidator class for loading and validating configuration files
against JSON schemas.
"""

import json
import pytest
import tempfile
from pathlib import Path
from config.validators import ConfigValidator, ValidationResult


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_validation_result_initialization(self):
        """Test ValidationResult can be initialized with default values."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.config_file is None
        assert result.schema_file is None
    
    def test_add_error_sets_invalid(self):
        """Test that adding an error sets is_valid to False."""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")
        assert result.is_valid is False
        assert "Test error" in result.errors
    
    def test_add_warning_preserves_validity(self):
        """Test that adding a warning doesn't change is_valid."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")
        assert result.is_valid is True
        assert "Test warning" in result.warnings
    
    def test_str_representation_valid(self):
        """Test string representation for valid result."""
        result = ValidationResult(is_valid=True, config_file="test.yaml")
        output = str(result)
        assert "✓ Valid" in output
        assert "test.yaml" in output
    
    def test_str_representation_invalid(self):
        """Test string representation for invalid result."""
        result = ValidationResult(is_valid=False, config_file="test.yaml")
        result.add_error("Missing required field")
        output = str(result)
        assert "✗ Invalid" in output
        assert "Missing required field" in output


class TestConfigValidator:
    """Tests for ConfigValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a ConfigValidator instance."""
        return ConfigValidator()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_validator_initialization(self, validator):
        """Test ConfigValidator can be initialized."""
        assert validator is not None
        assert validator.schema_dir == Path("config/schemas")
    
    def test_validator_custom_schema_dir(self, temp_dir):
        """Test ConfigValidator with custom schema directory."""
        validator = ConfigValidator(schema_dir=temp_dir)
        assert validator.schema_dir == temp_dir
    
    def test_load_yaml_config(self, validator, temp_dir):
        """Test loading a YAML configuration file."""
        config_file = temp_dir / "test.yaml"
        config_file.write_text("name: test\nversion: 1.0.0\n")
        
        config = validator.load_config(config_file)
        assert config["name"] == "test"
        assert config["version"] == "1.0.0"
    
    def test_load_json_config(self, validator, temp_dir):
        """Test loading a JSON configuration file."""
        config_file = temp_dir / "test.json"
        config_file.write_text('{"name": "test", "version": "1.0.0"}')
        
        config = validator.load_config(config_file)
        assert config["name"] == "test"
        assert config["version"] == "1.0.0"
    
    def test_load_config_file_not_found(self, validator):
        """Test loading a non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            validator.load_config("nonexistent.yaml")
    
    def test_load_config_unsupported_format(self, validator, temp_dir):
        """Test loading a file with unsupported format."""
        config_file = temp_dir / "test.txt"
        config_file.write_text("name: test")
        
        with pytest.raises(ValueError, match="Unsupported file format"):
            validator.load_config(config_file)
    
    def test_load_config_invalid_yaml(self, validator, temp_dir):
        """Test loading an invalid YAML file."""
        config_file = temp_dir / "test.yaml"
        config_file.write_text("name: test\n  invalid: indentation")
        
        with pytest.raises(ValueError, match="Failed to parse YAML"):
            validator.load_config(config_file)
    
    def test_load_config_invalid_json(self, validator, temp_dir):
        """Test loading an invalid JSON file."""
        config_file = temp_dir / "test.json"
        config_file.write_text('{"name": "test"')  # Missing closing brace
        
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            validator.load_config(config_file)
    
    def test_load_config_empty_file(self, validator, temp_dir):
        """Test loading an empty configuration file."""
        config_file = temp_dir / "test.yaml"
        config_file.write_text("")
        
        config = validator.load_config(config_file)
        assert config == {}
    
    def test_load_schema(self, validator, temp_dir):
        """Test loading a JSON schema file."""
        schema_file = temp_dir / "test.schema.json"
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"}
            }
        }
        schema_file.write_text(json.dumps(schema))
        
        loaded_schema = validator.load_schema(schema_file)
        assert loaded_schema["type"] == "object"
        assert "name" in loaded_schema["required"]
    
    def test_load_schema_file_not_found(self, validator):
        """Test loading a non-existent schema file."""
        with pytest.raises(FileNotFoundError):
            validator.load_schema("nonexistent.schema.json")
    
    def test_load_schema_invalid_json(self, validator, temp_dir):
        """Test loading an invalid JSON schema file."""
        schema_file = temp_dir / "test.schema.json"
        schema_file.write_text('{"type": "object"')  # Missing closing brace
        
        with pytest.raises(ValueError, match="Failed to parse schema"):
            validator.load_schema(schema_file)
    
    def test_load_schema_invalid_schema(self, validator, temp_dir):
        """Test loading a file with invalid JSON schema."""
        schema_file = temp_dir / "test.schema.json"
        schema = {"type": "invalid_type"}  # Invalid schema
        schema_file.write_text(json.dumps(schema))
        
        with pytest.raises(ValueError, match="Invalid JSON schema"):
            validator.load_schema(schema_file)
    
    def test_load_schema_caching(self, validator, temp_dir):
        """Test that schemas are cached after first load."""
        schema_file = temp_dir / "test.schema.json"
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object"
        }
        schema_file.write_text(json.dumps(schema))
        
        # Load twice
        schema1 = validator.load_schema(schema_file)
        schema2 = validator.load_schema(schema_file)
        
        # Should be the same object (cached)
        assert schema1 is schema2
    
    def test_validate_valid_config(self, validator):
        """Test validating a valid configuration."""
        config = {"name": "test", "version": "1.0.0"}
        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
            }
        }
        
        result = validator.validate(config, schema)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_missing_required_field(self, validator):
        """Test validating config with missing required field."""
        config = {"name": "test"}
        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
            }
        }
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "version" in result.errors[0]
        assert "required" in result.errors[0].lower()
    
    def test_validate_wrong_type(self, validator):
        """Test validating config with wrong field type."""
        config = {"name": "test", "version": 123}
        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
            }
        }
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "version" in result.errors[0]
        assert "type" in result.errors[0].lower()
    
    def test_validate_enum_violation(self, validator):
        """Test validating config with invalid enum value."""
        config = {"name": "test", "type": "invalid"}
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["valid1", "valid2"]}
            }
        }
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "type" in result.errors[0]
        assert "invalid" in result.errors[0]
    
    def test_validate_pattern_violation(self, validator):
        """Test validating config with pattern violation."""
        config = {"name": "test", "version": "invalid"}
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"}
            }
        }
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "version" in result.errors[0]
        assert "pattern" in result.errors[0].lower()
    
    def test_load_and_validate_success(self, validator, temp_dir):
        """Test load_and_validate with valid config and schema."""
        # Create config file
        config_file = temp_dir / "test.yaml"
        config_file.write_text("name: test\nversion: 1.0.0\n")
        
        # Create schema file
        schema_file = temp_dir / "test.schema.json"
        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
            }
        }
        schema_file.write_text(json.dumps(schema))
        
        result = validator.load_and_validate(config_file, schema_file)
        assert result.is_valid is True
        assert result.config_file == str(config_file)
        assert result.schema_file == str(schema_file)
    
    def test_load_and_validate_invalid_config(self, validator, temp_dir):
        """Test load_and_validate with invalid config."""
        # Create config file (missing required field)
        config_file = temp_dir / "test.yaml"
        config_file.write_text("name: test\n")
        
        # Create schema file
        schema_file = temp_dir / "test.schema.json"
        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
            }
        }
        schema_file.write_text(json.dumps(schema))
        
        result = validator.load_and_validate(config_file, schema_file)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_load_and_validate_config_not_found(self, validator, temp_dir):
        """Test load_and_validate with non-existent config file."""
        schema_file = temp_dir / "test.schema.json"
        schema = {"type": "object"}
        schema_file.write_text(json.dumps(schema))
        
        result = validator.load_and_validate("nonexistent.yaml", schema_file)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()
    
    def test_load_and_validate_schema_not_found(self, validator, temp_dir):
        """Test load_and_validate with non-existent schema file."""
        config_file = temp_dir / "test.yaml"
        config_file.write_text("name: test\n")
        
        result = validator.load_and_validate(config_file, "nonexistent.schema.json")
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()
    
    def test_validate_by_type_workflow(self, validator, temp_dir):
        """Test validate_by_type with workflow configuration."""
        # Create a minimal workflow config
        config_file = temp_dir / "workflow.yaml"
        config_file.write_text("name: test-workflow\nversion: 1.0.0\n")
        
        # This will fail if schema doesn't exist, but we're testing the method works
        result = validator.validate_by_type(config_file, "workflow")
        # Result may be valid or invalid depending on schema, but should not raise
        assert isinstance(result, ValidationResult)
    
    def test_validate_by_type_unknown_type(self, validator, temp_dir):
        """Test validate_by_type with unknown configuration type."""
        config_file = temp_dir / "test.yaml"
        config_file.write_text("name: test\n")
        
        result = validator.validate_by_type(config_file, "unknown_type")
        assert result.is_valid is False
        assert "Unknown configuration type" in result.errors[0]
    
    def test_format_validation_error_type(self, validator):
        """Test error formatting for type validation errors."""
        config = {"name": 123}
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        error_msg = result.errors[0]
        assert "name" in error_msg
        assert "string" in error_msg
        assert "int" in error_msg or "integer" in error_msg
    
    def test_format_validation_error_minimum(self, validator):
        """Test error formatting for minimum value violations."""
        config = {"count": 5}
        schema = {"type": "object", "properties": {"count": {"type": "integer", "minimum": 10}}}
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        error_msg = result.errors[0]
        assert "count" in error_msg
        assert "5" in error_msg
        assert "10" in error_msg
    
    def test_format_validation_error_maximum(self, validator):
        """Test error formatting for maximum value violations."""
        config = {"count": 100}
        schema = {"type": "object", "properties": {"count": {"type": "integer", "maximum": 50}}}
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        error_msg = result.errors[0]
        assert "count" in error_msg
        assert "100" in error_msg
        assert "50" in error_msg
    
    def test_format_validation_error_min_length(self, validator):
        """Test error formatting for minLength violations."""
        config = {"name": "ab"}
        schema = {"type": "object", "properties": {"name": {"type": "string", "minLength": 5}}}
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        error_msg = result.errors[0]
        assert "name" in error_msg
        assert "2" in error_msg
        assert "5" in error_msg
    
    def test_nested_field_validation(self, validator):
        """Test validation of nested fields."""
        config = {
            "name": "test",
            "metadata": {
                "version": 123  # Should be string
            }
        }
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "version": {"type": "string"}
                    }
                }
            }
        }
        
        result = validator.validate(config, schema)
        assert result.is_valid is False
        error_msg = result.errors[0]
        assert "metadata.version" in error_msg
