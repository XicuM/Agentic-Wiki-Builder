---
name: research
description: Conducts full-text scientific literature reviews using local Semantic Scholar and arXiv APIs.
metadata: { "openclaw": { "emoji": "🧬" } }
---
# Role: Scientific Researcher (`research-agent`)

Execute as `research-agent` (multi-agent) or sequentially (single agent).

## Workflow
1. **Survey**: Read `state.json` (specifically the `"ingestion_queue"`), `sources/_index.md`, and domain indices to check existing coverage.
2. **Search**: Run search script (never search the web directly):
   - Primary: `python .agents/skills/research/scripts/search_literature.py "<query>" --limit 5`
   - You can restrict to a single provider with `--provider <name>` (choices: `pubmed`, `openalex`, `googlebooks`, `arxiv`, `semanticscholar`).
   - Stop and report errors on failure. Do NOT fabricate results, papers, metadata, summaries, or quotes under any circumstances. All gathered research must be real and verifiable. Summaries, abstracts, or metadata must **NEVER** be generated from training memory/data. If the python scripts fail to find or download a paper, do not create any source entries for it.
3. **Download & Populate**: Run the download script to fetch the PDF and extract it:
   - `python .agents/skills/research/scripts/download_paper.py "<paperId>" "<FileNameBase>" "<domain>"`
   - Supported `<paperId>` formats:
     - `openalex:<workId>` (e.g., `openalex:W4280913955`)
     - `pmid:<pmid>` (e.g., `pmid:32165487`)
     - `googlebooks:<volumeId>` (e.g., `googlebooks:yE5ADwAAQBAJ`)
     - `arXiv:<arxivId>` (e.g., `arXiv:2101.12345`)
     - `local:<path_to_pdf>` (e.g., `local:sources/literature/user_uploads/my_file.pdf`)
     - Raw Semantic Scholar hash (e.g., from Semantic Scholar search output)
   - **Important**: The script will automatically try all fallbacks. If it fails to find an open-access PDF, it will exit with an error. If this happens, or if you need more sources than the ones available, **pause and ask the user** to manually provide the PDFs. Do NOT add failed papers to the manifest.
   - Note: Downloads/copies PDF to `sources/literature/<domain>/<FileNameBase>/original.pdf`, extracts to `raw.md`, and creates `metadata.md`.
4. **Update Manifest**:
   - Append the clean link (NO checkmarks) to the local subdirectory `sources/literature/<domain>/_index.md`:
     `[filenameBase/raw.md](filenameBase/raw.md) - <Summary>. (<YYYY-MM-DD>) #<tags>`
   - Append the pending item to the `ingestion_queue` in `state.json` at the root of the project as a JSON object:
     `{"id": "<filenameBase>", "type": "Literature", "path": "sources/literature/<domain>/<filenameBase>/raw.md", "summary": "<Summary>", "enqueued_at": "<YYYY-MM-DDTHH:MM:SS>", "status": "pending", "tags": ["<domain>", "<tags>"]}`
5. **Commit**: Commit activity using `git commit -m "..."` within the appropriate submodule.
