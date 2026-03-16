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

- Error responses:
  - 402: {"detail": "Active subscription required"}
  - 429: {"detail": "Monthly quota exceeded"}

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

## GEO Expansion (Proposed)
See docs/geo-expansion-contracts.md for shared contract definitions and docs/visibility-graph-v1-spec.md for the next delivery slice.

- GET /v1/geo/visibility?workspaceId={id}&brandId={id}&range=4w|12w&providers=openai,gemini&competitorIds=id1,id2
- Proposed response shape:
  {
    "workspaceId": "uuid",
    "brandId": "uuid",
    "range": "4w",
    "series": [
      {
        "entityType": "brand",
        "entityId": "uuid",
        "entityLabel": "EchoCheck",
        "provider": "openai",
        "points": [
          {
            "weekStart": "2026-03-02",
            "visibilityRate": 0.42,
            "sampleCount": 24,
            "deltaVsPreviousWeek": 0.05,
            "confidence": "medium"
          }
        ]
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

- GET /v1/billing/usage?workspaceId={id}
- Header: Authorization: Bearer <token>
- Response:
  {
    "workspaceId": "uuid",
    "month": "2026-03",
    "subscriptionStatus": "active|inactive|pending",
    "monthlyQuota": 100,
    "used": 12,
    "remaining": 88
  }
