# Auto-Huberman Life OS Builder

Modular agent system for automating literature synthesis into actionable protocols via an auto-recursive wiki.

## Skills Workflow
- `research`: Discover novel mechanisms/data.
- `ingest`: Synthesize raw literature into wiki.
- `wiki-lint`: Audit wiki integrity.
- `build-protocol`: Generate final deliverables.

## Conventions
- Standard markdown links (no `[[wikilinks]]`).
- **Files:** `snake_case.md`. No spaces/uppercase.
- **YAML Front-Matter:**
  ```yaml
  ---
  title: <Concept Name>
  summary: >
    One-paragraph concept summary.
  sources:
    - <literature_filename>.md
  ---
  ```
  *Rule:* Survey skills (`build-protocol`, `wiki-lint`) must read `summary` first, opening full notes only if detail is needed.
- **Manifest:** `literature/_manifest.yaml` tracks state. `research` appends; `ingest` marks processed.
- **Profile:** `user/profile.md` is a living document. Ask user for missing data and update.

## Log Updates
After each operation, append the changes to the current month's log file (`logs/<YYYY-MM>.md`). If it does not exist, create it. Previous months' logs are archived.

## Autonomy & Optimization
Agents have autonomy to evolve the system:
1. **Agent Refinement:** Optimize `AGENTS.md` and `SKILL.md` for precision AND brevity.
2. **Wiki Structure:** Reorganize `wiki/` hierarchy to improve retrieval.
