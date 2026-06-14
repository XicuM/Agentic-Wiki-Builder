# MCP Servers

Three FastMCP servers exposing project skills as typed, composable tools.

## Servers

| Server | Entry point | Skills covered |
|---|---|---|
| `finance-mcp` | `finance/server.py` | `investment-toolset`, `expense-tracker` |
| `wiki-mcp` | `wiki/server.py` | `wiki-query`, `lint` |
| `research-mcp` | `research/server.py` | `research`, `state.json` queue |

## Installation

```bash
# From project root — installs into the shared venv
.venv/bin/pip install -r requirements.txt
```

## Client Configuration

Add to your MCP host config (e.g. `~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "finance-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/.agents/mcp/finance/server.py"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/agentic-wiki-builder"
      }
    },
    "wiki-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/.agents/mcp/wiki/server.py"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/agentic-wiki-builder"
      }
    },
    "research-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/.agents/mcp/research/server.py"],
      "env": {
        "PROJECT_ROOT": "/absolute/path/to/agentic-wiki-builder",
        "SEMANTIC_SCHOLAR_API_KEY": "optional-api-key"
      }
    }
  }
}
```

Replace `/absolute/path/to/` with the actual filesystem path.

## Tool Reference

### finance-mcp

| Tool | Description |
|---|---|
| `calc_cagr` | Compound Annual Growth Rate |
| `calc_fv` | Future Value (lump sum + contributions) |
| `calc_dca` | Dollar-Cost Averaging projection |
| `calc_weights` | Current + optimal portfolio weights |
| `stock_price` | Current price and 1d/1m/6m/1y change |
| `stock_news` | Headlines with FinBERT sentiment |
| `stock_backtest` | SMA 20/50 crossover backtest (vectorbt) |
| `expense_parse` | Ingest a bank CSV into `transactions.csv` |
| `expense_monthly` | Category breakdown for a month |
| `expense_range` | Category totals over a date range |
| `expense_category` | All transactions in a category |
| `expense_uncategorized` | Transactions missing a category |
| `expense_summary` | All-time totals by category |
| `expense_trading` | BUY/SELL activity |
| `expense_transfers` | Peer-to-peer and partner transfers |
| `expense_top` | Top N merchants by spend |
| `expense_export_monthly` | Export per-month .md summaries |

Resources: `finance://transactions`, `finance://category-rules`

### wiki-mcp

| Tool | Description |
|---|---|
| `wiki_search` | Keyword/grep search |
| `wiki_vsearch` | Semantic vector search |
| `wiki_query` | Hybrid BM25 + vector + rerank (best quality) |
| `wiki_get` | Retrieve full document by path |
| `wiki_update_index` | Rebuild qmd semantic index |
| `lint_check_links` | Broken links, footnotes, bloat audit |
| `lint_backup_sources` | Snapshot sources metadata to JSON |

Resources: `wiki://collections/wiki`, `wiki://collections/protocols`, `wiki://collections/sources`

### research-mcp

| Tool | Description |
|---|---|
| `search_literature` | Search 19+ providers via academic-mcp |
| `download_paper` | Fetch metadata → PDF → markitdown → state.json |
| `queue_list` | View ingestion queue (filterable by status) |
| `queue_enqueue` | Manually add item to queue |
| `queue_dequeue` | Remove completed item from queue |

Resources: `research://state`, `research://sources/index`

## Conventions

- **Agent commits**: servers are stateless — git commits are always the agent's responsibility.
- **No fabrication**: `search_literature` returns empty list if no results found; never hallucinates papers.
- **No PDF, no ingest**: `download_paper` raises and cleans up the directory on failure. The agent should then ask the user to supply the PDF manually (`local:<path>` format).
