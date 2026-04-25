# AXIS ÑĀṆA Gemini Provider Guarded Mode

## Purpose

This document describes the guarded Gemini provider path for AXIS ÑĀṆA.

The Gemini provider exists as an optional real-provider adapter.
It does not replace the default safe path.

## Activation model

The Gemini provider is disabled by default.

It will only run when all of the following are true:

- `--provider gemini`
- `--enable-real-llm true`
- `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_CLOUD_PROJECT` exist in the environment, or `GOOGLE_API_KEY` exists in the environment
- the execution artifact has `decision == READY`

If any condition fails:

- the provider stays blocked
- `llm_called = false`
- `provider_decision = BLOCKED_OR_NOT_ENABLED`

## Authentication modes

The Gemini provider now supports two authentication modes, in this order:

### 1. Service Account / Vertex AI mode

Detection:

- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_CLOUD_PROJECT`

Runtime:

- `vertexai.init(project=..., location=...)`
- `google.cloud.aiplatform.init(project=..., location=...)`
- model from `GEMINI_VERTEX_MODEL`, default `gemini-2.5-pro`

Examples:

```bash
export GEMINI_VERTEX_MODEL="gemini-2.5-pro"
```

```bash
export GEMINI_VERTEX_MODEL="gemini-2.5-flash"
```

If Vertex mode is selected but the environment is incomplete:

- `provider_backend = "vertex"`
- `provider_status = "missing_vertex_env"`
- `provider_decision = "BLOCKED_OR_NOT_ENABLED"`
- `llm_called = false`

If the Vertex SDK is unavailable:

- `provider_backend = "vertex"`
- `provider_status = "sdk_missing"`
- `provider_decision = "BLOCKED_OR_NOT_ENABLED"`
- `llm_called = false`
- `provider_error` contains the import failure message

If Vertex authentication works but the requested model is unavailable to the project:

- `provider_backend = "vertex"`
- `provider_status = "model_unavailable"`
- `provider_decision = "BLOCKED_OR_NOT_ENABLED"`
- `llm_called = false`
- `answer_generated = false`
- `provider_error` contains the Vertex exception string

### 2. API Key / AI Studio mode

Detection:

- `GOOGLE_API_KEY`

Runtime:

- direct `generateContent` REST call
- model from `GEMINI_MODEL`, default `gemini-2.0-flash`

If no authentication variables are present, the provider stays blocked.

## Prompt discipline

The Gemini provider uses the existing source-bound prompt package only:

- exact `system_instruction`
- exact `user_prompt`
- or the already-derived `prepared_prompt` from the safe execution artifact in Vertex mode

That prompt package now explicitly requires a dedicated final section titled
exactly `Sources:`. Inline citations may appear in the answer, but they are not
sufficient by themselves.

It does not add extra context.
It does not rewrite the Canon.
It does not make the answer canonical.

## Model selection notes

For Vertex mode, model selection is fully environment-controlled through
`GEMINI_VERTEX_MODEL`.

This is important because project/model availability can differ across Vertex
accounts and regions. A model access failure is treated as a blocked provider
run, not as a successful LLM call.

Every Gemini provider result persists the exact requested model in
`model_requested`, even when the provider is blocked before any external call.

For successful Gemini executions, the runtime log is aligned to the actual
requested model so the terminal output matches `model_requested`.

The current Vertex SDK path uses `vertexai.generative_models`, which is under a
published deprecation window. AXIS keeps the integration guarded and opt-in,
and future SDK migration should preserve the same source-bound and
gate-respecting safety behavior.

## Storage and authority

Even if a real Gemini call succeeds:

- the answer remains derivative
- the answer remains non-canonical
- the answer must still pass downstream validation before display

## Safety posture

- no key in code
- no credential path in code
- no project id in code
- no auto-run
- no backend
- no Canon mutation
- no pipeline mutation
- no deployment mutation

The default provider remains `none`.
