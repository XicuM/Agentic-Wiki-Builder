"""Download an open-access PDF and extract its text into a Markdown file in literature/."""

import sys
import os
import re
import tempfile
import urllib.request

import fitz  # pymupdf


def _sanitize(text: str) -> str:
    """Collapse whitespace artifacts from PDF extraction."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return _sanitize("\n\n".join(pages))


def ingest_paper(url: str, filename: str):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    literature_dir = os.path.join(base_dir, "literature")
    os.makedirs(literature_dir, exist_ok=True)

    if not filename.endswith(".md"):
        filename += ".md"
    filepath = os.path.join(literature_dir, filename)

    # Download PDF to a temporary file
    print(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(resp.read())
        tmp_path = tmp.name

    try:
        body = _extract_text(tmp_path)
    finally:
        os.unlink(tmp_path)

    if not body:
        print("ERROR: PDF extraction returned empty text.", file=sys.stderr)
        sys.exit(1)

    content = f"---\nsource_url: {url}\nstatus: raw\n---\n\n{body}\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Ingested {len(body)} chars -> {filepath}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python ingest_paper.py "<URL>" "<FileName>"')
        sys.exit(1)
    ingest_paper(sys.argv[1], sys.argv[2])
