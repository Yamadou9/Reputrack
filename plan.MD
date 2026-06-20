# Plan de projet — Veille Reddit par marque
 
## 1. Objectif
 
Application web où l'utilisateur entre le nom d'une marque (ex: "Nike") et reçoit en retour une sélection de 10 à 15 posts Reddit pertinents et récents (moins d'une semaine) parlant de cette marque, sans biais introduit par l'utilisateur sur les angles de recherche.
 
## 2. Stack technique
 
- **Frontend** : React (Vite)
- **Backend** : Python (FastAPI recommandé pour la simplicité des endpoints async)
- **IA** : API Anthropic (Claude) pour les deux étapes IA du pipeline
- **Scraping** : API Reddit officielle (PRAW + credentials OAuth) en priorité, ou recherche JSON publique de Reddit en fallback
## 3. Structure du projet (à respecter strictement)
 
```
projet/
├── backend/
│   ├── app/
│   │   ├── main.py              # entrypoint FastAPI
│   │   ├── routers/
│   │   │   └── search.py        # endpoint POST /search
│   │   ├── services/
│   │   │   ├── query_generator.py   # étape 1 : IA génère les requêtes
│   │   │   ├── reddit_scraper.py    # étape 2 : scraping Reddit
│   │   │   └── curator.py           # étape 3 : IA sélectionne les posts pertinents
│   │   └── models/
│   │       └── schemas.py       # schémas Pydantic (requêtes/réponses)
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore                # venv/, __pycache__/, .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   ├── package.json
│   └── .gitignore                # node_modules/, dist/
└── README.md
```
 
⚠️ **Point de vigilance n°1** : le précédent projet a explosé en nombre de fichiers très probablement parce que `node_modules/` et/ou un environnement virtuel Python ont été commités ou copiés. Dès l'initialisation, mettre en place les `.gitignore` corrects et ne jamais zipper/donner à une IA un dossier sans avoir vérifié son contenu au préalable.
 
## 4. Workflow fonctionnel détaillé
 
### Étape 0 — Saisie utilisateur
L'utilisateur entre uniquement le nom de la marque dans un champ texte. Rien d'autre n'est demandé pour ne pas biaiser la suite.
 
### Étape 1 — Génération des requêtes de recherche (IA n°1)
- Le nom de marque est envoyé à Claude avec un prompt qui lui demande de générer N requêtes de recherche variées et non biaisées (ex: nom seul, "nom + défaut", "nom + arnaque", "nom + avis", "nom + alternative", "nom + problème", "nom + actualité récente", etc.)
- Sortie attendue : un tableau JSON de strings, rien d'autre.
- Le nombre de requêtes générées doit être paramétrable (ex: 6 à 10 par défaut).
- Important : le prompt système doit explicitement demander à l'IA de couvrir des angles variés (positifs, négatifs, neutres, actualité) sans favoriser une tonalité, pour éviter l'effet observé précédemment où l'IA orientait trop les résultats.
### Étape 2 — Scraping Reddit
- Chaque requête générée à l'étape 1 est utilisée pour chercher sur Reddit.
- Filtrage temporel : seulement les posts de moins d'une semaine (paramètre configurable pour pouvoir l'élargir plus tard).
- Les résultats de toutes les requêtes sont agrégés et dédupliqués (par id de post / URL).
- Sortie : un JSON unique contenant pour chaque post au minimum : titre, subreddit, URL, score, nombre de commentaires, date de création, extrait du texte (selftext tronqué), requête d'origine.
### Étape 3 — Sélection par IA (IA n°2)
- Le JSON complet (non trié, pas besoin de pré-tri) est envoyé directement à Claude.
- Prompt : sélectionner les 10 à 15 posts les plus pertinents et réellement liés à la marque (exclure le spam, les posts hors-sujet, les doublons de contenu).
- Sortie attendue : JSON structuré avec pour chaque post sélectionné : titre, URL, subreddit, extrait, et éventuellement une courte justification de pertinence.
### Étape 4 — Affichage
- Le frontend reçoit le JSON final et l'affiche sous forme de cartes (titre, sous-titre subreddit, extrait, lien vers le post original).
- Prévoir un état de chargement clair car le pipeline complet (IA → scraping → IA) prend plusieurs secondes, idéalement avec un retour visuel par étape ("Génération des recherches...", "Scraping en cours...", "Sélection des résultats...").
## 5. Design
 
Style épuré / minimaliste, à définir précisément à partir des captures d'écran du précédent site (à fournir). En attendant, partir sur les bases suivantes à ajuster ensuite :
- Palette neutre (blanc/gris/noir) avec une couleur d'accent unique
- Typographie sobre, beaucoup d'espace blanc
- Une seule page principale : champ de recherche centré, résultats qui apparaissent en dessous sous forme de liste de cartes
*(Section à compléter dès que les captures d'écran sont partagées avec Claude Code.)*
 
## 6. Phases de développement recommandées
 
1. **Setup** : initialisation des deux dossiers (backend/frontend), `.gitignore`, dépendances de base, README.
2. **Maquette frontend statique** : page de recherche + affichage de résultats avec des données factices, pour valider le design avant de brancher le backend.
3. **Backend squelette** : FastAPI avec un endpoint `/search` qui retourne des données factices.
4. **Module IA n°1** : génération des requêtes (testable isolément en script/CLI avant intégration).
5. **Module scraper Reddit** : récupération et agrégation des posts, testable isolément.
6. **Module IA n°2** : sélection des posts pertinents, testable isolément.
7. **Orchestration** : chaîner les 3 modules dans l'endpoint `/search`.
8. **Intégration frontend ↔ backend** : appel réel de l'API, gestion des états de chargement et des erreurs.
9. **Polissage** : gestion des cas sans résultat, limites de taux (rate limit Reddit), variables d'environnement / clés API sécurisées.
10. **Déploiement** (à définir selon préférence : Vercel pour le frontend, Railway/Render pour le backend, par exemple).
## 7. Points d'attention techniques
 
- Credentials Reddit (client_id/secret) nécessaires pour l'API officielle — à stocker en variables d'environnement, jamais en dur dans le code.
- Le coût/latence : utiliser un modèle rapide pour la génération de requêtes (étape 1, tâche simple) et garder un modèle plus capable pour la sélection finale (étape 3, tâche qui demande du jugement).
- Reddit ne permet pas un filtre "exactement moins d'une semaine" nativement sur toutes les recherches : prévoir un filtrage côté backend sur `created_utc` après récupération.
- Gérer le cas où une marque ne génère aucun résultat pertinent (message clair à l'utilisateur plutôt qu'une page vide).
