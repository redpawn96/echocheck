from pydantic import BaseModel, Field


class CheckoutSessionRequest(BaseModel):
    workspace_id: str = Field(alias="workspaceId")
    price_id: str = Field(alias="priceId")
    success_url: str = Field(alias="successUrl")
    cancel_url: str = Field(alias="cancelUrl")


class CheckoutSessionResponse(BaseModel):
    checkout_url: str = Field(alias="checkoutUrl")
    session_id: str = Field(alias="sessionId")
