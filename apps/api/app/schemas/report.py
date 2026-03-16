from pydantic import BaseModel, Field


class SentimentCounts(BaseModel):
    positive: int
    neutral: int
    negative: int


class ProviderReportItem(BaseModel):
    name: str
    mention_rate: float = Field(alias="mentionRate")


class WeeklyReportResponse(BaseModel):
    brand_id: str = Field(alias="brandId")
    mention_rate: float = Field(alias="mentionRate")
    sentiment: SentimentCounts
    providers: list[ProviderReportItem]
