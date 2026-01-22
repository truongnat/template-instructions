---
title: Naming Conventions
version: 1.0.0
category: rule
priority: high
---
# Naming Conventions
## File Naming
| Language | Convention | Example |
|----------|------------|---------|
| Python | snake_case.py | user_service.py |
| JavaScript/TypeScript | kebab-case.ts | user-service.ts |
| React Components | PascalCase.tsx | UserProfile.tsx |
| CSS/SCSS | kebab-case.css | user-profile.css |
| Tests | *.test.ts, *_test.py | user.test.ts |
## Code Naming
### Variables and Functions
| Element | Convention | Example |
|---------|------------|---------|
| Variables (JS/TS) | camelCase | userName, isActive |
| Variables (Python) | snake_case | user_name, is_active |
| Boolean Variables | Prefix with is, has, should, can | isActive, hasPermission |
| Constants | UPPER_SNAKE_CASE | MAX_RETRIES, API_URL |
| Functions (JS/TS) | camelCase (Verb First) | getUserById, validateToken |
| Functions (Python) | snake_case (Verb First) | get_user_by_id, validate_token |
| Private | Prefix with _ | _internalState |
### Classes and Types
| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | UserService, AuthController |
| Interfaces (TS) | PascalCase | IUserRepository |
| Type Aliases | PascalCase | UserId, ResponseData |
| Enums | PascalCase | UserStatus, OrderType |
| Enum Members | UPPER_SNAKE_CASE | USER_ACTIVE |
## Directory Naming
| Target | Convention | Example |
|--------|------------|---------|
| Feature Domains | Singular noun | /src/features/auth |
| Collections | Plural noun | /src/utils, /src/hooks |
| Grouping | kebab-case | /src/ui-components |
## Database Naming
| Element | Convention | Example |
|---------|------------|---------|
| Tables | snake_case plural | users, order_items |
| Columns | snake_case | user_id, created_at |
| Primary Keys | id or table_id | id, user_id |
| Foreign Keys | referenced_table_id | user_id, order_id |
| Indexes | idx_table_column | idx_users_email |
## API Endpoints
| Element | Convention | Example |
|---------|------------|---------|
| Resources | kebab-case plural | /api/users, /api/order-items |
| Query Params | camelCase | ?userId=123 |
| Path Params | camelCase | /users/:userId |
## Git Branch Names
| Type | Convention | Example |
|------|------------|---------|
| Feature | feat/description | feat/user-auth |
| Bugfix | fix/description | fix/login-error |
| Hotfix | hotfix/description | hotfix/security-patch |
| Release | release/version | release/1.2.0 |
#rules #naming #conventions

