"""SpotGPU MCP server (stdio only). Never write non-protocol bytes to stdout."""

from __future__ import annotations

import json
import logging
import sys

from mcp.server import MCPServer

from spotgpu_mcp.client import SpotGPUError, fetch_spot

# Stdio MCP: logging must go to stderr only
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("spotgpu_mcp")

mcp = MCPServer("spotgpu")


@mcp.tool()
def spot_price(
    gpu: str,
    qty: int = 1,
    markets: str = "vast,runpod",
    fresh: bool = False,
) -> str:
    """Get SpotGPU spot rental prices (best + alts) for a GPU type.

    Returns JSON from GET /v1/spot including best.usd_per_hr (upstream
    provider rental price, not a SpotGPU fee). Credits are for API calls,
    not GPU rental.

    Args:
        gpu: GPU type, e.g. RTX_4090, RTX_3090, RTX_A6000
        qty: Number of GPUs (>= 1). Default 1.
        markets: Comma-separated markets. Default "vast,runpod".
        fresh: If true, bypass cache (query fresh=1). Default false.
    """
    if qty < 1:
        raise SpotGPUError("Bad params — qty must be >= 1")
    try:
        data = fetch_spot(gpu=gpu, qty=qty, markets=markets, fresh=fresh)
    except SpotGPUError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface unexpected as tool error
        log.exception("spot_price unexpected failure")
        raise SpotGPUError(f"SpotGPU client error: {exc}") from exc
    return json.dumps(data, indent=2)


def main() -> None:
    """CLI entry: spotgpu-mcp — stdio transport only."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
