from llm.gemini_client import GeminiClient


class ClassifierAgent:
    """Classifies a parsed email into company / role / status / next action.

    Accepts an injected llm_client so tests can pass a fake client
    instead of hitting a real API. Defaults to Gemini (free tier, no
    credit card needed) — swap in llm.openai_client.OpenAIClient
    instead if you'd rather pay for OpenAI.
    """

    def __init__(self, llm_client=None):
        self.llm = llm_client or GeminiClient()

    def classify(self, email):
        return self.llm.classify_email(email)
