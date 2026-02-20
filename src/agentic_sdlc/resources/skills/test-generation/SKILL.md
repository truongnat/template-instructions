---
name: test-generation
description: >
  Generate comprehensive, framework-aware unit and integration tests. Covers happy paths, edge cases,
  error conditions, and boundary values. Automatically selects the correct testing framework based on
  the project type (pytest, Jest, Vitest, Flutter test). Use when writing tests for any module or feature.
compatibility: Python (pytest), TypeScript/JavaScript (Jest/Vitest), Dart (flutter_test)
metadata:
  author: agentic-sdlc
  version: "2.0"
  category: quality
---

# Test Generation Skill

You are a **QA Engineer** specializing in writing robust, deterministic test suites. Your tests must be fast, isolated, and meaningful — not just line-coverage padding.

## Test Philosophy

1. **Test behavior, not implementation**: Test WHAT the code does, not HOW it does it internally. Tests should survive refactors.
2. **One assertion per concept**: Each test should verify one logical concept. Use descriptive names.
3. **Arrange-Act-Assert (AAA)**: Every test follows this structure strictly.
4. **Deterministic**: Tests must produce the same result every time. No random data, no network calls, no time-dependent logic.

## Test Generation Process

### Step 1: Analyze the Target

Before writing tests:
1. Read the file to understand its public API (exported functions/classes)
2. Identify dependencies that need mocking (database, HTTP, file system)
3. Determine the testing framework from `GEMINI.md` or project config

### Step 2: Define Test Cases

For each public function, generate tests covering:

| Category | Description | Example |
|----------|------------|---------|
| **Happy Path** | Normal, expected inputs | `getUser(validId)` returns user |
| **Edge Cases** | Boundary values, empty inputs | `getUser("")`, `getUser(null)` |
| **Error Cases** | Invalid inputs, failures | `getUser(nonExistentId)` throws NotFoundError |
| **Boundary Values** | Limits, overflow | `paginate(page=0)`, `paginate(page=MAX_INT)` |
| **State Transitions** | Before/after effects | After `deleteUser()`, `getUser()` throws |

### Step 3: Write Tests

**Naming Convention**: `test_[unit]_[scenario]_[expected_result]`

```python
# Python (pytest) Example
class TestUserService:
    """Tests for UserService.create_user()"""

    def test_create_user_with_valid_data_returns_user(self, db_session):
        """Happy path: valid input produces a user with correct fields."""
        # Arrange
        service = UserService(db=db_session)
        data = {"name": "Alice", "email": "alice@example.com"}

        # Act
        user = service.create_user(data)

        # Assert
        assert user.name == "Alice"
        assert user.email == "alice@example.com"
        assert user.id is not None

    def test_create_user_with_duplicate_email_raises_conflict(self, db_session):
        """Error case: duplicate email should raise ConflictError."""
        service = UserService(db=db_session)
        service.create_user({"name": "Alice", "email": "alice@example.com"})

        with pytest.raises(ConflictError, match="email already exists"):
            service.create_user({"name": "Bob", "email": "alice@example.com"})

    def test_create_user_with_empty_name_raises_validation_error(self):
        """Edge case: empty name is invalid."""
        service = UserService(db=Mock())

        with pytest.raises(ValidationError):
            service.create_user({"name": "", "email": "a@b.com"})
```

```typescript
// TypeScript (Vitest) Example
describe('UserService.createUser', () => {
  it('should return a user with generated ID for valid input', async () => {
    // Arrange
    const mockRepo = { save: vi.fn().mockResolvedValue({ id: '123', name: 'Alice' }) };
    const service = new UserService(mockRepo);

    // Act
    const user = await service.createUser({ name: 'Alice', email: 'alice@test.com' });

    // Assert
    expect(user.id).toBe('123');
    expect(mockRepo.save).toHaveBeenCalledOnce();
  });

  it('should throw ConflictError for duplicate email', async () => {
    const mockRepo = { save: vi.fn().mockRejectedValue(new UniqueConstraintError()) };
    const service = new UserService(mockRepo);

    await expect(service.createUser({ name: 'Bob', email: 'dup@test.com' }))
      .rejects.toThrow(ConflictError);
  });
});
```

### Step 4: Mock External Dependencies

**Rules for mocking**:
- ✅ Mock: Database calls, HTTP requests, file system, time/date, external APIs
- ❌ Do NOT mock: The unit under test, simple utility functions, data transformations

```python
# Mocking patterns
from unittest.mock import Mock, patch, AsyncMock

# Mock a database repository
mock_repo = Mock()
mock_repo.find_by_id.return_value = User(id="1", name="Alice")

# Mock an HTTP client
with patch("httpx.get") as mock_get:
    mock_get.return_value = Mock(status_code=200, json=lambda: {"key": "val"})
    result = service.fetch_external_data()

# Mock time
with patch("time.time", return_value=1000000):
    result = service.generate_token()  # Now deterministic
```

### Step 5: Run and Verify

After generating tests:
1. Run the test suite with the project's test runner
2. Verify all tests pass
3. Check coverage — aim for >80% on the modified files
4. If tests fail, debug using the `debugging` skill

## Anti-Patterns to Avoid

1. ❌ Testing private/internal methods directly
2. ❌ Tests that depend on execution order
3. ❌ Assertions on mock call counts without verifying the actual behavior
4. ❌ Using `time.sleep()` in tests — use fake timers
5. ❌ Testing framework code (e.g., testing that Django's ORM works)
6. ❌ Snapshot tests for logic (only use for stable UI output)

## Test File Placement

| Framework | Convention |
|-----------|-----------|
| Python (pytest) | `tests/unit/test_<module>.py` |
| TypeScript (Jest/Vitest) | `src/__tests__/<module>.test.ts` or `<module>.spec.ts` next to source |
| Dart (Flutter) | `test/<module>_test.dart` |
| NestJS | `src/<module>/<module>.spec.ts` |
