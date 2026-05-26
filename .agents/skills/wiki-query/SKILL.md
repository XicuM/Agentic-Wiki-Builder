---
name: wiki-query
description: Queries the wiki, protocols, and literature folders via local qmd utility.
metadata: { "openclaw": { "emoji": "🔎" } }
---
# Role: Vault Querier (Universal Utility)

Uses local [`qmd`](https://github.com/tobi/qmd) engine (BM25 + vector + LLM re-ranking).

## Setup & Maintenance (From `.agents/` directory)
Run once to setup:
```sh
cd .agents
qmd collection add ../wiki --name wiki
qmd collection add ../user/protocols --name protocols
qmd collection add ../sources/literature --name sources
qmd context add qmd://wiki "Objective evidence base: mechanisms, studies, hypotheses"
qmd context add qmd://protocols "Personalized actionable protocols for the user"
qmd context add qmd://sources "Raw ingested literature and source documents"
qmd embed
```
**Update Index**: Run `qmd update` from `.agents/` whenever files are added or changed.

## Workflow
1. **Search**: Choose the appropriate mode from `.agents/`:
   - *Keyword/Grep*: `qmd search "<query>"`
   - *Semantic (Vector)*: `qmd vsearch "<query>" -n 5`
   - *Hybrid + Rerank (Best Precision)*: `qmd query "<query>"`
2. **Flags**: Append `--json` (structured output), `--files --min-score 0.4` (only paths above relevance threshold), or `-c <collection>` (`wiki`, `protocols`, `sources`).
3. **Retrieve**: Run `qmd get "<relative_path>"` (e.g. `wiki/sleep.md`) to read a document's full contents.
