"""
CVAlign Lens — LLM Client (Groq)
Uses Groq's free API tier for fast, cost-free LLM inference.
"""

import os
import json
import re
from groq import Groq


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY environment variable is not set. "
                "Get a free key at https://console.groq.com"
            )

        self.client = Groq(api_key=api_key)

        # ✅ DEFINE MODEL HERE
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def call(self, system_prompt: str, user_prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2048,  # safer limit than 4096
        )

        raw_text = response.choices[0].message.content.strip()
        return self._extract_json(raw_text)

    def _extract_json(self, text: str) -> dict:
        cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned.strip())

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

            raise ValueError(
                f"LLM response could not be parsed as JSON. "
                f"Raw response: {text[:300]}... Error: {e}"
            )