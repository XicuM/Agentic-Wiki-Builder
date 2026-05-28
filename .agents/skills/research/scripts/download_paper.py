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

# Enforce runtime permission gating
_harness_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "harness", "scripts"))
if _harness_path not in sys.path:
    sys.path.append(_harness_path)
try:
    from runtime_gate import check_permission
    _original_urlopen = urllib.request.urlopen
    def gated_urlopen(url_or_req, *args, **kwargs):
        url = url_or_req.full_url if hasattr(url_or_req, "full_url") else str(url_or_req)
        check_permission("network", url)
        return _original_urlopen(url_or_req, *args, **kwargs)
    urllib.request.urlopen = gated_urlopen
except ImportError:
    print("Warning: runtime_gate module not found. Network calls will proceed ungated.", file=sys.stderr)

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
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,authors,year,abstract,publicationTypes,openAccessPdf,externalIds,url"
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

def fetch_unpaywall_pdf(doi: str):
    """Fetch PDF URL from Unpaywall API using DOI."""
    email = "xicu.research.agent@gmail.com"
    url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get("best_oa_location") and data["best_oa_location"].get("url_for_pdf"):
                return data["best_oa_location"]["url_for_pdf"]
    except Exception as e:
        print(f"Error fetching from Unpaywall: {e}", file=sys.stderr)
    return None

def fetch_openalex_metadata(work_id: str):
    """Fetch metadata from OpenAlex API."""
    if work_id.startswith("openalex:"):
        work_id = work_id[9:]
    url = f"https://api.openalex.org/works/{work_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            work = json.loads(response.read().decode("utf-8"))
            
        title = work.get("title") or "Unknown Title"
        abstract = ""
        inv_index = work.get("abstract_inverted_index")
        if inv_index:
            pos_to_word = {}
            for word, positions in inv_index.items():
                for pos in positions:
                    pos_to_word[pos] = word
            if pos_to_word:
                max_pos = max(pos_to_word.keys())
                words = [pos_to_word.get(i, "") for i in range(max_pos + 1)]
                abstract = " ".join(words)
                
        authorships = work.get("authorships", [])
        authors = []
        for auth in authorships:
            name = auth.get("author", {}).get("display_name")
            if name:
                authors.append({"name": name})
                
        year = work.get("publication_year") or 0
        doi_url = work.get("doi")
        doi = doi_url.replace("https://doi.org/", "").lower() if doi_url else None
        
        pdf_url = work.get("primary_location", {}).get("pdf_url")
        
        return {
            "title": title,
            "abstract": abstract or "No abstract available.",
            "authors": authors,
            "year": year,
            "openAccessPdf": {"url": pdf_url} if pdf_url else None,
            "externalIds": {"DOI": doi} if doi else {},
            "url": work.get("doi") or work.get("id"),
            "publicationTypes": [work.get("type", "journal-article")]
        }
    except Exception as e:
        print(f"Error fetching from OpenAlex: {e}", file=sys.stderr)
        return None

def fetch_pubmed_metadata(pmid: str):
    """Fetch metadata from Entrez summary API."""
    if pmid.startswith("pmid:"):
        pmid = pmid[5:]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        item = data.get("result", {}).get(pmid)
        if not item:
            return None
            
        title = item.get("title") or "Unknown Title"
        authors = [{"name": a.get("name")} for a in item.get("authors", []) if a.get("name")]
        pubdate = item.get("pubdate", "")
        year_match = re.search(r"\d{4}", pubdate)
        year = int(year_match.group(0)) if year_match else 0
        
        doi = None
        pmcid = None
        for articleid in item.get("articleids", []):
            if articleid.get("idtype") == "doi":
                doi = articleid.get("id")
            elif articleid.get("idtype") == "pmc":
                pmcid = articleid.get("id")
                
        pdf_url = None
        if pmcid:
            pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
            
        abstract = ""
        fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
        try:
            with urllib.request.urlopen(fetch_url, timeout=15) as fetch_resp:
                xml_data = fetch_resp.read().decode("utf-8")
                import xml.etree.ElementTree as ET
                xml_root = ET.fromstring(xml_data)
                abstract_elem = xml_root.find(".//Abstract")
                if abstract_elem is not None:
                    abstract_texts = [t.text for t in abstract_elem.findall(".//AbstractText") if t.text]
                    abstract = " ".join(abstract_texts)
        except Exception:
            pass
            
        return {
            "title": title,
            "abstract": abstract or "No abstract available.",
            "authors": authors,
            "year": year,
            "openAccessPdf": {"url": pdf_url} if pdf_url else None,
            "externalIds": {"DOI": doi} if doi else {},
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "publicationTypes": ["journal-article"]
        }
    except Exception as e:
        print(f"Error fetching PubMed metadata: {e}", file=sys.stderr)
        return None

