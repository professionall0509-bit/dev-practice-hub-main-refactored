"""
ResumeMatchAgent — not implemented yet.

Same situation as planner_agent.py: this file existed but was empty.
Left as a documented stub rather than silently empty.

Intended purpose: compare a stored resume against a job description
(pulled from a tracked application's email body) and score how well
they match, to help prioritize which applications to focus on.

See README.md "Roadmap" section.
"""


class ResumeMatchAgent:
    def score_match(self, resume_text, job_description):
        raise NotImplementedError(
            "ResumeMatchAgent.score_match is not implemented yet. "
            "See README.md 'Roadmap'."
        )
