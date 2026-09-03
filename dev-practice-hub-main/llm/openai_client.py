import json
import os

from openai import OpenAI


class OpenAIClient:
    """Thin wrapper around the OpenAI chat completions API.

    Previously `classify_email` returned the raw string from the
    model with no JSON parsing, so every caller had to re-parse it
    (and often didn't). This now returns a parsed dict, with a safe
    fallback if the model ever returns malformed JSON.
    """

    def __init__(self, api_key=None, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    def classify_email(self, email):
        prompt = f"""You are an AI recruiter assistant that extracts structured
data from job-application-related emails.

Return ONLY a valid JSON object with these fields:
- company (string, or "Unknown")
- role (string, or "Unknown")
- status (one of: Applied, Interview, Assessment, Offer, Rejected, Unknown)
- confidence (integer 0-100)
- next_action (short string, or "")

Email subject: {email.get('subject', '')}
Email sender: {email.get('sender', '')}
Email body (first 800 chars): {email.get('body', '')[:800]}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )

        try:
            return json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, IndexError, AttributeError, KeyError):
            return {
                "company": "Unknown",
                "role": "Unknown",
                "status": "Unknown",
                "confidence": 0,
                "next_action": "",
            }