def fetch_google_books_metadata(volume_id: str):
    """Fetch metadata from Google Books API."""
    if volume_id.startswith("googlebooks:"):
        volume_id = volume_id[12:]
    url = f"https://www.googleapis.com/books/v1/volumes/{volume_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            item = json.loads(response.read().decode("utf-8"))
            
        volume_info = item.get("volumeInfo", {})
        title = volume_info.get("title") or "Unknown Book Title"
        authors = [{"name": a} for a in volume_info.get("authors", [])]
        published_date = volume_info.get("publishedDate", "")
        year_match = re.search(r"\d{4}", published_date)
        year = int(year_match.group(0)) if year_match else 0
        
        isbn = None
        for ident in volume_info.get("industryIdentifiers", []):
            if ident.get("type") in ["ISBN_13", "ISBN_10"]:
                isbn = ident.get("identifier")
                break
                
        pdf_url = None
        access_info = item.get("accessInfo", {})
        if access_info.get("pdf", {}).get("isAvailable"):
            dl = access_info.get("pdf", {}).get("downloadLink")
            if dl:
                pdf_url = dl
                
        return {
            "title": title,
            "abstract": volume_info.get("description") or "No description available.",
            "authors": authors,
            "year": year,
            "openAccessPdf": {"url": pdf_url} if pdf_url else None,
            "externalIds": {"ISBN": isbn} if isbn else {},
            "url": volume_info.get("infoLink") or volume_info.get("previewLink"),
            "publicationTypes": ["book"]
        }
    except Exception as e:
        print(f"Error fetching Google Books metadata: {e}", file=sys.stderr)
        return None

def fetch_local_pdf_metadata(pdf_path: str):
    """Attempt to parse local PDF file using markitdown, and extract metadata."""
    if pdf_path.startswith("local:"):
        pdf_path = pdf_path[6:]
        
    if not os.path.exists(pdf_path):
        print(f"Error: Local PDF file not found at {pdf_path}", file=sys.stderr)
        return None
        
    print(f"Extracting local PDF content with MarkItDown for metadata processing...")
    extracted_text = _extract_text(pdf_path)
    if not extracted_text:
        return None
        
    title = os.path.basename(pdf_path)
    if title.lower().endswith(".pdf"):
        title = title[:-4]
        
    authors = []
    year = "Unknown"
    doi = None
    abstract = ""
    
    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", extracted_text, re.IGNORECASE)
    if doi_match:
        doi = doi_match.group(0).rstrip(".").rstrip(",")
        print(f"Found DOI in PDF: {doi}")
        
    if doi:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,authors,year,abstract,publicationTypes,openAccessPdf,url"
        try:
            time.sleep(1.0)
            headers = {"User-Agent": "Mozilla/5.0"}
            if API_KEY:
                headers["x-api-key"] = API_KEY
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                ss_meta = json.loads(resp.read().decode())
                if ss_meta:
                    return {
                        "title": ss_meta.get("title") or title,
                        "abstract": ss_meta.get("abstract") or "No abstract available.",
                        "authors": ss_meta.get("authors") or [],
                        "year": ss_meta.get("year") or "Unknown",
                        "openAccessPdf": ss_meta.get("openAccessPdf"),
                        "externalIds": {"DOI": doi},
                        "url": ss_meta.get("url"),
                        "publicationTypes": ss_meta.get("publicationTypes") or [],
                        "local_path": pdf_path
                    }
        except Exception:
            print("Failed to look up DOI on Semantic Scholar. Proceeding with text-derived metadata.")
            
    abstract_match = re.search(r"abstract\s*(.*?)\s*(?:1\.?\s+introduction|introduction|keywords|background)", extracted_text, re.IGNORECASE | re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1).strip()
        abstract = re.sub(r"\s+", " ", abstract)
        if len(abstract) > 1000:
            abstract = abstract[:997] + "..."
            
    return {
        "title": title,
        "abstract": abstract or "Metadata extraction fallback from PDF.",
        "authors": authors,
        "year": year,
        "openAccessPdf": None,
        "externalIds": {"DOI": doi} if doi else {},
        "url": "local-file",
        "publicationTypes": ["local-pdf"],
        "local_path": pdf_path
    }

