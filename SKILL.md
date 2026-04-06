---
name: oauth-coder-bridge
description: HTTP bridge server that routes OpenClaw's Anthropic API calls through oauth-cli-coder, enabling Claude Code usage via the official CLI without direct Anthropic API access. Transparently translates between Anthropic-messages API format and oauth-coder's tmux-based CLI interface.
homepage: https://github.com/codeninja/oauth-cli-coder
---

# oauth-coder-bridge

HTTP bridge that enables OpenClaw to use [oauth-cli-coder](https://github.com/codeninja/oauth-cli-coder) for Claude Code access.

**Upstream project:** [codeninja/oauth-cli-coder](https://github.com/codeninja/oauth-cli-coder)

This skill creates a local HTTP server that:
- Accepts Anthropic-messages API format on `localhost:8787`
- Translates requests to `oauth-coder ask claude ...` calls
- Returns Anthropic-compatible responses
- Maintains standard OpenClaw model routing (`anthropic/claude-*`)

## Why?

- **Least detectable:** Uses the actual `claude` CLI binary with existing OAuth tokens
- **Zero API changes:** Existing OpenClaw workflows continue working
- **Transparent fallback:** Works alongside regular Anthropic provider

## Prerequisites

1. [oauth-cli-coder](https://github.com/codeninja/oauth-cli-coder) installed and authenticated:
   ```bash
   # Via oauth-coder-claude skill
   bash ~/.openclaw/skills/oauth-coder-claude/scripts/setup.sh
   # Authenticate: claude login
   ```

2. `oauth-coder` binary in `~/bin/`

## Installation

```bash
# Copy skill to workspace
bash scripts/setup.sh

# Start the bridge server
python3 scripts/oauth-coder-bridge.py &

# Or use systemd auto-start
systemctl --user enable --now oauth-coder-bridge
```

## Usage

```bash
# Test the bridge
curl http://127.0.0.1:8787/health

# Set as OpenClaw model
openclaw models set oauth-coder-anthropic/claude-opus-4-6
# Or use alias
openclaw models set claude
```

## Available Models

- `oauth-coder-anthropic/claude-opus-4-6` (alias: `claude`)
- `oauth-coder-anthropic/claude-sonnet-4-6` (alias: `sonnet`)
- `oauth-coder-anthropic/claude-sonnet-4-5`
- `oauth-coder-anthropic/claude-haiku-4-5`

## How It Works

1. OpenClaw sends Anthropic-messages API request to `http://127.0.0.1:8787/v1/messages`
2. Bridge converts JSON → text prompt
3. Bridge spawns: `oauth-coder ask claude "<prompt>" --model <opus|sonnet|haiku> --close`
4. oauth-coder launches real `claude` CLI in tmux session
5. Response is captured and returned as Anthropic JSON

## Architecture

```
OpenClaw ──HTTP──▶ oauth-coder-bridge ──subprocess──▶ oauth-coder ──tmux──▶ claude CLI
     │                                                    │
     └────────────────── Anthropic API format ────────────┘
                          (from Anthropic's perspective:
                           requests come from official CLI)
```

## Troubleshooting

**Bridge not responding:**
```bash
curl http://127.0.0.1:8787/health
# Should return {"status": "ok"}
```

**oauth-coder not found:**
```bash
which oauth-coder
# Expected: /home/user/bin/oauth-coder
# If missing: run oauth-coder-claude setup
```

**Claude auth expired:**
```bash
claude login  # Re-authenticate
```

**Session conflicts:**
```bash
# Clear stuck tmux sessions
~/.local/share/oauth-cli-coder-venv/bin/oauth-coder stop-all
```

## Files

- `scripts/oauth-coder-bridge.py` — HTTP bridge server
- `scripts/setup.sh` — Install bridge and update OpenClaw config
- `scripts/update-openclaw-config.py` — Add provider to openclaw.json
- `references/oauth-coder-bridge.service` — systemd service template

## License

Same as oauth-cli-coder (MIT-compatible). See upstream repo for details.
