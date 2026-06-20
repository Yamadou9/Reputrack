from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.query_generator import generate_queries
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/search")
def search(data: dict):
  marque = data["marque"]
  queries = generate_queries(marque)
  print(queries)
  return {"queries": queries}