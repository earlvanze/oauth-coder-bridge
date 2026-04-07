#!/usr/bin/env python3
"""Update openclaw.json to add claude-cli provider for oauth-coder bridge."""

import json
import sys
from pathlib import Path

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

def main():
    if not CONFIG_PATH.exists():
        print(f"Error: {CONFIG_PATH} not found", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    # Ensure models.providers exists
    if "models" not in config:
        config["models"] = {}
    if "providers" not in config["models"]:
        config["models"]["providers"] = {}

    # Add claude-cli provider (uses oauth-coder bridge on localhost:8787)
    config["models"]["providers"]["claude-cli"] = {
        "baseUrl": "http://127.0.0.1:8787",
        "apiKey": "local-bridge-no-key-needed",
        "api": "anthropic-messages",
        "models": [
            {
                "id": "claude-opus-4-6",
                "name": "Claude Opus 4.6 (claude-cli)",
                "reasoning": True,
                "input": ["text"],
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "contextWindow": 200000,
                "maxTokens": 8192
            },
            {
                "id": "claude-sonnet-4-6",
                "name": "Claude Sonnet 4.6 (claude-cli)",
                "reasoning": True,
                "input": ["text"],
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "contextWindow": 200000,
                "maxTokens": 8192
            },
            {
                "id": "claude-sonnet-4-5",
                "name": "Claude Sonnet 4.5 (claude-cli)",
                "reasoning": True,
                "input": ["text"],
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "contextWindow": 200000,
                "maxTokens": 8192
            }
        ]
    }

    # Write updated config
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Updated {CONFIG_PATH}")
    print("Added claude-cli provider with models:")
    print("  - claude-cli/claude-opus-4-6")
    print("  - claude-cli/claude-sonnet-4-6")
    print("  - claude-cli/claude-sonnet-4-5")
    print("\nStart the bridge with: python3 ~/.openclaw/scripts/oauth-coder-bridge.py")

if __name__ == "__main__":
    main()
