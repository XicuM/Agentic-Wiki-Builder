---
name: ingest
description: Synthesizes raw text from the literature folder into an auto-recursive Obsidian wiki. Use this skill to update the knowledge base after new research is gathered.
---
# Role: Knowledge Synthesizer

## Workflow
1. **Manifest:** Read `literature/_manifest.yaml`. Process files where `ingested: false`.
2. **Read:** Parse unprocessed markdown in `literature/`.
3. **Organize:** Assign domains. Use existing `wiki/<domain>/` folders or create new ones with an `_index.md`.
4. **Concepts:** Create/update `wiki/<domain>/<concept>.md` for key mechanisms/findings.
   - Use YAML front-matter:
     ```yaml
     ---
     title: <Concept Name>
     summary: <One-paragraph summary of mechanisms and takeaways>
     sources:
       - <literature_filename>.md
     ---
     ```
   - Use standard links: `[Concept](../domain/concept.md)`.
   - Resolve conflicts explicitly (favor recency/quality).
5. **Indices:** Link new notes in parent `_index.md`. Link new domain folders in `wiki/_index.md`.
6. **Mark Processed:** Set `ingested: true` in `literature/_manifest.yaml`.
7. **Log:** Append to `logs/<YYYY-MM>.md` (`## [YYYY-MM-DD] ingest | <Topic>`).
