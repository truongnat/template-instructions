---
name: performance-audit
description: >
  Audit and optimize application performance across frontend, backend, and database layers.
  Identifies bottlenecks, provides actionable optimization recommendations, and measures improvements.
  Use when the app feels slow, Lighthouse scores are low, or API response times exceed targets.
compatibility: Works with web apps, APIs, mobile apps, and database queries
metadata:
  author: agentic-sdlc
  version: "2.0"
  category: quality
---

# Performance Audit Skill

You are a **Performance Engineer** focused on measurable improvements. Every optimization must be backed by data — never optimize without profiling first.

## Audit Process

### Step 1: Establish Baselines

Before optimizing, measure the current state:

**Frontend (Web)**:
```bash
# Run Lighthouse CI
npx lighthouse http://localhost:3000 --output=json --output-path=./lighthouse-report.json
```

Key metrics to capture:
| Metric | Target | Description |
|--------|--------|------------|
| **LCP** (Largest Contentful Paint) | < 2.5s | When the main content becomes visible |
| **FID** (First Input Delay) | < 100ms | Time until the page responds to interaction |
| **CLS** (Cumulative Layout Shift) | < 0.1 | Visual stability — no unexpected jumps |
| **TTFB** (Time to First Byte) | < 800ms | Server response time |
| **Bundle Size** | < 200KB gzipped | Total JavaScript sent to client |

**Backend (API)**:
```bash
# Measure API response time (p50/p95/p99)
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:3000/api/endpoint
```

| Metric | Target |
|--------|--------|
| **p50 latency** | < 100ms |
| **p95 latency** | < 500ms |
| **p99 latency** | < 1000ms |
| **Error rate** | < 0.1% |

### Step 2: Frontend Optimization

#### Bundle Size
```javascript
// ❌ BAD: Importing entire library
import _ from 'lodash';
_.get(obj, 'path');

// ✅ GOOD: Tree-shakeable import
import get from 'lodash/get';
get(obj, 'path');
```

#### Image Optimization
- Use `<img loading="lazy">` for below-the-fold images
- Use WebP/AVIF format (30-50% smaller than JPEG)
- Set explicit `width` and `height` to prevent CLS
- Use responsive `srcset` for different screen densities

```html
<img
  src="hero.webp"
  srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
  sizes="(max-width: 768px) 100vw, 50vw"
  width="800"
  height="600"
  loading="lazy"
  alt="Hero section"
/>
```

#### Rendering Performance
- Avoid layout thrashing (reading then writing DOM in a loop)
- Use `transform` and `opacity` for animations (GPU-accelerated)
- Debounce scroll/resize event handlers (16ms minimum)
- Use `content-visibility: auto` for long lists

### Step 3: Backend Optimization

#### Database Queries
```sql
-- ❌ BAD: N+1 query pattern
SELECT * FROM orders WHERE user_id = 1;
-- then for EACH order:
SELECT * FROM order_items WHERE order_id = ?;

-- ✅ GOOD: Single JOIN query
SELECT o.*, oi.*
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.user_id = 1;
```

#### Query Analysis
```sql
-- Always EXPLAIN before optimizing
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
-- Look for: Seq Scan (bad for large tables) → Add an index
CREATE INDEX idx_users_email ON users(email);
```

#### Caching Strategy
| Layer | Tool | TTL | Use For |
|-------|------|-----|---------|
| **HTTP Cache** | Cache-Control headers | 1h-1d | Static assets, CDN |
| **Application Cache** | Redis/Memcached | 5m-1h | Computed results, session data |
| **Query Cache** | ORM-level | 1m-5m | Frequent identical queries |
| **Edge Cache** | CDN (Vercel, Cloudflare) | 1d+ | HTML pages, API responses |

### Step 4: Measure Improvements

After each optimization:
1. Re-run the same benchmark/Lighthouse test
2. Compare before vs after metrics
3. Document the improvement in a table:

```markdown
| Optimization | Before | After | Improvement |
|-------------|--------|-------|-------------|
| Bundle splitting | 450KB | 180KB | -60% |
| Image WebP conversion | LCP 3.2s | LCP 1.8s | -44% |
| Add DB index | p95 850ms | p95 120ms | -86% |
```

## Optimization Priority

Always optimize in this order (highest impact first):
1. **Network**: Reduce payload size, enable compression, use CDN
2. **Database**: Fix N+1 queries, add missing indexes, optimize JOINs
3. **Caching**: Add appropriate caching layers
4. **Code**: Algorithmic improvements, memoization
5. **Infrastructure**: Scaling, load balancing (last resort)

## Anti-Patterns

1. ❌ Premature optimization without profiling data
2. ❌ Micro-optimizing code while ignoring N+1 database queries
3. ❌ Caching everything without invalidation strategy
4. ❌ Adding indexes on every column (slows down writes)
5. ❌ Using `SELECT *` in production queries
