---
name: investment-toolset
description: Performs CAGR, future value, DCA projections, portfolio weights, and stock trends. Output is structured JSON.
compatibility: Requires Python 3.10+
metadata: { "openclaw": { "emoji": "🧮" } }
---
# Role: Financial Calculator (`investor-agent`)

CLI calculator at `.agents/skills/investment-toolset/scripts/calc.py`.

## Available Subcommands

| Subcommand | Purpose | Key Flags |
|:---|:---|:---|
| `cagr` | Compound Annual Growth Rate | `--start`, `--end`, `--years` |
| `fv` | Future Value | `--rate`, `--years`, `--pmt`, `--pv` |
| `dca` | Dollar-Cost Averaging | `--monthly`, `--rate`, `--years` |
| `weights` | Portfolio allocation | `--holdings` (JSON array: `'[["VWCE", 5000]]'`) |
| `stock` | Yahoo Finance price & trends | `--ticker` |
| `news` | Yahoo Finance RSS headlines | `--ticker` |

## Workflow & Examples
1. Run appropriate subcommand using `.agents/skills/investment-toolset/scripts/calc.py`:

```bash
# CAGR: python3 .agents/skills/investment-toolset/scripts/calc.py cagr --start 10000 --end 18000 --years 5
# FV: python3 .agents/skills/investment-toolset/scripts/calc.py fv --rate 0.07 --years 20 --pmt 12000 --pv 15000
# DCA: python3 .agents/skills/investment-toolset/scripts/calc.py dca --monthly 1000 --rate 0.08 --years 25
# Weights: python3 .agents/skills/investment-toolset/scripts/calc.py weights --holdings '[["VWCE", 5000], ["AAPL", 1200]]'
# Stock: python3 .agents/skills/investment-toolset/scripts/calc.py stock --ticker AAPL
# News: python3 .agents/skills/investment-toolset/scripts/calc.py news --ticker ASTS
```
2. Parse output JSON. Present results or pass to calling skill.
