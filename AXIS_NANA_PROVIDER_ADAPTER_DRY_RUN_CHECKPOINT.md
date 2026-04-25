# AXIS ÑĀṆA Provider Adapter Dry Run Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files created

- `scripts/nana/providers/__init__.py`
- `scripts/nana/providers/base_provider.py`
- `scripts/nana/providers/none_provider.py`
- `scripts/nana/providers/mock_provider.py`
- `scripts/nana/run_provider_adapter.py`
- `scripts/nana/validate_provider_result.py`
- `docs/AXIS_NANA_PROVIDER_ADAPTER_DRY_RUN.md`
- `outputs/nana/provider_runs/.gitkeep`
- `outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-anicca-none-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-nibbana-none-bootstrap-v1.json`

## Files modified

- `scripts/nana/README.md`

## Provider modes available

- `none`
  - default safe mode
  - no API call
  - no answer generation
  - `provider_status: "not_configured"`
  - `provider_decision: "DRY_RUN_ONLY"`
  - `llm_called: false`
- `mock`
  - deterministic local placeholder mode
  - no API call
  - no doctrinal answer
  - `provider_status: "mocked"`
  - `provider_decision: "MOCK_ONLY"`
  - `llm_called: false`
  - `simulated_answer: "[SIMULATED PLACEHOLDER — no model was called] ..."`

## Provider runs generated

- `outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json`
  - provider: `none`
  - status: `not_configured`
- `outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json`
  - provider: `mock`
  - status: `mocked`
- `outputs/nana/provider_runs/provider-anicca-none-bootstrap-v1.json`
  - provider: `none`
  - status: `not_configured`
- `outputs/nana/provider_runs/provider-nibbana-none-bootstrap-v1.json`
  - provider: `none`
  - status: `not_configured`

## Gate-respecting behavior

The Provider Adapter does not bypass the ÑĀṆA safety chain.

If the execution artifact contains:

```json
{
  "decision": "BLOCKED"
}
```

Then the adapter refuses to proceed, including in `mock` mode, and returns:

- `provider_decision: "BLOCKED_BY_GATE"`
- `llm_called: false`
- `answer_generated: false`
- `simulated_answer: null`

This preserves the invariant:

```text
Gate first. Provider second.
```

## Validation commands and results

Commands executed:

```bash
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider none --dry-run
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider mock --output outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-anicca-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-anicca-none-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-nibbana-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-nibbana-none-bootstrap-v1.json
python3 scripts/nana/validate_provider_result.py outputs/nana/provider_runs/*.json
node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- provider adapter dry-run: passed
- provider run write for `dukkha/none`: passed
- provider run write for `dukkha/mock`: passed
- provider run write for `anicca/none`: passed
- provider run write for `nibbana/none`: passed
- provider result validation: all generated outputs passed
- `navigator.js` syntax check: passed
- `navigator-store.js` syntax check: passed

## Safety guarantees

- local-only default behavior
- no API calls by default
- no real LLM calls by default
- `none` provider is safe by construction
- `mock` provider is deterministic and explicitly simulated
- gate-respecting behavior is enforced before provider output
- no deploy changes
- no `build.py` changes
- no Navigator UI changes for this layer
- no CSL or canonical layer mutation
- no source ZIP changes
- no `03-translations/` changes
- no SG/SP/SA/SD pipeline changes
- provider outputs remain derivative artifacts only

## What remains intentionally unimplemented

- no real provider integration with OpenAI
- no real provider integration with Vertex
- no local model runtime integration
- no credential handling
- no provider retries, rate limits, or network handling
- no doctrinal answer generation
- no publication pipeline ingestion
- no automatic provider selection logic

## Rollback instructions

Remove only the Provider Adapter layer artifacts:

```bash
rm -f AXIS_NANA_PROVIDER_ADAPTER_DRY_RUN_CHECKPOINT.md
rm -f docs/AXIS_NANA_PROVIDER_ADAPTER_DRY_RUN.md
rm -f outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json
rm -f outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json
rm -f outputs/nana/provider_runs/provider-anicca-none-bootstrap-v1.json
rm -f outputs/nana/provider_runs/provider-nibbana-none-bootstrap-v1.json
rm -f outputs/nana/provider_runs/.gitkeep
rm -f scripts/nana/run_provider_adapter.py
rm -f scripts/nana/validate_provider_result.py
rm -f scripts/nana/providers/__init__.py
rm -f scripts/nana/providers/base_provider.py
rm -f scripts/nana/providers/none_provider.py
rm -f scripts/nana/providers/mock_provider.py
```

If you want to keep the directory scaffold, remove only the generated JSON outputs and leave the provider code plus `.gitkeep` in place.

## Relationship to the ÑĀṆA chain

The Provider Adapter sits after the existing safe ÑĀṆA chain:

```text
Retrieval -> Prompt -> Gate -> Safe Execution -> Council -> Provider Adapter
```

Layer roles:

- `Retrieval`
  - resolves concept to cited canonical context
- `Prompt`
  - prepares a source-bound prompt package
- `Gate`
  - blocks weak or insufficient context
- `Safe Execution`
  - simulates pre-LLM execution without calling a model
- `Council`
  - simulates future multi-model comparison without calling models
- `Provider Adapter`
  - introduces provider abstraction while remaining dry-run first and safe by default

This means AXIS ÑĀṆA is now architecturally prepared for future provider-specific execution, while still preserving the current invariant:

```text
No provider configured = no real model call.
```
