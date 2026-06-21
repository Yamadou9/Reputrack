from mistralai.client import Mistral
import os
import re
import json


def clean_text(text: str) -> str:
  """Nettoie le raw_content de Reddit : enlève images, liens, pubs et navigation."""
  if not text:
    return ""

  text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
  text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
  text = re.sub(r"\[\s*\]\([^)]*\)", "", text)

  bruit = [
    "Skip to main content", "Open menu", "Open navigation", "Go to Reddit Home",
    "Sign Up", "Log In", "Sign up for Reddit", "Log in to Reddit",
    "Expand user menu", "Open settings menu", "Open comment sort options",
    "Reply", "Share", "Promoted", "Shop Now", "Learn More", "View in app",
    "more reply", "more replies", "More replies", "Collapse video player",
  ]
  lignes_propres = []
  couper = False
  for ligne in text.split("\n"):
    nettoyee = ligne.strip()
    if nettoyee in ("# People also ask about section", "People also ask"):
      couper = True
    if couper:
      continue
    if not nettoyee:
      continue
    if nettoyee in bruit:
      continue

    if re.fullmatch(r"•?\s*\d+\s*(mo|hr|min|day|days|yr|year|years|hours|minutes|months)\.?\s*ago", nettoyee):
      continue
    lignes_propres.append(nettoyee)

  text = "\n".join(lignes_propres)

  text = re.sub(r"\n{3,}", "\n\n", text)

  return text.strip()


def analyze_reputation(marque: str, posts: list[dict]) -> dict:
  client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

  bloc = ""
  for i, post in enumerate(posts, start=1):
    bloc += f"--- POST {i} (score {post['score']:.2f}) ---\n"
    bloc += f"Titre : {post['title']}\n"
    bloc += f"{post['clean']}\n\n"

  prompt = f"""
  Voici des discussions Reddit à propos de la marque "{marque}".
  Analyse la réputation de la marque à partir de ces avis réels d'utilisateurs.
  Base-toi UNIQUEMENT sur les discussions fournies. N'invente aucun modèle ou fait absent du texte."

  {bloc}

  Réponds UNIQUEMENT en JSON avec ce format exact :
  {{
    "sentiment_global": "positif | negatif | neutre | mitige",
    "score": <entier de 0 à 100, 0 = très mauvaise réputation, 100 = excellente>,
    "resume": "<2-3 phrases résumant ce que pensent les gens>",
    "points_positifs": ["...", "..."],
    "points_negatifs": ["...", "..."],
    "themes": ["...", "..."],
    "posts": [
      {{
        "id": <le numéro du POST tel qu'indiqué ci-dessus>,
        "pertinent": <true si le post parle vraiment de la marque "{marque}", false sinon>,
        "pertinence": <entier de 0 à 100, à quel point le post concerne la marque>,
        "sentiment": "positif | negatif | neutre",
        "score": <entier de 0 à 100 pour CE post précis>
      }}
    ]
  }}
  Dans "posts", inclus UN objet par POST fourni (même les hors-sujet, avec pertinent=false).
  """

  messages = [{"role": "user", "content": prompt}]
  response = client.chat.complete(
    model="mistral-small-latest",
    messages=messages,
    response_format={"type": "json_object"},
  )

  content = response.choices[0].message.content.strip()
  # Mistral entoure parfois le JSON de ```json ... ```
  if content.startswith("```"):
    content = content.split("\n", 1)[1]
    content = content.rsplit("```", 1)[0]

  try:
    return json.loads(content)
  except json.JSONDecodeError:
    # Filet de sécurité : on isole le premier objet JSON du texte
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
      return json.loads(match.group(0))
    raise


def curate(marque: str, posts: list[dict]) -> dict:
  for post in posts:
    brut = post.get("raw_content") or post.get("content") or ""
    propre = clean_text(brut)
    post["clean"] = propre[:3000]

  analyse = analyze_reputation(marque, posts)

  # On fusionne l'analyse par post (renvoyée par Mistral) avec les vraies
  # données scrapées (titre, contenu, url) pour alimenter les cartes du front.
  analyse_par_post = {p.get("id"): p for p in analyse.get("posts", [])}
  cartes = []
  for i, post in enumerate(posts, start=1):
    info = analyse_par_post.get(i, {})

    # On supprime les posts qui n'ont rien à voir avec la marque.
    if info.get("pertinent") is False:
      continue

    cartes.append({
      "title": post["title"],
      "content": post["clean"][:500],
      "lien": post["url"],
      "pertinence": info.get("pertinence", 0),
      "sentiment": info.get("sentiment", "neutre"),
      "score": info.get("score", 0),
    })

  # Posts en principal : triés du plus pertinent au moins pertinent.
  cartes.sort(key=lambda c: c["pertinence"], reverse=True)

  analyse["posts"] = cartes
  return analyse


if __name__ == "__main__":
  from dotenv import load_dotenv
  from scraper import scrape
  load_dotenv()

  posts = scrape(["Nike running shoes review"])
  print(f"{len(posts)} posts récupérés, analyse en cours...")

  analyse = curate("Nike", posts)
  print(json.dumps(analyse, indent=2, ensure_ascii=False))
