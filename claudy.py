#!/usr/bin/env python3
"""
claudy.py - Streaming Claude shell assistant
Uses only stdlib. Streams command suggestions token-by-token.
"""

import json
import os
import platform
import sys
from pathlib import Path

SHELL_HISTORY_CTX_LINES = 200


def get_recent_commands():
    """Get the most recent n unique commands from zsh history."""
    history_file = Path.home() / ".zsh_history"
    if not history_file.exists():
        return []

    try:
        with open(history_file, encoding="utf-8", errors="ignore") as f:
            # Read last 4x ctx lines to ensure we get ctx unique commands
            lines = f.readlines()[-SHELL_HISTORY_CTX_LINES * 4 :]
    except (OSError, UnicodeDecodeError):
        return []

    # Parse zsh history format and get unique commands
    commands = []
    seen = set()

    for line in reversed(lines):  # Process most recent first
        line = line.strip()
        if line.startswith(": "):
            # Extended format: ": timestamp:0;command"
            parts = line.split(";", 1)
            if len(parts) == 2:
                cmd = parts[1]
                # Filter out short commands (less signal) and claudy itself
                if "claudy" not in cmd and len(cmd) >= 4 and cmd not in seen:
                    seen.add(cmd)
                    commands.append(cmd)
        elif line and "claudy" not in line and len(line) >= 4 and line not in seen:
            seen.add(line)
            commands.append(line)

        if len(commands) >= SHELL_HISTORY_CTX_LINES:
            break

    return commands


def stream_claude_suggestion(context, prompt, api_key):
    """Stream command suggestion from Claude token-by-token."""
    # System info
    system_type = platform.system()
    if system_type == "Darwin":
        system_info = f"OS: macOS {platform.mac_ver()[0]}, Shell: {os.environ.get('SHELL', 'unknown')}"
    else:
        system_info = f"OS: {system_type} {platform.release()}, Shell: {os.environ.get('SHELL', 'unknown')}"

    # Prepare context
    history_context = "\n".join(f"- {cmd}" for cmd in context)

    # Load additional context from ~/.claudy-prompt if it exists
    additional_context = ""
    custom_context_file = Path.home() / ".claudy-prompt"
    if custom_context_file.exists():
        try:
            with open(custom_context_file, encoding="utf-8") as f:
                additional_context = "\n\nAdditional context:\n" + f.read().strip()
        except OSError:
            pass

    request_data = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 500,
        "temperature": 0.3,
        "stream": True,
        "system": "You are a shell command assistant. Based on the user's command history and request, suggest ONE relevant shell command. Return ONLY the command, no explanation or markdown. It's critical that the command works on the user's system, so consider the system information when constructing commands.",
        "messages": [
            {
                "role": "user",
                "content": f"System: {system_info}\n\nRecent commands:\n{history_context}{additional_context}\n\nUser request: {prompt}\n\nProvide exactly ONE command:",
            }
        ],
    }

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    try:
        import urllib.request

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(request_data).encode("utf-8"),
            headers=headers,
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            # Read SSE stream line by line
            for line in response:
                line = line.decode("utf-8").strip()

                # SSE format: "data: {...}"
                if line.startswith("data: "):
                    data_str = line[6:]  # Remove "data: " prefix

                    # Handle special cases
                    if data_str == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)

                        # Extract text deltas
                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                text = delta.get("text", "")
                                if text:
                                    # Output each token immediately
                                    print(text, end="", flush=True)
                    except json.JSONDecodeError:
                        continue

        # End with newline
        print()

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: claudy.py <query>", file=sys.stderr)
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Get recent commands as context
    recent_commands = get_recent_commands()

    # Stream suggestion from Claude
    stream_claude_suggestion(recent_commands, query, api_key)


if __name__ == "__main__":
    main()
