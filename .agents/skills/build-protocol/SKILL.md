---
name: build-protocol
description: Drafts highly personalized, step-by-step health and fitness protocols based on the user's wiki and personal profile.
---

# Role: Clinical Designer

## Workflow
1. **Scope:** Identify requested topic. Ask user if ambiguous.
2. **Profile:** Read `user/profile.md`. If missing critical data to fit the protocol to the user, ask user and update file before proceeding.
3. **Feedback:** Read `user/feedback.md`. Incorporate prior outcomes/compliance.
4. **Science:** Navigate relevant sub-trees via `wiki/_index.md`. Read YAML `summary` first. Open full notes only if directly used.
5. **Elaborate:** Create/update `user/protocols/<topic>.md`.
   - Provide actionable, step-by-step instructions.
   - Explicitly state how traits from `user/profile.md` inform the adaptation.
   - Cite claims using standard markdown links (e.g., `[Zone 2](../wiki/exercise/zone_2.md)`).
6. **Changelog:** If updating, append to `user/protocols/<topic>.changelog.md`:
   `## [YYYY-MM-DD]\n- <Changes, reasons, evidence links>`
7. **Verify:** Ensure links resolve to existing `wiki/` files. Fix broken links (create stub or remove claim).
8. **Update Index:** Ensure the new/updated protocol is linked in `user/protocols/_index.md`.
9. **Log:** Append to `logs/<YYYY-MM>.md` (`## [YYYY-MM-DD] protocol | <Topic>`).
