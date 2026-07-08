import pytest

from ask_scotty.providers.base import get_provider
from ask_scotty.providers.bedrock import BedrockProvider
from ask_scotty.providers.stub import StubProvider


def test_default_provider_is_stub(monkeypatch):
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    assert isinstance(get_provider(), StubProvider)


def test_provider_swapped_by_config(monkeypatch):
    # "Swap models by config, not rewrite" — no code change, one env var.
    monkeypatch.setenv("MODEL_PROVIDER", "bedrock")
    assert isinstance(get_provider(), BedrockProvider)


def test_unknown_provider_rejected():
    with pytest.raises(ValueError, match="MODEL_PROVIDER"):
        get_provider("gpt-on-a-floppy")


def test_stub_answers_carry_sources():
    resp = StubProvider().complete("", "Where is the registrar office?")
    assert resp.validate().sources


def test_stub_refusal_escalates():
    resp = StubProvider().complete("", "Tell me a joke about entropy")
    assert resp.escalation_flag is True
    assert resp.confidence == "low"


def test_bedrock_parses_contract_json():
    text = (
        'Here you go:\n{"answer": "Drop deadline is on the calendar.",'
        ' "sources": ["Academic Calendar"], "confidence": "high",'
        ' "escalation_flag": false}'
    )
    resp = BedrockProvider.parse_model_output(text)
    assert resp.answer.startswith("Drop deadline")
    assert resp.escalation_flag is False


def test_bedrock_malformed_output_becomes_safe_refusal():
    resp = BedrockProvider.parse_model_output("I think the answer is probably 42.")
    assert resp.escalation_flag is True
    assert resp.confidence == "low"
