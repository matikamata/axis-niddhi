# AXIS ÑĀṆA Gemini Provider Guarded Checkpoint

## Current branch

- `feat-axis-nana-gemini-vertex`

## Files created for Gemini provider

- `scripts/nana/providers/gemini_provider.py`
- `docs/AXIS_NANA_GEMINI_PROVIDER_GUARDED.md`
- `outputs/nana/provider_runs/provider-dukkha-gemini-bootstrap-v1.json`

## Files modified for Gemini provider

- `scripts/nana/providers/__init__.py`
- `scripts/nana/run_provider_adapter.py`
- `scripts/nana/validate_provider_result.py`

## Gemini activation rules

The Gemini provider is guarded and opt-in only.

It may run only if all conditions are true:

```text
--provider gemini
--enable-real-llm true
GOOGLE_API_KEY present in environment
execution.decision == READY
```

If any condition fails:

- `provider_decision = BLOCKED_OR_NOT_ENABLED`
- `llm_called = false`
- no real request is sent

Additional safety constraints:

- source-bound prompt package only
- no context augmentation
- no hardcoded key
- no secrets stored in repo
- output remains derivative and non-canonical

## Blocked test cases

The following blocked cases were exercised in this environment:

### 1. Without explicit flag

Command:

```bash
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider gemini --dry-run
```

Result:

- blocked as expected
- `provider_status: "not_enabled"`
- `provider_decision: "BLOCKED_OR_NOT_ENABLED"`
- `llm_called: false`

### 2. With flag but no API key

Command:

```bash
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider gemini --enable-real-llm true --output outputs/nana/provider_runs/provider-dukkha-gemini-bootstrap-v1.json
```

Result:

- blocked as expected
- `provider_status: "missing_api_key"`
- `provider_decision: "BLOCKED_OR_NOT_ENABLED"`
- `llm_called: false`

## Validation commands and results

Commands executed:

```bash
python3 -m py_compile scripts/nana/providers/__init__.py scripts/nana/providers/gemini_provider.py scripts/nana/run_provider_adapter.py scripts/nana/validate_provider_result.py
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider gemini --dry-run
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider gemini --enable-real-llm true --output outputs/nana/provider_runs/provider-dukkha-gemini-bootstrap-v1.json
python3 scripts/nana/validate_provider_result.py outputs/nana/provider_runs/provider-dukkha-gemini-bootstrap-v1.json
```

Results:

- Python compile checks: passed
- blocked `gemini` without flag: passed
- blocked `gemini` without key: passed
- provider result validation: passed

## Confirmation no real API call occurred

No real API call occurred in this environment.

Reason:

- `GOOGLE_API_KEY` was not present
- guarded mode remained blocked
- tested Gemini runs returned `llm_called: false`

## Safety guarantees

- Gemini provider remains opt-in only
- no API calls by default
- no key in code
- no secrets committed
- gate must allow execution before any real provider call
- prompt remains source-bound
- output is marked derivative and non-canonical
- no deploy changes
- no `build.py` changes
- no Navigator UI changes for this layer
- no CSL or canonical layer mutation
- no source ZIP changes
- no SG/SP/SA/SD pipeline changes

## Rollback instructions

Remove only the guarded Gemini provider layer:

```bash
rm -f AXIS_NANA_GEMINI_PROVIDER_GUARDED_CHECKPOINT.md
rm -f docs/AXIS_NANA_GEMINI_PROVIDER_GUARDED.md
rm -f scripts/nana/providers/gemini_provider.py
rm -f outputs/nana/provider_runs/provider-dukkha-gemini-bootstrap-v1.json
```

Then revert the Gemini-related edits in:

```bash
scripts/nana/providers/__init__.py
scripts/nana/run_provider_adapter.py
scripts/nana/validate_provider_result.py
```

This preserves the earlier provider adapter path while removing Gemini readiness.

## Relationship to OpenAI provider and Provider Adapter Dry Run

This layer extends two earlier foundations:

### OpenAI provider

- provided the first guarded real-provider structural pattern
- established the real-provider contract:
  - opt-in flag
  - env-based auth
  - source-bound prompt usage
  - derivative/non-canonical storage

The Gemini provider follows the same guarded contract, but is implemented separately.

### Provider Adapter Dry Run

- introduced provider abstraction
- established `none` and `mock` providers
- kept default behavior local and deterministic

The guarded Gemini provider builds on that abstraction without changing the safe default.

In short:

- `Provider Adapter Dry Run` = safe default provider layer
- `OpenAI provider` = first guarded real-provider pattern
- `Gemini provider` = second guarded real-provider implementation following the same safety model
