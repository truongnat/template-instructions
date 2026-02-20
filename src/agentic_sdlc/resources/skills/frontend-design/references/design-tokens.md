# Design Tokens Reference

## Color Tokens

```css
:root {
  /* Primary */
  --color-primary-50:  hsl(217, 91%, 95%);
  --color-primary-100: hsl(217, 91%, 90%);
  --color-primary-200: hsl(217, 91%, 80%);
  --color-primary-300: hsl(217, 91%, 70%);
  --color-primary-400: hsl(217, 91%, 60%);
  --color-primary-500: hsl(217, 91%, 50%); /* Base */
  --color-primary-600: hsl(217, 91%, 40%);
  --color-primary-700: hsl(217, 91%, 30%);
  --color-primary-foreground: hsl(0, 0%, 100%);

  /* Neutral */
  --color-neutral-50:  hsl(0, 0%, 98%);
  --color-neutral-100: hsl(0, 0%, 96%);
  --color-neutral-200: hsl(0, 0%, 90%);
  --color-neutral-300: hsl(0, 0%, 83%);
  --color-neutral-400: hsl(0, 0%, 64%);
  --color-neutral-500: hsl(0, 0%, 45%);
  --color-neutral-600: hsl(0, 0%, 32%);
  --color-neutral-700: hsl(0, 0%, 25%);
  --color-neutral-800: hsl(0, 0%, 15%);
  --color-neutral-900: hsl(0, 0%, 9%);

  /* Semantic */
  --color-success: hsl(142, 71%, 45%);
  --color-warning: hsl(38, 92%, 50%);
  --color-error:   hsl(0, 84%, 60%);
  --color-info:    hsl(199, 89%, 48%);

  /* Focus */
  --color-focus-ring: hsl(217, 91%, 60%);
}
```

## Spacing Scale (4px base)

```css
:root {
  --space-1:  4px;   /* 0.25rem */
  --space-2:  8px;   /* 0.5rem  */
  --space-3:  12px;  /* 0.75rem */
  --space-4:  16px;  /* 1rem    */
  --space-5:  20px;  /* 1.25rem */
  --space-6:  24px;  /* 1.5rem  */
  --space-8:  32px;  /* 2rem    */
  --space-10: 40px;  /* 2.5rem  */
  --space-12: 48px;  /* 3rem    */
  --space-16: 64px;  /* 4rem    */
  --space-20: 80px;  /* 5rem    */
}
```

## Typography Scale (1.25 ratio)

```css
:root {
  --font-heading: 'Outfit', system-ui, sans-serif;
  --font-body:    'Inter', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', monospace;

  --text-xs:   0.75rem;   /* 12px */
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  1.875rem;  /* 30px */
  --text-4xl:  2.25rem;   /* 36px */
  --text-5xl:  3rem;      /* 48px */

  --leading-tight:  1.25;
  --leading-normal: 1.5;
  --leading-loose:  1.75;
}
```

## Border Radius

```css
:root {
  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-xl:   16px;
  --radius-2xl:  24px;
  --radius-full: 9999px;
}
```

## Shadow Scale

```css
:root {
  --shadow-sm:  0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md:  0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg:  0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl:  0 20px 25px rgba(0, 0, 0, 0.1);
  --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.3);
}
```
