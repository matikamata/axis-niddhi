# AXIS NANA Provider Adapter Dry Run

## What this layer is

This layer introduces a provider abstraction for future AXIS NANA execution without enabling real provider calls.

Its default posture is:

- provider optional
- dry-run first
- local only
- no API calls
- no real LLM calls

## Why this exists

The provider layer prepares AXIS NANA for future adapters such as OpenAI, Vertex, or local model connectors while preserving a safe default state when no provider is configured.

Canon remains authority.
Providers are optional processors only.

## Current providers

### none_provider

Default provider.

- never calls any API
- never generates an answer
- returns `provider_status: not_configured`
- keeps `llm_called: false`

### mock_provider

Deterministic local mock.

- never calls any API
- never generates a doctrinal answer
- returns a clearly marked placeholder only
- returns `provider_status: mocked`
- keeps `llm_called: false`

## Gate safety

If the input execution artifact is blocked, the provider adapter must not proceed even in mock mode.

In that case it returns:

- `provider_decision: BLOCKED_BY_GATE`
- `answer_generated: false`
- `llm_called: false`

## Why this is safe

The adapter is safe by construction because:

- no real provider is required
- no network access is needed
- no answer generation is trusted by default
- blocked executions remain blocked

This makes the layer suitable for future provider expansion without weakening the current local-only chain.
