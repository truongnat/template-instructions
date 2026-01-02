---
title: "Lazy Loading and Code Splitting Optimization"
category: performance
priority: medium
sprint: sprint-current
date: 2026-01-02
tags: [performance, lazy-loading, code-splitting, optimization, web]
related_files: []
attempts: 1
time_saved: "1 hour (future reuse)"
author: "DEV"
---

## Problem
Initial page load slow due to loading all JavaScript/components at once, even those not immediately visible.

## Root Cause
Bundle includes all components regardless of whether they're needed on initial render. No code splitting enabled.

## Solution

### 1. Route-based Code Splitting (React/Next.js)
```tsx
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
  ssr: false
});
```

### 2. Component-based Lazy Loading (React)
```tsx
import { lazy, Suspense } from 'react';

const LazyChart = lazy(() => import('./ChartComponent'));

function Dashboard() {
  return (
    <Suspense fallback={<Loading />}>
      <LazyChart />
    </Suspense>
  );
}
```

### 3. Intersection Observer for Images
```tsx
const [isVisible, setIsVisible] = useState(false);
const ref = useRef();

useEffect(() => {
  const observer = new IntersectionObserver(
    ([entry]) => setIsVisible(entry.isIntersecting),
    { threshold: 0.1 }
  );
  observer.observe(ref.current);
  return () => observer.disconnect();
}, []);
```

### 4. Astro Islands (for Astro projects)
```astro
<HeavyComponent client:visible />
<InteractiveWidget client:idle />
```

## Metrics to Track
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Bundle size reduction

## Prevention
1. Audit bundle size regularly with `webpack-bundle-analyzer`
2. Lazy load all below-fold content
3. Use `client:visible` in Astro for interactive components
4. Implement skeleton loading states

#performance #lazy-loading #optimization #web
