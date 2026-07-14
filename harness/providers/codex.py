"""ChatGPT OAuth Codex provider via chatgpt.com/backend-api/codex/responses.

Uses tokens from ~/.codex/auth.json (auth_mode=chatgpt). The endpoint requires:
  - stream: true
  - input: list of message items (not a bare string)
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from harness.providers.xai import SYSTEM_PROMPTS

DEFAULT_BASE = "https://chatgpt.com/backend-api/codex"
DEFAULT_MODEL = "gpt-5.6-sol"
AUTH_PATH = Path.home() / ".codex" / "auth.json"


def _load_auth() -> dict[str, Any]:
    if not AUTH_PATH.exists():
        raise RuntimeError(f"Missing Codex auth at {AUTH_PATH} (run `codex login`)")
    data = json.loads(AUTH_PATH.read_text())
    tokens = data.get("tokens") or {}
    access = tokens.get("access_token")
    account_id = tokens.get("account_id")
    if not access:
        raise RuntimeError("Codex auth.json has no access_token")
    if not account_id:
        raise RuntimeError("Codex auth.json has no account_id")
    return {
        "access_token": access,
        "account_id": account_id,
        "refresh_token": tokens.get("refresh_token"),
        "auth_mode": data.get("auth_mode"),
    }


def resolve_model(model: str | None = None) -> str:
    return (
        model
        or os.environ.get("CODEX_MODEL")
        or DEFAULT_MODEL
    ).strip()


def _parse_sse_text(raw: str) -> str:
    """Extract assistant text from Responses API SSE stream."""
    texts: list[str] = []
    final_text = ""
    for line in raw.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            ev = json.loads(payload)
        except json.JSONDecodeError:
            continue
        et = ev.get("type") or ""
        # Incremental deltas
        if et in (
            "response.output_text.delta",
            "response.content_part.delta",
            "response.output_item.delta",
        ):
            delta = ev.get("delta")
            if isinstance(delta, str):
                texts.append(delta)
            elif isinstance(delta, dict):
                t = delta.get("text") or delta.get("content")
                if isinstance(t, str):
                    texts.append(t)
        # Completed output item with full text
        if et == "response.output_item.done":
            item = ev.get("item") or {}
            if item.get("type") == "message":
                for part in item.get("content") or []:
                    if isinstance(part, dict) and part.get("type") in (
                        "output_text",
                        "text",
                    ):
                        t = part.get("text") or ""
                        if t:
                            final_text = t
        if et == "response.completed":
            resp = ev.get("response") or {}
            for item in resp.get("output") or []:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "message":
                    for part in item.get("content") or []:
                        if isinstance(part, dict) and part.get("type") in (
                            "output_text",
                            "text",
                        ):
                            t = part.get("text") or ""
                            if t:
                                final_text = t
    if final_text:
        return final_text.strip()
    return "".join(texts).strip()


def chat(
    prompt: str,
    *,
    track: str = "T1",
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 2048,
    retries: int = 4,
    reasoning_effort: str | None = None,
) -> str:
    auth = _load_auth()
    model_name = resolve_model(model)
    system = SYSTEM_PROMPTS.get(track, SYSTEM_PROMPTS["T1"])
    effort = (
        reasoning_effort
        or os.environ.get("CODEX_REASONING_EFFORT")
        or "max"
    )

    # Responses API (Codex ChatGPT path): input MUST be a list; stream MUST be true.
    user_content = f"{system}\n\n---\n\n{prompt}"
    # ChatGPT Codex path is strict: stream=true, input=list, no temp/max_tokens.
    payload: dict[str, Any] = {
        "model": model_name,
        "stream": True,
        "store": False,
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": user_content},
                ],
            }
        ],
    }
    # Reasoning effort when model supports it
    if effort and effort != "none":
        payload["reasoning"] = {"effort": effort}
    _ = (temperature, max_tokens)  # API symmetry only

    url = (
        os.environ.get("CODEX_BASE_URL", DEFAULT_BASE).rstrip("/")
        + "/responses"
    )
    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "ChatGPT-Account-Id": auth["account_id"],
        "OpenAI-Beta": "responses=experimental",
    }

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            text = _parse_sse_text(raw)
            if not text:
                # Keep a short raw snippet for debugging empty parses
                raise RuntimeError(
                    f"empty codex response (raw head): {raw[:400]!r}"
                )
            return text
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:800]
            last_err = RuntimeError(f"HTTP {e.code}: {err_body}")
            if e.code in (401, 403):
                raise last_err from e
            if e.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                time.sleep(2.0 * (attempt + 1))
                continue
            raise last_err from e
        except Exception as e:
            last_err = e
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"codex chat failed: {last_err}")
