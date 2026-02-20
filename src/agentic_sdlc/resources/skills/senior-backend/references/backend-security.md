# Backend Security Standards

## API Security
- **Rate Limiting**: Implement per-IP and per-user limits to prevent DoS/Brute-force.
- **CORS**: Strict allow-list for origins. No `*` in production.
- **Security Headers**: HSTS, Content-Security-Policy (CSP), X-Frame-Options.
- **Versioning**: Break APIs by version (`/v1/`) to avoid breaking clients during security refactors.

## Data Protection
- **Encryption at Rest**: PII (Personally Identifiable Information) must be encrypted in the database.
- **Encryption in Transit**: TLS 1.3 only. 
- **Secrets Management**: No secrets in environment variables on disk. Use HashiCorp Vault or AWS/GCP Secret Manager.
- **Sensitive Data Masking**: PII must be masked in logs. Use a middleware to scrub `password`, `token`, `ssn` fields.

## Authorization (RBAC vs ABAC)
- **Role-Based Access Control (RBAC)**: Simple hierarchical roles (User, Admin).
- **Attribute-Based Access Control (ABAC)**: Used for granular ownership checks (e.g. `User can edit Post IF user.id == post.owner_id`).
- **Never trust IDs from client**: Always verify resource ownership server-side after authentication.

## Injection Prevention
- **SQLi**: Parameterized queries/ORMs only.
- **NoSQLi**: Sanitize operators (e.g. `$ne`, `$gt`) in MongoDB inputs.
- **Command Injection**: Avoid `shell=True` in subprocesses. Use argument arrays.
- **Deserialization**: Never deserialize untrusted binary data (e.g. Python `pickle`). Use JSON/Protobuf.
