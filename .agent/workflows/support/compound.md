---
description: Capture Knowledge - Document → Categorize → Index → Verify
---

# /compound - Capture Knowledge

**When to Use:** After solving non-obvious problems
**Flow:** Document → Categorize → Index → Verify
**Output:** Searchable Knowledge Entry

## Overview
The `/compound` workflow captures solved problems as searchable knowledge entries. This is the core of the compound learning system - every solution becomes permanent knowledge that makes future work easier.

## Philosophy
**"Each unit of engineering work should make subsequent units of work easier—not harder."**

## When to Compound

### ALWAYS Compound When:
- ✅ Bug required 3+ attempts to fix
- ✅ Solution was non-obvious or creative
- ✅ Issue likely to recur across sprints
- ✅ Pattern applies to multiple features
- ✅ Security vulnerability discovered
- ✅ Performance optimization achieved
- ✅ Architecture decision made
- ✅ Platform-specific issue resolved

### NEVER Skip Compounding For:
- ❌ Critical/High priority bugs
- ❌ Architecture decisions
- ❌ Security fixes
- ❌ Cross-cutting concerns
- ❌ Complex features (> 4 hours)

## Workflow Steps

### 1. Capture Problem Context
**Document:**
- What was the problem?
- When did it occur?
- What symptoms were observed?
- What was attempted initially?

### 2. Analyze Root Cause
**Investigate:**
- Why did the problem occur?
- What was the underlying cause?
- What assumptions were wrong?
- What was missed initially?

### 3. Document Solution
**Record:**
- What fixed the problem?
- Step-by-step solution
- Code changes made
- Configuration changes
- Dependencies updated

### 4. Extract Patterns
**Identify:**
- Is this a recurring pattern?
- What category does it belong to?
- What tags apply?
- What files are affected?

### 5. Categorize Entry
**Choose Category:**
```
.agent/knowledge-base/
├── bugs/           # Bug fixes and root causes
│   ├── critical/
│   ├── high/
│   ├── medium/
│   └── low/
├── features/       # Feature implementations
│   ├── authentication/
│   ├── performance/
│   └── integration/
├── architecture/   # Architecture decisions
├── security/       # Security fixes
├── performance/    # Optimizations
└── platform-specific/ # OS/environment issues
```

### 6. Create YAML Frontmatter
**Required Fields:**
```yaml
---
title: "Brief descriptive title"
category: bug|feature|architecture|security|performance|platform
priority: critical|high|medium|low
sprint: sprint-N
date: YYYY-MM-DD
tags: [tag1, tag2, tag3]
related_files: [path/to/file1, path/to/file2]
attempts: 3
time_saved: "2 hours"
author: @ROLE
---
```

### 7. Write Entry Content
**Structure:**
```markdown
## Problem
[Clear description of the issue]

## Root Cause
[What actually caused the problem]

## Solution
[Step-by-step solution]

## Code Changes
```language
[Relevant code snippets]
```

## Prevention
[How to avoid this in the future]

## Related Patterns
- KB-YYYY-MM-DD-###: [Related entry]
- GitHub Issue #123: [Related issue]

## Verification
[How to verify the fix works]
```

### 8. Update Index
Add entry to `.agent/knowledge-base/INDEX.md`:
```markdown
### [Category] - [Date]
- **KB-YYYY-MM-DD-###:** [Title] ([Priority]) - [One-line summary]
  - Tags: [tag1, tag2, tag3]
  - Time Saved: [X hours]
```

### 9. Verify Searchability
**Test:**
- Can you find it by title?
- Can you find it by tags?
- Can you find it by category?
- Is the YAML valid?

## Usage Examples

### Example 1: Bug Fix
```
@DEV /compound - Document the React hydration fix for SSR
```

**Entry:**
```yaml
---
title: "React Hydration Mismatch in SSR with Dynamic Content"
category: bug
priority: high
sprint: sprint-3
date: 2026-01-01
tags: [react, ssr, hydration, nextjs]
related_files: [pages/_app.tsx, components/DynamicContent.tsx]
attempts: 4
time_saved: "3 hours"
author: @DEV
---

## Problem
React hydration errors in production when rendering dynamic content
that differs between server and client (timestamps, user-specific data).

## Root Cause
Server-rendered HTML contained timestamps that didn't match client
hydration due to time passing between render and hydration.

## Solution
1. Use `useEffect` to render dynamic content only on client
2. Show placeholder during SSR
3. Suppress hydration warning for specific elements

## Code Changes
```tsx
// Before (causes hydration error)
<div>{new Date().toISOString()}</div>

// After (hydration-safe)
const [mounted, setMounted] = useState(false);
useEffect(() => setMounted(true), []);
<div suppressHydrationWarning>
  {mounted ? new Date().toISOString() : 'Loading...'}
</div>
```

## Prevention
- Always use `useEffect` for client-only rendering
- Use `suppressHydrationWarning` sparingly
- Test SSR in development mode

## Related Patterns
- KB-2025-12-15-001: Next.js SSR Best Practices
```

### Example 2: Architecture Decision
```
@SA /compound - Document the decision to use Redis for session storage
```

