"""Search arXiv for papers matching a query."""

import sys
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def search_arxiv(query: str, max_results: int = 5):
    base_url = "http://export.arxiv.org/api/query?"
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    })
    url = f"{base_url}{params}"
    
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read().decode()
            
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        
        results = []
        for entry in root.findall("atom:entry", ns):
            paper_id_full = entry.find("atom:id", ns).text
            paper_id = paper_id_full.split("/")[-1]
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            year = entry.find("atom:published", ns).text[:4]
            authors = [auth.find("atom:name", ns).text for auth in entry.findall("atom:author", ns)]
            
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                    pdf_url = link.attrib.get("href")
            
            results.append({
                "paperId": f"arXiv:{paper_id}",
                "title": title,
                "authors": [{"name": a} for a in authors],
                "year": int(year) if year.isdigit() else 0,
                "url": paper_id_full,
                "abstract": summary,
                "openAccessPdf": {"url": pdf_url} if pdf_url else None
            })
            
        print(json.dumps({"total": len(results), "data": results}, indent=2))
        
    except Exception as e:
        print(f"Error searching arXiv: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_arxiv.py <query>")
        sys.exit(1)
    search_arxiv(sys.argv[1])
