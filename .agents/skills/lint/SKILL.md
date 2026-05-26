---
name: lint
description: Audits wiki and protocols for contradictions, gaps, and structural integrity.
metadata: { "openclaw": { "emoji": "🧹" } }
---
# Role: Knowledge Auditor (`audit-agent`)

Execute as `audit-agent` (multi-agent) or sequentially (single agent).

## Scope
Scope to a sub-tree/files if implied (ask user if ambiguous).

## Workflow
1. **Automated Audit**: Run `python .agents/skills/lint/scripts/check_links.py "<scope_path>"` to check for broken links, missing/unused footnotes, directory bloat (> 15 files), and page length limits (max 1500 words for wiki/user pages).
2. **Sources Backup**: Run `python .agents/skills/lint/scripts/backup_sources.py` to backup sources URLs to `user/sources_backup.json`.
2. **Scan & Resolve**: Read `_index.md` summaries. If conflicting, inspect full files and propose synthesis. List broken links as stubs to create. Ensure `_index.md` files list all folder contents correctly.
3. **Privacy Audit**: Ensure `wiki/` has NO user-specific data/schedules (flag for removal/generalization).
4. **Citation Audit**: 
   - Verify all statements have `markdown-it` footnotes.
   - **Forbidden**: Citations referencing search engines or external URLs directly (must reference `sources/` or `wiki/` relative paths).
   - Wiki pages must only cite `sources/` files (never `user/` or `protocols/`).
5. **Epistemic Audit**: Flag articles lacking confidence markers, using advocacy language, missing alternative viewpoints, or relying on `status: stub` sources.
6. **Commit**: Commit activity using `git commit -m "[wiki-lint] <Scope> — <Issues Summary>"` within the appropriate submodule.
