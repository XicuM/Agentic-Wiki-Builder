"""Search Semantic Scholar for open-access papers matching a query."""

import sys
import json
import urllib.request
import urllib.parse


def search_papers(query: str, limit: int = 5):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,url,openAccessPdf",
    })
    url = f"{base_url}?{params}"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode())

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_papers.py <query>")
        sys.exit(1)
    search_papers(sys.argv[1])
