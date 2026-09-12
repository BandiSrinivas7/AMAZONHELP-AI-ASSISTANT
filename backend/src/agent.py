from __future__ import annotations
import os, joblib
from pathlib import Path
from src.models.intent import predict
from src.retrieval.hybrid import HybridRetriever
from src.generation.agent import ReplyGenerator

class SupportAgent:
    def __init__(self,model_path,retrieval_path):
        self.intent_model=joblib.load(model_path)
        self.retriever=HybridRetriever.from_jsonl(retrieval_path)
        self.generator=ReplyGenerator()
        self.intent_threshold=float(os.getenv("INTENT_CONFIDENCE_THRESHOLD","0.62"))
        self.retrieval_threshold=float(os.getenv("RETRIEVAL_SCORE_THRESHOLD","0.08"))
    def run(self,message,top_k=5):
        intent,conf=predict(self.intent_model,message)
        evidence=self.retriever.search(message,top_k)
        best=float(evidence[0]["retrieval_score"]) if evidence else 0.0
        reasons=[]
        if conf<self.intent_threshold: reasons.append(f"low intent confidence ({conf:.2f})")
        if best<self.retrieval_threshold: reasons.append(f"weak historical evidence ({best:.3f})")
        risk_terms=["fraud","unauthorized","stolen","identity theft","lawsuit","legal","chargeback","account hacked","payment dispute"]
        lowered=message.lower()
        if any(t in lowered for t in risk_terms): reasons.append("high-risk/account-sensitive request")
        reply,_=self.generator.generate(message,intent,evidence)
        escalate=bool(reasons) or reply.startswith("I’m sorry")
        return {"intent":intent,"intent_confidence":conf,"reply":reply,"decision":"ESCALATE" if escalate else "AUTO-HANDLE","reason":reasons or ["sufficient intent confidence and historical evidence"],"evidence":evidence}
