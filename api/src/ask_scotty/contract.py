"""Response contract for POST /ask.

The API returns a checked, structured answer — never free-form chat:

    {
      "answer": "The registrar is in Warner Hall 250.",
      "sources": ["Campus Directory 2024"],
      "confidence": "high",
      "escalation_flag": false
    }

Every response the service emits must pass validate() before leaving the
handler. escalation_flag=true means "a human should take this from here"
and is always accompanied by a referral in the answer text.
"""

from dataclasses import dataclass, field

CONFIDENCE_LEVELS = ("high", "medium", "low")


@dataclass
class AskResponse:
    answer: str
    sources: list[str] = field(default_factory=list)
    confidence: str = "low"
    escalation_flag: bool = False

    def validate(self) -> "AskResponse":
        if not isinstance(self.answer, str) or not self.answer.strip():
            raise ValueError("answer must be a non-empty string")
        if not isinstance(self.sources, list) or not all(
            isinstance(s, str) for s in self.sources
        ):
            raise ValueError("sources must be a list of strings")
        if self.confidence not in CONFIDENCE_LEVELS:
            raise ValueError(
                f"confidence must be one of {CONFIDENCE_LEVELS}, got {self.confidence!r}"
            )
        if not isinstance(self.escalation_flag, bool):
            raise ValueError("escalation_flag must be a bool")
        return self

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "sources": self.sources,
            "confidence": self.confidence,
            "escalation_flag": self.escalation_flag,
        }
