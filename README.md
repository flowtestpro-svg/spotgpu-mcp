> **Discontinued Oct 2026: the SpotGPU API has been shut down. This package no longer works.**

# spotgpu-mcp

MCP (Model Context Protocol) server for [SpotGPU](https://spotgpu-api.fly.dev) spot GPU rental prices.

Exposes one tool: **`spot_price`** → `GET /v1/spot` (Vast + RunPod best + alts).

> **Credits ≠ rental.** SpotGPU API credits pay for price lookups.  
> **`usd_per_hr` is the upstream provider rental price**, not a SpotGPU fee.

<!-- mcp-name: io.github.flowtestpro-svg/spotgpu-mcp -->

## Install / run

Requires Python 3.10+ and a SpotGPU API key.

### Get an API key (free trial, 25 credits)

```bash
curl -X POST https://spotgpu-api.fly.dev/v1/keys
```

No auth, no email. The response contains `api_key` (shown **once** — store it) with 25 trial
credits (1 credit per successful lookup). Limit: 3 keys per IP per 24h. Put it in
`SPOTGPU_API_KEY` in your MCP client config. Check your balance:

```bash
curl -H "Authorization: Bearer $SPOTGPU_API_KEY" https://spotgpu-api.fly.dev/v1/account
```

### Out of credits (HTTP 402)

When credits run out the API returns **402 `insufficient_credits`** and the tool error points to
the top-up page. Buy a credit pack ($5 / 500, $10 / 1000, $50 / 5000) at
**https://spotgpu-api.fly.dev/topup**, or `POST /v1/checkout` with `{"pack_id": "credits_500"}`
and your Bearer key to get a Stripe Checkout URL. A 401 tool error includes the signup curl above.

### One-shot (PyPI)

```bash
uvx spotgpu-mcp
```

### Local (this monorepo package)

```bash
cd packages/mcp-spotgpu
uv sync   # or: pip install -e .
export SPOTGPU_API_KEY=sk_…
spotgpu-mcp
```

Env:

| Variable | Required | Default |
|----------|----------|---------|
| `SPOTGPU_API_KEY` | **yes** | — |
| `SPOTGPU_BASE_URL` | no | `https://spotgpu-api.fly.dev` |

Never hardcode keys. The server speaks MCP on **stdio** only (do not print to stdout).

## Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "spotgpu": {
      "command": "uvx",
      "args": ["spotgpu-mcp"],
      "env": {
        "SPOTGPU_API_KEY": "sk_…"
      }
    }
  }
}
```

Local editable install instead of `uvx`:

```json
{
  "mcpServers": {
    "spotgpu": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/spotgpu/packages/mcp-spotgpu", "spotgpu-mcp"],
      "env": {
        "SPOTGPU_API_KEY": "sk_…"
      }
    }
  }
}
```

## Cursor

Add to `.cursor/mcp.json` (or user MCP config):

```json
{
  "mcpServers": {
    "spotgpu": {
      "command": "uvx",
      "args": ["spotgpu-mcp"],
      "env": {
        "SPOTGPU_API_KEY": "sk_…"
      }
    }
  }
}
```

## Tool: `spot_price`

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `gpu` | string | required | e.g. `RTX_4090` |
| `qty` | int | `1` | ≥ 1 |
| `markets` | string | `"vast,runpod"` | comma-separated |
| `fresh` | bool | `false` | maps to `fresh=1` |

On success returns JSON text of the API body (`best.usd_per_hr`, `alts`, …).

## Attribution

Requests send `X-SpotGPU-Client: mcp-spotgpu`.


## Published

- PyPI: https://pypi.org/project/spotgpu-mcp/
- MCP Registry: `io.github.flowtestpro-svg/spotgpu-mcp`
- Glama: https://glama.ai/mcp/servers/flowtestpro-svg/spotgpu-mcp
- GitHub: https://github.com/flowtestpro-svg/spotgpu-mcp
