---
title: Folder Structure & Organization
version: 1.0.0
category: rule
priority: high
---
# Folder Structure & Organization

## Feature-Centric Architecture
Source code MUST be organized by **Feature/Domain** rather than by file type. This promotes modularity and scalability.

### Recommended Structure (Web/TS)
```
src/
├── assets/             # Static assets (images, fonts)
├── shared/             # Reusable components, hooks, etc.
│   ├── components/
│   ├── hooks/
│   └── utils/
├── features/           # Domain-specific logic
│   └── [feature-name]/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       ├── tests/      # Co-located tests
│       └── index.ts    # Public API for the feature
└── main.tsx            # Entry point
```

## Hierarchy Rules
1. **Shallow Hierarchy**: Aim for a maximum depth of **3 levels** below `src/`. Excessively nested folders increase cognitive load for both humans and agents.
2. **Co-location**: Place unit tests, styles, and assets directly alongside the components or logic they serve if they are not shared.
3. **Module Boundaries**: Each feature folder should have an `index.ts` file that explicitly exports the public API of that feature. Internal details should not be imported from other features directly.

## Infrastructure Organization
1. **`.agent/`**: Reserved ONLY for system instructions, rules, and workflows. NO project source code should live here.
2. **`tools/`**: Contains domain-specific scripts, CLI bridges, and infrastructure utilities.
3. **`docs/`**:
   - `docs/global/`: System-wide guides and architecture.
   - `docs/sprints/`: Sprint-specific artifacts (plans, reports, logs).
   - `docs/research-reports/`: Technical research and decision records.

## Prohibited Practices
- ❌ **Deep Nesting**: Avoid `src/components/common/buttons/primary/small/SubmitButton.tsx`.
- ❌ **Type-Based Grouping**: Avoid `src/controllers/`, `src/models/` for large projects.
- ❌ **Hidden Dependencies**: Do not import private files from other features; use the feature's `index` entry point.

#rules #structure #organization
