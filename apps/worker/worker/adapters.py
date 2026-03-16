from dataclasses import dataclass
from enum import Enum

from worker.prompt_templates import build_geo_intent_prompt


class ProviderErrorCode(str, Enum):
    timeout = "timeout"
    rate_limit = "rate_limit"
    auth = "auth"
    upstream = "upstream"
    unknown = "unknown"


class ProviderAdapterError(RuntimeError):
    def __init__(self, provider: str, code: ProviderErrorCode, message: str):
        super().__init__(message)
        self.provider = provider
        self.code = code


@dataclass
class MentionEvaluation:
    provider: str
    mentioned: bool
    sentiment: str
    rationale: str
    raw_response: str


class BaseProviderAdapter:
    provider_name = "base"

    def __init__(self, api_key: str | None):
        self.api_key = api_key or ""

    def evaluate(self, brand_name: str, industry: str, intent: str) -> MentionEvaluation:
        prompt = build_geo_intent_prompt(brand_name=brand_name, industry=industry, intent=intent)
        return self._evaluate_prompt(prompt=prompt, brand_name=brand_name, intent=intent)

    def _evaluate_prompt(self, prompt: str, brand_name: str, intent: str) -> MentionEvaluation:
        # Deterministic scaffold behavior with stable output when provider API is not wired yet.
        score = abs(hash(f"{self.provider_name}:{brand_name}:{intent}"))
        mentioned = (score % 2) == 0
        sentiment_idx = score % 3
        sentiment = ["positive", "neutral", "negative"][sentiment_idx]

        if not self.api_key:
            rationale = "Provider API key missing, returned deterministic scaffold evaluation."
            raw = f"scaffold::{self.provider_name}::{prompt}"
        else:
            rationale = "Provider adapter scaffold path used with configured API key."
            raw = f"configured-key::{self.provider_name}::{prompt}"

        return MentionEvaluation(
            provider=self.provider_name,
            mentioned=mentioned,
            sentiment=sentiment,
            rationale=rationale,
            raw_response=raw,
        )


class OpenAIAdapter(BaseProviderAdapter):
    provider_name = "openai"


class GeminiAdapter(BaseProviderAdapter):
    provider_name = "gemini"


class AnthropicAdapter(BaseProviderAdapter):
    provider_name = "anthropic"


def get_provider_adapter(provider_name: str, openai_key: str, gemini_key: str, anthropic_key: str) -> BaseProviderAdapter:
    normalized = provider_name.strip().lower()

    if normalized == "openai":
        return OpenAIAdapter(openai_key)
    if normalized == "gemini":
        return GeminiAdapter(gemini_key)
    if normalized == "anthropic":
        return AnthropicAdapter(anthropic_key)

    raise ProviderAdapterError(provider=provider_name, code=ProviderErrorCode.unknown, message="Unsupported provider")
