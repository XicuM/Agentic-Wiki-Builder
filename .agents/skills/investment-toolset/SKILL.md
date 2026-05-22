---
name: investment-toolset
description: >-
  Performs investment math — CAGR, future value, DCA projections, and portfolio
  weight analysis. Use when the user asks to calculate returns, project
  contributions, compare growth scenarios, or analyze portfolio allocation
  percentages.
compatibility: Requires Python 3.10+
metadata: { "openclaw": { "emoji": "🧮" } }
---
# Role: Financial Calculator

Analytical engine for the `investor-agent` persona.
All output is **structured JSON** so results can be parsed programmatically by
other skills (e.g., `build-protocol` or `investor-agent`).

## Available Scripts

- **`scripts/calc.py`** — Core CLI calculator with the following subcommands:

| Subcommand   | Purpose                                   | Key Flags                                      |
|:-------------|:------------------------------------------|:-----------------------------------------------|
| `cagr`       | Compound Annual Growth Rate               | `--start`, `--end`, `--years`                  |
| `fv`         | Future Value (lump sum + contributions)   | `--rate`, `--years`, `--pmt`, `--pv`           |
| `dca`        | Dollar-Cost Averaging projection          | `--monthly`, `--rate`, `--years`               |
| `weights`    | Portfolio weight percentages              | `--holdings` (JSON array of `[name, value]`)   |
| `stock`      | Fetch stock price and 1m/6m/1y trends     | `--ticker`                                     |
| `news`       | Fetch recent stock news headlines         | `--ticker`                                     |

## Workflow

1. **Identify the calculation** the user or calling agent needs.
2. **Run the appropriate subcommand**:

```bash
# CAGR — "What annualised return did I get?"
python3 .agents/skills/investment-calculator/scripts/calc.py cagr \
  --start 10000 --end 18000 --years 5

# Future Value — "How much will I have in 20 years?"
python3 .agents/skills/investment-calculator/scripts/calc.py fv \
  --rate 0.07 --years 20 --pmt 12000 --pv 15000

# DCA — "What does €1,000/month at 8% look like over 25 years?"
python3 .agents/skills/investment-calculator/scripts/calc.py dca \
  --monthly 1000 --rate 0.08 --years 25

# Weights — "What percentage is each holding?"
python3 .agents/skills/investment-calculator/scripts/calc.py weights \
  --holdings '[["VWCE", 5000], ["AAPL", 1200], ["BTC", 800]]'

# Stock — "What is AAPL's price and 1-year trend?"
python3 .agents/skills/investment-calculator/scripts/calc.py stock --ticker AAPL

# News — "Any recent news on ASTS?"
python3 .agents/skills/investment-calculator/scripts/calc.py news --ticker ASTS
```

3. **Parse the JSON output** and present it to the user or feed it into another skill.
4. **Log** the calculation to `logs/<YYYY-MM>.md` if it was a user-facing request.
