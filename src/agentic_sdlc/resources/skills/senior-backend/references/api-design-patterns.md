# API Design Patterns

## Resource Modeling
- **Nouns over Verbs**: `/orders/{id}` instead of `/get-order/{id}`.
- **Pluralization**: Standardize on plural nouns (`/users/`).
- **Consistency**: Use camelCase or snake_case consistently across all endpoints.

## Collections & Pagination
- **Cursor-based Pagination**: Preferred for large/real-time datasets (prevents skipped items).
- **Limit/Offset Pagination**: Acceptable for small, static datasets.
- **Max Limit**: Strictly enforce a maximum `limit` (e.g. 100) to prevent OOM.

## Idempotency
- **PUT**: Must be idempotent. Multiple calls return same result.
- **DELETE**: Must be idempotent. Multiple calls return same result (usually 204 or 404).
- **POST Idempotency Keys**: Use `Idempotency-Key` header for critical operations like payments/orders to prevent double processing.

## Versioning Strategies
- **URL Versioning**: `/api/v1/resource` (Most common/explicit).
- **Header Versioning**: `Accept: application/vnd.company.v1+json`.
- **Media Type Versioning**: Flexible but harder to proxy/cache.

## Standard Success Status Codes
- `200 OK`: Success (GET, PUT).
- `201 Created`: Success (POST).
- `202 Accepted`: Long-running task started (returns task URL).
- `204 No Content`: Success (DELETE).

## Standard Error Codes
- `400 Bad Request`: Validation failure.
- `401 Unauthorized`: Authentication missing.
- `403 Forbidden`: Authorization failure (correct credentials, wrong permissions).
- `404 Not Found`: Resource doesn't exist.
- `409 Conflict`: Resource already exists or state conflict.
- `429 Too Many Requests`: Rate limit hit.
- `500 Internal Server Error`: Implementation bug.
- `503 Service Unavailable`: Dependent system (DB/Downstream) is failing.
