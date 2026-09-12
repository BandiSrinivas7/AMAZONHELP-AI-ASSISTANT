from __future__ import annotations
import os
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class ReplyGenerator:
    def __init__(self, model=None):
        self.model=model or os.getenv("OPENAI_MODEL","gpt-5.6-luna")
        self.client=OpenAI() if (OpenAI is not None and os.getenv("OPENAI_API_KEY")) else None
    def generate(self,message,intent,evidence):
        if not self.client:
            return "I’m sorry you’re dealing with this. I’d like to verify the details before giving you a definitive answer. Please share the relevant order or account details through the official support channel.", "no_api_key"
        evidence_text="\n\n".join(f"Historical customer: {e['customer']}\nHistorical AmazonHelp reply: {e['reply']}" for e in evidence)
        prompt=f"""You are an Amazon customer-support drafting assistant.\nIntent: {intent}\nCustomer message: {message}\n\nHistorical support examples:\n{evidence_text}\n\nDraft a concise, helpful reply grounded ONLY in the historical examples. Do not invent order status, refund amounts, policies, dates, links, or account actions. If the evidence is insufficient, explicitly say the case should be escalated instead of guessing."""
        r=self.client.responses.create(model=self.model,input=prompt)
        return r.output_text.strip(), None
