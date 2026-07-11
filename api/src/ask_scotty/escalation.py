"""Structural guardrails that run BEFORE any model call.

The IA1 scope lines that must never depend on model behavior are enforced
here in code: crisis language, immigration/visa topics, and requests for
personal records are intercepted and answered with a referral, so no model
output can cross them. Exclusions are enforced by structure, not by an
accuracy target.
"""

import re

from ask_scotty.contract import AskResponse

# Crisis language is matched by patterns, not fixed phrases, for the same
# reason as the personal-record guard below: fixed substrings miss common
# paraphrases ("end it all", "can't go on anymore" were verified misses).
# Bias is toward safety — a false crisis referral is jarring; a missed one is
# unacceptable. Patterns deliberately avoid known figurative collisions:
# "this deadline is killing me", "dying to know", "hurt my transcript",
# "can't go on the waitlist" must NOT trigger.
_CRISIS_PATTERNS = tuple(
    re.compile(p)
    for p in (
        # "academic/career/social suicide" is campus figurative speech, not crisis
        r"(?<!academic\s)(?<!career\s)(?<!social\s)\bsuicid\w*",
        r"\bself[- ]?harm\w*",                             # self-harm / self harm
        r"\b(?:kill|hurt|harm|cut|shoot|hang|drown|poison)\w*\s+myself\b",
        r"\bunaliv\w+",                                    # unalive / unaliving
        # "kms" slang; guard "5 kms", "how many kms", "kms away/from"
        r"(?<![\d.,]\s)(?<!many\s)(?<!few\s)\bkms\b(?!\s*(?:away|from))",
        r"\bend(?:ing)?\s+(?:it\s+all|things|my\s+(?:own\s+)?life)\b",
        r"\bending\s+it\b",
        r"\b(?:ways?\s+to|how\s+to)\s+end\s+it\b",
        r"\btake\s+my\s+(?:own\s+)?life\b",
        r"\b(?:want(?:ed)?|wish(?:ing)?|ready)\s+to\s+die\b",
        r"\bwanna\s+die\b",
        r"\bwish\s+i\s+(?:was|were)\s+(?:dead|gone|never\s+born)\b",
        r"\bbetter\s+(?:off\s+)?(?:dead|without\s+me|if\s+i\s+(?:was|were)\s+(?:gone|dead))\b",
        r"\bno\s+(?:reason|point)\s+(?:to|in)\s+(?:keep\s+)?(?:liv\w*|go(?:ing)?\s+on)",
        r"\b(?:isn'?t|not|no\s+longer)\s+worth\s+living\b",
        r"\bcan'?t\s+go\s+on\b(?!\s+(?:the|a|an|to|with|in|at|until)\b)",
        r"\bcan'?t\s+(?:take|do)\s+(?:it|this)\s+(?:anymore|any\s+more)\b",
        # "live" must not swallow "live in the dorms / live on campus"
        r"\b(?:don'?t|no\s+longer)\s+want\s+to\s+(?:be\s+alive|live\b(?!\s+(?:in|on|at|with|off|near|there))|exist|wake\s+up)",
        r"\bdon'?t\s+want\s+to\s+be\s+here\s+(?:anymore|any\s+more)\b",
        r"\b(?:rather\s+not|don'?t\s+want\s+to)\s+wake\s+up\b",
        r"\b(?:thinking|thought)s?\s+(?:about|of)\s+(?:dying|death\b|ending\s+(?:it|things|my\s+life)|jumping)\b",
        r"\bjump(?:ing)?\s+off\s+(?:the\s+|a\s+)?(?:bridge|roof|building)\b",
        r"\bwon'?t\s+be\s+around\s+much\s+longer\b",
        r"\bgoodbye\s+letters?\b",
        r"\bdo\s+to\s+myself\b",
        r"\boverdos\w+",
        r"\bhopeless\s+and\s+(?:alone|done)\b",
    )
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
    q = question.lower().replace("’", "'")  # normalize curly apostrophes
    if any(p.search(q) for p in _CRISIS_PATTERNS):
        return CRISIS_RESPONSE
    if any(term in q for term in IMMIGRATION_TERMS):
        return IMMIGRATION_RESPONSE
    if _PERSONAL_RECORD_RE.search(q):
        return PERSONAL_RECORD_RESPONSE
    return None
