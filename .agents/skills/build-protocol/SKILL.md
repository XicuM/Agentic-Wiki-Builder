---
name: build-protocol
description: Drafts highly personalized, step-by-step protocols based on the user's wiki and profile.
metadata: { "openclaw": { "emoji": "🏗️" } }
---
# Role: Clinical Designer (`protocol-agent`)

Execute as `protocol-agent` (multi-agent) or sequentially (single agent).

## Workflow
1. **Scope & Profile**: Identify topic (ask if ambiguous). Read `user/profile.md` (profile index) and the linked profile sections. Ask user for missing critical context, then update profile.
2. **Feedback & Science**: Read `user/feedback.md` for compliance. Read target directory's `_index.md` first to survey files via one-line summaries. Open notes only as needed. If data is missing, halt and use `research` skill (never search web directly).
3. **Elaborate**: Create/update `user/protocols/<topic>.md`:
   - Provide **strictly actionable**, step-by-step instructions.
   - **No justifications**: Do not explain "why" a recommendation is made in the protocol.
   - **Citations**: Cite every action/parameter via `markdown-it` footnotes (e.g. `[^1]`) linking to the relevant wiki page.
   - State how traits from `user/profile.md` (and its sections) inform adaptations (e.g., "Scaled to your [Trait]").
4. **Verify & Link**: Ensure links resolve to existing `wiki/` files. Add new/updated protocol to `user/protocols/_index.md`.
5. **Commit**: Commit activity using `git commit -m "..."` within the appropriate submodule.
