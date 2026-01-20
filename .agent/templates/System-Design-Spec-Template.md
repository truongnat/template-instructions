# System Design Specification - Version [X]

## Document Info
| Field | Value |
|-------|-------|
| Version | [X.0] |
| Date | [YYYY-MM-DD] |
| Author | @SA |
| Project Type | Web / Mobile / Desktop / Embedded / CLI / API / Library |
| Status | Draft / Review / Approved |

---

## 1. Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   System    │────▶│  Storage    │
│             │     │   Layer     │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 2. Technology Stack
| Layer | Technology | Justification |
|-------|------------|---------------|
| Platform | [e.g., Web/iOS/Android/Windows/Linux] | [Reason] |
| Runtime | [e.g., Node.js 20/Python 3.11/JVM] | [Reason] |
| Framework | [e.g., SvelteKit/React Native/Electron] | [Reason] |
| Storage | [e.g., PostgreSQL/SQLite/File System] | [Reason] |
| Auth | [e.g., Supabase Auth/OAuth/JWT] | [Reason] |

## 3. Interface Design

### 3.1 API Endpoints (for Web/Mobile Backend)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/[resource] | List all | Required |
| POST | /api/[resource] | Create new | Required |

**Request/Response Example:**
```json
// POST /api/[resource]
// Request
{ "field": "value" }

// Response 201
{ "id": "uuid", "field": "value", "createdAt": "ISO8601" }
```

### 3.2 Public API (for Libraries/SDKs)
```typescript
// Main interface
interface [LibraryName] {
  method1(param: Type): ReturnType;
  method2(options: Options): Promise<Result>;
}
```

### 3.3 CLI Commands (for CLI Tools)
```bash
# Command structure
tool-name <command> [options]

# Examples
tool-name init --template=basic
tool-name build --output=dist
```

### 3.4 Communication Protocol (for Embedded/IoT)
```
Message Format: [Header][Payload][Checksum]
- Header: 4 bytes (command ID + length)
- Payload: Variable length
- Checksum: 2 bytes CRC16
```

## 4. Data Model

### 4.1 Database Schema (for Web/Mobile with DB)
| Table | Columns | Constraints |
|-------|---------|-------------|
| [table_name] | id, field1, field2 | PK, FK, etc. |

### 4.2 Data Structures (for Desktop/CLI/Library)
```typescript
interface DataModel {
  id: string;
  field: Type;
}
```

### 4.3 File Format (for Desktop/CLI tools)
```json
{
  "version": "1.0",
  "data": {}
}
```

### 4.4 Relationships
```
[Entity A] 1──────N [Entity B]
              └── foreign_key: entity_a_id
```

## 5. Authentication & Authorization
| Role | Permissions | Platform Notes |
|------|-------------|----------------|
| Guest | Read public | N/A for CLI tools |
| User | Read/Write own | Session/Token based |
| Admin | Full access | Elevated privileges |

## 6. Error Handling
| Code/Type | Meaning | Response |
|-----------|---------|----------|
| 400 / InvalidInput | Bad Request | { "error": "message" } |
| 401 / Unauthorized | Not authenticated | { "error": "Not authenticated" } |
| 403 / Forbidden | Access denied | { "error": "Access denied" } |
| 404 / NotFound | Resource not found | { "error": "Resource not found" } |
| 500 / InternalError | Server Error | { "error": "Internal error" } |

## 7. Platform-Specific Considerations

### For Mobile Apps:
- Offline support strategy: [describe]
- Background sync: [describe]
- Push notifications: [describe]
- Battery optimization: [describe]

### For Desktop Apps:
- Auto-update mechanism: [describe]
- Multi-window support: [describe]
- System tray integration: [describe]

### For Embedded Systems:
- Memory constraints: [X KB RAM, Y KB Flash]
- Power management: [describe]
- Firmware update: [OTA/USB/etc.]

### For CLI Tools:
- Configuration file location: [~/.config/tool/]
- Output formats: [JSON/YAML/Table]
- Piping support: [Yes/No]

### For Libraries:
- Dependency management: [peer/bundled]
- Tree-shaking support: [Yes/No]
- TypeScript definitions: [Included/Separate]

## 8. Performance & Scalability
| Metric | Target | Strategy |
|--------|--------|----------|
| Response Time | < 200ms | Caching, indexing |
| Throughput | [X req/s] | Load balancing |
| Memory Usage | < [X MB] | Optimization |
| Battery Impact | Minimal | Background throttling |

## 9. Open Questions
- [ ] @UIUX: [Question about UI requirements]
- [ ] @PO: [Question about business logic]
- [ ] @DEVOPS: [Question about deployment]

---

### Next Step:
- @QA - Review design for testability
- @SECA - Security review of architecture and interfaces
- @DEV - Prepare for implementation

#designing
