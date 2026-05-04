---
name: wiki-lint
description: Audits the wiki for contradictions, gaps, and structural integrity. Use this to maintain a high-quality knowledge base.
---
# Role: Knowledge Auditor

## Scope
1. **Infer:** Scope to specific sub-tree if implied (e.g., "sleep").
2. **Ask:** If ambiguous, ask user for domain or if a full audit is desired.
3. **Full:** If requested, iterate all sub-folders sequentially.

## Workflow (Per Scope)
1. **Scan Summaries:** Read YAML `summary` for scoped notes. Do NOT read full bodies yet.
2. **Contradictions:** If summaries conflict, open full notes. Flag conflict and propose synthesis or document uncertainty.
3. **Gaps:** List broken markdown links as stubs to be created.
4. **Citations:** Verify `sources` map to existing files in `literature/`. Flag orphaned citations.
5. **Indices:** Ensure each `_index.md` lists all directory notes. Fix omissions.
6. **Cross-Links:** Validate links pointing outside the scoped sub-folder.
7. **Log:** Append to `logs/<YYYY-MM>.md` (`## [YYYY-MM-DD] wiki-lint | <Scope> — <Issues Summary>`).
