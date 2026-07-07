#!/usr/bin/env python3
"""LLM provider registry and lightweight client helpers."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO_ROOT / ".coquery" / "llm_providers.json"
REGISTRY_ENV_VAR = "COQUERY_LLM_REGISTRY_PATH"
SUPPORTED_PROVIDER_KINDS = {"ollama", "openai_compatible"}
SUPPORTED_SQL_INTENTS = {"select", "count", "insert", "update", "delete"}

PROVIDER_PRESETS: dict[str, dict[str, Any]] = {
    "openai": {
        "label": "OpenAI",
        "kind": "openai_compatible",
        "base_url": "https://api.openai.com",
        "chat_completions_url": "https://api.openai.com/v1/chat/completions",
        "models_url": "https://api.openai.com/v1/models",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": None,
        "cost_profile": "balanced",
        "docs_url": "https://platform.openai.com/docs/api-reference/chat/create",
    },
    "groq": {
        "label": "Groq",
        "kind": "openai_compatible",
        "base_url": "https://api.groq.com/openai/v1",
        "chat_completions_url": "https://api.groq.com/openai/v1/chat/completions",
        "models_url": "https://api.groq.com/openai/v1/models",
        "api_key_env": "GROQ_API_KEY",
        "default_model": None,
        "cost_profile": "cheap_or_free",
        "docs_url": "https://console.groq.com/docs/openai",
    },
    "openrouter": {
        "label": "OpenRouter",
        "kind": "openai_compatible",
        "base_url": "https://openrouter.ai/api/v1",
        "chat_completions_url": "https://openrouter.ai/api/v1/chat/completions",
        "models_url": "https://openrouter.ai/api/v1/models",
        "api_key_env": "OPENROUTER_API_KEY",
        "default_model": None,
        "cost_profile": "free_or_cheap_router",
        "docs_url": "https://openrouter.ai/docs/quickstart",
    },
    "gemini": {
        "label": "Gemini API",
        "kind": "openai_compatible",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "chat_completions_url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "models_url": "https://generativelanguage.googleapis.com/v1beta/openai/models",
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-3.5-flash",
        "cost_profile": "free_or_low_cost",
        "docs_url": "https://ai.google.dev/gemini-api/docs/openai",
    },
    "deepseek": {
        "label": "DeepSeek",
        "kind": "openai_compatible",
        "base_url": "https://api.deepseek.com",
        "chat_completions_url": "https://api.deepseek.com/chat/completions",
        "models_url": "https://api.deepseek.com/models",
        "api_key_env": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-v4-flash",
        "cost_profile": "low_cost",
        "docs_url": "https://api-docs.deepseek.com/",
    },
}


class CoQueryLLMError(Exception):
    """Structured LLM/runtime error used by CLI handlers."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class LLMProviderProfile:
    """One repo-local LLM provider entry."""

    name: str
    kind: str
    model_name: str
    base_url: str
    api_key_env: Optional[str] = None
    preset: Optional[str] = None
    cost_profile: Optional[str] = None
    chat_completions_url: Optional[str] = None
    models_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMProviderProfile":
        return cls(
            name=str(data.get("name", "")).strip(),
            kind=str(data.get("kind", "")).strip(),
            model_name=str(data.get("model_name", "")).strip(),
            base_url=str(data.get("base_url", "")).strip(),
            api_key_env=(str(data["api_key_env"]).strip() if data.get("api_key_env") else None),
            preset=(str(data["preset"]).strip() if data.get("preset") else None),
            cost_profile=(str(data["cost_profile"]).strip() if data.get("cost_profile") else None),
            chat_completions_url=(
                str(data["chat_completions_url"]).strip() if data.get("chat_completions_url") else None
            ),
            models_url=(str(data["models_url"]).strip() if data.get("models_url") else None),
        )

    def normalized(self) -> "LLMProviderProfile":
        kind = self.kind.strip().lower()
        if kind not in SUPPORTED_PROVIDER_KINDS:
            raise CoQueryLLMError(
                "invalid_provider_kind",
                f"Unsupported provider kind: {self.kind}.",
            )

        if not self.name:
            raise CoQueryLLMError("missing_provider_name", "Provider name is required.")
        if not self.model_name:
            raise CoQueryLLMError("missing_model_name", "Model name is required.")

        base_url = self.base_url.strip()
        if kind == "ollama" and not base_url:
            base_url = "http://127.0.0.1:11434"
        chat_completions_url = (self.chat_completions_url or "").strip().rstrip("/") or None
        models_url = (self.models_url or "").strip().rstrip("/") or None
        if not base_url and not chat_completions_url:
            raise CoQueryLLMError("missing_base_url", "Base URL is required.")

        return LLMProviderProfile(
            name=self.name.strip(),
            kind=kind,
            model_name=self.model_name.strip(),
            base_url=base_url.rstrip("/"),
            api_key_env=self.api_key_env,
            preset=(self.preset.strip() if self.preset else None),
            cost_profile=(self.cost_profile.strip() if self.cost_profile else None),
            chat_completions_url=chat_completions_url,
            models_url=models_url,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LLMProviderRegistry:
    """Simple repo-local JSON registry for local/API-backed models."""

    def __init__(self, registry_path: str | None = None):
        env_path = os.environ.get(REGISTRY_ENV_VAR)
        self.path = Path(registry_path or env_path or DEFAULT_REGISTRY_PATH)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"providers": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def list_profiles(self) -> list[dict[str, Any]]:
        payload = self._load()
        profiles = [LLMProviderProfile.from_dict(item).normalized().to_dict() for item in payload.get("providers", [])]
        return sorted(profiles, key=lambda item: item["name"])

    def get_profile(self, name: str) -> LLMProviderProfile:
        normalized_name = (name or "").strip()
        if not normalized_name:
            raise CoQueryLLMError("missing_provider_name", "Provider name is required.")

        for item in self._load().get("providers", []):
            profile = LLMProviderProfile.from_dict(item).normalized()
            if profile.name == normalized_name:
                return profile

        raise CoQueryLLMError("provider_not_found", f"Provider not found: {normalized_name}.")

    def upsert_profile(
        self,
        name: str,
        kind: str,
        model_name: str,
        base_url: str,
        api_key_env: str | None = None,
        preset: str | None = None,
        cost_profile: str | None = None,
        chat_completions_url: str | None = None,
        models_url: str | None = None,
    ) -> dict[str, Any]:
        profile = LLMProviderProfile(
            name=name,
            kind=kind,
            model_name=model_name,
            base_url=base_url,
            api_key_env=api_key_env,
            preset=preset,
            cost_profile=cost_profile,
            chat_completions_url=chat_completions_url,
            models_url=models_url,
        ).normalized()

        payload = self._load()
        providers = []
        replaced = False
        for item in payload.get("providers", []):
            existing = LLMProviderProfile.from_dict(item).normalized()
            if existing.name == profile.name:
                providers.append(profile.to_dict())
                replaced = True
            else:
                providers.append(existing.to_dict())
        if not replaced:
            providers.append(profile.to_dict())

        payload["providers"] = sorted(providers, key=lambda item: item["name"])
        self._save(payload)
        return profile.to_dict()

    def remove_profile(self, name: str) -> dict[str, Any]:
        profile = self.get_profile(name)
        payload = self._load()
        payload["providers"] = [
            LLMProviderProfile.from_dict(item).normalized().to_dict()
            for item in payload.get("providers", [])
            if LLMProviderProfile.from_dict(item).normalized().name != profile.name
        ]
        self._save(payload)
        return profile.to_dict()


def list_provider_presets() -> list[dict[str, Any]]:
    """Return stable metadata for known provider presets."""

    presets: list[dict[str, Any]] = []
    for name, payload in PROVIDER_PRESETS.items():
        item = {"name": name, **payload}
        presets.append(item)
    return sorted(presets, key=lambda item: item["name"])


def get_provider_preset(name: str | None) -> dict[str, Any]:
    preset_name = (name or "").strip().lower()
    if not preset_name:
        raise CoQueryLLMError("missing_provider_preset", "Provider preset is required.")
    if preset_name not in PROVIDER_PRESETS:
        raise CoQueryLLMError("provider_preset_not_found", f"Provider preset not found: {preset_name}.")
    return {"name": preset_name, **PROVIDER_PRESETS[preset_name]}


def _decode_json_response(response: Any) -> dict[str, Any]:
    raw = response.read().decode("utf-8")
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CoQueryLLMError("provider_response_invalid", "Provider returned invalid JSON.") from exc


def _http_json(
    method: str,
    url: str,
    payload: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    timeout: int = 60,
) -> dict[str, Any]:
    request_headers = {"Accept": "application/json"}
    if payload is not None:
        request_headers["Content-Type"] = "application/json"
    request_headers.update(headers or {})

    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=data, headers=request_headers, method=method.upper())

    try:
        with urlopen(request, timeout=timeout) as response:
            return _decode_json_response(response)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        message = body.strip() or f"HTTP {exc.code}"
        raise CoQueryLLMError(
            "provider_request_failed",
            f"Provider request failed: {message}",
        ) from exc
    except URLError as exc:
        raise CoQueryLLMError(
            "provider_unreachable",
            f"Provider is unreachable: {exc.reason}.",
        ) from exc
    except TimeoutError as exc:
        raise CoQueryLLMError("provider_timeout", "Provider request timed out.") from exc


