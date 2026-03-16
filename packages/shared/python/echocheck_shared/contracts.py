from enum import Enum

from pydantic import BaseModel


class ProviderName(str, Enum):
    openai = "openai"
    gemini = "gemini"
    anthropic = "anthropic"


class SentimentLabel(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class MentionResult(BaseModel):
    provider: ProviderName
    brand_name: str
    mentioned: bool
    sentiment: SentimentLabel
    rationale: str
