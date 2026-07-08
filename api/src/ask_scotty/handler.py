"""Lambda handler for POST /ask.

Orchestration: receive → guardrails → build prompt → call model → parse →
log → return. Every response validates against the contract before leaving.
"""

import json
import logging
import os
import time
import uuid
from pathlib import Path

from ask_scotty import escalation
from ask_scotty.contract import AskResponse
from ask_scotty.providers.base import get_provider

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PROMPT_PATH = Path(__file__).parent / "prompts" / "system_prompt.md"
LOG_RETENTION_SECONDS = 90 * 24 * 3600  # IA1: anonymized logs, 90-day retention


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def answer_question(question: str) -> AskResponse:
    """The full model-driven workflow for one question."""
    guarded = escalation.check(question)
    if guarded is not None:
        return guarded.validate()
    provider = get_provider()
    return provider.complete(load_system_prompt(), question).validate()


def log_exchange(question: str, response: AskResponse) -> None:
    """Write an anonymized exchange record to DynamoDB (deployed only —
    env-gated so local runs and tests make no AWS calls). No user
    identifiers are ever stored."""
    table_name = os.environ.get("LOG_TABLE")
    if not table_name:
        return
    import boto3  # lazy: present in the Lambda runtime

    now = int(time.time())
    boto3.resource("dynamodb").Table(table_name).put_item(
        Item={
            "exchange_id": str(uuid.uuid4()),
            "asked_at": now,
            "expires_at": now + LOG_RETENTION_SECONDS,  # DynamoDB TTL
            "question": question,
            "answer": response.answer,
            "sources": response.sources,
            "confidence": response.confidence,
            "escalation_flag": response.escalation_flag,
            "provider": os.environ.get("MODEL_PROVIDER", "stub"),
        }
    )


def _http_response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event: dict, context=None) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _http_response(400, {"error": "request body must be JSON"})

    question = (body.get("question") or "").strip()
    if not question:
        return _http_response(400, {"error": "missing required field: question"})

    response = answer_question(question)
    try:
        log_exchange(question, response)
    except Exception:  # logging must never break an answer
        logger.exception("failed to log exchange")
    return _http_response(200, response.to_dict())
