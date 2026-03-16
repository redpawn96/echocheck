# API Contracts (Initial)

## Health
- GET /health
- Response: {"status": "ok"}

## Auth
- POST /v1/auth/register
- Payload:
  {
    "email": "user@example.com",
    "password": "strong-password"
  }
- Response:
  {
    "accessToken": "jwt",
    "tokenType": "bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com"
    }
  }

- POST /v1/auth/login
- Payload:
  {
    "email": "user@example.com",
    "password": "strong-password"
  }

- GET /v1/auth/me
- Header: Authorization: Bearer <token>

## GEO Run
- POST /v1/geo/runs
- Payload:
  {
    "workspaceId": "uuid",
    "brandId": "uuid",
    "industry": "string",
    "providers": ["openai", "gemini", "anthropic"],
    "intents": ["best tool for x", "top solutions for x"]
  }
- Response:
  {
    "runId": "uuid",
    "status": "queued"
  }

## Workspaces
- POST /v1/workspaces
- Header: Authorization: Bearer <token>
- Payload:
  {
    "name": "Acme Marketing"
  }

- GET /v1/workspaces
- Header: Authorization: Bearer <token>

## Brands
- POST /v1/brands
- Header: Authorization: Bearer <token>
- Payload:
  {
    "workspaceId": "uuid",
    "name": "Acme",
    "industry": "MarTech"
  }

- GET /v1/brands?workspace_id={id}
- Header: Authorization: Bearer <token>

## GEO Run Status
- GET /v1/geo/runs/{runId}
- Response:
  {
    "runId": "uuid",
    "status": "queued|running|completed|failed",
    "startedAt": "iso8601|null",
    "finishedAt": "iso8601|null"
  }

## Weekly Report
- GET /v1/reports/weekly?brandId={id}
- Response:
  {
    "brandId": "uuid",
    "mentionRate": 0.0,
    "sentiment": {
      "positive": 0,
      "neutral": 0,
      "negative": 0
    },
    "providers": [
      {
        "name": "openai",
        "mentionRate": 0.0
      }
    ]
  }

## Billing
- POST /v1/billing/checkout-session
- Header: Authorization: Bearer <token>
- Payload:
  {
    "workspaceId": "uuid",
    "priceId": "price_123",
    "successUrl": "https://example.com/success",
    "cancelUrl": "https://example.com/cancel"
  }

- POST /v1/billing/webhook
- Header: Stripe-Signature
