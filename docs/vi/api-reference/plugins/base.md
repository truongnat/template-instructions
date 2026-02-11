# API Reference: agentic_sdlc.plugins.base

**Phiên bản**: 3.0.0  
**Cập nhật lần cuối**: 11/02/2026


**Module:** `agentic_sdlc.plugins.base`

**Phiên bản:** 3.0.0

**Cập nhật lần cuối:** 2024-01-01

---

## Tổng Quan

Base classes and interfaces for the plugin system.

This module defines the plugin interface that all plugins must implement,
as well as metadata structures for plugin discovery and configuration.

---

## Classes

## Class `Plugin`

**Mô tả:**

Abstract base class for all plugins.

All plugins must inherit from this class and implement the required
abstract properties and methods. The plugin lifecycle consists of:

1. Instantiation: Plugin object is created
2. Initialization: initialize() is called with configuration
3. Operation: Plugin provides its functionality
4. Shutdown: shutdown() is called for cleanup

Example:
    >>> class MyPlugin(Plugin):
    ...     @property
    ...     def name(self) -> str:
    ...         return "my-plugin"
    ...
    ...     @property
    ...     def version(self) -> str:
    ...         return "1.0.0"
    ...
    ...     def initialize(self, config: Dict[str, Any]) -> None:
    ...         # Setup plugin with configuration
    ...         pass
    ...
    ...     def shutdown(self) -> None:
    ...         # Cleanup resources
    ...         pass

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, /, *args, **kwargs)
```text

**Mô tả:**

Initialize self.  See help(type(self)) for accurate signature.

**Tham số (Parameters):**

- `args` (Any): Tham số args
- `kwargs` (Any): Tham số kwargs

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Properties

- `name` (str) (chỉ đọc): Get the plugin name.

Returns:
    Unique identifier for this plugin. Should be lowercase with hyphens
    (e.g., "my-plugin"). Must be consistent across plugin versions.
- `version` (str) (chỉ đọc): Get the plugin version.

Returns:
    Version string following semantic versioning (e.g., "1.0.0").
    Used for compatibility checking and dependency resolution.

### Methods

#### `initialize`

**Chữ ký (Signature):**

```python
initialize(self, config: Dict[str, Any]) -> None
```javascript

**Mô tả:**

Initialize the plugin with configuration.

This method is called once when the plugin is loaded. It should
perform any setup required for the plugin to function, such as:
- Validating configuration
- Initializing resources (connections, files, etc.)
- Registering handlers or callbacks
- Loading dependencies

Args:
    config: Configuration dictionary for this plugin. The structure
           depends on the plugin's requirements.

Raises:
    PluginError: If initialization fails for any reason. The error
                should include context about what failed and why.

**Tham số (Parameters):**

- `config` (Dict): Tham số config

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

**Ngoại lệ (Raises):**

- `PluginError`

#### `shutdown`

**Chữ ký (Signature):**

```python
shutdown(self) -> None
```text

**Mô tả:**

Shut down the plugin and clean up resources.

This method is called when the plugin is being unloaded. It should
perform cleanup such as:
- Closing connections
- Releasing file handles
- Unregistering handlers
- Freeing memory

This method should not raise exceptions. If cleanup fails, it should
log the error but not propagate it.

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng Plugin**

```python
# Ví dụ sử dụng Plugin
from agentic_sdlc.plugins.base import Plugin

