"""Model access is abstracted behind one interface — swap models by config,
not rewrite. The active provider is chosen by the MODEL_PROVIDER environment
variable (configuration, not a secret)."""

import os
from typing import Protocol

from ask_scotty.contract import AskResponse


class ModelProvider(Protocol):
    def complete(self, system_prompt: str, question: str) -> AskResponse: ...


def get_provider(name: str | None = None) -> ModelProvider:
    """Resolve the model provider from config. Defaults to the stub so the
    service runs anywhere (devcontainer, CI, Learner Lab) with zero AWS calls."""
    name = (name or os.environ.get("MODEL_PROVIDER", "stub")).lower()
    if name == "stub":
        from ask_scotty.providers.stub import StubProvider

        return StubProvider()
    if name == "bedrock":
        from ask_scotty.providers.bedrock import BedrockProvider

        return BedrockProvider()
    raise ValueError(f"Unknown MODEL_PROVIDER: {name!r} (expected 'stub' or 'bedrock')")
