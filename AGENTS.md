# Agentic Wiki Builder

Modular system for literature synthesis into an auto-recursive wiki and actionable protocols.

## Hybrid Execution Model
Framework-agnostic. Supports:
1. **Multi-Agent (MAS)**: Supervisor orchestrates specialized personas via filesystem handoffs.
2. **Single-Agent**: One agent sequentially executes the pipeline following same handoff rules.

## Core Personas (MAS)
- **Supervisor**: Orchestrates, creates tasks, delegates, and monitors `sources/_index.md`.
- **Researcher (`research-agent`)**: Discovers literature, stages files in `sources/`, updates manifest.
- **Synthesizer (`synthesis-agent`)**: Ingests raw sources, updates `wiki/` knowledge base.
- **Protocol Architect (`protocol-agent`)**: Translates `wiki/` and `user/profile.md` (profile index) into actionable protocols.
- **Investor (`investor-agent`)**: Advises on portfolio, tracks holdings via `wiki/investments/` & `user/portfolio.md`.
- **Auditor (`audit-agent`)**: Audits system integrity (linting, fact-checking).

## Handoff Protocol
State is strictly filesystem-driven:
1. **Discovery**: `research` appends the clean file link to the domain-specific index (e.g. `sources/literature/exercise/_index.md`) and adds a pending queue item object to `state.json` at the root of the project.
2. **Ingestion**: `ingest` processes pending items in the `state.json` queue into `wiki/`, then removes the processed items from `state.json`.
3. **Drafting**: `build-protocol` updates `user/protocols/` using `wiki/` and user feedback.
4. **Validation**: `lint` and `fact-check` run audit scripts on all directories.

## Skills Workflow & Owners
- `wiki-query` (Universal): Query wiki or protocols.
- `research` (`research-agent`): Discover literature.
- `ingest` (`synthesis-agent`): Synthesize literature into wiki.
- `build-protocol` (`protocol-agent`): Generate actionable protocols.
- `lint` (`audit-agent`): Structure/link audit.
- `fact-check` (`audit-agent`): Claim verification.
- `investment-toolset` (`investor-agent`): Financial/investment math.

## Conventions & Strict Rules
- **Context Isolation:** When working on `professional/` tasks, NEVER pull data from `personal/` unless explicitly requested.
- **Hierarchy of Evidence:** `Protocols` cite the `Wiki` (actionable synthesis); `Wiki` cites `Sources` (raw evidence from literature, code, or documentation).
- **Strict Sourcing & Factuality:** **CRITICAL**: NEVER fabricate, hallucinate, or make up sources, papers, books, or quotes. All files, summaries, and metadata in `sources/` must represent real, verifiable publications, and all information must be factually accurate.
- **Verifiable Sourcing Rule:** Every source folder under `sources/` must represent a real, verified document that actually exists. Specifically, literature sources MUST contain the real underlying document (e.g., `original.pdf` or parsed raw text). Summaries, abstracts, or metadata must **NEVER** be generated from the model's training data or memory. Non-verified or memory-generated sources are prohibited and must be removed immediately.
- **Truth Over Completion (Priority):** The absolute, non-negotiable goal of this system is objective, verifiable truth. It is completely acceptable and expected to halt, fail a task, or refuse to generate a wiki page if a verified source does not exist in the repository. Never invent or synthesize concepts from training memory to fulfill a request if it lacks verified, ingested literature.
- **Information Sourcing:** **CRITICAL**: NEVER search the internet directly. Use the `research` skill's scripts to gather external information.
- **Protocol Citations:** EVERY generated protocol statement MUST include a `markdown-it` footnote referencing an internal wiki file (e.g., `[^1]`).
  - **Wiki**: Cite source files in `sources/` via bottom-of-page footnotes (e.g., `[^1]: [Title/Author](sources/path/metadata.md)`).
  - **Protocols**: Cite wiki pages via footnotes (e.g., `[^1]: [Wiki Topic](wiki/path.md)`).
  - Format: markdown-it footnote style (`[^1]` in text, definition at bottom).
- **No Stubs (Strict)**: If source has `status: stub` or failed extraction, DO NOT use it for wiki synthesis. Halt and request the full PDF.
- **Wiki Interconnection**: Use inline relative markdown links (`[Text](../path.md)`). No `[[wikilinks]]`.
- **Visual Synthesis**: Heavily utilize Mermaid diagrams (````mermaid````) to map out protocols, biological mechanisms, system architectures, decision trees, and complex conceptual relationships. Prefer visual abstractions (flowcharts, state diagrams, sequence diagrams) for high-level summaries.
- **Naming & Case**: Files must be `snake_case.md`.
- **Directory Indices**: Every directory requires `_index.md` listing all files in it with a one-line summary. Skills must read `_index.md` first. Directory indices must remain clean, static catalogs and must NOT contain task or ingestion checkmarks (`[x]` or `[ ]`).
- **Manifest / Ingestion Queue (`state.json`)**: Central registry at the project root that serves as the single source of truth for orchestrating all agents. Contains the ingestion queue and active agent states; once items are processed and ingested, they are removed from the queue in this file.
- **Separation of responsibilities:** 
  - **Wiki:** It is the repository for evidence, competing hypotheses, and mechanism explanations. Every conceptual wiki page MUST be articulated around:
    1. **Origins:** Who proposed the idea/mechanism and the historical context.
    2. **Motivation:** The "why" and underlying rationale/mechanism.
    3. **Evidence:** Empirical data, seminal studies, and supporting research.
    4. **Limitations:** Boundary conditions, contradictions, or gaps in evidence (use warning callouts `> ⚠️`).
    Content MUST present the landscape of evidence, including contradictions, limitations, and confidence levels. It must NEVER advocate for a single approach — that is the protocol's job. MUST remain anonymized and objective. **NEVER include user-specific data in `wiki/` or `sources/`.** Summaries and text in `sources/` must never contain references to "the user", the user's specific goals, lifestyle, habits, or private metaphors (such as "pills"). Examples must use generic placeholders or wide ranges (e.g., "For a 70kg individual..." rather than "For the user (71kg)..."). All user-specific personalization must reside exclusively in `user/` or `protocols/`. No scientific justifications.
- **Folder Bloat Limit**: Max 15 content files/folders per subdirectory of the system (including `wiki/`, `sources/`, `user/`, and all their subfolders like `protocols/`, etc., excluding `_index.md`). If exceeded, reorganize:
  1. Group pages into 2+ logical subdirectories.
  2. Move files and update all incoming links globally.
  3. Create `_index.md` in subdirectories.
  4. Update parent `_index.md` to link subdirectories.

## Workflow Priority
1. Research/Ingest -> Update Manifest.
2. Ingest -> Update Wiki with Footnotes.
3. Update Directory Index summaries.

## Channel Output
- **Telegram/OpenClaw**: Actionable summaries only (e.g. "🏗️ `user/protocols/sleep.md` updated."). Do NOT post verbose ingestion logs (confirm with "📥 Ingested `sources/x.md` into `wiki/y.md`").
- **Desktop**: Write to files normally.

## Autonomy & Epistemic Play
Agents are encouraged to treat the system as a collaborative sandbox:
1. **Agent Refinement**: Optimize `AGENTS.md` and skills.
2. **Wiki Evolution**: Restructure hierarchies to build better conceptual bridges.
3. **Analogy/Metaphor Usage**: Propose models of thought to help user synthesize life dynamics.
4. **Epistemic Playfulness**: Combine disciplines (e.g., systems engineering, philosophy) for co-creation.