def _extract_json_object(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text[:-3].strip()

    decoder = json.JSONDecoder()
    start = text.find("{")
    while start != -1:
        try:
            parsed, _ = decoder.raw_decode(text[start:])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
        start = text.find("{", start + 1)

    raise CoQueryLLMError("provider_response_invalid", "Provider did not return a JSON object.")


def _llm_headers(profile: LLMProviderProfile) -> dict[str, str]:
    if not profile.api_key_env:
        return {}

    api_key = os.environ.get(profile.api_key_env)
    if not api_key:
        raise CoQueryLLMError(
            "missing_api_key",
            f"Environment variable {profile.api_key_env} is required for this provider.",
        )
    return {"Authorization": f"Bearer {api_key}"}


def _natural_sql_prompt(nl_text: str) -> str:
    return (
        "You are CoQuery's SQL drafting assistant. "
        "Return only one JSON object with keys intent, sql, confidence. "
        "intent must be one of select, count, insert, update, delete. "
        "confidence must be a number between 0 and 1. "
        "Do not use markdown. Prefer a safe SELECT if the request is ambiguous.\n"
        f"User request: {nl_text}"
    )


class LLMProviderClient:
    """Minimal HTTP client for Ollama and OpenAI-compatible APIs."""

    def __init__(self, profile: LLMProviderProfile):
        self.profile = profile.normalized()

    def _chat_completions_url(self) -> str:
        if self.profile.chat_completions_url:
            return self.profile.chat_completions_url
        return f"{self.profile.base_url}/v1/chat/completions"

    def _models_url(self) -> str:
        if self.profile.models_url:
            return self.profile.models_url
        return f"{self.profile.base_url}/v1/models"

    def list_remote_models(self) -> list[str]:
        if self.profile.kind == "ollama":
            payload = _http_json("GET", f"{self.profile.base_url}/api/tags")
            return [item.get("name") or item.get("model") for item in payload.get("models", []) if item.get("name") or item.get("model")]

        payload = _http_json(
            "GET",
            self._models_url(),
            headers=_llm_headers(self.profile),
        )
        return [item.get("id") for item in payload.get("data", []) if item.get("id")]

    def _ollama_generate(self, prompt: str) -> str:
        payload = _http_json(
            "POST",
            f"{self.profile.base_url}/api/generate",
            payload={
                "model": self.profile.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
        )
        return str(payload.get("response", "")).strip()

    def _openai_chat_completion(self, prompt: str) -> str:
        payload = _http_json(
            "POST",
            self._chat_completions_url(),
            payload={
                "model": self.profile.model_name,
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": "Return concise, exact answers only."},
                    {"role": "user", "content": prompt},
                ],
            },
            headers=_llm_headers(self.profile),
        )
        try:
            return str(payload["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise CoQueryLLMError(
                "provider_response_invalid",
                "OpenAI-compatible provider returned an unexpected chat completion payload.",
            ) from exc

    def complete_text(self, prompt: str) -> str:
        if self.profile.kind == "ollama":
            return self._ollama_generate(prompt)
        if self.profile.kind == "openai_compatible":
            return self._openai_chat_completion(prompt)
        raise CoQueryLLMError("invalid_provider_kind", f"Unsupported provider kind: {self.profile.kind}.")

    def test_connection(self) -> dict[str, Any]:
        remote_models: list[str] = []
        if self.profile.kind == "ollama":
            remote_models = self.list_remote_models()
            if remote_models and self.profile.model_name not in remote_models:
                raise CoQueryLLMError(
                    "model_not_found",
                    f"Ollama model not found: {self.profile.model_name}.",
                )

        response_text = self.complete_text("Return exactly the text OK.")
        return {
            "provider_name": self.profile.name,
            "kind": self.profile.kind,
            "model_name": self.profile.model_name,
            "base_url": self.profile.base_url,
            "remote_models": remote_models,
            "response_preview": response_text[:120],
        }

    def generate_structured_sql(self, nl_text: str) -> dict[str, Any]:
        response_text = self.complete_text(_natural_sql_prompt(nl_text))
        parsed = _extract_json_object(response_text)

        intent = str(parsed.get("intent", "select")).strip().lower()
        sql = str(parsed.get("sql", "")).strip()
        confidence_raw = parsed.get("confidence", 0.0)

        if intent not in SUPPORTED_SQL_INTENTS:
            raise CoQueryLLMError("provider_response_invalid", f"Unsupported SQL intent from provider: {intent}.")
        if not sql:
            raise CoQueryLLMError("provider_response_invalid", "Provider returned an empty SQL string.")

        try:
            confidence = max(0.0, min(1.0, float(confidence_raw)))
        except (TypeError, ValueError) as exc:
            raise CoQueryLLMError("provider_response_invalid", "Provider returned an invalid confidence value.") from exc

        return {
            "intent": intent,
            "sql": sql,
            "confidence": confidence,
            "provider_name": self.profile.name,
            "provider_kind": self.profile.kind,
            "model_name": self.profile.model_name,
        }
