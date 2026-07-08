import pytest

from ask_scotty.contract import AskResponse


def test_valid_response_roundtrip():
    resp = AskResponse(
        answer="The registrar is in Warner Hall 250.",
        sources=["Campus Directory 2024"],
        confidence="high",
        escalation_flag=False,
    ).validate()
    assert resp.to_dict() == {
        "answer": "The registrar is in Warner Hall 250.",
        "sources": ["Campus Directory 2024"],
        "confidence": "high",
        "escalation_flag": False,
    }


def test_empty_answer_rejected():
    with pytest.raises(ValueError, match="answer"):
        AskResponse(answer="  ").validate()


def test_bad_confidence_rejected():
    with pytest.raises(ValueError, match="confidence"):
        AskResponse(answer="x", confidence="very high").validate()


def test_bad_sources_rejected():
    with pytest.raises(ValueError, match="sources"):
        AskResponse(answer="x", sources=[1, 2]).validate()


def test_contract_has_exactly_four_fields():
    # The course contract: answer, sources, confidence, escalation_flag.
    assert set(AskResponse(answer="x").to_dict()) == {
        "answer",
        "sources",
        "confidence",
        "escalation_flag",
    }
