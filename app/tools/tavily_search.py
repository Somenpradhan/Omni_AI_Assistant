import os
import urllib.request
import json
from app.config.settings import settings

def search_tavily(query: str) -> list:
    """
    Direct urllib request handler for Tavily search API.
    """
    api_key = settings.TAVILY_API_KEY
    if not api_key or api_key == "your_tavily_api_key_here":
        return []
        
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 5
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            results = []
            for item in res_data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")
                })
            return results
    except Exception as e:
        print(f"Tavily tool call failed: {e}")
        return []

def search_ddg(query: str) -> list:
    """
    DuckDuckGo search package helper fallback.
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            return [{
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "content": r.get("body", "")
            } for r in results]
    except Exception as e:
        print(f"DuckDuckGo search fallback failed: {e}")
        return []

def search_web(query: str) -> str:
    """
    Consolidated web search function for web tool and agent queries.
    """
    results = search_tavily(query)
    if not results:
        results = search_ddg(query)
        
    if not results:
        return "No web search results found."
        
    formatted = []
    for i, r in enumerate(results, 1):
        formatted.append(f"[{i}] {r['title']}\nLink: {r['url']}\nSummary: {r['content']}\n")
    return "\n".join(formatted)
