---
name: fact-check
description: Verifies specific claims against the wiki, protocols, and scientific literature. Use this when you need to confirm if a statement is accurate or supported by evidence.
metadata: { "openclaw": { "emoji": "✅" } }
---
# Role: Fact Checker

## Persona Context
- **Persona:** `audit-agent`
- **Framework Support:** If operating in a multi-agent framework, assume the role of **audit-agent**. If operating as a single agent, execute this as a sequential procedure.

## Workflow
1. **Atomic Claims:** Break down the user's statement into specific, verifiable claims.
2. **Internal Search:** Use the `wiki-query` skill to find what the wiki and protocols say about these claims.
   - Run `qmd query "<claim_keywords>" --json` from `.agents/` for hybrid search (best precision).
   - Fall back to `qmd search "<claim_keywords>"` for fast keyword lookup.
3. **External Research:** If internal evidence is missing, conflicting, or the claim is about "scientific truth," use the `research` skill.
   - Run `python .agents/skills/research/scripts/search_papers.py "<claim_keywords>"`.
4. **Synthesize Verdict:**
   - **Supported:** Claim matches existing wiki and/or literature.
   - **Contradicted:** Evidence explicitly refutes the claim.
   - **Mixed:** Evidence is conflicting or inconclusive.
5. **Report & Update:**
   - Present findings with citations.
   - If the wiki is outdated or wrong, propose a specific edit to the relevant `wiki/` file.
   - Log the activity to `logs/<YYYY-MM>.md`.

## Example Log Entry
`## [YYYY-MM-DD] fact-check | <Claim> — <Verdict> (Citations: <Files>)`
