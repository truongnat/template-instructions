# End-to-End Testing Best Practices

## Selector Strategy
- **Prioritize Accessibility**: Use `getByRole`, `getByLabel`, `getByPlaceholder`, and `getByText`. This ensures your tests verify that the app is actually usable.
- **Data Attributes as Fallback**: If accessibility selectors aren't enough, use `data-testid="component-name"`. Never use generated CSS classes (e.g., `.css-1ab2c3`).
- **Avoid Fragile Paths**: Never use absolute XPaths or deep-nested CSS selectors (e.g., `div > div > p > span`).

## Stability & Waiting
- **Actionability Checks**: Playwright/Cypress automatically wait for elements to be "actionable" (visible, stable, enabled). Trust the framework.
- **Custom Waiting**: If you must wait for a network response, use `page.waitForResponse(url)` instead of `time.sleep()`.
- **Race Condition Prevention**: Ensure that clicking a button that triggers an async action is followed by an `expect()` on the resulting state change.

## State Management
- **Isolate Sessions**: Use separate browser contexts or clear cookies/localStorage between tests.
- **Bypass UI for Setup**: If a test verifies the "Profile Page", don't use the UI to Login. Use an API call to set the authentication state to save time.

## CI/CD Optimization
- **Headless Mode**: Run tests in headless mode in CI to save resources.
- **Parallelization**: Split test suites across multiple workers to reduce execution time.
- **Artifacts**: Capture screenshots on failure, and full traces for debugging. Use the Playwright Trace Viewer to step through the execution.
