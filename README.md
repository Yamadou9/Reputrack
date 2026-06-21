# ReputTrack

Outil de suivi de réputation de marque. On saisit une marque, le backend génère
des requêtes de recherche, scrape le web (Tavily) et analyse les résultats avec
Mistral pour produire une synthèse.

## Architecture

```
reputrack/
├── backend/      API FastAPI (Python) — génération de requêtes, scraping, analyse
├── frontend/     Interface React (Vite)
└── start.sh      Lance tout en une commande
```

- **Backend** : FastAPI + uvicorn, port `8000`, endpoint `POST /search`
- **Frontend** : React + Vite, port `5173`

## Prérequis

- Python 3.10+
- Node.js 18+ et npm

## Configuration

Créer un fichier `backend/.env` avec tes clés API :

```env
MISTRAL_API_KEY=ta_cle_mistral
TAVILY_API_KEY=ta_cle_tavily
```

## Lancement rapide

Une seule commande à la racine du projet :

```bash
./start.sh
```

Le script s'occupe de tout :

1. Crée le venv du backend (si absent)
2. Installe les dépendances Python (`requirements.txt`)
3. Démarre le backend avec uvicorn → http://localhost:8000
4. Installe les dépendances du frontend (si absentes)
5. Démarre le frontend Vite → http://localhost:5173

`Ctrl+C` arrête les deux serveurs.

## Lancement manuel (optionnel)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API

### `POST /search`

Requête :

```json
{ "marque": "NomDeLaMarque" }
```

Retourne la synthèse de réputation produite par l'analyse Mistral.