def ingest_paper(paper_id: str, filename_base: str, domain: str = None, retries: int = 5):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    literature_dir = os.path.join(base_dir, "sources", "literature")
    if domain:
        literature_dir = os.path.join(literature_dir, domain)
    os.makedirs(literature_dir, exist_ok=True)

    print(f"Fetching metadata for paper {paper_id}...")
    
    metadata = None
    is_local = False
    
    if paper_id.startswith("openalex:"):
        metadata = fetch_openalex_metadata(paper_id)
    elif paper_id.startswith("pmid:") or paper_id.startswith("pmcid:"):
        metadata = fetch_pubmed_metadata(paper_id)
    elif paper_id.startswith("googlebooks:"):
        metadata = fetch_google_books_metadata(paper_id)
    elif paper_id.startswith("local:"):
        metadata = fetch_local_pdf_metadata(paper_id)
        is_local = True
    elif paper_id.startswith("arXiv:"):
        metadata = fetch_paper_metadata(paper_id)
        if not metadata:
            print("INFO: Semantic Scholar metadata not found. Trying arXiv directly...")
            metadata = fetch_arxiv_metadata(paper_id)
    else:
        metadata = fetch_paper_metadata(paper_id)
        
    if not metadata:
        print("Error: Could not fetch metadata from any source.", file=sys.stderr)
        sys.exit(1)
    
    pdf_info = metadata.get("openAccessPdf")
    pdf_url = pdf_info["url"] if pdf_info and pdf_info.get("url") else None
    
    # ArXiv Fallback
    if not is_local and not pdf_url and (paper_id.startswith("arXiv:") or "arxiv" in metadata.get("url", "").lower()):
        print("INFO: PDF not found in Semantic Scholar. Checking arXiv fallback...")
        arxiv_id = paper_id if paper_id.startswith("arXiv:") else None
        if not arxiv_id:
            match = re.search(r"arxiv.org/abs/([\d.]+)", metadata.get("url", ""))
            if match:
                arxiv_id = match.group(1)
        
        if arxiv_id:
            arxiv_meta = fetch_arxiv_metadata(arxiv_id)
            if arxiv_meta and arxiv_meta.get("openAccessPdf"):
                pdf_url = arxiv_meta["openAccessPdf"]["url"]
                print(f"Found arXiv PDF: {pdf_url}")
                if not metadata.get("abstract") and arxiv_meta.get("abstract"):
                    metadata["abstract"] = arxiv_meta["abstract"]

    if filename_base.endswith(".pdf"):
        filename_base = filename_base[:-4]
    elif filename_base.endswith(".pdf.md"):
        filename_base = filename_base[:-7]

    paper_dir = os.path.join(literature_dir, filename_base)
    os.makedirs(paper_dir, exist_ok=True)

    pdf_filepath = os.path.join(paper_dir, "original.pdf")
    md_filepath = os.path.join(paper_dir, "raw.md")
    summary_filepath = os.path.join(paper_dir, "metadata.md")

    def download_pdf_helper(url, filepath):
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
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                    with open(filepath, "wb") as f:
                        f.write(resp.read())
                return True
            except HTTPError as e:
                if e.code == 429 or 500 <= e.code < 600:
                    wait = (2 ** attempt) + random.random() + 1.0
                    print(f"Error {e.code}. Retrying in {wait:.2f}s...", file=sys.stderr)
                    time.sleep(wait)
                else:
                    print(f"HTTP Error: {e.code} {e.reason} when downloading PDF.", file=sys.stderr)
                    return False
            except (URLError, TimeoutError) as e:
                wait = (2 ** attempt) + random.random()
                print(f"Network error: {e}. Retrying in {wait:.2f}s...", file=sys.stderr)
                time.sleep(wait)
        print("Failed to download PDF after maximum retries.", file=sys.stderr)
        return False

    pdf_downloaded = False
    if is_local:
        local_path = metadata.get("local_path")
        if local_path and os.path.exists(local_path):
            print(f"Copying local PDF from {local_path} to {pdf_filepath} ...")
            import shutil
            try:
                shutil.copy2(local_path, pdf_filepath)
                pdf_downloaded = True
                pdf_url = f"file://{local_path}"
            except Exception as e:
                print(f"Error copying local PDF: {e}", file=sys.stderr)
    else:
        if pdf_url:
            print(f"Downloading {pdf_url} to {pdf_filepath} ...")
            pdf_downloaded = download_pdf_helper(pdf_url, pdf_filepath)

        # Unpaywall Fallback
        if not pdf_downloaded and metadata.get("externalIds") and metadata["externalIds"].get("DOI"):
            print("INFO: PDF download failed or not found. Checking Unpaywall API...")
            doi = metadata["externalIds"]["DOI"]
            unpaywall_url = fetch_unpaywall_pdf(doi)
            if unpaywall_url:
                print(f"Found Unpaywall PDF: {unpaywall_url}. Downloading...")
                pdf_downloaded = download_pdf_helper(unpaywall_url, pdf_filepath)
                if pdf_downloaded:
                    pdf_url = unpaywall_url

        if not pdf_downloaded:
            print("ERROR: No open access PDF found across any provider or fallback. Aborting.", file=sys.stderr)
            import shutil
            shutil.rmtree(paper_dir, ignore_errors=True)
            sys.exit(2)

    print(f"Extracting text from PDF...")
    try:
        body = _extract_text(pdf_filepath)
    except Exception as e:
        print(f"ERROR: PDF extraction failed: {e}. Aborting.", file=sys.stderr)
        import shutil
        shutil.rmtree(paper_dir, ignore_errors=True)
        sys.exit(3)
        
    if not body:
        print("ERROR: PDF extraction returned empty text. Aborting.", file=sys.stderr)
        import shutil
        shutil.rmtree(paper_dir, ignore_errors=True)
        sys.exit(3)

    body = f"---\nsource_url: {pdf_url}\nstatus: raw\n---\n\n{body}\n"
    
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

    add_to_manifest_and_index(filename_base, domain, title, abstract, year)

