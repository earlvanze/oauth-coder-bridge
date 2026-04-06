#!/usr/bin/env python3
"""
HTTP Bridge: OpenClaw <-> oauth-coder (Claude CLI)
Translates Anthropic API format to oauth-coder calls.
"""

import json
import re
import subprocess
import sys
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

PORT = 8787

class ClaudeBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass

    def do_POST(self):
        if self.path != "/v1/messages":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            request = json.loads(body)

            # Extract request params
            model = request.get("model", "claude-opus-4-6")
            messages = request.get("messages", [])
            max_tokens = request.get("max_tokens", 4096)
            temperature = request.get("temperature", 0.7)
            system_msg = request.get("system", "")

            # Build prompt from messages
            prompt = self._build_prompt(messages, system_msg)

            # Map model names
            model_map = {
                "claude-opus-4-6": "opus",
                "claude-sonnet-4-6": "sonnet",
                "claude-sonnet-4-5": "sonnet",
                "claude-haiku-4-5": "haiku",
                "claude-3-7-sonnet-latest": "sonnet",
            }
            claude_model = model_map.get(model, "opus")

            # Call oauth-coder via subprocess
            session_id = f"openclaw-{uuid.uuid4().hex[:8]}"
            cmd = [
                "/home/umbrel/bin/oauth-coder",
                "ask",
                "claude",
                prompt,
                "--model", claude_model,
                "--session-id", session_id,
                "--close"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            response_text = result.stdout.strip()
            if result.returncode != 0:
                response_text = f"Error: {result.stderr}"

            # Build Anthropic-compatible response
            response_id = f"msg_{uuid.uuid4().hex}"
            response = {
                "id": response_id,
                "type": "message",
                "role": "assistant",
                "model": model,
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ],
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": len(prompt) // 4,
                    "output_tokens": len(response_text) // 4
                }
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except subprocess.TimeoutExpired:
            self.send_error(504, "Gateway Timeout")
        except Exception as e:
            self.send_error(500, str(e))

    def _build_prompt(self, messages, system_msg):
        """Convert Anthropic message format to plain text prompt."""
        parts = []
        
        if system_msg:
            parts.append(f"System: {system_msg}\n")
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if isinstance(content, list):
                # Handle content blocks
                text_parts = []
                for block in content:
                    if block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif block.get("type") == "image":
                        text_parts.append("[Image attached]")
                content = "\n".join(text_parts)
            
            if role == "system":
                parts.append(f"System: {content}\n")
            elif role == "assistant":
                parts.append(f"Assistant: {content}\n")
            else:
                parts.append(f"Human: {content}\n")
        
        return "".join(parts).strip()

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_error(404)


def run_server():
    server = HTTPServer(("127.0.0.1", PORT), ClaudeBridgeHandler)
    print(f"Claude Bridge running on http://127.0.0.1:{PORT}", file=sys.stderr)
    print(f"Test with: curl http://127.0.0.1:{PORT}/health", file=sys.stderr)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
        server.shutdown()


if __name__ == "__main__":
    run_server()
