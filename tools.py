import requests
from crewai.tools import tool

@tool("CrossRef API - Free")
def crossref_search(query: str) -> str:
    """Search CrossRef for DOI and metadata - 100% free, no key"""
    try:
        r = requests.get(f"https://api.crossref.org/works?query={query}&rows=3", timeout=10)
        data = r.json()
        items = data.get("message", {}).get("items", [])
        return str([{ "title": i.get("title"), "DOI": i.get("DOI"), "author": i.get("author") } for i in items])[:2000]
    except Exception as e:
        return f"CrossRef error: {e}"

@tool("Semantic Scholar API - Free")
def semantic_scholar_search(query: str) -> str:
    """Search Semantic Scholar - free tier"""
    try:
        r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=3&fields=title,authors,year,externalIds", timeout=10)
        return str(r.json())[:2000]
    except Exception as e:
        return f"Semantic error: {e}"

@tool("DOI Resolver - Free")
def doi_resolver(doi: str) -> str:
    """Resolve DOI to citation - free"""
    try:
        r = requests.get(f"https://doi.org/{doi}", headers={"Accept": "application/vnd.citationstyles.csl+json"}, timeout=10)
        return str(r.json())[:2000]
    except Exception as e:
        return f"DOI error: {e}"
