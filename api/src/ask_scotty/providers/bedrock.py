"""Amazon Bedrock provider — the managed-inference path from the course's
baseline architecture ("Model Access: managed inference endpoint (Bedrock)
or external API").

Enable with MODEL_PROVIDER=bedrock. Model choice is configuration:
BEDROCK_MODEL_ID (defaults to Claude Haiku, the cheapest sensible option
for a Learner Lab budget). boto3 is imported lazily so the stub path and
the test suite never require AWS.

NOTE: Verify Bedrock is enabled in your Learner Lab region before flipping
the switch — "some services restricted by design."
"""

import json
import os

from ask_scotty.contract import AskResponse

DEFAULT_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

FALLBACK = AskResponse(
    answer=(
        "I couldn't produce a reliable answer for that question, so I'd rather "
        "refer you to a person than guess. The HUB (cmu.edu/hub) can help."
    ),
    sources=["The HUB — cmu.edu/hub"],
    confidence="low",
    escalation_flag=True,
)


class BedrockProvider:
    def __init__(self) -> None:
        self.model_id = os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import boto3  # lazy: only needed when this provider is active

            self._client = boto3.client("bedrock-runtime")
        return self._client

    def complete(self, system_prompt: str, question: str) -> AskResponse:
        result = self.client.converse(
            modelId=self.model_id,
            system=[{"text": system_prompt}],
            messages=[{"role": "user", "content": [{"text": question}]}],
            inferenceConfig={"maxTokens": 512, "temperature": 0.0},
        )
        text = result["output"]["message"]["content"][0]["text"]
        return self.parse_model_output(text)

    @staticmethod
    def parse_model_output(text: str) -> AskResponse:
        """The system prompt instructs the model to answer with contract JSON.
        Anything that doesn't parse or validate becomes a safe refusal — a
        malformed model answer must never reach a student."""
        try:
            start, end = text.index("{"), text.rindex("}") + 1
            data = json.loads(text[start:end])
            return AskResponse(
                answer=data["answer"],
                sources=list(data.get("sources", [])),
                confidence=data.get("confidence", "low"),
                escalation_flag=bool(data.get("escalation_flag", False)),
            ).validate()
        except (ValueError, KeyError, TypeError):
            return FALLBACK
