---
name: research
description: Conducts full-text scientific literature reviews. Use this skill when you need to find recent papers, mechanisms, or data not currently present in the user's knowledge base.
---
# Role: Scientific Researcher

## Workflow
1. **Manifest:** Read `literature/_manifest.yaml`. Skip topics with sufficient coverage.
2. **Search:** Run `python .agents/skills/research/scripts/search_papers.py "<query>"`. Parse JSON output.
   - Stop and report errors on failure. Do NOT fabricate results.
3. **Download:** Pick 1-3 highly relevant papers with `openAccessPdf`. Run `python .agents/skills/research/scripts/ingest_paper.py "<PDF_URL>" "<FileName>"`.
4. **Manifest Update:** Append downloaded papers to `literature/_manifest.yaml`:
   ```yaml
   - file: <filename>.md
     ingested: false
     date: <YYYY-MM-DD>
     topics: [<domain1>, <domain2>]
   ```
5. **Log & Handoff:** Append to `logs/<YYYY-MM>.md` (`## [YYYY-MM-DD] research | <Topic>`).
