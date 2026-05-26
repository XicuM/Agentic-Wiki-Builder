"""Search Semantic Scholar for open-access papers matching a query."""

import sys
import json
import urllib.request
import urllib.parse
import time
import random
from urllib.error import HTTPError, URLError

from config import API_KEY

def search_papers(query: str, limit: int = 5, retries: int = 5):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "paperId,title,authors,year,url,openAccessPdf",
    })
    url = f"{base_url}?{params}"

    for attempt in range(retries):
        try:
            # Enforce 1 request per second
            time.sleep(1.0)
            
            headers = {"User-Agent": "Mozilla/5.0"}
            if API_KEY:
                headers["x-api-key"] = API_KEY
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                print(json.dumps(data, separators=(',', ':')))
                return
        except HTTPError as e:
            if e.code == 429 or 500 <= e.code < 600:
                wait = (2 ** attempt) + random.random() + 1.0 # Extra second for safety
                print(f"Error {e.code}. Retrying in {wait:.2f}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"HTTP Error: {e.code} {e.reason}", file=sys.stderr)
                sys.exit(1)
        except (URLError, TimeoutError) as e:
            wait = (2 ** attempt) + random.random()
            print(f"Network error: {e}. Retrying in {wait:.2f}s...", file=sys.stderr)
            time.sleep(wait)
    
    print("Failed after maximum retries.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_papers.py <query>")
        sys.exit(1)
    search_papers(sys.argv[1])
