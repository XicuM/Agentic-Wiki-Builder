"""wiki-mcp — FastMCP server for wiki querying and lint auditing.

Wraps the qmd CLI (BM25 + vector + LLM re-ranking) and lint scripts.
Set PROJECT_ROOT env var to the repository root.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP

# ── Path bootstrap ────────────────────────────────────────────────────────────

def _find_root() -> Path:
    env = os.environ.get("PROJECT_ROOT")
    if env:
        return Path(env).resolve()
    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").exists():
            return parent
    raise RuntimeError(
        "Cannot locate project root. Set the PROJECT_ROOT environment variable."
    )

ROOT = _find_root()
_AGENTS_DIR = ROOT / ".agents"
_WIKI_DIR = Path(__file__).resolve().parent
_VENV_PYTHON = ROOT / ".venv" / "bin" / "python"

# Add lint scripts to sys.path for direct import
for _p in (_WIKI_DIR,):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# Import lint scripts directly (they expose importable functions)
import check_links   # noqa: E402
import backup_sources  # noqa: E402

# ── Server ────────────────────────────────────────────────────────────────────

mcp = FastMCP(
    "wiki-mcp",
    instructions=(
        "Knowledge base querier and auditor for the agentic wiki. "
        "Use wiki_* tools to search or retrieve documents, lint_* tools for audits. "
        "All wiki_* tools query across wiki/, user/protocols/, and sources/literature/."
    ),
)

# ── Helpers ───────────────────────────────────────────────────────────────────

async def _qmd(
    *args: str,
    json_output: bool = False,
) -> str:
    """Run a qmd command from the .agents/ working directory and return stdout."""
    cmd = ["qmd", *args]
    if json_output:
        cmd.append("--json")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(_AGENTS_DIR),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err = stderr.decode().strip()
        raise RuntimeError(f"qmd {' '.join(args)} failed: {err}")
    return stdout.decode()


async def _run_script(script: str, *args: str) -> str:
    """Run a lint Python script and return its stdout."""
    proc = await asyncio.create_subprocess_exec(
        str(_VENV_PYTHON), str(_WIKI_DIR / script), *args,
        cwd=str(ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    output = stdout.decode()
    if stderr:
        output += f"\n---\n{stderr.decode()}"
    return output

# ─────────────────────────────────────────────────────────────────────────────
# Wiki Query Tools
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
async def wiki_search(
    query: Annotated[str, "Keyword or grep-style query"],
    collection: Annotated[
        Literal["wiki", "protocols", "sources", "all"],
        "Restrict to a specific collection (default: all)",
    ] = "all",
) -> str:
    """Keyword/grep search across the wiki, protocols, and sources collections."""
    args = ["search", query]
    if collection != "all":
        args += ["-c", collection]
    return await _qmd(*args)


@mcp.tool()
async def wiki_vsearch(
    query: Annotated[str, "Natural-language semantic query"],
    n: Annotated[int, "Number of results to return (default 5)"] = 5,
    collection: Annotated[
        Literal["wiki", "protocols", "sources", "all"],
        "Restrict to a specific collection (default: all)",
    ] = "all",
) -> str:
    """Semantic (vector) search using the pre-built sentence-transformers index."""
    args = ["vsearch", query, "-n", str(n)]
    if collection != "all":
        args += ["-c", collection]
    return await _qmd(*args)


@mcp.tool()
async def wiki_query(
    query: Annotated[str, "Query string — hybrid BM25 + vector + LLM re-ranking"],
    collection: Annotated[
        Literal["wiki", "protocols", "sources", "all"],
        "Restrict to a specific collection (default: all)",
    ] = "all",
    min_score: Annotated[float, "Minimum relevance score threshold (0–1, default 0.0)"] = 0.0,
) -> str:
    """Best-quality hybrid search: BM25 + vector + LLM re-ranking. Use for precision queries."""
    args = ["query", query]
    if collection != "all":
        args += ["-c", collection]
    if min_score > 0:
        args += ["--min-score", str(min_score)]
    return await _qmd(*args)


@mcp.tool()
async def wiki_get(
    path: Annotated[
        str,
        "Relative path to a document (e.g. 'wiki/nutrition/protein.md'). "
        "Relative to PROJECT_ROOT.",
    ],
) -> str:
    """Retrieve the full content of a specific document by its relative path."""
    return await _qmd("get", path)


@mcp.tool()
async def wiki_update_index() -> str:
    """Rebuild the qmd semantic index after adding or modifying wiki/source files."""
    return await _qmd("update")


# ─────────────────────────────────────────────────────────────────────────────
# Lint / Audit Tools
# ─────────────────────────────────────────────────────────────────────────────

@mcp.tool()
async def lint_check_links(
    scope_path: Annotated[
        str,
        "Directory or file to audit (relative to PROJECT_ROOT, e.g. 'wiki/' or 'wiki/nutrition/').",
    ],
) -> str:
    """Check for broken links, missing/unused footnotes, directory bloat, and page length."""
    path = ROOT / scope_path
    return await _run_script("check_links.py", str(path))

@mcp.tool()
async def lint_backup_sources() -> str:
    """Snapshot sources/ metadata to user/sources_backup.json and report stats."""
    return await _run_script("backup_sources.py")


# ─────────────────────────────────────────────────────────────────────────────
# Resources
# ─────────────────────────────────────────────────────────────────────────────

@mcp.resource("wiki://collections/wiki")
def resource_wiki_index() -> str:
    """Directory listing of all pages in the wiki collection."""
    wiki_dir = ROOT / "wiki"
    files = sorted(wiki_dir.rglob("*.md"))
    lines = [f"# Wiki Collection ({len(files)} pages)\n"]
    for f in files:
        rel = f.relative_to(ROOT)
        lines.append(f"- [{rel}]({rel})")
    return "\n".join(lines)


@mcp.resource("wiki://collections/protocols")
def resource_protocols_index() -> str:
    """Directory listing of all pages in the protocols collection."""
    proto_dir = ROOT / "user" / "protocols"
    files = sorted(proto_dir.rglob("*.md")) if proto_dir.exists() else []
    lines = [f"# Protocols Collection ({len(files)} pages)\n"]
    for f in files:
        rel = f.relative_to(ROOT)
        lines.append(f"- [{rel}]({rel})")
    return "\n".join(lines)


@mcp.resource("wiki://collections/sources")
def resource_sources_index() -> str:
    """Directory listing of all pages in the sources/literature collection."""
    src_dir = ROOT / "sources" / "literature"
    files = sorted(src_dir.rglob("*.md")) if src_dir.exists() else []
    lines = [f"# Sources Collection ({len(files)} pages)\n"]
    for f in files:
        rel = f.relative_to(ROOT)
        lines.append(f"- [{rel}]({rel})")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
