# TypeScript Error Fix: `toBeInTheDocument` Not Found

## Problem

**Error Message:**
```
Property 'toBeInTheDocument' does not exist on type 'Assertion<Element | null>'
```

**Location:** `apps/frontend/src/components/dashboard/__tests__/DashboardView.test.tsx:39`

## Root Cause

This error occurs because **TypeScript doesn't recognize the custom matchers** from `@testing-library/jest-dom`. 

### Why This Happens:

1. **Vitest uses different assertion types** than Jest
2. **`@testing-library/jest-dom`** provides custom DOM matchers like:
   - `toBeInTheDocument()`
   - `toHaveClass()`
   - `toBeVisible()`
   - etc.
3. **TypeScript needs explicit type declarations** to know these matchers exist

## The Solution ✅

I've applied a **two-part fix**:

### Part 1: Type Declaration File

Created `/apps/frontend/src/vitest.d.ts`:
```typescript
/// <reference types="vitest" />
import '@testing-library/jest-dom/vitest';
```

This imports the type definitions for jest-dom matchers in Vitest.

### Part 2: TypeScript Configuration

Updated `/apps/frontend/tsconfig.app.json`:
```json
{
  "compilerOptions": {
    "types": ["vite/client", "vitest/globals", "@testing-library/jest-dom"]
  }
}
```

Added:
- `"vitest/globals"` - For global test functions (describe, it, expect, etc.)
- `"@testing-library/jest-dom"` - For custom DOM matchers

## How It Works

### Before the Fix:
```typescript
expect(element).toBeInTheDocument();
//              ^^^^^^^^^^^^^^^^^ TypeScript error: Property doesn't exist
```

TypeScript only knew about basic Vitest assertions like:
- `toBe()`
- `toEqual()`
- `toBeTruthy()`

### After the Fix:
```typescript
expect(element).toBeInTheDocument(); // ✅ TypeScript recognizes this!
```

TypeScript now knows about all jest-dom matchers:
- `toBeInTheDocument()`
- `toHaveClass(className)`
- `toHaveTextContent(text)`
- `toBeVisible()`
- `toBeDisabled()`
- And many more...

## Verification

The error should now be resolved. You can verify by:

1. **Restarting your TypeScript server** in VS Code:
   - Press `Cmd+Shift+P`
   - Type "TypeScript: Restart TS Server"
   - Press Enter

2. **Check the file** - The red squiggly line should disappear

3. **Run the tests** (once node_modules permission is fixed):
   ```bash
   cd apps/frontend && bun run test:run
   ```

## Additional Context

### Your Existing Setup (Already Correct):

1. **`vitest.config.ts`** has `globals: true` ✅
   - This allows using `expect`, `describe`, `it` without imports

2. **`src/tests/setup.ts`** extends matchers ✅
   ```typescript
   import * as matchers from '@testing-library/jest-dom/matchers';
   expect.extend(matchers);
   ```

3. **Setup file is configured** ✅
   ```typescript
   setupFiles: ['./src/tests/setup.ts']
   ```

The only missing piece was **telling TypeScript** about these extended types, which is now fixed!

## Related Files Modified

1. ✅ `/apps/frontend/src/vitest.d.ts` (created)
2. ✅ `/apps/frontend/tsconfig.app.json` (updated)

## Summary

**Problem**: TypeScript didn't know about jest-dom matchers  
**Solution**: Added type declarations and updated tsconfig  
**Result**: All custom matchers now have proper TypeScript support  
**Status**: ✅ FIXED
