#!/usr/bin/env bash
#
# ReputTrack - lancement complet (backend + frontend)
#
# Usage : ./start.sh
#
# Ce script :
#   1. crée le venv du backend s'il n'existe pas
#   2. installe les dépendances Python (requirements.txt)
#   3. lance le backend FastAPI avec uvicorn (port 8000)
#   4. installe les dépendances du frontend si besoin
#   5. lance le frontend Vite (port 5173)
#
# Ctrl+C arrête les deux serveurs proprement.

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Détecte la commande python disponible
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  PYTHON=python
fi

echo "==> Backend : préparation de l'environnement virtuel"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
  echo "    venv introuvable, création..."
  "$PYTHON" -m venv venv
fi

# Active le venv
# shellcheck disable=SC1091
source venv/bin/activate

echo "==> Backend : installation des dépendances"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Vérifie le fichier .env
if [ ! -f ".env" ]; then
  echo "    ⚠️  Aucun fichier backend/.env trouvé."
  echo "       Crée-le avec :"
  echo "         MISTRAL_API_KEY=ta_cle"
  echo "         TAVILY_API_KEY=ta_cle"
fi

echo "==> Backend : démarrage de uvicorn sur http://localhost:8000"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Arrête le backend quand le script se termine
cleanup() {
  echo ""
  echo "==> Arrêt des serveurs..."
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "==> Frontend : installation des dépendances"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  npm install
fi

echo "==> Frontend : démarrage de Vite sur http://localhost:5173"
npm run dev
