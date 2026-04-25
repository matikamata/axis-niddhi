# AXIS NANA Council Simulation Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files created

- `scripts/nana/simulate_council.py`
- `scripts/nana/validate_council_result.py`
- `docs/AXIS_NANA_COUNCIL_SIMULATION.md`
- `outputs/nana/council/.gitkeep`
- `outputs/nana/council/council-dukkha-bootstrap-v1.json`
- `outputs/nana/council/council-anicca-bootstrap-v1.json`
- `outputs/nana/council/council-nibbana-bootstrap-v1.json`

## Council outputs generated

- `outputs/nana/council/council-dukkha-bootstrap-v1.json`
  - concept: `dukkha`
  - execution: `execution-dukkha-bootstrap-v1`
  - consensus status: `NO_REAL_COUNCIL_YET`
- `outputs/nana/council/council-anicca-bootstrap-v1.json`
  - concept: `anicca`
  - execution: `execution-anicca-bootstrap-v1`
  - consensus status: `NO_REAL_COUNCIL_YET`
- `outputs/nana/council/council-nibbana-bootstrap-v1.json`
  - concept: `nibbana`
  - execution: `execution-nibbana-bootstrap-v1`
  - consensus status: `NO_REAL_COUNCIL_YET`

All council outputs are deterministic derivative artifacts with:

- `council_type: nana_council_simulation`
- `llm_called: false`
- explicit `candidate_responses`
- explicit `citation_agreement_score`
- `validation_status: pending`

## Candidate simulation model

The bootstrap Council generates exactly 3 simulated candidates:

- `simulated_model_a`
- `simulated_model_b`
- `simulated_model_c`

Each candidate is:

- `provider: simulated`
- `llm_called: false`
- `answer_status: simulated_placeholder`
- populated with the canonical refs from the execution artifact
- marked with:
  - `external_claims_detected: false`
  - `notes: "Placeholder candidate. No model was called."`

No doctrinal answer text is generated.

## Citation agreement formula

Implemented deterministic formula:

```txt
citation_agreement_score =
  number of candidates citing all canonical_refs / total candidates
```

Bootstrap result in this phase:

- all 3 simulated candidates cite all canonical refs
- therefore `citation_agreement_score = 1.0`

Consensus mapping logic:

```txt
if llm_called == false:
  consensus_status = NO_REAL_COUNCIL_YET
elif citation_agreement_score >= 0.8:
  consensus_status = CITATION_CONSENSUS
else:
  consensus_status = DISSENT_REVIEW_REQUIRED
```

Because no real LLM is called in this bootstrap, `consensus_status` must remain:

- `NO_REAL_COUNCIL_YET`

## Validation commands and results

Commands executed:

```bash
python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --dry-run

python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --output outputs/nana/council/council-dukkha-bootstrap-v1.json

python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-anicca-bootstrap-v1.json --output outputs/nana/council/council-anicca-bootstrap-v1.json

python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-nibbana-bootstrap-v1.json --output outputs/nana/council/council-nibbana-bootstrap-v1.json

python3 scripts/nana/validate_council_result.py outputs/nana/council/council-dukkha-bootstrap-v1.json outputs/nana/council/council-anicca-bootstrap-v1.json outputs/nana/council/council-nibbana-bootstrap-v1.json

node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `dukkha` dry-run council simulation: passed
- explicit council generation for all 3 outputs: passed
- council result validation: all 3 outputs passed
- `navigator.js` syntax check: passed
- `navigator-store.js` syntax check: passed

## Safety guarantees

- local-only implementation
- no API calls
- no real LLM calls
- no embeddings
- no backend
- no deploy changes
- no `build.py` changes
- no Navigator UI changes
- no CSL or canonical layer mutation
- no source ZIP changes
- no `03-translations/` changes
- no SG/SP/SA/SD pipeline changes
- council outputs are deterministic, derivative, and disposable
- citation agreement is treated as a structural signal, not as doctrinal authority

## What remains intentionally unimplemented

- no real multi-model execution
- no doctrinal answers
- no semantic comparison
- no dissent analysis beyond placeholder structure
- no hallucination classifier beyond bootstrap fields
- no backend service
- no cloud sync
- no publication-pipeline integration

## Rollback instructions

Remove only the council-simulation artifacts created for this layer:

```bash
rm -f AXIS_NANA_COUNCIL_SIMULATION_CHECKPOINT.md
rm -f docs/AXIS_NANA_COUNCIL_SIMULATION.md
rm -f outputs/nana/council/council-dukkha-bootstrap-v1.json
rm -f outputs/nana/council/council-anicca-bootstrap-v1.json
rm -f outputs/nana/council/council-nibbana-bootstrap-v1.json
rm -f outputs/nana/council/.gitkeep
rm -f scripts/nana/simulate_council.py
rm -f scripts/nana/validate_council_result.py
```

If you want to keep the directory skeleton, remove only the generated JSON outputs and leave `outputs/nana/council/.gitkeep` in place.

## Relationship to Full NANA Chain

Current AXIS NANA chain:

```txt
Retrieval
  -> Prompt
  -> Gate
  -> Safe Execution
  -> Council
```

Layer roles:

- `Retrieval`
  - builds non-interpreted context packs from canonical refs
- `Prompt`
  - binds a question to source-bound canonical context
- `Gate`
  - blocks or flags weak context before execution
- `Safe Execution`
  - prepares execution payloads without calling any model
- `Council`
  - simulates future multi-model comparison structure
  - tracks citation agreement shape
  - preserves canonical authority while preparing BeYond review visibility

This means the Council layer is downstream of execution and upstream of any future real model-comparison system.
