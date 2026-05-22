---
name: ingest
description: Synthesizes raw text from the literature folder into an auto-recursive Obsidian wiki. Use this skill to update the knowledge base after new research is gathered.
metadata: { "openclaw": { "emoji": "📥" } }
---
# Role: Knowledge Synthesizer

## Persona Context
- **Persona:** `synthesis-agent`
- **Framework Support:** If operating in a multi-agent framework, assume the role of **synthesis-agent**. If operating as a single agent, execute this as a sequential procedure.

## Workflow
1. **Manifest:** Read `sources/_index.md` and relevant sub-indices (e.g., `sources/literature/_index.md`). Process files marked as pending (`- [ ]`).
2. **Read:** Parse unprocessed markdown in `sources/` (e.g., `sources/literature/`, `sources/code/`, `sources/internal_documentation/`).
3. **Auto-Discovery:** Read `_index.md` files to identify existing notes and their summaries.
4. **Synthesize:** Based on existing content and source type, either update a relevant note or create a new page.
   - **Focus:** Map the source landscape. For every claim/pattern:
     1. State the finding/pattern and its source.
     2. Note limitations or context (sample size, design, code dependencies, meeting participants).
     3. Present conflicting or alternative evidence/implementations if they exist.
     4. Mark confidence and disclaimers: Use callouts (`> ⚠️`) for confidence levels (**Strong consensus**, **Moderate evidence**, or **Preliminary/Contested**), limitations, conflicting evidence, and critical disclaimers or practical considerations.
   - Protocols decide *what to do*. The wiki explains *what we know and don't know*.
   - **Citation Diversity:** If a page's claims all trace to a single source, add a note (e.g., `> ⚠️ This page relies on a single source.`) and flag the gap for future `research` runs.
   - **ANONYMIZATION:** Never include user-specific data. Use general conditional logic (e.g., "In individuals with [Trait]...") instead of referring to the user or their profile.
   - **CITATIONS:** Every single statement MUST be cited using `markdown-it` footnotes (e.g., `[^1]`) pointing to the source file in `sources/`. Definitions MUST be at the bottom of the page.
   - **Interconnection:** Actively link related wiki pages using inline markdown links: `[Concept](../domain/concept.md)`. This ensures a highly interconnected knowledge base. Do not use footnotes for internal wiki references.
   - Resolve conflicts explicitly (favor recency/quality).
5. **Indices:** Update `_index.md` files. Ensure all links in the directory are present, with a one-line summary for each one.
6. **Mark Processed:** Mark the item as completed (`- [x]`) in the relevant source `_index.md` files and the main `sources/_index.md`.
7. **Log:** Append to `logs/<YYYY-MM>.md` (`## [YYYY-MM-DD] ingest | <Topic>`).
