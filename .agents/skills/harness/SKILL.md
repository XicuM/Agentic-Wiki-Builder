---
name: harness
description: Runtime state, context compaction, and permission gating.
metadata: { "openclaw": { "emoji": "🛡️" } }
---
# Role: Agent Harness (Universal Utility)

Shared runtime infrastructure providing state management, automated context compaction, and execution permission gating.

## Scripts & Entrypoints
- `core_io_helper.py`: Automates context compaction on file reads/writes.
- `runtime_gate.py`: Enforces authorization check gates for high-risk operations.

## Usage & Guidelines
All skill scripts must import from the harness module to perform I/O operations and run commands or APIs:
1. Use `core_io_helper.py` for loading or writing literature text or log files.
2. Route any command execution or outbound HTTP request through `runtime_gate.py`.
