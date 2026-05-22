"""Download an open-access PDF, extract text, and generate a summary note for the Obsidian base."""

import sys
import os
import re
import json
import urllib.request
import time
import random
import ssl
from urllib.error import HTTPError, URLError

from config import API_KEY
from markitdown import MarkItDown

def _sanitize(text: str) -> str:
    """Collapse whitespace artifacts from PDF extraction."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _extract_text(pdf_path: str) -> str:
    try:
        md = MarkItDown()
        result = md.convert(pdf_path)
        return _sanitize(result.text_content)
    except Exception as e:
        print(f"MarkItDown PDF conversion failed: {e}", file=sys.stderr)
        return ""

def fetch_paper_metadata(paper_id: str, retries: int = 5):
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,authors,year,abstract,publicationTypes,openAccessPdf"
    for attempt in range(retries):
        try:
            time.sleep(1.0)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            if API_KEY:
                headers["x-api-key"] = API_KEY
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 429 or 500 <= e.code < 600:
                wait = (2 ** attempt) + random.random() + 1.0
                print(f"Error {e.code}. Retrying in {wait:.2f}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"HTTP Error: {e.code} {e.reason}", file=sys.stderr)
                return None
        except (URLError, TimeoutError) as e:
            wait = (2 ** attempt) + random.random()
            print(f"Network error: {e}. Retrying in {wait:.2f}s...", file=sys.stderr)
            time.sleep(wait)
    print("Failed to fetch metadata after maximum retries.", file=sys.stderr)
    sys.exit(1)

def fetch_arxiv_metadata(arxiv_id: str):
    """Fetch metadata from arXiv API."""
    if arxiv_id.startswith("arXiv:"):
        arxiv_id = arxiv_id[6:]
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read().decode()
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entry = root.find("atom:entry", ns)
        if entry is None:
            return None
            
        title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
        summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
        year = entry.find("atom:published", ns).text[:4]
        authors = [{"name": auth.find("atom:name", ns).text} for auth in entry.findall("atom:author", ns)]
        
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = link.attrib.get("href")
        
        return {
            "title": title,
            "abstract": summary,
            "authors": authors,
            "year": int(year) if year.isdigit() else 0,
            "openAccessPdf": {"url": pdf_url} if pdf_url else None
        }
    except Exception as e:
        print(f"Error fetching from arXiv: {e}", file=sys.stderr)
        return None

def ingest_paper(paper_id: str, filename_base: str, domain: str = None, retries: int = 5):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    literature_dir = os.path.join(base_dir, "sources", "literature")
    if domain:
        literature_dir = os.path.join(literature_dir, domain)
    os.makedirs(literature_dir, exist_ok=True)

    print(f"Fetching metadata for paper {paper_id}...")
    metadata = fetch_paper_metadata(paper_id)
    
    if not metadata:
        if paper_id.startswith("arXiv:"):
            print("INFO: Semantic Scholar metadata not found. Trying arXiv directly...")
            metadata = fetch_arxiv_metadata(paper_id)
        
        if not metadata:
            print("Error: Could not fetch metadata from any source.", file=sys.stderr)
            sys.exit(1)
    
    pdf_info = metadata.get("openAccessPdf")
    pdf_url = pdf_info["url"] if pdf_info and pdf_info.get("url") else None
    
    # ArXiv Fallback
    if not pdf_url and (paper_id.startswith("arXiv:") or "arxiv" in metadata.get("url", "").lower()):
        print("INFO: PDF not found in Semantic Scholar. Checking arXiv fallback...")
        arxiv_id = paper_id if paper_id.startswith("arXiv:") else None
        if not arxiv_id:
            # Try to extract arXiv ID from Semantic Scholar URL
            match = re.search(r"arxiv.org/abs/([\d.]+)", metadata.get("url", ""))
            if match:
                arxiv_id = match.group(1)
        
        if arxiv_id:
            arxiv_meta = fetch_arxiv_metadata(arxiv_id)
            if arxiv_meta and arxiv_meta.get("openAccessPdf"):
                pdf_url = arxiv_meta["openAccessPdf"]["url"]
                print(f"Found arXiv PDF: {pdf_url}")
                # Supplement abstract if missing
                if not metadata.get("abstract") and arxiv_meta.get("abstract"):
                    metadata["abstract"] = arxiv_meta["abstract"]

    if not pdf_url:
        print("WARNING: No open access PDF URL found. Falling back to abstract.", file=sys.stderr)
        

    if filename_base.endswith(".pdf"):
        filename_base = filename_base[:-4]
    elif filename_base.endswith(".pdf.md"):
        filename_base = filename_base[:-7]

    paper_dir = os.path.join(literature_dir, filename_base)
    os.makedirs(paper_dir, exist_ok=True)

    pdf_filepath = os.path.join(paper_dir, "original.pdf")
    md_filepath = os.path.join(paper_dir, "raw.md")
    summary_filepath = os.path.join(paper_dir, "metadata.md")

    if pdf_url:
        print(f"Downloading {pdf_url} to {pdf_filepath} ...")
        for attempt in range(retries):
            try:
                time.sleep(1.0)
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/pdf"
                }
                if API_KEY:
                    headers["x-api-key"] = API_KEY
                req = urllib.request.Request(pdf_url, headers=headers)
                with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                    with open(pdf_filepath, "wb") as f:
                        f.write(resp.read())
                break
            except HTTPError as e:
                if e.code == 429 or 500 <= e.code < 600:
                    wait = (2 ** attempt) + random.random() + 1.0
                    print(f"Error {e.code}. Retrying in {wait:.2f}s...", file=sys.stderr)
                    time.sleep(wait)
                else:
                    print(f"HTTP Error: {e.code} {e.reason} when downloading PDF. Falling back to abstract.", file=sys.stderr)
                    pdf_url = None
                    break
            except (URLError, TimeoutError) as e:
                wait = (2 ** attempt) + random.random()
                print(f"Network error: {e}. Retrying in {wait:.2f}s...", file=sys.stderr)
                time.sleep(wait)
        else:
            print("Failed to download PDF after maximum retries. Falling back to abstract.", file=sys.stderr)
            pdf_url = None

    if pdf_url:
        print(f"Extracting text from PDF...")
        try:
            body = _extract_text(pdf_filepath)
        except Exception as e:
            print(f"WARNING: PDF extraction failed: {e}. Falling back to abstract.", file=sys.stderr)
            body = metadata.get("abstract") or "No abstract available."
            
        if not body:
            print("WARNING: PDF extraction returned empty text. Falling back to abstract.", file=sys.stderr)
            body = metadata.get("abstract") or "No abstract available."
    else:
        body = metadata.get("abstract") or "No abstract available."

    if pdf_url:
        body = f"---\nsource_url: {pdf_url}\nstatus: raw\n---\n\n{body}\n"
    else:
        body = f"---\nsource_url: None\nstatus: stub\n---\n\n> ⚠️ **STUB:** PDF download failed. Content limited to abstract only. Do NOT use for deep mechanism synthesis.\n\n{body}\n"
    
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(body)

    print(f"Generating summary note...")
    title = metadata.get("title", "Unknown Title").replace('"', "'")
    abstract = metadata.get("abstract") or "No abstract available."
    year = metadata.get("year") or "Unknown"
    authors = [a.get("name", "") for a in metadata.get("authors", [])]
    authors_str = json.dumps(authors)
    pub_types = metadata.get("publicationTypes") or []
    pub_types_str = json.dumps(pub_types)

    # Use relative path for internal links in metadata.md
    summary_content = f"""---
title: "{title}"
source: "[[raw.md]]"
raw_pdf: "[[original.pdf]]"
tags: [literature-summary]
authors: {authors_str}
year: {year}
paper_type: {pub_types_str}
---
# {title}

## Abstract
{abstract}
"""
    with open(summary_filepath, "w", encoding="utf-8") as f:
        f.write(summary_content)

    print(f"Ingested paper successfully!")
    print(f"  - Folder: {paper_dir}")
    print(f"  - PDF: original.pdf")
    print(f"  - Markdown: raw.md")
    print(f"  - Metadata: metadata.md")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python ingest_paper.py "<paperId>" "<FileNameBase>" ["<domain>"]')
        sys.exit(1)
    
    paper_id = sys.argv[1]
    filename_base = sys.argv[2]
    domain = sys.argv[3] if len(sys.argv) > 3 else None
    
    ingest_paper(paper_id, filename_base, domain)
