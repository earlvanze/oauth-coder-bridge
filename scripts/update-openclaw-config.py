#!/usr/bin/env python3
"""Update openclaw.json to add oauth-coder anthropic provider."""

import json
import sys
from pathlib import Path

CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

def main():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    # Ensure models.providers exists
    if "models" not in config:
        config["models"] = {}
    if "providers" not in config["models"]:
        config["models"]["providers"] = {}

    # Add oauth-coder-anthropic provider
    config["models"]["providers"]["oauth-coder-anthropic"] = {
        "baseUrl": "http://127.0.0.1:8787",
        "apiKey": "local-bridge-no-key-needed",
        "api": "anthropic-messages",
        "models": [
            {
                "id": "claude-opus-4-6",
                "name": "Claude Opus 4.6 (oauth-coder)",
                "reasoning": True,
                "input": ["text"],
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "contextWindow": 200000,
                "maxTokens": 8192
            },
            {
                "id": "claude-sonnet-4-6",
                "name": "Claude Sonnet 4.6 (oauth-coder)",
                "reasoning": True,
                "input": ["text"],
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "contextWindow": 200000,
                "maxTokens": 8192
            },
            {
                "id": "claude-sonnet-4-5",
                "name": "Claude Sonnet 4.5 (oauth-coder)",
                "reasoning": True,
                "input": ["text"],
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "contextWindow": 200000,
                "maxTokens": 8192
            }
        ]
    }

    # Add aliases for these models
    if "agents" not in config:
        config["agents"] = {}
    if "defaults" not in config["agents"]:
        config["agents"]["defaults"] = {}
    if "models" not in config["agents"]["defaults"]:
        config["agents"]["defaults"]["models"] = {}

    defaults = config["agents"]["defaults"]["models"]
    
    # Add aliases for oauth-coder models
    defaults["oauth-coder-anthropic/claude-opus-4-6"] = {"alias": "claude"}
    defaults["oauth-coder-anthropic/claude-sonnet-4-6"] = {"alias": "sonnet"}

    # Update fallbacks to include oauth-coder versions alongside regular anthropic
    if "model" not in config["agents"]["defaults"]:
        config["agents"]["defaults"]["model"] = {}
    
    fallbacks = config["agents"]["defaults"]["model"].get("fallbacks", [])
    
    # Insert oauth-coder anthropic fallbacks after regular anthropic ones
    new_fallbacks = []
    for fb in fallbacks:
        new_fallbacks.append(fb)
        # After each anthropic fallback, add oauth-coder equivalent
        if fb.startswith("anthropic/"):
            model_name = fb.split("/")[1]
            oauth_fb = f"oauth-coder-anthropic/{model_name}"
            if oauth_fb not in fallbacks:
                new_fallbacks.append(oauth_fb)
    
    # Add any oauth-coder fallbacks that weren't already there
    oauth_fallbacks = [
        "oauth-coder-anthropic/claude-opus-4-6",
        "oauth-coder-anthropic/claude-sonnet-4-6",
        "oauth-coder-anthropic/claude-sonnet-4-5"
    ]
    for ofb in oauth_fallbacks:
        if ofb not in new_fallbacks:
            new_fallbacks.append(ofb)
    
    config["agents"]["defaults"]["model"]["fallbacks"] = new_fallbacks

    # Write updated config
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Updated {CONFIG_PATH}")
    print("Added oauth-coder-anthropic provider with models:")
    print("  - oauth-coder-anthropic/claude-opus-4-6 (alias: claude)")
    print("  - oauth-coder-anthropic/claude-sonnet-4-6 (alias: sonnet)")
    print("  - oauth-coder-anthropic/claude-sonnet-4-5")
    print("\nStart the bridge with: python3 ~/.openclaw/scripts/oauth-coder-bridge.py")

if __name__ == "__main__":
    main()
