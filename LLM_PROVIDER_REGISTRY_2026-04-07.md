# CoQuery LLM Provider Registry

Date: 2026-04-07

Workspace: `/Users/Agent/ps-workspace/CoQuery`

## Purpose

Add one small provider registry for local models and OpenAI-compatible API endpoints without changing the DB command contracts.

This slice exists so CoQuery can:

- register local Ollama models
- register OpenAI-compatible API endpoints
- test provider connectivity before using them
- route the `natural` command through a selected provider when requested

## Registry contract

Default repo-local path:

- `.coquery/llm_providers.json`

Override for tests or smoke:

- `COQUERY_LLM_REGISTRY_PATH`

Supported provider kinds:

- `ollama`
- `openai_compatible`

Stored fields per provider:

- `name`
- `kind`
- `model_name`
- `base_url`
- `api_key_env`

## CLI commands

Register or update a provider:

```bash
python3 main.py --command provider_add \
  --provider-name local_ollama \
  --provider-kind ollama \
  --base-url http://127.0.0.1:11434 \
  --model-name qwen3.5:4b-nvfp4
```

List providers:

```bash
python3 main.py --command provider_list
```

Test one provider:

```bash
python3 main.py --command provider_test --provider-name local_ollama
```

Use a registered provider for `natural`:

```bash
python3 main.py --command natural \
  --provider-name local_ollama \
  --sql "count users"
```

## OpenAI-compatible endpoint example

```bash
python3 main.py --command provider_add \
  --provider-name remote_api \
  --provider-kind openai_compatible \
  --base-url http://127.0.0.1:8000 \
  --model-name gpt-oss-20b \
  --api-key-env OPENAI_COMPAT_API_KEY
```

Notes:

- the registry stores only the environment variable name, not the secret
- the endpoint is expected to support `/v1/chat/completions`

## Ollama local smoke

Repeatable runner:

```bash
env COQUERY_OLLAMA_MODEL=qwen3.5:4b-nvfp4 bash scripts/run_ollama_local_smoke.sh
```

Observed on 2026-04-07:

- provider registration succeeded
- provider connectivity test succeeded
- `natural` with registered Ollama provider succeeded

Observed `natural` output:

```json
{
  "ok": true,
  "command": "natural",
  "intent": "count",
  "sql": "SELECT COUNT(*) FROM users;",
  "complexity": "low",
  "confidence": 1.0,
  "mode": "provider",
  "provider_name": "local_ollama",
  "provider_kind": "ollama",
  "model_name": "qwen3.5:4b-nvfp4",
  "error": null
}
```

## Scope lock

What this slice proves:

- provider registration works
- repo-local registry works
- Ollama local test works
- OpenAI-compatible endpoint registration exists
- `natural` can use a selected provider

What this slice does not prove:

- broad LLM quality across many schemas
- write-safe NL execution
- provider-backed SQL validation parity with every backend
- production readiness for remote API services
