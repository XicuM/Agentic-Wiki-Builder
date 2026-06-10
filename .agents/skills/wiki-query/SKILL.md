# Role: Vault Querier (Universal)

Uses [`qmd`](https://github.com/tobi/qmd) engine (BM25 + vector + LLM re-ranking). Config at `.agents/qmd.yml`.

## Commands (run from `.agents/`)
| Mode | Command |
|:---|:---|
| Keyword/Grep | `qmd search "<query>"` |
| Semantic (vector) | `qmd vsearch "<query>" -n 5` |
| Hybrid + rerank (best) | `qmd query "<query>"` |
| Read full document | `qmd get "<relative_path>"` |

## Flags
- `--json` — structured output
- `--files --min-score 0.4` — only paths above relevance
- `-c <collection>` — restrict to `wiki`, `protocols`, or `sources`

## Maintenance
After adding/changing files, reindex: `qmd update` (from `.agents/`).
