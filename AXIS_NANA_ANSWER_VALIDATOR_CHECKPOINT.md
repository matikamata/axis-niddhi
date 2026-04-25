# AXIS ÑĀṆA Answer Validator Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files created

- `scripts/nana/validate_answer.py`
- `outputs/nana/answer_validation/.gitkeep`
- `docs/AXIS_NANA_ANSWER_VALIDATOR.md`

## Answer validation outputs generated

- `outputs/nana/answer_validation/answer-validation-dukkha-none-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-dukkha-mock-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-dukkha-openai-bootstrap-v1.json`

Current outcome for all generated samples:

- `answer_validation_status = NOT_APPLICABLE_NO_LLM_CALL`
- `display_allowed = false`

This is expected because no real provider call occurred in this environment.

## Validation logic

The Answer Validator consumes:

- one provider run
- one source-bound prompt package
- one gate result

Decision flow:

### 1. No LLM call

If:

```text
llm_called == false
```

Then:

- `answer_validation_status = NOT_APPLICABLE_NO_LLM_CALL`
- `display_allowed = false`

### 2. Gate blocked

If:

```text
gate.allowed_to_answer == false
```

Then:

- `answer_validation_status = REJECTED_GATE_BLOCKED`
- `display_allowed = false`

### 3. Real answer checks

If:

```text
llm_called == true
```

The validator checks:

1. `raw_answer` exists and is non-empty
2. answer contains `Sources:`
3. at least one approved canonical ref appears in the answer
4. no unknown canonical-looking refs appear
5. answer does not claim canonical authority
6. provider output is marked derivative / non-canonical
7. `answer_quality_flag == "UNVERIFIED"`

### Unknown ref detection

The validator scans for refs matching:

```text
[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}
```

If any detected ref is outside `prompt_package.canonical_refs`, the answer is rejected with:

- `REJECTED_UNKNOWN_REF`

## Status values

The validator currently uses only these status values:

```text
NOT_APPLICABLE_NO_LLM_CALL
REJECTED_GATE_BLOCKED
REJECTED_EMPTY_ANSWER
REJECTED_NO_SOURCES
REJECTED_UNKNOWN_REF
REJECTED_CANONICAL_AUTHORITY_CLAIM
REJECTED_NOT_MARKED_DERIVATIVE
REJECTED_NOT_UNVERIFIED
DISPLAY_ALLOWED_DERIVATIVE
```

## Validation commands and results

Commands executed:

```bash
python3 -m py_compile scripts/nana/validate_answer.py
python3 scripts/nana/validate_answer.py --provider-run outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --gate outputs/nana/gates/gate-dukkha-bootstrap-v1.json --dry-run
python3 scripts/nana/validate_answer.py --provider-run outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --gate outputs/nana/gates/gate-dukkha-bootstrap-v1.json --output outputs/nana/answer_validation/answer-validation-dukkha-none-bootstrap-v1.json
python3 scripts/nana/validate_answer.py --provider-run outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --gate outputs/nana/gates/gate-dukkha-bootstrap-v1.json --output outputs/nana/answer_validation/answer-validation-dukkha-mock-bootstrap-v1.json
python3 scripts/nana/validate_answer.py --provider-run outputs/nana/provider_runs/provider-dukkha-openai-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --gate outputs/nana/gates/gate-dukkha-bootstrap-v1.json --output outputs/nana/answer_validation/answer-validation-dukkha-openai-bootstrap-v1.json
node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `py_compile`: passed
- validator dry-run: passed
- validator write for `dukkha/none`: passed
- validator write for `dukkha/mock`: passed
- validator write for `dukkha/openai`: passed
- all three generated validations returned `NOT_APPLICABLE_NO_LLM_CALL`
- `navigator.js` syntax check: passed
- `navigator-store.js` syntax check: passed

## Safety guarantees

- local-only validation
- no API calls
- no LLM calls
- no backend
- no deploy changes
- no `build.py` changes
- no Navigator UI changes for this layer
- no CSL or canonical layer mutation
- no source ZIP changes
- no `03-translations/` changes
- no SG/SP/SA/SD pipeline changes
- validator does not trust provider outputs by default
- display remains blocked unless structural checks pass

## What remains intentionally unimplemented

- no semantic validation of doctrinal correctness
- no citation-content matching beyond allowed ref detection
- no secondary validator for answer-validation artifacts themselves
- no UI integration yet
- no display workflow for validated real answers
- no escalation/review workflow for borderline answers

## Rollback instructions

Remove only the Answer Validator layer:

```bash
rm -f AXIS_NANA_ANSWER_VALIDATOR_CHECKPOINT.md
rm -f docs/AXIS_NANA_ANSWER_VALIDATOR.md
rm -f scripts/nana/validate_answer.py
rm -f outputs/nana/answer_validation/answer-validation-dukkha-none-bootstrap-v1.json
rm -f outputs/nana/answer_validation/answer-validation-dukkha-mock-bootstrap-v1.json
rm -f outputs/nana/answer_validation/answer-validation-dukkha-openai-bootstrap-v1.json
rm -f outputs/nana/answer_validation/.gitkeep
```

If you want to keep the directory scaffold, remove only the generated JSON outputs and leave `.gitkeep` in place.

## Relationship to Real Provider Guarded and Provider Adapter Dry Run

This layer depends on two earlier foundations:

### Real Provider Guarded

- introduced the first opt-in real provider path
- added `raw_answer`, derivative markers, and guarded execution behavior
- ensured that real provider execution stays blocked unless explicitly enabled

The Answer Validator is the next safety step after a real provider run.

### Provider Adapter Dry Run

- introduced the provider output shape
- established `none` and `mock` provider runs as safe local artifacts
- made provider outputs inspectable before any UI display

The Answer Validator consumes that provider-run shape uniformly, whether the run is:

- `none`
- `mock`
- `openai`

In short:

- `Provider Adapter Dry Run` defines the provider artifact surface
- `Real Provider Guarded` enables the first opt-in real provider path
- `Answer Validator` decides whether any provider answer is safe enough to display as derivative, non-canonical output
