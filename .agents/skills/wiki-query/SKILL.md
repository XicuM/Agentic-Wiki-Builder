---
name: wiki-query
description: Queries the wiki, protocols, and literature folders for specific keywords or patterns. Use this as a prerequisite for auditing, fact-checking, or cross-referencing information.
metadata: { "openclaw": { "emoji": "🔎" } }
---
# Role: Vault Querier

## Persona Context
- **Persona:** Universal Utility
- **Framework Support:** Shared utility used by all personas to navigate the knowledge base.
- **Engine:** [`qmd`](https://github.com/tobi/qmd) — BM25 + vector + LLM re-ranking, all local.
- **Index DB:** `.agents/.qmd/index.sqlite` (SQLite, incremental).

## Setup (First-Time Only)
Run once when the skill is first used or after a fresh clone:
```sh
cd .agents

# Register the three vault collections
qmd collection add ../wiki --name wiki
qmd collection add ../user/protocols --name protocols
qmd collection add ../sources/literature --name sources

# Attach context metadata (improves re-ranking quality)
qmd context add qmd://wiki "Objective evidence base: mechanisms, studies, hypotheses"
qmd context add qmd://protocols "Personalized actionable protocols for the user"
qmd context add qmd://sources "Raw ingested literature and source documents"

# Generate vector embeddings (first-time; takes a few minutes)
qmd embed
```

## Workflow
1. **Update Index:** Run `qmd update` from `.agents/` whenever new files have been added to the vault (e.g., after `ingest` completes). This is incremental — only new or changed files are reprocessed.
2. **Execute Search** (choose the right mode for the task):
   - **Keyword/Regex:** `qmd search "<query>"` — fast, no model needed. Use for exact terms, filenames, or grep-style lookup.
   - **Semantic:** `qmd vsearch "<query>" -n 5` — vector similarity. Use for concept-based retrieval.
   - **Hybrid + Rerank (best quality):** `qmd query "<query>"` — BM25 + vector + LLM re-ranking via RRF. Use when precision matters (fact-checking, synthesis).
3. **Retrieve Full Document:** `qmd get "wiki/path/to/file.md"` — returns full content. Use after a search to read the source.
4. **Analyze Results:** Review returned file paths, scores, and snippets.
5. **Follow-up:** Use `qmd get` on the top-ranked paths to read full context if needed.

## Agent-Friendly Output Flags
Append these to any command for structured output:
- `--json` — machine-readable results (path, score, snippet)
- `--files --min-score 0.4` — list only file paths above a relevance threshold
- `-n <N>` — limit to top N results (default: 5)
- `-c <collection>` — scope search to `wiki`, `protocols`, or `sources` only

### Examples
```sh
# Keyword search across all collections
qmd search "circadian rhythm"

# Semantic search, top 10, wiki only
qmd vsearch "how does sleep affect cognition" -n 10 -c wiki

# Best-quality hybrid search with JSON output for an agent
qmd query "protein synthesis window post-exercise" --json

# List all relevant files above 0.4 threshold
qmd query "intermittent fasting" --all --files --min-score 0.4

# Retrieve a full document
qmd get "wiki/personal/sleep.md"
```

## Integration
- **Ingest:** Call `qmd update` at the end of every `ingest` run to keep the index fresh.
- **Linting:** Use `qmd search` to find broken links or verify term consistency across files.
- **Fact-Checking:** Use `qmd query` to find existing claims before looking for external literature.
- **Build-Protocol:** Use `qmd query` with `--files` to surface the most relevant wiki sections.
