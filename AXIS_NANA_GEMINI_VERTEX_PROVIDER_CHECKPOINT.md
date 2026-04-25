# AXIS ÑĀṆA Gemini Vertex Provider Checkpoint

## Current branch

- `feat-axis-nana-gemini-vertex`

## Files modified

- `scripts/nana/providers/gemini_provider.py`
- `docs/AXIS_NANA_GEMINI_PROVIDER_GUARDED.md`
- `scripts/nana/providers/base_provider.py`
- `scripts/nana/run_provider_adapter.py`

Generated validation artifacts from the no-real-call checks:

- `outputs/nana/provider_runs/provider-dukkha-gemini-no-env-v1.json`
- `outputs/nana/provider_runs/provider-dukkha-gemini-missing-project-v1.json`

## Auth modes supported

The Gemini provider now supports both:

### 1. AI Studio API key mode

Environment:

- `GOOGLE_API_KEY`

Output:

- `provider_backend: "api_key"`

### 2. Vertex AI service account mode

Environment:

- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_CLOUD_PROJECT`
- optional `GOOGLE_CLOUD_LOCATION`
- optional `GEMINI_VERTEX_MODEL`

Output:

- `provider_backend: "vertex"`

## Detection order

The provider uses this detection order:

```text
if GOOGLE_APPLICATION_CREDENTIALS exists:
    use Vertex mode
elif GOOGLE_API_KEY exists:
    use API key mode
else:
    block execution
```

This preserves the safety model and keeps default behavior blocked unless the environment is explicit.

## Vertex env vars

The Vertex branch uses:

- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
  - default: `us-central1`
- `GEMINI_VERTEX_MODEL`
  - default: `gemini-1.5-pro`

If `GOOGLE_APPLICATION_CREDENTIALS` exists but `GOOGLE_CLOUD_PROJECT` is missing:

- `provider_backend = "vertex"`
- `provider_status = "missing_vertex_env"`
- `provider_decision = "BLOCKED_OR_NOT_ENABLED"`
- `llm_called = false`

If the Vertex SDK import fails:

- `provider_backend = "vertex"`
- `provider_status = "sdk_missing"`
- `provider_decision = "BLOCKED_OR_NOT_ENABLED"`
- `llm_called = false`

## No-real-call test results

Commands executed:

```bash
python3 -m py_compile scripts/nana/providers/gemini_provider.py scripts/nana/run_provider_adapter.py scripts/nana/validate_provider_result.py scripts/nana/providers/base_provider.py

env -u GOOGLE_API_KEY -u GOOGLE_APPLICATION_CREDENTIALS -u GOOGLE_CLOUD_PROJECT \
python3 scripts/nana/run_provider_adapter.py \
  --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json \
  --provider gemini \
  --enable-real-llm true \
  --output outputs/nana/provider_runs/provider-dukkha-gemini-no-env-v1.json

python3 scripts/nana/validate_provider_result.py outputs/nana/provider_runs/provider-dukkha-gemini-no-env-v1.json

env GOOGLE_APPLICATION_CREDENTIALS=/tmp/axis-dummy-sa.json bash -lc 'unset GOOGLE_API_KEY GOOGLE_CLOUD_PROJECT; python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider gemini --enable-real-llm true --output outputs/nana/provider_runs/provider-dukkha-gemini-missing-project-v1.json'

python3 scripts/nana/validate_provider_result.py outputs/nana/provider_runs/provider-dukkha-gemini-missing-project-v1.json
```

Results:

- compile checks: passed
- no env case: blocked safely
  - `provider_status: "not_enabled"`
  - `provider_backend: null`
  - `provider_decision: "BLOCKED_OR_NOT_ENABLED"`
  - `llm_called: false`
- missing Vertex project case: blocked safely
  - `provider_status: "missing_vertex_env"`
  - `provider_backend: "vertex"`
  - `provider_decision: "BLOCKED_OR_NOT_ENABLED"`
  - `llm_called: false`
- both generated artifacts passed `validate_provider_result.py`

## SDK availability

Checked in this environment:

- `google.cloud.aiplatform`: missing
- `vertexai`: missing

This is acceptable for the current checkpoint because the provider blocks safely when the SDK is unavailable.

## Confirmation no real API call occurred

No real API call occurred in this environment.

Reason:

- no API-key execution path was exercised with a real key
- no Vertex execution path was exercised with a complete service-account environment
- the tested Gemini runs returned `llm_called: false`

## Safety guarantees

- opt-in only
- no API calls by default
- no secrets in code
- no credentials read, printed, copied, or committed
- source-bound prompt only
- gate-respecting execution model preserved
- output remains derivative and non-canonical
- no deploy changes
- no `build.py` changes
- no Navigator changes
- no CSL or canonical layer mutation
- no source ZIP changes
- no SG/SP/SA/SD pipeline changes

## Rollback instructions

Remove only the Vertex extension artifacts if needed:

```bash
rm -f AXIS_NANA_GEMINI_VERTEX_PROVIDER_CHECKPOINT.md
rm -f outputs/nana/provider_runs/provider-dukkha-gemini-no-env-v1.json
rm -f outputs/nana/provider_runs/provider-dukkha-gemini-missing-project-v1.json
```

Then revert the Vertex-related changes in:

```bash
scripts/nana/providers/gemini_provider.py
docs/AXIS_NANA_GEMINI_PROVIDER_GUARDED.md
scripts/nana/providers/base_provider.py
scripts/nana/run_provider_adapter.py
```

This preserves the earlier Gemini guarded provider while removing Vertex AI service-account support.

## Relationship to Gemini Provider Guarded and Provider Adapter

### Gemini Provider Guarded

- introduced Gemini as a guarded real-provider path
- established opt-in activation, source-bound prompting, and derivative-only storage

The Vertex extension adds a second authentication backend without changing the guarded behavior.

### Provider Adapter

- provides the shared provider abstraction
- keeps default execution on `provider=none`
- standardizes provider outputs for validation and later UI visibility

The Vertex extension stays inside that same abstraction:

- same CLI flags
- same gate-respecting behavior
- same derivative/non-canonical contract

In short:

- `Provider Adapter` = common execution shell
- `Gemini Provider Guarded` = guarded Gemini real-provider path
- `Gemini Vertex Provider` = additional Gemini authentication backend using service-account environment auth