# Tạo instance
obj = Plugin()
```python

---

## Class `PluginMetadata`

**Mô tả:**

Metadata describing a plugin.

This model contains information about a plugin including its identity,
version, dependencies, and configuration schema. It's used for plugin
discovery, validation, and documentation.

Attributes:
    name: Unique identifier for the plugin
    version: Plugin version following semantic versioning
    author: Plugin author or organization
    description: Human-readable description of plugin functionality
    dependencies: List of required Python packages
    entry_point: Fully qualified class name for plugin entry point
    config_schema: JSON schema for plugin configuration validation

### Constructor

#### `__init__`

**Chữ ký (Signature):**

```python
__init__(self, /, **data: 'Any') -> 'None'
```text

**Mô tả:**

Create a new model by parsing and validating input data from keyword arguments.

Raises [`ValidationError`][pydantic_core.ValidationError] if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

**Tham số (Parameters):**

- `data` (Any): Tham số data

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Properties

- `model_extra` (dict[str, Any] | None) (chỉ đọc): Get extra fields set during validation.

Returns:
    A dictionary of extra fields, or `None` if `config.extra` is not set to `"allow"`.
- `model_fields_set` (set) (chỉ đọc): Returns the set of fields that have been explicitly set on this model instance.

Returns:
    A set of strings representing the fields that have been set,
        i.e. that were not filled from defaults.

### Methods

#### `__repr__`

**Chữ ký (Signature):**

```python
__repr__(self) -> 'str'
```text

**Mô tả:**

Return repr(self).

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `__str__`

**Chữ ký (Signature):**

```python
__str__(self) -> 'str'
```text

**Mô tả:**

Return str(self).

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `copy`

**Chữ ký (Signature):**

```python
copy(self, *, include: 'AbstractSetIntStr | MappingIntStrAny | None' = None, exclude: 'AbstractSetIntStr | MappingIntStrAny | None' = None, update: 'Dict[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'
```text

**Mô tả:**

Returns a copy of the model.

!!! warning "Deprecated"
    This method is now deprecated; use `model_copy` instead.

If you need `include` or `exclude`, use:

```python {test="skip" lint="skip"}
data = self.model_dump(include=include, exclude=exclude, round_trip=True)
data = {**data, **(update or {})}
copied = self.model_validate(data)
```text

Args:
    include: Optional set or mapping specifying which fields to include in the copied model.
    exclude: Optional set or mapping specifying which fields to exclude in the copied model.
    update: Optional dictionary of field-value pairs to override field values in the copied model.
    deep: If True, the values of fields that are Pydantic models will be deep-copied.

Returns:
    A copy of the model with included, excluded and updated fields as specified.

**Tham số (Parameters):**

- `include` (AbstractSetIntStr | MappingIntStrAny | None): Tham số include
- `exclude` (AbstractSetIntStr | MappingIntStrAny | None): Tham số exclude
- `update` (Dict[str, Any] | None): Tham số update
- `deep` (bool), mặc định: `False`: Tham số deep

**Giá trị trả về (Returns):**

- `Self`: Giá trị trả về

#### `dict`

**Chữ ký (Signature):**

```python
dict(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False) -> 'Dict[str, Any]'
```text

**Mô tả:**

Method dict

**Tham số (Parameters):**

- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `by_alias` (bool), mặc định: `False`: Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none

**Giá trị trả về (Returns):**

- `Dict`: Giá trị trả về

#### `json`

**Chữ ký (Signature):**

```python
json(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, by_alias: 'bool' = False, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, encoder: 'Callable[[Any], Any] | None' = PydanticUndefined, models_as_dict: 'bool' = PydanticUndefined, **dumps_kwargs: 'Any') -> 'str'
```text

**Mô tả:**

Method json

**Tham số (Parameters):**

- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `by_alias` (bool), mặc định: `False`: Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none
- `encoder` (Optional), mặc định: `PydanticUndefined`: Tham số encoder
- `models_as_dict` (bool), mặc định: `PydanticUndefined`: Tham số models_as_dict
- `dumps_kwargs` (Any): Tham số dumps_kwargs

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `model_copy`

**Chữ ký (Signature):**

```python
model_copy(self, *, update: 'Mapping[str, Any] | None' = None, deep: 'bool' = False) -> 'Self'
```text

**Mô tả:**

!!! abstract "Usage Documentation"
    [`model_copy`](../concepts/models.md#model-copy)

Returns a copy of the model.

!!! note
    The underlying instance's [`__dict__`][object.__dict__] attribute is copied. This
    might have unexpected side effects if you store anything in it, on top of the model
    fields (e.g. the value of [cached properties][functools.cached_property]).

Args:
    update: Values to change/add in the new model. Note: the data is not validated
        before creating the new model. You should trust this data.
    deep: Set to `True` to make a deep copy of the model.

Returns:
    New model instance.

**Tham số (Parameters):**

- `update` (collections.abc.Mapping[str, Any] | None): Tham số update
- `deep` (bool), mặc định: `False`: Tham số deep

**Giá trị trả về (Returns):**

- `Self`: Giá trị trả về

#### `model_dump`

**Chữ ký (Signature):**

```python
model_dump(self, *, mode: "Literal['json', 'python'] | str" = 'python', include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False) -> 'dict[str, Any]'
```javascript

**Mô tả:**

!!! abstract "Usage Documentation"
    [`model_dump`](../concepts/serialization.md#python-mode)

Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

Args:
    mode: The mode in which `to_python` should run.
        If mode is 'json', the output will only contain JSON serializable types.
        If mode is 'python', the output may contain non-JSON-serializable Python objects.
    include: A set of fields to include in the output.
    exclude: A set of fields to exclude from the output.
    context: Additional context to pass to the serializer.
    by_alias: Whether to use the field's alias in the dictionary key if defined.
    exclude_unset: Whether to exclude fields that have not been explicitly set.
    exclude_defaults: Whether to exclude fields that are set to their default value.
    exclude_none: Whether to exclude fields that have a value of `None`.
    exclude_computed_fields: Whether to exclude computed fields.
        While this can be useful for round-tripping, it is usually recommended to use the dedicated
        `round_trip` parameter instead.
    round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
    warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
        "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
    fallback: A function to call when an unknown value is encountered. If not provided,
        a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
    serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.

Returns:
    A dictionary representation of the model.

**Tham số (Parameters):**

- `mode` (Union), mặc định: `python`: Tham số mode
- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `context` (Any | None): Tham số context
- `by_alias` (bool | None): Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none
- `exclude_computed_fields` (bool), mặc định: `False`: Tham số exclude_computed_fields
- `round_trip` (bool), mặc định: `False`: Tham số round_trip
- `warnings` (Union), mặc định: `True`: Tham số warnings
- `fallback` (Optional): Tham số fallback
- `serialize_as_any` (bool), mặc định: `False`: Tham số serialize_as_any

**Giá trị trả về (Returns):**

- `dict`: Giá trị trả về

#### `model_dump_json`

**Chữ ký (Signature):**

```python
model_dump_json(self, *, indent: 'int | None' = None, ensure_ascii: 'bool' = False, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, context: 'Any | None' = None, by_alias: 'bool | None' = None, exclude_unset: 'bool' = False, exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, exclude_computed_fields: 'bool' = False, round_trip: 'bool' = False, warnings: "bool | Literal['none', 'warn', 'error']" = True, fallback: 'Callable[[Any], Any] | None' = None, serialize_as_any: 'bool' = False) -> 'str'
```javascript

**Mô tả:**

!!! abstract "Usage Documentation"
    [`model_dump_json`](../concepts/serialization.md#json-mode)

Generates a JSON representation of the model using Pydantic's `to_json` method.

Args:
    indent: Indentation to use in the JSON output. If None is passed, the output will be compact.
    ensure_ascii: If `True`, the output is guaranteed to have all incoming non-ASCII characters escaped.
        If `False` (the default), these characters will be output as-is.
    include: Field(s) to include in the JSON output.
    exclude: Field(s) to exclude from the JSON output.
    context: Additional context to pass to the serializer.
    by_alias: Whether to serialize using field aliases.
    exclude_unset: Whether to exclude fields that have not been explicitly set.
    exclude_defaults: Whether to exclude fields that are set to their default value.
    exclude_none: Whether to exclude fields that have a value of `None`.
    exclude_computed_fields: Whether to exclude computed fields.
        While this can be useful for round-tripping, it is usually recommended to use the dedicated
        `round_trip` parameter instead.
    round_trip: If True, dumped values should be valid as input for non-idempotent types such as Json[T].
    warnings: How to handle serialization errors. False/"none" ignores them, True/"warn" logs errors,
        "error" raises a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError].
    fallback: A function to call when an unknown value is encountered. If not provided,
        a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] error is raised.
    serialize_as_any: Whether to serialize fields with duck-typing serialization behavior.

Returns:
    A JSON string representation of the model.

**Tham số (Parameters):**

- `indent` (int | None): Tham số indent
- `ensure_ascii` (bool), mặc định: `False`: Tham số ensure_ascii
- `include` (Union): Tham số include
- `exclude` (Union): Tham số exclude
- `context` (Any | None): Tham số context
- `by_alias` (bool | None): Tham số by_alias
- `exclude_unset` (bool), mặc định: `False`: Tham số exclude_unset
- `exclude_defaults` (bool), mặc định: `False`: Tham số exclude_defaults
- `exclude_none` (bool), mặc định: `False`: Tham số exclude_none
- `exclude_computed_fields` (bool), mặc định: `False`: Tham số exclude_computed_fields
- `round_trip` (bool), mặc định: `False`: Tham số round_trip
- `warnings` (Union), mặc định: `True`: Tham số warnings
- `fallback` (Optional): Tham số fallback
- `serialize_as_any` (bool), mặc định: `False`: Tham số serialize_as_any

**Giá trị trả về (Returns):**

- `str`: Giá trị trả về

#### `model_post_init`

**Chữ ký (Signature):**

```python
model_post_init(self, context: 'Any', /) -> 'None'
```text

**Mô tả:**

Override this method to perform additional initialization after `__init__` and `model_construct`.
This is useful if you want to do some validation that requires the entire model to be initialized.

**Tham số (Parameters):**

- `context` (Any): Tham số context

**Giá trị trả về (Returns):**

- `None`: Giá trị trả về

### Ví dụ sử dụng

**Ví dụ cơ bản sử dụng PluginMetadata**

```python
# Ví dụ sử dụng PluginMetadata
from agentic_sdlc.plugins.base import PluginMetadata

# Tạo instance
obj = PluginMetadata()
```

---
