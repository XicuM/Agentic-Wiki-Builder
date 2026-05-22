---
name: research
description: Conducts full-text scientific literature reviews. Use this skill when you need to find recent papers, mechanisms, or data not currently present in the user's knowledge base.
metadata: { "openclaw": { "emoji": "🧬" } }
---
# Role: Scientific Researcher

## Persona Context
- **Persona:** `research-agent`
- **Framework Support:** If operating in a multi-agent framework, assume the role of **research-agent**. If operating as a single agent, execute this as a sequential procedure.

## Workflow
1. **Manifest:** Read `sources/_index.md` and relevant domain indices (e.g., `sources/literature/exercise/_index.md`). Skip topics with sufficient coverage.
2. **Search:** 
   - Primary: Run `python .agents/skills/research/scripts/search_papers.py "<query>"` (Semantic Scholar).
   - Fallback/Direct: Run `python .agents/skills/research/scripts/search_arxiv.py "<query>"` for recent preprints or when Semantic Scholar misses results.
   - Parse JSON output.
   - NEVER use direct internet search tools. You MUST rely exclusively on the provided Python scripts.
   - Stop and report errors on failure. Do NOT fabricate results.
3. **Download & Populate:** Pick 1-3 highly relevant papers. Identify the correct domain (e.g., `exercise`, `nutrition`). Run `python .agents/skills/research/scripts/ingest_paper.py "<paperId>" "<FileNameBase>" "<domain>"`.
   - `paperId` can be a Semantic Scholar ID or an `arXiv:<id>` string.
   - The script automatically falls back to arXiv for PDF downloads if Semantic Scholar's open-access link is missing.
   - This script downloads the PDF to `sources/literature/<domain>/<FileNameBase>/original.pdf`, extracts text to `raw.md`, and creates `metadata.md`.
4. **Manifest Update:** 
   - Update `sources/literature/<domain>/_index.md`: Append the new paper entry.
   - Update `sources/_index.md`: If the paper is a major addition or if tracking "Pending Ingestion", add/update it there. (Note: `sources/_index.md` serves as the SOURCE OF TRUTH for high-level ingestion state).
   - Entry format: `- [ ] [Literature] [literature/<domain>/<filenameBase>/raw.md](literature/<domain>/<filenameBase>/raw.md) - <Brief Summary>. (<YYYY-MM-DD>) #<domain> #<tags>`
5. **Log & Handoff:** Append to `logs/<YYYY-MM>.md` (`## [YYYY-MM-DD] research | <Topic>`).
