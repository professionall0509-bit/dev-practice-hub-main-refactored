"""
Previously this "test" just called the real OpenAI API and printed
the result — it needed a live key and asserted nothing. This uses a
fake LLM client instead, so it runs offline and actually checks
something.
"""

from unittest.mock import MagicMock

from agents.classifier_agent import ClassifierAgent


def test_classify_returns_expected_fields():
    fake_llm = MagicMock()
    fake_llm.classify_email.return_value = {
        "company": "TCS",
        "role": "GenAI Engineer",
        "status": "Interview",
        "confidence": 90,
        "next_action": "Prepare for interview",
    }

    agent = ClassifierAgent(llm_client=fake_llm)

    result = agent.classify({
        "subject": "You've been shortlisted",
        "sender": "hr@tcs.com",
        "body": "Congratulations! You have been shortlisted for the next round.",
    })

    assert result["company"] == "TCS"
    assert result["status"] == "Interview"
    fake_llm.classify_email.assert_called_once()


if __name__ == "__main__":
    test_classify_returns_expected_fields()
    print("PASS: test_classifier")
