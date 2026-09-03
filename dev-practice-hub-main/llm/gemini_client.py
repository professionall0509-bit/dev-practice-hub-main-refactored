import json
import os
import time

import google.generativeai as genai


class GeminiClient:
    """Google Gemini equivalent of OpenAIClient — same classify_email()
    interface, so ClassifierAgent doesn't need to change at all.

    Gemini's free tier (no credit card required) is rate-limited per
    minute, so a couple of 429s while processing a big backlog of
    emails is normal, not a bug — this retries a few times with a
    short backoff before giving up on a single email.
    """

    def __init__(self, api_key=None, model="gemini-1.5-flash"):
        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(model)

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

        default = {
            "company": "Unknown",
            "role": "Unknown",
            "status": "Unknown",
            "confidence": 0,
            "next_action": "",
        }

        for attempt in range(3):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0,
                    },
                )
                return json.loads(response.text)
            except json.JSONDecodeError:
                return default
            except Exception as e:
                # Free-tier rate limit — back off and retry a couple of times.
                if "429" in str(e) and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                return default

        return default
