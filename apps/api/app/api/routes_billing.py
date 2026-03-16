from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
import stripe

from app.api.dependencies import get_current_user
from app.api.routes_workspaces import assert_workspace_owner
from app.core.config import settings
from app.db.models import Subscription, User
from app.db.session import get_db
from app.schemas.billing import CheckoutSessionRequest, CheckoutSessionResponse

router = APIRouter(prefix="/v1/billing", tags=["billing"])

stripe.api_key = settings.stripe_secret_key


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    payload: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CheckoutSessionResponse:
    workspace = assert_workspace_owner(db, payload.workspace_id, current_user.id)

    subscription = db.query(Subscription).filter(Subscription.workspace_id == workspace.id).first()
    if subscription is None:
        subscription = Subscription(workspace_id=workspace.id, status="pending")
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": payload.price_id, "quantity": 1}],
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
        client_reference_id=workspace.id,
        metadata={"workspace_id": workspace.id},
    )

    return CheckoutSessionResponse(checkoutUrl=session.url, sessionId=session.id)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Webhook not configured")

    if stripe_signature is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Stripe-Signature")

    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, settings.stripe_webhook_secret)
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature") from exc

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        workspace_id = data.get("metadata", {}).get("workspace_id")
        subscription = db.query(Subscription).filter(Subscription.workspace_id == workspace_id).first()
        if subscription:
            subscription.status = "active"
            subscription.stripe_customer_id = data.get("customer")
            subscription.stripe_subscription_id = data.get("subscription")
            subscription.monthly_quota = 100
            db.add(subscription)
            db.commit()

    return {"received": True}
