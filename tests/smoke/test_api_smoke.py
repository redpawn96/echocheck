#!/usr/bin/env python3
"""End-to-end API smoke test for EchoCheck.

Flow:
1. Register user
2. Create workspace
3. Create brand
4. Queue GEO run
5. Read GEO run status
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest


@dataclass
class SmokeResult:
    register: dict
    workspace: dict
    brand: dict
    geo_run: dict
    geo_run_status: dict


def request_json(method: str, url: str, payload: dict | None = None, token: str | None = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = Request(url=url, data=data, headers=headers, method=method)

    try:
        with urlopen(req, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"{method} {url} failed: {exc.reason}") from exc


def run_smoke(base_url: str) -> SmokeResult:
    email = f"smoke_{uuid.uuid4().hex[:10]}@example.com"
    password = "TestPass123!"

    register = request_json(
        "POST",
        f"{base_url}/v1/auth/register",
        {"email": email, "password": password},
    )
    token = register["accessToken"]

    workspace = request_json(
        "POST",
        f"{base_url}/v1/workspaces",
        {"name": "Smoke Workspace"},
        token=token,
    )
    workspace_id = workspace["id"]

    brand = request_json(
        "POST",
        f"{base_url}/v1/brands",
        {
            "workspaceId": workspace_id,
            "name": "EchoCheck",
            "industry": "MarTech",
        },
        token=token,
    )
    brand_id = brand["id"]

    geo_run = request_json(
        "POST",
        f"{base_url}/v1/geo/runs",
        {
            "workspaceId": workspace_id,
            "brandId": brand_id,
            "industry": "MarTech",
            "providers": ["openai", "gemini"],
            "intents": ["best martech tools", "top geo monitoring tools"],
        },
        token=token,
    )
    run_id = geo_run["runId"]

    geo_run_status = request_json(
        "GET",
        f"{base_url}/v1/geo/runs/{run_id}",
        token=token,
    )

    return SmokeResult(
        register={"userId": register["user"]["id"], "email": register["user"]["email"]},
        workspace=workspace,
        brand=brand,
        geo_run=geo_run,
        geo_run_status=geo_run_status,
    )


@pytest.mark.smoke
def test_api_smoke_flow() -> None:
    base_url = os.getenv("SMOKE_BASE_URL", "http://localhost:8000").rstrip("/")
    result = run_smoke(base_url)

    assert result.register["userId"]
    assert result.workspace["id"]
    assert result.brand["id"]
    assert result.geo_run["status"] == "queued"
    assert result.geo_run_status["runId"] == result.geo_run["runId"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EchoCheck API smoke test")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    try:
        result = run_smoke(args.base_url.rstrip("/"))
    except Exception as exc:  # noqa: BLE001
        print(f"SMOKE_TEST_FAILED: {exc}", file=sys.stderr)
        return 1

    print("SMOKE_TEST_PASSED")
    print(
        json.dumps(
            {
                "register": result.register,
                "workspace": result.workspace,
                "brand": result.brand,
                "geoRun": result.geo_run,
                "geoRunStatus": result.geo_run_status,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
