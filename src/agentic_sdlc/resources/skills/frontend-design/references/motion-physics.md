# Motion Physics & Micro-interactions

## 1. The "Ease-Out" Rule
UI elements should start fast and slow down. Never use `linear`.
- **Default**: `cubic-bezier(0.16, 1, 0.3, 1)` (Swift ease-out).
- **Entrance**: `cubic-bezier(0.34, 1.56, 0.64, 1)` (Subtle bounce/overshoot).

## 2. Staggered Entrances
Never animate a whole grid at once. Stagger items by `0.05s` to create a "wave" effect that feels intentional and smooth.

## 3. Directional Momentum
- **Opening**: Move *up* from bottom or *out* from center.
- **Closing**: Move *towards* the dismissal point (e.g., sliding out to the side).
- **Expansion**: Elements should grow from their trigger point.

## 4. Micro-interactions
- **Hover Scale**: `scale(1.02)` is enough. `scale(1.1)` is too much.
- **Active Press**: `scale(0.96)` with a quick `0.1s` transition.
- **Glint Effect**: A subtle diagonal shine moving across a button on hover for that "premium" feel.

## 5. Performance Matters
- Animate `transform` and `opacity` only. Avoid animating `width`, `height`, or `top/left` to prevent layout thrashing (Reflow).
- Use `will-change` sparingly on complex animated elements.
