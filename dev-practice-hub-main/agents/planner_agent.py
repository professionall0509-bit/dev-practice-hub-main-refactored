"""
PlannerAgent — not implemented yet.

This file previously existed but was completely empty even though it
was implied by the README's "agentic system" framing. Rather than
leave it silently empty (which looks like a bug when someone tries to
import it), it's now a documented stub that fails loudly and points
to what it's meant to do.

Intended purpose: given the current set of tracked applications,
suggest next actions — e.g. "you applied to Company X 10 days ago
with no response, consider following up."

See README.md "Roadmap" section.
"""


class PlannerAgent:
    def plan_next_actions(self, applications):
        raise NotImplementedError(
            "PlannerAgent.plan_next_actions is not implemented yet. "
            "See README.md 'Roadmap'."
        )
