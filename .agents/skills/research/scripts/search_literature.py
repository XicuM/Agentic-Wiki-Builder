"""Search multiple literature and academic book providers in parallel and return unified JSON results."""

import sys
import os
import re
import json
import urllib.request
import urllib.parse
import time
import random
import ssl
import threading
import argparse

# Add current directory to path just in case
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import API_KEY

def make_request(url, headers=None, timeout=15, retries=3):
    """Make an HTTP request with retries and timeout."""
    if not headers:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                return response.read()
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(1.0 + random.random())
    return None

def normalize_title(title):
    """Normalize title for deduplication."""
    if not title:
        return ""
    return re.sub(r'[^a-z0-9]', '', title.lower())

def search_semantic_scholar(query, limit=5):
    """Search Semantic Scholar for open-access papers."""
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "paperId,title,authors,year,url,openAccessPdf,externalIds",
    })
    url = f"{base_url}?{params}"
    headers = {"User-Agent": "Mozilla/5.0"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    
    raw_data = make_request(url, headers=headers)
    if not raw_data:
        return []
    
    try:
        data = json.loads(raw_data.decode("utf-8"))
        results = []
        for item in data.get("data", []):
            doi = item.get("externalIds", {}).get("DOI")
            results.append({
                "paperId": item.get("paperId"),
                "title": item.get("title"),
                "authors": item.get("authors", []),
                "year": item.get("year"),
                "url": item.get("url"),
                "openAccessPdf": item.get("openAccessPdf"),
                "doi": doi.lower() if doi else None,
                "provider": "semanticscholar"
            })
        return results
    except Exception:
        return []

def search_arxiv(query, limit=5):
    """Search arXiv API."""
    import xml.etree.ElementTree as ET
    base_url = "http://export.arxiv.org/api/query?"
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "max_results": limit,
        "sortBy": "relevance",
        "sortOrder": "descending"
    })
    url = f"{base_url}{params}"
    
    raw_data = make_request(url)
    if not raw_data:
        return []
    
    try:
        root = ET.fromstring(raw_data.decode("utf-8"))
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            paper_id_full = entry.find("atom:id", ns).text
            paper_id = paper_id_full.split("/")[-1]
            arxiv_id = paper_id.split("v")[0]
            
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            year = entry.find("atom:published", ns).text[:4]
            authors = [auth.find("atom:name", ns).text for auth in entry.findall("atom:author", ns)]
            
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                    pdf_url = link.attrib.get("href")
            
            doi_elem = entry.find("arxiv:doi", ns)
            doi = doi_elem.text.strip().lower() if doi_elem is not None and doi_elem.text else None
            
            results.append({
                "paperId": f"arXiv:{arxiv_id}",
                "title": title,
                "authors": [{"name": a} for a in authors],
                "year": int(year) if year.isdigit() else 0,
                "url": paper_id_full,
                "openAccessPdf": {"url": pdf_url} if pdf_url else None,
                "doi": doi,
                "provider": "arxiv"
            })
        return results
    except Exception:
        return []

def search_openalex(query, limit=5):
    """Search OpenAlex catalog."""
    base_url = "https://api.openalex.org/works"
    params = urllib.parse.urlencode({
        "search": query,
        "per_page": limit,
    })
    url = f"{base_url}?{params}"
    
    raw_data = make_request(url)
    if not raw_data:
        return []
    
    try:
        data = json.loads(raw_data.decode("utf-8"))
        results = []
        for work in data.get("results", []):
            full_id = work.get("id", "")
            short_id = full_id.split("/")[-1] if "/" in full_id else full_id
            
            doi_url = work.get("doi")
            doi = doi_url.replace("https://doi.org/", "").lower() if doi_url else None
            
            authorships = work.get("authorships", [])
            authors = []
            for auth in authorships:
                name = auth.get("author", {}).get("display_name")
                if name:
                    authors.append({"name": name})
            
            pdf_url = work.get("primary_location", {}).get("pdf_url")
            
            results.append({
                "paperId": f"openalex:{short_id}",
                "title": work.get("title") or "Unknown Title",
                "authors": authors,
                "year": work.get("publication_year"),
                "url": work.get("doi") or work.get("id"),
                "openAccessPdf": {"url": pdf_url} if pdf_url else None,
                "doi": doi,
                "provider": "openalex"
            })
        return results
    except Exception:
        return []

