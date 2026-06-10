# Role: Expense Tracker (Universal)

Canonical CSV at `user/finance/transactions.csv`. Scripts at `.agents/skills/expense-tracker/scripts/`.

## Workflow
1. **Parse**: `.venv/bin/python .agents/skills/expense-tracker/scripts/parse.py "sources/scratch/<file>.csv"` — deduplicates by `transaction_id`, maps `mcc_code` → `spend_category`, appends to canonical CSV. Returns JSON: `new_rows`, `skipped`, `categories`.
2. **Query**: Run `.venv/bin/python .agents/skills/expense-tracker/scripts/query.py <subcommand> [args...]`
