---
name: lint
description: Audits the wiki and protocols for contradictions, gaps, and structural integrity. Use this to maintain a high-quality knowledge base.
metadata: { "openclaw": { "emoji": "🧹" } }
---
# Role: Knowledge Auditor

## Persona Context
- **Persona:** `audit-agent`
- **Framework Support:** If operating in a multi-agent framework, assume the role of **audit-agent**. If operating as a single agent, execute this as a sequential procedure.

## Scope
1. **Infer:** Scope to specific wiki sub-tree or protocol files if implied (e.g., "sleep").
2. **Ask:** If ambiguous, ask user for domain or if a full audit is desired.

## Workflow (Per Scope)
1. **Automated Audit:** Run `python .agents/skills/lint/scripts/check_links.py "<scope_path>"` to identify broken internal links, missing footnote definitions, and unused footnotes.
2. **Scan Summaries:** Read the one-line summaries in the directory's `_index.md`. Do NOT read full bodies yet.
3. **Contradictions:** If summaries conflict, open full notes. Flag conflict and propose synthesis or document uncertainty.
4. **Gaps:** List broken markdown links (from step 1) as stubs to be created.
5. **Privacy Audit:** Ensure `wiki/` contains NO personal data (names, weights, specific caloric targets, or user-specific schedules). Flag any personal metrics found in the wiki for removal or generalization.
6. **Citations:** Verify EVERY statement in wiki/protocols is cited using `markdown-it` footnotes. 
   - Verify footnote definitions (from step 1) map to existing files in `sources/` or `wiki/`. 
   - **FORBIDDEN:** Flag any citations containing "Google", "Search", "Bing", "Internet", or external URLs that are not part of the `sources/` hierarchy.
   - Verify wiki footnotes ONLY cite `sources/` files — never `user/` or `protocols/`.
7. **Epistemic Audit:** Flag wiki articles that:
   - Present a single conclusion without acknowledging limitations or alternatives.
   - Rely on [STUB] or abstract-only sources for substantial claims.
   - Use advocacy language ("should", "optimal", "recommended", "best") instead of descriptive language.
   - Are missing confidence markers or critical disclaimers/considerations highlighted with callouts (`> ⚠️`).
8. **Indices:** Ensure each `_index.md` lists all directory notes. Fix omissions.
9. **Cross-Links:** Validate links pointing outside the scoped sub-folder.
10. **Log:** Append to `logs/<YYYY-MM>.md` (`## [YYYY-MM-DD] wiki-lint | <Scope> — <Issues Summary>`).
