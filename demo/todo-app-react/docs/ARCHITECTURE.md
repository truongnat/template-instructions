# ADR 002: React + GSAP Todo App Demo

## Status
Approved

## Context
Create a second demo for the `agentic-sdlc` framework, focusing on popular modern frontend technologies: React and GSAP.

## Decision
We will use **Vite + React** for the UI structure and **GSAP** for advanced, smooth animations.

### Rationale
1. **React**: Provides a robust component-based architecture which is standard in the industry.
2. **GSAP**: The industry standard for high-performance web animations. It allows for complex timelines and smoother transitions than CSS alone.
3. **UX**: The combination allows for a "premium" feel with organic-feeling animations (bounce, stagger, elastic).

## Alternatives Considered
- **Framer Motion**: Strong contender, but GSAP offers more fine-grained control for complex sequences.
- **Vanilla JS (Previous Demo)**: Good for simplicity, but React showcases how the framework handles ecosystem integration.

## Consequences
- **Positive**: State-of-the-art animations, modular code.
- **Negative**: Increased bundle size (mitigated by Vite's treeshaking).
