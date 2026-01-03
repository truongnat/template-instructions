# Which Workflow Should I Use?

## Quick Decision Tree

1. **Is this a production emergency?**
   - YES → `/emergency`
   - NO → Continue to 2

2. **Are you unsure which workflow to use?**
   - YES → `/route` (it will analyze and recommend)
   - NO → Continue to 3

3. **What are you trying to do?**

   **Start a new project:**
   - Complex/unknown → `/explore` first, then `@PM`
   - Clear requirements → `@PM` directly

   **Execute a small task (<4 hours):**
   - `/cycle`

   **Document a solution:**
   - `/compound`

   **Investigate a complex feature:**
   - `/explore`

   **Handle a production incident:**
   - `/emergency`

   **Manage sprints:**
   - Start: `/sprint start [N]`
   - Review: `/sprint review`
   - Retro: `/sprint retro`
   - Close: `/sprint close [N]`

   **Release a version:**
   - `/release`

   **Clean up project:**
   - `/housekeeping`

   **Check system health:**
   - `/validate`

   **View analytics:**
   - `/metrics`

   **Run full SDLC:**
   - `@PM` → `@BA` → `@SA` + `@UIUX` → `@TESTER` + `@SECA` → `@DEV` + `@DEVOPS` → `@TESTER` → `@DEVOPS` → `@PM`

## Role-Specific

**I need to:**
- Plan a project → `@PM`
- Gather requirements → `@BA`
- Design architecture → `@SA`
- Design UI/UX → `@UIUX`
- Implement code → `@DEV`
- Setup infrastructure → `@DEVOPS`
- Test/verify → `@TESTER`
- Security review → `@SECA`

---

Still confused? Use `/route` - it's smart! 🧠
