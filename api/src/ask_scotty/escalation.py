"""Structural guardrails that run BEFORE any model call.

The IA1 scope lines that must never depend on model behavior are enforced
here in code: crisis language, immigration/visa topics, and requests for
personal records are intercepted and answered with a referral, so no model
output can cross them. Exclusions are enforced by structure, not by an
accuracy target.
"""

import re

from ask_scotty.contract import AskResponse

CRISIS_TERMS = (
    "suicide",
    "suicidal",
    "kill myself",
    "hurt myself",
    "self-harm",
    "self harm",
    "end my life",
    "want to die",
)

IMMIGRATION_TERMS = (
    "visa",
    "immigration",
    "cpt",
    "opt",
    "i-20",
    "sevis",
)

# Personal-record requests are refused structurally. We match the possessive
# pattern "my … <record noun>" rather than fixed phrases, so intervening words
# can't defeat the guard: "my balance", "my financial aid balance", and "the
# balance on my aid" all trip it. Erring toward referral is the product's
# stated bias — better to hand a student to a person than to guess about a
# record we cannot see.
PERSONAL_RECORD_NOUNS = (
    "balance",
    "account",
    "aid",
    "gpa",
    "grade",
    "grades",
    "hold",
    "record",
    "records",
    "transcript",
    "bill",
    "refund",
    "status",
    "standing",
)
_PERSONAL_RECORD_RE = re.compile(
    r"\bmy\b[\w' ]{0,30}?\b(?:" + "|".join(PERSONAL_RECORD_NOUNS) + r")\b"
)

CRISIS_RESPONSE = AskResponse(
    answer=(
        "If you are in crisis or need someone to talk to right now, please contact "
        "CMU Counseling and Psychological Services (CaPS), available 24/7 at "
        "412-268-2922, or call or text the 988 Suicide & Crisis Lifeline. "
        "You matter, and people are available to help immediately."
    ),
    sources=["CMU CaPS — cmu.edu/counseling", "988 Suicide & Crisis Lifeline"],
    confidence="high",
    escalation_flag=True,
)

IMMIGRATION_RESPONSE = AskResponse(
    answer=(
        "Questions involving visas, immigration status, CPT/OPT, or enrollment "
        "requirements for international students are handled by the Office of "
        "International Education (OIE) — these are consequential topics where you "
        "should speak with an advisor directly: cmu.edu/oie."
    ),
    sources=["Office of International Education — cmu.edu/oie"],
    confidence="high",
    escalation_flag=True,
)

PERSONAL_RECORD_RESPONSE = AskResponse(
    answer=(
        "I can't access individual student records, so I can't answer questions "
        "about your specific account, aid status, or registration. The HUB can "
        "help with your personal records: cmu.edu/hub, or visit in person."
    ),
    sources=["The HUB — cmu.edu/hub"],
    confidence="high",
    escalation_flag=True,
)


def check(question: str) -> AskResponse | None:
    """Return a mandatory referral response if the question crosses a scope
    boundary, else None (safe to proceed to the model)."""
    q = question.lower()
    if any(term in q for term in CRISIS_TERMS):
        return CRISIS_RESPONSE
    if any(term in q for term in IMMIGRATION_TERMS):
        return IMMIGRATION_RESPONSE
    if _PERSONAL_RECORD_RE.search(q):
        return PERSONAL_RECORD_RESPONSE
    return None
