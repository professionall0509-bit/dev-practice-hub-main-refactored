from llm.openai_client import OpenAIClient


class ClassifierAgent:
    """Classifies a parsed email into company / role / status / next action.

    Accepts an injected llm_client so tests can pass a fake client
    instead of hitting the real OpenAI API.
    """

    def __init__(self, llm_client=None):
        self.llm = llm_client or OpenAIClient()

    def classify(self, email):
        return self.llm.classify_email(email)
