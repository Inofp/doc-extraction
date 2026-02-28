import json
from openai import OpenAI

SYSTEM = """
You extract invoice fields into strict JSON only.
Return JSON object matching keys:
invoice_number, invoice_date, seller_name, buyer_name, total_amount, iban.
If unknown, use null. No extra text.
""".strip()

class LLMRepair:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def repair(self, raw_text: str, extracted: dict) -> dict:
        payload = {
            "text": raw_text,
            "current": extracted
        }
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
            ],
            temperature=0
        )
        content = resp.choices[0].message.content
        return json.loads(content)