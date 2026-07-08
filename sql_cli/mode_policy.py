#!/usr/bin/env python3
"""Mode context and provider policy helpers for app-facing CoQuery flows."""

from __future__ import annotations

from typing import Any

from sql_cli.llm_registry import CoQueryLLMError, LLMProviderRegistry

TRAINING_MODE = "training"
PRODUCTION_ASSIST_MODE = "production_assist"

MODE_ALIASES = {
    "training": TRAINING_MODE,
    "train": TRAINING_MODE,
    "practice": TRAINING_MODE,
    "production": PRODUCTION_ASSIST_MODE,
    "production_assist": PRODUCTION_ASSIST_MODE,
    "assist": PRODUCTION_ASSIST_MODE,
}


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y", "on", "allow", "allowed"}


def normalize_app_mode(value: Any) -> str:
    text = str(value or TRAINING_MODE).strip().lower()
    return MODE_ALIASES.get(text, text or TRAINING_MODE)


def build_mode_context(
    *,
    mode: Any = None,
    allow_external_provider: Any = None,
    provider_policy: Any = None,
) -> dict[str, Any]:
    return {
        "mode": normalize_app_mode(mode),
        "allow_external_provider": coerce_bool(allow_external_provider),
        "provider_policy": str(provider_policy or "default"),
    }


def _provider_profile(provider_name: str | None) -> dict[str, Any] | None:
    if not provider_name:
        return None
    try:
        return LLMProviderRegistry().get_profile(provider_name).to_dict()
    except CoQueryLLMError as exc:
        if exc.code in {"missing_provider_name", "provider_not_found"}:
            return None
        raise


def provider_policy_block_result(
    command: str,
    provider_name: str | None,
    mode_context: dict[str, Any],
) -> dict[str, Any] | None:
    profile = _provider_profile(provider_name)
    if not profile:
        return None
    provider_kind = str(profile.get("kind") or "")
    if provider_kind == "ollama":
        return None
    if mode_context["mode"] != PRODUCTION_ASSIST_MODE or mode_context["allow_external_provider"]:
        return None

    message = "Production Assist Mode blocks external AI providers by default."
    return {
        "ok": False,
        "command": command,
        "data": {
            "mode_context": mode_context,
            "provider_name": provider_name,
            "provider_kind": provider_kind,
            "readable_message": message,
            "next_step": (
                "Switch to Training Mode, use a local/internal provider, or pass an explicit "
                "policy override with allow_external_provider=true."
            ),
            "security_boundary": (
                "Production Assist may include live schema or query intent; external provider use "
                "requires an explicit policy override."
            ),
        },
        "error": {
            "code": "production_external_provider_blocked",
            "message": message,
        },
    }