def search_pubmed(query, limit=5):
    """Search PubMed/Entrez API."""
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": limit
    })
    raw_search = make_request(search_url)
    if not raw_search:
        return []
    
    try:
        search_data = json.loads(raw_search.decode("utf-8"))
        id_list = search_data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []
            
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?" + urllib.parse.urlencode({
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json"
        })
        raw_summary = make_request(summary_url)
        if not raw_summary:
            return []
            
        summary_data = json.loads(raw_summary.decode("utf-8"))
        results = []
        uid_results = summary_data.get("result", {})
        for uid in id_list:
            item = uid_results.get(uid)
            if not item:
                continue
            
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
            
            results.append({
                "paperId": f"pmid:{uid}",
                "title": title,
                "authors": authors,
                "year": year,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                "openAccessPdf": {"url": pdf_url} if pdf_url else None,
                "doi": doi.lower() if doi else None,
                "provider": "pubmed"
            })
        return results
    except Exception:
        return []

def search_google_books(query, limit=5):
    """Search Google Books volumes."""
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = urllib.parse.urlencode({
        "q": query,
        "maxResults": limit,
    })
    url = f"{base_url}?{params}"
    
    raw_data = make_request(url)
    if not raw_data:
        return []
    
    try:
        data = json.loads(raw_data.decode("utf-8"))
        results = []
        for item in data.get("items", []):
            volume_id = item.get("id")
            volume_info = item.get("volumeInfo", {})
            
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
            
            results.append({
                "paperId": f"googlebooks:{volume_id}",
                "title": volume_info.get("title") or "Unknown Book Title",
                "authors": authors,
                "year": year,
                "url": volume_info.get("infoLink") or volume_info.get("previewLink"),
                "openAccessPdf": {"url": pdf_url} if pdf_url else None,
                "doi": f"isbn:{isbn}" if isbn else None,
                "provider": "googlebooks"
            })
        return results
    except Exception:
        return []

def deduplicate_and_rank(all_results, max_results):
    """Deduplicate and rank results across all providers."""
    unique_results = []
    
    # Priority rank: preferred providers and open access options
    provider_priority = {
        "pubmed": 1,
        "semanticscholar": 2,
        "openalex": 3,
        "arxiv": 4,
        "googlebooks": 5
    }
    
    def score_result(r):
        has_pdf = 1 if (r.get("openAccessPdf") and r["openAccessPdf"].get("url")) else 0
        priority = provider_priority.get(r.get("provider", "googlebooks"), 10)
        return (has_pdf, -priority)
    
    # Group results by similar identifier or normalized title
    groups = {}
    for r in all_results:
        doi = r.get("doi")
        norm_title = normalize_title(r.get("title"))
        
        key = None
        if doi:
            key = f"doi:{doi}"
        elif norm_title:
            key = f"title:{norm_title}"
            
        if not key:
            unique_results.append(r)
            continue
            
        if key not in groups:
            groups[key] = []
        groups[key].append(r)
        
    for key, items in groups.items():
        best_item = max(items, key=score_result)
        other_providers = list(set(it["provider"] for it in items if it["provider"] != best_item["provider"]))
        if other_providers:
            best_item["other_providers"] = other_providers
        unique_results.append(best_item)
        
    # Re-sort based on original list indexes to preserve relative search relevance
    result_index = {id(r): idx for idx, r in enumerate(all_results)}
    unique_results.sort(key=lambda r: result_index.get(id(r), 999))
    
    return unique_results[:max_results]

def main():
    parser = argparse.ArgumentParser(description="Search academic literature & books across multiple providers in parallel.")
    parser.add_argument("query", help="The search query.")
    parser.add_argument("-p", "--provider", default="all", 
                        choices=["all", "semanticscholar", "arxiv", "openalex", "pubmed", "googlebooks"],
                        help="Specify a provider or search all in parallel.")
    parser.add_argument("-l", "--limit", type=int, default=5, 
                        help="Number of results per provider (default: 5).")
    
    args = parser.parse_args()
    
    providers = {
        "semanticscholar": search_semantic_scholar,
        "arxiv": search_arxiv,
        "openalex": search_openalex,
        "pubmed": search_pubmed,
        "googlebooks": search_google_books
    }
    
    selected_providers = {}
    if args.provider == "all":
        selected_providers = providers
    else:
        selected_providers = {args.provider: providers[args.provider]}
        
    results_lock = threading.Lock()
    all_results = []
    
    threads = []
    
    def worker(name, func):
        try:
            res = func(args.query, args.limit)
            with results_lock:
                all_results.extend(res)
        except Exception as e:
            print(f"Error in thread for provider {name}: {e}", file=sys.stderr)
            
    for name, func in selected_providers.items():
        t = threading.Thread(target=worker, args=(name, func))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    # Deduplicate and sort
    final_results = deduplicate_and_rank(all_results, args.limit * len(selected_providers))
    
    print(json.dumps({"total": len(final_results), "data": final_results}, separators=(',', ':')))

if __name__ == "__main__":
    main()