**Entry:**
```yaml
---
title: "Redis vs Database for Session Storage"
category: architecture
priority: high
sprint: sprint-2
date: 2026-01-01
tags: [redis, sessions, architecture, scalability]
related_files: [lib/session.ts, config/redis.ts]
attempts: 1
time_saved: "0 hours (future savings expected)"
author: @SA
---

## Problem
Need to choose session storage solution that scales horizontally
and provides fast access times.

## Analysis
Evaluated three options:
1. Database (PostgreSQL)
2. Redis
3. In-memory (not suitable for multi-instance)

## Decision
Chose Redis for session storage.

## Rationale
- **Performance:** Sub-millisecond access times
- **Scalability:** Horizontal scaling with Redis Cluster
- **TTL Support:** Automatic session expiration
- **Cost:** Lower than database for high-frequency reads

## Trade-offs
- **Cons:** Additional infrastructure component
- **Cons:** Data not persisted (acceptable for sessions)
- **Pros:** 10x faster than database
- **Pros:** Built-in expiration

## Implementation
```typescript
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export async function getSession(sessionId: string) {
  const data = await redis.get(`session:${sessionId}`);
  return data ? JSON.parse(data) : null;
}

export async function setSession(sessionId: string, data: any, ttl = 3600) {
  await redis.setex(`session:${sessionId}`, ttl, JSON.stringify(data));
}
```

## Related Patterns
- KB-2025-11-20-003: Redis Connection Pooling
- KB-2025-12-01-007: Session Security Best Practices
```

### Example 3: Performance Optimization
```
@DEV /compound - Document the image optimization that reduced load time by 60%
```

**Entry:**
```yaml
---
title: "Image Optimization with Next.js Image Component"
category: performance
priority: medium
sprint: sprint-4
date: 2026-01-01
tags: [performance, images, nextjs, optimization]
related_files: [components/Gallery.tsx, next.config.js]
attempts: 2
time_saved: "1 hour"
author: @DEV
---

## Problem
Gallery page loading slowly (4.5s) due to large unoptimized images.

## Measurement
- **Before:** 4.5s load time, 12MB transferred
- **After:** 1.8s load time, 2.3MB transferred
- **Improvement:** 60% faster, 81% less data

## Solution
1. Replace `<img>` with Next.js `<Image>` component
2. Enable automatic WebP conversion
3. Implement lazy loading
4. Add responsive image sizes

## Code Changes
```tsx
// Before
<img src="/gallery/photo.jpg" alt="Photo" />

// After
import Image from 'next/image';

<Image
  src="/gallery/photo.jpg"
  alt="Photo"
  width={800}
  height={600}
  loading="lazy"
  sizes="(max-width: 768px) 100vw, 800px"
/>
```

## Configuration
```javascript
// next.config.js
module.exports = {
  images: {
    formats: ['image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
  },
};
```

## Prevention
- Always use Next.js Image component for static images
- Configure responsive sizes
- Enable WebP format
- Use lazy loading for below-fold images

## Related Patterns
- KB-2025-12-10-004: Lazy Loading Best Practices
```

## Integration with Roles

### @DEV
- Primary creator of bug/feature entries
- Documents implementation patterns
- Captures performance optimizations

### @SA
- Documents architecture decisions
- Captures design patterns
- Records technology evaluations

### @SECA
- Documents security vulnerabilities
- Captures security patterns
- Records threat mitigations

### @TESTER
- Documents test strategies
- Captures bug patterns
- Records edge cases

## Success Criteria

**Entry Complete When:**
- [ ] YAML frontmatter complete and valid
- [ ] Problem clearly described
- [ ] Root cause identified
- [ ] Solution documented with code
- [ ] Prevention strategy provided
- [ ] Related patterns linked
- [ ] Index updated
- [ ] Searchability verified

## Metrics

Track compound effectiveness:
- **Total Entries:** Count of KB entries
- **Entries This Week:** New entries added
- **Time Saved:** Cumulative hours saved
- **Reuse Rate:** % of entries referenced
- **Coverage:** % of bugs with KB entries

## Compound Metrics Dashboard

Generate weekly report:
```markdown
## 📊 Compound System Health - Week [N]

### Growth
- Total Entries: [N] (+[X] this week)
- Categories:
  - Bugs: [N] (+[X])
  - Features: [N] (+[X])
  - Architecture: [N] (+[X])
  - Security: [N] (+[X])
  - Performance: [N] (+[X])

### Impact
- Time Saved This Week: [X hours]
- Cumulative Time Saved: [Y hours]
- Reuse Rate: [Z%]
- First-Time Fix Rate: [W%]

### Top Contributors
1. @DEV - [N] entries
2. @SA - [N] entries
3. @SECA - [N] entries

### Most Referenced
1. KB-YYYY-MM-DD-###: [Title] ([N] references)
2. KB-YYYY-MM-DD-###: [Title] ([N] references)
```

## Handoff Template

```markdown
### /compound Complete: [Title]
- **Entry:** KB-YYYY-MM-DD-###
- **Category:** [category]
- **Priority:** [priority]
- **Location:** .agent/knowledge-base/[category]/KB-YYYY-MM-DD-###.md
- **Time Saved:** [X hours] (estimated future savings)
- **Next Step:** Entry available for search and reuse

#compound #knowledge-base #continuous-improvement
```

#workflow #compound #knowledge-capture
