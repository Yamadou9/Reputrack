import os
import json
from tavily import TavilyClient

def scrape(queries: list[str]) -> list[dict]:
  tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
  resultas = []

  for query in queries:
    result = tavily.search(query, include_domains=["reddit.com"], max_results=5, search_depth="advanced", include_raw_content=True, time_range="week")
    for item in result["results"]:
        if "/comments/" not in item["url"]:
            continue
        resultas.append({
            "title":   item["title"],
            "url":     item["url"],
            "content": item["content"],
            "score":   item["score"],
            "raw_content": item.get("raw_content"),
        })

  return resultas

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    test_queries = ["Nike running shoes review"]
    res = scrape(test_queries)

    print(f"Nombre de résultats : {len(res)}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
