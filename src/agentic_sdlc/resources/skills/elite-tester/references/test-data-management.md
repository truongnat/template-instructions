# Test Data Management (TDM)

## Principles
- **Hermeticity**: Each test is a silo. It creates its own data and expects a clean slate.
- **Reproducibility**: Use fixed seeds for random generators (Faker) if necessary to reproduce specific failure cases.
- **Minimalism**: Create only the data required for the specific test case. Avoid "God Fixtures" (massive JSON files shared by all tests).

## Setup Patterns
### 1. Factories over Fixtures
Factories are dynamic and programmable. Use libraries like `factory_boy` (Python) or `Fishery` (TypeScript).

```python
# Factory pattern example
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Faker('user_name')
    email = factory.Faker('email')
```

### 2. Database Fixtures
Use scoped fixtures to provide data that is reused across multiple tests in a file but cleaned up afterwards.

```python
@pytest.fixture(scope="function")
def authorized_client(client, db):
    user = UserFactory()
    client.force_authenticate(user=user)
    return client
```

## Data Cleanup (Teardown)
- **Database Transactions**: The most efficient way to clean up. Wrap each test in a transaction and roll it back at the end.
- **Hook-based cleanup**: Use `afterEach` or `teardown()` to delete files, stop mock servers, or clear cache keys.

## Handling External Data
- **VCR/Recording**: Record real HTTP interactions and replay them in subsequent test runs (e.g., `vcr_py`, `Polly.js`). This provides "real" integration confidence without the network flakiness.
- **Contract Testing**: Use tools like `Pact` to verify that the provider (API) hasn't broken the contract expected by the consumer (Client).
