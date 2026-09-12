from __future__ import annotations
import json, os
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

RUBRIC="""Score the support reply from 1 to 5 on each dimension: correctness, groundedness in evidence, helpfulness, brand consistency, and unsupported-claim avoidance. A 5 means excellent. Return JSON only with keys correctness, groundedness, helpfulness, brand_consistency, unsupported_claim_avoidance, overall, rationale."""

def judge(customer,reply,evidence,model=None):
    if OpenAI is None or not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OpenAI SDK/API key not available")
    client=OpenAI(); model=model or os.getenv("OPENAI_MODEL","gpt-5.6-luna")
    ev="\n".join(f"Customer: {x['customer']}\nReply: {x['reply']}" for x in evidence)
    r=client.responses.create(model=model,input=f"{RUBRIC}\n\nCustomer: {customer}\nCandidate reply: {reply}\nEvidence:\n{ev}")
    text=r.output_text.strip()
    return json.loads(text)
