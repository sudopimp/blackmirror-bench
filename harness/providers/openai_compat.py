"""Generic OpenAI-compatible chat completions provider."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

# Reuse system prompts from xai for track consistency
from harness.providers.xai import SYSTEM_PROMPTS


def chat(
    prompt: str,
    *,
    track: str = "T1",
    model: str,
    base_url: str,
    api_key: str,
    temperature: float = 0.1,
    max_tokens: int = 2048,
    retries: int = 4,
    extra_headers: dict[str, str] | None = None,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    system = SYSTEM_PROMPTS.get(track, SYSTEM_PROMPTS["T1"])
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            choices = body.get("choices") or []
            if not choices:
                raise RuntimeError(f"empty choices: {body!r}"[:500])
            msg = choices[0].get("message") or {}
            content = msg.get("content") or ""
            # MiniMax sometimes returns list content parts
            if isinstance(content, list):
                content = "".join(
                    (p.get("text") if isinstance(p, dict) else str(p)) for p in content
                )
            # Strip MiniMax thinking blocks if present
            if "</think>" in content:
                content = content.split("</think>", 1)[-1].strip()
            return str(content).strip()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:800]
            last_err = RuntimeError(f"HTTP {e.code}: {err_body}")
            if e.code in (429, 500, 502, 503, 504) and attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise last_err from e
        except Exception as e:
            last_err = e
            if attempt + 1 < retries:
                time.sleep(1.2 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"chat failed: {last_err}")


def resolve_minimax_key() -> str:
    key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("M3_API_KEY")
    if not key:
        raise RuntimeError("Set MINIMAX_API_KEY or M3_API_KEY")
    return key.strip()


def resolve_zai_key() -> str:
    key = os.environ.get("ZAI_API_KEY") or os.environ.get("Z_AI_API_KEY") or os.environ.get("ZHIPU_API_KEY")
    if not key:
        raise RuntimeError("Set ZAI_API_KEY")
    return key.strip()


def chat_minimax(prompt: str, *, track: str = "T1", model: str = "MiniMax-M3") -> str:
    return chat(
        prompt,
        track=track,
        model=model,
        base_url=os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.io/v1"),
        api_key=resolve_minimax_key(),
    )


def chat_zai(prompt: str, *, track: str = "T1", model: str = "glm-4.5") -> str:
    # Z.AI / BigModel OpenAI-ish path under /api/paas/v4
    base = os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/paas/v4")
    return chat(
        prompt,
        track=track,
        model=model,
        base_url=base,
        api_key=resolve_zai_key(),
    )
