from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from src.agent import SupportAgent

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "data/processed/intent_model.joblib"
RETRIEVAL = ROOT / "data/processed/retrieval/rows.json"

app = FastAPI(
    title="AmazonHelp BrandSupport-AI",
    version="1.0.0",
    description="Evidence-grounded customer support drafting API."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_agent = None

class Request(BaseModel):
    message: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_exists": MODEL.exists(),
        "retrieval_exists": RETRIEVAL.exists(),
    }

@app.post("/api/support")
def support(req: Request):
    global _agent
    if _agent is None:
        _agent = SupportAgent(str(MODEL), str(RETRIEVAL))
    return _agent.run(req.message, req.top_k)
