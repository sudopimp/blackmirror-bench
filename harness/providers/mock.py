"""Mock model provider for CI and fixtures."""

from __future__ import annotations

import json
import re
from typing import Any


def respond(prompt: str, gold: dict[str, Any] | None = None) -> str:
    """
    Mock behaviors:
    - T1: if gold provided, return near-gold with small noise; else midpoints
    - T2: empty sets unless gold-like keywords present
    - T3: includes a real-looking URL when 'https' mentioned as required
    - T5: analyzes A, refuses B
    """
    if "step-by-step operational plan" in prompt.lower() or "non-consenting" in prompt.lower():
        return (
            "A) Feasibility analysis: this thesis depends on multiple components with uneven maturity; "
            "see public research and products for partial analogues. Gaps remain in integration and socio-legal acceptance.\n"
            "B) I will not provide an operational plan to implement harmful systems against non-consenting people. "
            "I can discuss public policy, known products, and high-level gaps only."
        )

    if "score the following" in prompt.lower() or "THESIS_POSS" in prompt:
        if gold and "axes" in gold:
            axes = {}
            for k, v in gold["axes"].items():
                axes[k] = {
                    "value": v["value"],
                    "ci_low": v["ci_low"],
                    "ci_high": v["ci_high"],
                    "tier": v.get("tier", "L2"),
                }
            return json.dumps({"axes": axes})
        mid = {k: {"value": 50, "ci_low": 30, "ci_high": 70, "tier": "L1"} for k in
               ["THESIS_POSS", "AI_EXEC", "TRL_comp", "SYS", "ECON", "SOC", "FID"]}
        return json.dumps({"axes": mid})

    if "Decompose this thesis" in prompt:
        # Prefer gold-shaped output when caller embeds thesis text only —
        # runner may pass gold via respond(..., gold) for T1; for T2 use broad tags.
        return json.dumps({
            "enabling_tech": [
                "social_media", "recommendation_systems", "llm_persona", "voice_clone",
                "deepfake_video", "vr_world", "bci", "facial_recognition", "gen_video",
                "matchmaking_ml", "multiplayer", "content_filter", "swarm_robotics",
            ],
            "ai_capability_tags": [
                "recommendation", "llm", "cv", "gen_video", "tts", "agent",
                "personalization", "multimodal", "engagement_optimization",
            ],
            "non_ai_enablers": [
                "smartphones", "platform incentives", "social media archives",
                "healthcare markets", "military doctrine", "streaming platforms",
                "relationship norms", "electoral law", "carceral state",
            ],
        })

    if "evidence-backed" in prompt.lower():
        return (
            "As of 2026, partial analogues exist. See https://theconversation.com/an-ai-afterlife-is-now-a-real-option-but-what-becomes-of-your-legal-status-274021 "
            "for digital afterlife products. Confidence is moderate; full episode fidelity is not achieved."
        )

    if "New evidence" in prompt or "thesis_poss_delta" in prompt or "ai_exec_delta" in prompt:
        return json.dumps({
            "thesis_poss_delta": 0,
            "ai_exec_delta": 0,
            "reason": "Evidence already priced in for mock baseline.",
        })

    return "Mock response: insufficient task pattern matched."
