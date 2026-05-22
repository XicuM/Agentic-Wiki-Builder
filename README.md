# Agentic Wiki Builder

A modular system for automating the transformation of information into highly personalized, actionable protocols. This project utilizes a **Hybrid Agentic Architecture**, supporting both multi-agent orchestration and sequential single-agent execution.

## 🚀 The Workflow

The system operates on a strict **Hierarchy of Evidence** using file-based state handoffs:
1.  **Research (`research-agent`):** Automatically discovery and ingest relevant scientific papers based on specific goals. Updates `sources/_index.md`.
2.  **Ingest (`synthesis-agent`):** Synthesize raw literature into an anonymized, evidence-based Wiki. Reads `sources/`.
3.  **Build Protocol (`protocol-agent`):** Generate strictly actionable, step-by-step instructions for the user, tailored to their profile and feedback. Reads `wiki/`.

**Execution Modes:**
- **Framework-Agnostic:** Can be run by a single monolithic agent or a multi-agent framework.
- **Orchestration:** Handoffs are managed via the filesystem state, ensuring robust operation regardless of the underlying LLM framework.

**Citations are mandatory at every step:**
*   **Protocols** cite the **Wiki** (Actionable synthesis).
*   **Wiki** cites **Literature** (Raw evidence).

## 📁 Repository Structure

```text
├── .agents/          # Specialized logic and scripts for AI agents
├── sources/          # Unified staging area for all inputs
│   ├── literature/   # Raw research papers and processing metadata
│   ├── code/         # Repositories, snippets, and architectural docs
│   ├── internal_documentation/ # Meeting notes, internal reports, and decisions
│   └── _index.md     # The unified Manifest (Source of Truth)
├── wiki/             # Synthesized, objective knowledge base (anonymized)
├── user/             # Personal context and deliverables
│   ├── profile.md    # Demographics, goals, and constraints
│   ├── feedback.md   # Historical outcomes and compliance notes
│   └── protocols/    # Actionable personal protocols (Training, Diet, etc.)
└── logs/             # Monthly activity and execution logs
```

## 🛠 Skills & Capabilities

*   **`research`**: Scours scientific databases to find high-impact, peer-reviewed data.
*   **`ingest`**: Distills complex mechanisms into a clear, searchable knowledge base.
*   **`lint`**: Audits the entire system for contradictions, gaps, and structural integrity.
*   **`build-protocol`**: Adapts science to the user's specific lifestyle, constraints, and feedback.

## 📱 Mobile Access (OpenClaw)

This system is compatible with **OpenClaw** for mobile interaction via Telegram.

### **Canonical Installation Prompt**
To install this project as a skill in your OpenClaw agent, send the following prompt:

> "Clone this repository: `https://github.com/XicuM/agentic-wiki-builder.git`. Keep the work for this project scoped to this workspace only. Install the skills in your main workspace. After install, inspect the project structure and help me finish setup. Ask before making any broader changes."

---

*This repository is managed by an autonomous agent system. All changes are logged in the `logs/` directory.*
