import json
from openai import OpenAI

class LLMRepair:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def repair(self, raw_text: str, extracted: dict) -> dict:
        prompt = f"""
        Extract structured invoice fields from text.

        TEXT:
        {raw_text}

        CURRENT_JSON:
        {json.dumps(extracted)}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return json.loads(response.choices[0].message.content)