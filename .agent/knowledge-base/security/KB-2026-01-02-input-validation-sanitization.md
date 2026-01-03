---
title: "Input Validation and Sanitization Best Practices"
category: security
priority: high
sprint: sprint-[N]
date: 2026-01-02
tags: [security, validation, sanitization, xss, injection]
related_files: []
attempts: 1
time_saved: "2 hours (future reuse)"
author: "SECA"
---

## Problem
User input passed directly to database, HTML output, or system commands leads to injection attacks (SQL, XSS, Command Injection).

## Root Cause
Trust in user input without validation or sanitization. Missing output encoding.

## Solution

### 1. Input Validation (Whitelist Approach)
```typescript
const validateEmail = (input: string): boolean => {
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return pattern.test(input);
};

const validateUsername = (input: string): boolean => {
  const pattern = /^[a-zA-Z0-9_]{3,20}$/;
  return pattern.test(input);
};
```

### 2. Output Encoding (XSS Prevention)
```typescript
const escapeHtml = (unsafe: string): string => {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};
```

### 3. SQL Parameterization
```python
# ❌ Vulnerable
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Safe
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### 4. Content Security Policy
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'">
```

## Validation Libraries
- **Zod** (TypeScript) - Schema validation
- **Joi** (Node.js) - Object schema validation
- **Pydantic** (Python) - Data validation

## Prevention
1. Never trust user input
2. Validate on both client and server
3. Use parameterized queries always
4. Encode output based on context
5. Implement CSP headers

#security #validation #xss #injection
