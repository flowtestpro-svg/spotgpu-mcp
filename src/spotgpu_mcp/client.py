"""Thin httpx client for SpotGPU GET /v1/spot. No app-internal imports."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://spotgpu-api.fly.dev"
CLIENT_HEADER = "mcp-spotgpu"
TIMEOUT_S = 60.0


def _signup_hint(base: str) -> str:
    return (
        f"Get a free trial key (25 credits, no auth/email): curl -X POST {base}/v1/keys "
        f"— then set SPOTGPU_API_KEY in your MCP client env. "
        f"Buy more credits at {base}/topup"
    )


class SpotGPUError(Exception):
    """Raised for API/config failures; message is safe for MCP tool errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _base_url() -> str:
    return (os.environ.get("SPOTGPU_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def _api_key() -> str:
    key = os.environ.get("SPOTGPU_API_KEY")
    if not key or not key.strip():
        raise SpotGPUError(
            "SPOTGPU_API_KEY not set. Set it in your MCP client env (Claude Desktop / Cursor). "
            + _signup_hint(_base_url())
        )
    return key.strip()


def _detail_snippet(body: Any) -> str:
    """Extract a short human detail without leaking secrets."""
    if body is None:
        return ""
    if isinstance(body, str):
        text = body.strip()
        return f" — {text[:300]}" if text else ""
    if isinstance(body, dict):
        for k in ("message", "detail", "error"):
            v = body.get(k)
            if isinstance(v, str) and v.strip():
                return f" — {v.strip()[:300]}"
            if isinstance(v, list) and v:
                return f" — {json.dumps(v)[:300]}"
        # FastAPI validation often nests under detail
        detail = body.get("detail")
        if detail is not None:
            try:
                return f" — {json.dumps(detail)[:300]}"
            except (TypeError, ValueError):
                return f" — {str(detail)[:300]}"
    try:
        return f" — {json.dumps(body)[:300]}"
    except (TypeError, ValueError):
        return ""


def _map_http_error(status: int, body: Any, base: str) -> SpotGPUError:
    if status == 401:
        return SpotGPUError(
            "Invalid or missing API key — check SPOTGPU_API_KEY"
            + _detail_snippet(body)
            + ". "
            + _signup_hint(base)
        )
    if status == 402:
        return SpotGPUError(
            f"Insufficient credits (HTTP 402) — buy a credit pack at {base}/topup "
            f"(or POST {base}/v1/checkout with your key)"
            + _detail_snippet(body)
        )
    if status == 404:
        return SpotGPUError(
            "No offers / unknown GPU" + _detail_snippet(body)
        )
    if status == 422:
        return SpotGPUError("Bad params" + _detail_snippet(body))
    if status in (502, 503):
        return SpotGPUError(
            "Upstream markets unavailable — retry later" + _detail_snippet(body)
        )
    return SpotGPUError(f"SpotGPU API HTTP {status}" + _detail_snippet(body))


def fetch_spot(
    *,
    gpu: str,
    qty: int = 1,
    markets: str = "vast,runpod",
    fresh: bool = False,
) -> dict[str, Any]:
    """
    GET {BASE}/v1/spot with Bearer auth.

    Maps fresh=True → query fresh=1. Returns parsed JSON body on 200.
    """
    base = _base_url()
    key = _api_key()
    params: dict[str, str | int] = {
        "gpu": gpu,
        "qty": qty,
        "markets": markets,
    }
    if fresh:
        params["fresh"] = 1

    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "X-SpotGPU-Client": CLIENT_HEADER,
    }
    url = f"{base}/v1/spot"

    try:
        with httpx.Client(timeout=TIMEOUT_S) as client:
            resp = client.get(url, params=params, headers=headers)
    except httpx.TimeoutException as exc:
        raise SpotGPUError("Connection failed to SpotGPU API (timeout)") from exc
    except httpx.RequestError as exc:
        raise SpotGPUError("Connection failed to SpotGPU API") from exc

    if resp.status_code == 200:
        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise SpotGPUError("SpotGPU API returned non-JSON body") from exc
        if not isinstance(data, dict):
            raise SpotGPUError("SpotGPU API returned unexpected JSON shape")
        return data

    body: Any
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = resp.text
    raise _map_http_error(resp.status_code, body, base)