import datetime
import threading

state_lock = threading.Lock()

def add_to_manifest_and_index(filename_base: str, domain: str, title: str, abstract: str, year: int):
    # 1. Update state.json (Manifest queue)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    state_path = os.path.join(base_dir, "state.json")
    
    abstract_summary = abstract.replace("\n", " ").strip()
    if len(abstract_summary) > 200:
        abstract_summary = abstract_summary[:197] + "..."

    with state_lock:
        if os.path.exists(state_path):
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
            except Exception:
                state_data = {"version": "1.0", "ingestion_queue": []}
        else:
            state_data = {"version": "1.0", "ingestion_queue": []}

        # Check if already enqueued
        queue = state_data.setdefault("ingestion_queue", [])
        already_enqueued = any(item.get("id") == filename_base for item in queue)
        
        if not already_enqueued:
            new_item = {
                "id": filename_base,
                "type": "Literature",
                "path": f"sources/literature/{domain}/{filename_base}/raw.md" if domain else f"sources/literature/{filename_base}/raw.md",
                "summary": f"{title} - {abstract_summary}",
                "enqueued_at": datetime.datetime.now().isoformat(),
                "status": "pending",
                "tags": [domain] if domain else []
            }
            queue.append(new_item)
            try:
                with open(state_path, "w", encoding="utf-8") as f:
                    json.dump(state_data, f, indent=2)
            except Exception as e:
                print(f"Error writing to state.json: {e}", file=sys.stderr)

    # 2. Update local subdirectory sources/literature/<domain>/_index.md
    if domain:
        local_index_dir = os.path.join(base_dir, "sources", "literature", domain)
        os.makedirs(local_index_dir, exist_ok=True)
        local_index_path = os.path.join(local_index_dir, "_index.md")
        
        # Format entry line
        year_str = str(year) if year else "Unknown"
        entry_line = f"- [{filename_base}/raw.md]({filename_base}/raw.md) - {title} - {abstract_summary}. ({year_str}) #{domain}\n"
        
        with state_lock:
            existing_content = ""
            if os.path.exists(local_index_path):
                try:
                    with open(local_index_path, "r", encoding="utf-8") as f:
                        existing_content = f.read()
                except Exception:
                    pass
            
            if not existing_content:
                existing_content = f"# {domain.replace('_', ' ').title()} Literature\n\n"
            
            if filename_base not in existing_content:
                if existing_content and not existing_content.endswith("\n"):
                    existing_content += "\n"
                existing_content += entry_line
                try:
                    with open(local_index_path, "w", encoding="utf-8") as f:
                        f.write(existing_content)
                except Exception as e:
                    print(f"Error writing local index: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python download_paper.py "<paperId>" "<FileNameBase>" ["<domain>"]')
        sys.exit(1)
    
    paper_id = sys.argv[1]
    filename_base = sys.argv[2]
    domain = sys.argv[3] if len(sys.argv) > 3 else None
    
    if paper_id.startswith("query:"):
        query = paper_id[6:]
        print(f"Resolving query: '{query}'...")
        
        # Resolve path to search_literature
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        try:
            import search_literature
        except ImportError as e:
            print(f"Error importing search_literature: {e}", file=sys.stderr)
            sys.exit(1)
            
        print("Searching Semantic Scholar & arXiv...")
        results = []
        def ss_worker():
            try:
                results.extend(search_literature.search_semantic_scholar(query, limit=3))
            except Exception:
                pass
        def ax_worker():
            try:
                results.extend(search_literature.search_arxiv(query, limit=3))
            except Exception:
                pass
                
        t1 = threading.Thread(target=ss_worker)
        t2 = threading.Thread(target=ax_worker)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Deduplicate
        final_res = search_literature.deduplicate_and_rank(results, max_results=3)
        if not final_res:
            print("No open-access papers found matching the query.", file=sys.stderr)
            sys.exit(2)
            
        print(f"Found {len(final_res)} papers to download in parallel:")
        for r in final_res:
            print(f"  - {r.get('title')} ({r.get('year')}) [ID: {r.get('paperId')}]")
            
        from concurrent.futures import ThreadPoolExecutor
        
        def download_and_ingest_worker(paper_info):
            p_id = paper_info.get("paperId")
            p_title = paper_info.get("title")
            p_year = paper_info.get("year") or "Unknown"
            
            clean_title = re.sub(r"[^a-zA-Z0-9\s]", "", p_title).lower()
            words = clean_title.split()
            short_title = "_".join(words[:4])
            
            author_name = "unknown"
            if paper_info.get("authors"):
                first_author = paper_info["authors"][0].get("name", "unknown")
                author_words = first_author.split()
                if author_words:
                    author_name = re.sub(r"[^a-zA-Z0-9]", "", author_words[-1]).lower()
                    
            p_filename_base = f"{author_name}_{p_year}_{short_title}"
            
            print(f"Starting parallel download for: {p_filename_base} ...")
            try:
                ingest_paper(p_id, p_filename_base, domain)
            except SystemExit as se:
                print(f"Failed to ingest {p_filename_base}: exit code {se.code}", file=sys.stderr)
            except Exception as e:
                print(f"Failed to ingest {p_filename_base}: {e}", file=sys.stderr)
                
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(download_and_ingest_worker, final_res)
            
        print("Batch ingestion completed.")
        sys.exit(0)
    else:
        ingest_paper(paper_id, filename_base, domain)

