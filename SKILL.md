---
name: oauth-coder-bridge
description: HTTP bridge server that routes OpenClaw's Anthropic API calls through oauth-coder (Claude CLI with OAuth tokens), enabling Claude usage without direct Anthropic API access. Transparently translates between Anthropic-messages API format and oauth-coder's CLI interface.
homepage: https://github.com/earlvanze/oauth-coder-bridge
---

# oauth-coder-bridge

HTTP bridge that enables OpenClaw to use [oauth-coder](https://github.com/codeninja/oauth-cli-coder) for Claude Code access.

**Upstream project:** [codeninja/oauth-cli-coder](https://github.com/codeninja/oauth-cli-coder)

This skill creates a local HTTP server that:
- Accepts Anthropic-messages API format on `localhost:8787`
- Translates requests to `oauth-coder ask claude ...` calls
- Returns Anthropic-compatible responses
- Maintains standard OpenClaw model routing

## Why?

- **Least detectable:** Uses the actual `claude` CLI binary with existing OAuth tokens
- **Zero API changes:** Existing OpenClaw workflows continue working
- **Transparent fallback:** Works alongside regular Anthropic provider

## Prerequisites

1. [oauth-coder](https://github.com/codeninja/oauth-cli-coder) installed and authenticated:
   ```bash
   # Authenticate
   claude login
   ```

2. `oauth-coder` binary on PATH or at a known location (auto-detected)

## Installation

```bash
# Run setup
bash scripts/setup.sh

# Start the bridge server
python3 ~/.openclaw/scripts/oauth-coder-bridge.py &

# Or use systemd auto-start
systemctl --user enable --now oauth-coder-bridge
```

## Usage

```bash
# Test the bridge
curl http://127.0.0.1:8787/health

# Set as OpenClaw model (after setup adds provider)
# Using alias:
openclaw models set claude
# Or full provider path:
openclaw models set claude-cli/claude-opus-4-6
```

## Available Models

After setup, the `claude-cli` provider is added to OpenClaw with these models:

- `claude-cli/claude-opus-4-6` (alias: `claude`)
- `claude-cli/claude-sonnet-4-6` (alias: `sonnet`)
- `claude-cli/claude-sonnet-4-5`

## How It Works

1. OpenClaw sends Anthropic-messages API request to `http://127.0.0.1:8787/v1/messages`
2. Bridge converts JSON → text prompt (sanitized/truncated)
3. Bridge spawns: `oauth-coder ask claude "<prompt>" --model <opus|sonnet|haiku> --close`
4. oauth-coder launches real `claude` CLI in tmux session
5. Response is captured and returned as Anthropic JSON

## Architecture

```
OpenClaw ──HTTP──▶ oauth-coder-bridge ──subprocess──▶ oauth-coder ──tmux──▶ claude CLI
     │                                                    │
     └────────────────── Anthropic API format ────────────┘
```

## Configuration

Environment variables (all optional):

| Variable | Default | Description |
|----------|---------|-------------|
| `OAUTH_CODER_BIN` | auto-detect | Path to oauth-coder binary |
| `OAUTH_CODER_BRIDGE_PORT` | 8787 | Bridge listen port |
| `OAUTH_CODER_BRIDGE_HOST` | 127.0.0.1 | Bridge bind address |
| `OAUTH_CODER_BRIDGE_TIMEOUT` | 300 | Request timeout (seconds) |
| `OAUTH_CODER_BRIDGE_MAX_SIZE` | 1048576 | Max request size (bytes) |
| `OAUTH_CODER_BRIDGE_MAX_PROMPT` | 100000 | Max prompt length (chars) |
| `OAUTH_CODER_BRIDGE_LOG_LEVEL` | INFO | Logging level |
| `OAUTH_CODER_BRIDGE_LOG_FILE` | (empty) | Log file path (stderr only if unset) |

## Security Notes

- The bridge passes prompts to the `oauth-coder`/`claude` CLI subprocess. Conversation text will be handled by that CLI.
- If `OAUTH_CODER_BRIDGE_LOG_FILE` is set, prompts/responses may be logged locally.
- The bridge binds to `127.0.0.1` by default (localhost only).
- Rate limiting: 30 requests/minute per client IP.
- Request size and prompt length are bounded.

## Troubleshooting

**Bridge not responding:**
```bash
curl http://127.0.0.1:8787/health
# Should return {"status": "ok"}
```

**oauth-coder not found:**
```bash
which oauth-coder
# If missing: install oauth-coder and ensure it's on PATH
# Or set: export OAUTH_CODER_BIN=/path/to/oauth-coder
```

**Claude auth expired:**
```bash
claude login  # Re-authenticate
```

**Session conflicts:**
```bash
oauth-coder stop-all  # Clear stuck tmux sessions
```

## Files

- `scripts/oauth-coder-bridge.py` — HTTP bridge server
- `scripts/setup.sh` — Install bridge and update OpenClaw config
- `scripts/update-openclaw-config.py` — Add provider to openclaw.json
- `references/oauth-coder-bridge.service` — systemd user service template

## License

MIT
