# spotgpu-mcp

MCP (Model Context Protocol) server for [SpotGPU](https://spotgpu-api.fly.dev) spot GPU rental prices.

Exposes one tool: **`spot_price`** → `GET /v1/spot` (Vast + RunPod best + alts).

> **Credits ≠ rental.** SpotGPU API credits pay for price lookups.  
> **`usd_per_hr` is the upstream provider rental price**, not a SpotGPU fee.

<!-- mcp-name: io.github.flowtestpro-svg/spotgpu-mcp -->

## Install / run

Requires Python 3.10+ and a SpotGPU API key (`sk_…` from https://spotgpu-api.fly.dev).

### One-shot (after PyPI publish)

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

## Not published yet

PyPI / Official MCP Registry / Smithery / Glama publish is deferred until Biz Bot approval. `server.json` and `glama.json` stubs are in this package for later.
