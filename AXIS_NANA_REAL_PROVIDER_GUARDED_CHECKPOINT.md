# AXIS ÑĀṆA Real Provider Guarded Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files created

- `scripts/nana/providers/openai_provider.py`
- `docs/AXIS_NANA_REAL_PROVIDER_GUARDED.md`

## Files modified

- `scripts/nana/run_provider_adapter.py`
- `scripts/nana/validate_provider_result.py`
- `scripts/nana/providers/base_provider.py`
- `scripts/nana/providers/__init__.py`
- `scripts/nana/providers/none_provider.py`
- `scripts/nana/providers/mock_provider.py`

## Provider activation rules

The real provider is guarded and opt-in only.

It may run only if all conditions are true:

```text
--provider openai
--enable-real-llm true
OPENAI_API_KEY present in environment
execution.decision == READY
```

If any condition fails:

- `provider_decision = BLOCKED_OR_NOT_ENABLED`
- `llm_called = false`
- no real request is sent

Additional safety constraints:

- source-bound prompt package only
- no extra context injection
- no prompt augmentation
- no hardcoded API key
- no secret stored in repo

## Blocked test cases

The following blocked cases were exercised in this environment:

### 1. Without explicit flag

Command:

```bash
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider openai --dry-run
```

Result:

- blocked as expected
- `provider_status: "not_enabled"`
- `provider_decision: "BLOCKED_OR_NOT_ENABLED"`
- `llm_called: false`

### 2. With flag but no API key

Command:

```bash
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider openai --enable-real-llm true --output outputs/nana/provider_runs/provider-dukkha-openai-bootstrap-v1.json
```

Result:

- blocked as expected
- `provider_status: "missing_api_key"`
- `provider_decision: "BLOCKED_OR_NOT_ENABLED"`
- `llm_called: false`

### 3. With blocked gate

Command:

```bash
python3 scripts/nana/run_provider_adapter.py --execution /tmp/axis-execution-dukkha-blocked.json --provider openai --enable-real-llm true --output /tmp/provider-dukkha-openai-blocked.json
```

Result:

- blocked as expected
- `provider_status: "not_enabled"`
- `provider_decision: "BLOCKED_OR_NOT_ENABLED"`
- `llm_called: false`

## Validation commands and results

Commands executed:

```bash
python3 -m py_compile scripts/nana/providers/__init__.py scripts/nana/providers/base_provider.py scripts/nana/providers/none_provider.py scripts/nana/providers/mock_provider.py scripts/nana/providers/openai_provider.py scripts/nana/run_provider_adapter.py scripts/nana/validate_provider_result.py
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider mock --output outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-anicca-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-anicca-none-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-nibbana-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-nibbana-none-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider openai --dry-run
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider openai --enable-real-llm true --output outputs/nana/provider_runs/provider-dukkha-openai-bootstrap-v1.json
python3 scripts/nana/validate_provider_result.py outputs/nana/provider_runs/*.json
node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- Python compile checks: passed
- dry-run provider regeneration: passed
- blocked `openai` without flag: passed
- blocked `openai` without key: passed
- provider result validation: all generated outputs passed
- `navigator.js` syntax check: passed
- `navigator-store.js` syntax check: passed

## Confirmation no real API call occurred

No real API call occurred in this environment.

Reason:

- `OPENAI_API_KEY` was not present
- guarded mode remained blocked
- all tested `openai` runs returned `llm_called: false`

## Safety guarantees

- real provider remains opt-in only
- no API calls by default
- no API key in code
- no secrets committed
- gate must allow execution before any real provider call
- prompt must remain source-bound
- output is marked derivative and non-canonical
- no deploy changes
- no `build.py` changes
- no Navigator UI changes for this layer
- no CSL or canonical layer mutation
- no source ZIP changes
- no `03-translations/` changes
- no SG/SP/SA/SD pipeline changes

## Rollback instructions

Remove only the guarded real-provider layer:

```bash
rm -f AXIS_NANA_REAL_PROVIDER_GUARDED_CHECKPOINT.md
rm -f docs/AXIS_NANA_REAL_PROVIDER_GUARDED.md
rm -f scripts/nana/providers/openai_provider.py
```

Then revert the provider adapter edits in:

```bash
scripts/nana/run_provider_adapter.py
scripts/nana/validate_provider_result.py
scripts/nana/providers/base_provider.py
scripts/nana/providers/__init__.py
scripts/nana/providers/none_provider.py
scripts/nana/providers/mock_provider.py
```

If desired, also remove:

```bash
rm -f outputs/nana/provider_runs/provider-dukkha-openai-bootstrap-v1.json
```

This preserves the earlier dry-run adapter path while removing real-provider readiness.

## Relationship to Provider Adapter Dry Run and Safe Execution Wrapper

This layer extends two earlier foundations:

### Provider Adapter Dry Run

- introduced provider abstraction
- established `none` and `mock` providers
- kept all provider behavior local and deterministic

The guarded real provider builds on that abstraction without changing the default safe path.

### Safe Execution Wrapper

- established the execution artifact used before any provider run
- encoded `decision`, `allowed_to_answer`, and prepared prompt state

The guarded real provider depends on that wrapper:

- if execution is not `READY`, it must not run
- if execution is `READY`, it may still remain blocked unless explicitly enabled

In short:

- `Safe Execution Wrapper` decides whether execution may proceed
- `Provider Adapter Dry Run` defines the provider abstraction
- `Real Provider Guarded` adds one opt-in real provider without changing the safe default
