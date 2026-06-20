from mistralai.client import Mistral
import os
import json
from tavily import TavilyClient


tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Recherche sur internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La requête de recherche"
                    }
                },
                "required": ["query"]
            }
        }
    }
]



def generate_queries(marque: str) -> list[str]:
  client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
  tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

  prompt = f"""
  Génère exactement 10 requêtes de recherche Reddit pour la marque "{marque}".
  Les requêtes doivent être en anglais et couvrir :
  - Avis positifs (2 requêtes)
  - Plaintes et problèmes (2 requêtes)  
  - Comparaisons avec concurrents (2 requêtes)
  - Scandales ou controverses (2 requêtes)
  - Expérience client / SAV (2 requêtes)

  Réponds uniquement en JSON : {{"requetes": ["...", "..."]}}
  Ne mets PAS "site:reddit.com" dans les requêtes.

  """
  messages = [{"role": "user", "content": prompt}]
  model = "mistral-small-latest"
  while True:
    response = client.chat.complete(model=model, messages=messages, tools=tools, tool_choice="auto")

    message = response.choices[0].message
    messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})

    if message.tool_calls:
      for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)
        print(f"🔍 Recherche : {args['query']}")

        result = tavily.search(args["query"])

        messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result)
        })
    else:
      content = message.content
      content = content.strip()
      if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]
      print("=== RÉPONSE MISTRAL ===")
      print(content)
      print("=======================")
      data = json.loads(content)
      res = data["requetes"]
      return res
    