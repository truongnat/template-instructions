# Security Review Checklist

Use this checklist when performing code reviews. Check each item against the code being reviewed.

## Authentication & Authorization
- [ ] All endpoints require authentication unless explicitly public
- [ ] Authorization checks verify the user has permission for the specific resource
- [ ] JWT tokens have reasonable expiration times
- [ ] Refresh tokens are stored securely (httpOnly cookies, not localStorage)
- [ ] Password hashing uses bcrypt/argon2 with appropriate work factor (≥12)

## Input Validation
- [ ] All user input is validated on the server side (never trust client-only validation)
- [ ] SQL queries use parameterized statements (no string concatenation)
- [ ] File uploads validate file type, size, and content (not just extension)
- [ ] URLs from user input are validated against an allowlist (prevent SSRF)
- [ ] Path inputs are sanitized to prevent directory traversal (`../`)

## Data Exposure
- [ ] API responses do not include passwords, tokens, or internal IDs unnecessarily
- [ ] Error messages do not leak stack traces or internal details to the client
- [ ] Logs do not contain sensitive data (PII, passwords, tokens)
- [ ] Database queries select only needed columns (no `SELECT *` returning sensitive fields)

## Transport & Storage
- [ ] All external communication uses HTTPS
- [ ] Sensitive data at rest is encrypted
- [ ] CORS is configured with specific origins (not `*` in production)
- [ ] Security headers are set: `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`

## Dependencies
- [ ] No known vulnerabilities in dependencies (`npm audit` / `pip-audit`)
- [ ] Dependencies are pinned to specific versions in lockfile
- [ ] No unnecessary dependencies that increase attack surface
