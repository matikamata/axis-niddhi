# AXIS NANA Insufficient Context Gate Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files created

- `scripts/nana/evaluate_context_sufficiency.py`
- `scripts/nana/validate_gate_result.py`
- `docs/AXIS_NANA_INSUFFICIENT_CONTEXT_GATE.md`
- `outputs/nana/gates/.gitkeep`
- `outputs/nana/gates/gate-dukkha-bootstrap-v1.json`
- `outputs/nana/gates/gate-anicca-bootstrap-v1.json`
- `outputs/nana/gates/gate-nibbana-bootstrap-v1.json`

## Gate outputs generated

- `outputs/nana/gates/gate-dukkha-bootstrap-v1.json`
  - concept: `dukkha`
  - prompt package: `prompt-dukkha-bootstrap-v1`
  - decision: `ANSWER_CONFIDENT`
- `outputs/nana/gates/gate-anicca-bootstrap-v1.json`
  - concept: `anicca`
  - prompt package: `prompt-anicca-bootstrap-v1`
  - decision: `ANSWER_CONFIDENT`
- `outputs/nana/gates/gate-nibbana-bootstrap-v1.json`
  - concept: `nibbana`
  - prompt package: `prompt-nibbana-bootstrap-v1`
  - decision: `ANSWER_CONFIDENT`

All gate outputs are deterministic derivative artifacts with:

- `gate_type: context_sufficiency_evaluation`
- cited `canonical_refs`
- explicit `decision`
- explicit `allowed_to_answer`
- `llm_allowed: false`
- `validation_status: pending`

## Decision rules

- `NO_CANONICAL_SUPPORT`
  - when `ref_count == 0`
- `ANSWER_PARTIAL`
  - when `ref_count >= 1` and `coverage_score < 0.5`
- `ANSWER_CONFIDENT`
  - when `ref_count >= 2` and `coverage_score >= 0.5`

Decision mapping implemented:

```txt
if ref_count == 0 -> NO_CANONICAL_SUPPORT
elif coverage_score < 0.5 -> ANSWER_PARTIAL
else -> ANSWER_CONFIDENT
```

## Coverage score formula

Implemented heuristic:

```txt
coverage_score =
  (ref_count * 0.6)
  + (related_concepts_count * 0.2)
  + (question_length_factor * 0.2)
```

Additional rules:

- score is clamped between `0.0` and `1.0`
- `question_length_factor` is a bounded local proxy derived from question word count
- no NLP
- no embeddings
- no semantic inference

## Validation commands and results

Commands executed:

```bash
python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --dry-run

python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --output outputs/nana/gates/gate-dukkha-bootstrap-v1.json

python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-anicca-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-anicca-bootstrap-v1.json --output outputs/nana/gates/gate-anicca-bootstrap-v1.json

python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-nibbana-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json --output outputs/nana/gates/gate-nibbana-bootstrap-v1.json

python3 scripts/nana/validate_gate_result.py outputs/nana/gates/gate-dukkha-bootstrap-v1.json outputs/nana/gates/gate-anicca-bootstrap-v1.json outputs/nana/gates/gate-nibbana-bootstrap-v1.json

node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `dukkha` dry-run gate evaluation: passed
- explicit gate generation for all 3 outputs: passed
- gate result validation: all 3 outputs passed
- `navigator.js` syntax check: passed
- `navigator-store.js` syntax check: passed

## Safety guarantees

- local-only implementation
- no API calls
- no LLM calls
- no embeddings
- no backend
- no deploy changes
- no `build.py` changes
- no Navigator UI changes
- no CSL or canonical layer mutation
- no source ZIP changes
- no `03-translations/` changes
- no SG/SP/SA/SD pipeline changes
- gate outputs are deterministic, derivative, and disposable
- weak context is explicitly blocked before any future answer layer

## What remains intentionally unimplemented

- no model invocation
- no answer generation
- no semantic reasoning
- no doctrinal inference
- no embeddings
- no graph engine
- no backend service
- no cloud sync
- no ingestion into publication pipeline

## Relationship to Source-Bound Prompt Builder and Retrieval Skeleton

These layers form a strict local AXIS NANA sequence.

- Retrieval Skeleton
  - creates non-interpreted canonical context packs
- Source-Bound Prompt Builder
  - binds a user question to a context pack
  - adds source-only prompt constraints
- Insufficient Context Gate
  - evaluates whether the bound context is strong enough to proceed
  - blocks or flags weak support before any future answer layer

Practical order:

- retrieval
- prompt package
- sufficiency gate
- only then any future answer engine

This means the gate is the hard safety checkpoint between prompt preparation and any later model usage.

## Rollback instructions

Remove only the gate artifacts created for this layer:

```bash
rm -f AXIS_NANA_INSUFFICIENT_CONTEXT_GATE_CHECKPOINT.md
rm -f docs/AXIS_NANA_INSUFFICIENT_CONTEXT_GATE.md
rm -f outputs/nana/gates/gate-dukkha-bootstrap-v1.json
rm -f outputs/nana/gates/gate-anicca-bootstrap-v1.json
rm -f outputs/nana/gates/gate-nibbana-bootstrap-v1.json
rm -f outputs/nana/gates/.gitkeep
rm -f scripts/nana/evaluate_context_sufficiency.py
rm -f scripts/nana/validate_gate_result.py
```

If you want to keep the directory skeleton, remove only the generated JSON outputs and leave `outputs/nana/gates/.gitkeep` in place.
