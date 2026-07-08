"""Stub provider — the TM1 walking skeleton.

Returns canned, source-cited answers for a handful of routine questions and
refuses everything else with a referral to The HUB. This exercises the full
request path (contract, escalation, logging) without any model dependency.
The canned entries mirror the IA1 whitelist idea: every answer names its
source page.
"""

from ask_scotty.contract import AskResponse

# (keywords that must all appear, response) — first match wins.
CANNED: list[tuple[tuple[str, ...], AskResponse]] = [
    (
        ("drop",),
        AskResponse(
            answer=(
                "The last day to drop a course (or withdraw without a 'W') is "
                "published on the official academic calendar for each semester. "
                "[STUB — real dates will come from the retrieval layer in a later "
                "milestone.] See the academic calendar for the current deadline."
            ),
            sources=["CMU Academic Calendar — cmu.edu/hub/calendar"],
            confidence="high",
            escalation_flag=False,
        ),
    ),
    (
        ("registrar",),
        AskResponse(
            answer=(
                "The University Registrar's Office is located in Warner Hall and "
                "is reachable through The HUB. [STUB response.]"
            ),
            sources=["University Registrar — cmu.edu/hub/registrar"],
            confidence="high",
            escalation_flag=False,
        ),
    ),
    (
        ("financial", "aid"),
        AskResponse(
            answer=(
                "The financial aid application process (steps, forms, and deadlines) "
                "is documented by The HUB. [STUB — process steps only; I can never "
                "answer questions about an individual aid package.]"
            ),
            sources=["The HUB Financial Aid — cmu.edu/sfs/financial-aid"],
            confidence="medium",
            escalation_flag=False,
        ),
    ),
]

REFUSAL = AskResponse(
    answer=(
        "I don't have a reliable, sourced answer for that yet, so I'd rather hand "
        "you to a person than guess. The HUB (cmu.edu/hub) can help directly, "
        "or point you to the right office."
    ),
    sources=["The HUB — cmu.edu/hub"],
    confidence="low",
    escalation_flag=True,
)


class StubProvider:
    def complete(self, system_prompt: str, question: str) -> AskResponse:
        q = question.lower()
        for keywords, response in CANNED:
            if all(k in q for k in keywords):
                return response
        return REFUSAL
