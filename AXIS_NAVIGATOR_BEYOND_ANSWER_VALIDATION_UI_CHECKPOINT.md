# AXIS Navigator BeYond Answer Validation UI Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files modified

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

## UI sections added

Inside the existing `NANA Study` area in BeYond Mode, the following Answer Validation UI was added after `Provider Runs`:

- `Answer Validation`
  - `answer_validation_id`
  - `concept_id`
  - `llm_called`
  - `gate_decision`
  - `answer_validation_status`
  - `display_allowed`
  - `canonical_refs_found`
  - `unknown_refs_found`
- compact validation cards
- check matrix derived from `checks`
  - `raw answer present`
  - `Sources section present`
  - `refs within allowed set`
  - `no canonical authority claim`
  - `marked derivative`
  - `quality unverified`

Safety display behavior:

- `Display allowed` is always shown visibly
- if `display_allowed == false`
  - no answer text is rendered
  - only validation metadata and checks are shown

Visual status mapping:

- `DISPLAY_ALLOWED_DERIVATIVE` -> green
- `NOT_APPLICABLE_NO_LLM_CALL` -> neutral
- any `REJECTED_*` -> danger / warn

## Data sources read

The UI reads local static JSON artifacts only:

- `outputs/nana/context-pack-*.json`
- `outputs/nana/prompts/prompt-*.json`
- `outputs/nana/gates/gate-*.json`
- `outputs/nana/execution/execution-*.json`
- `outputs/nana/council/council-*.json`
- `outputs/nana/provider_runs/provider-*.json`
- `outputs/nana/answer_validation/answer-validation-*.json`

More specifically for answer validation:

- `outputs/nana/answer_validation/answer-validation-<concept>-none-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-<concept>-mock-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-<concept>-openai-bootstrap-v1.json`

No backend calls are made.
No provider execution occurs.
No real model calls are made.
No data is mutated.

## Visibility rules

Answer Validation UI appears only when all conditions are true:

- internal cockpit mode is `javana`
- `study_mode == true`

UI label may show `BeYond Mode`, but internal mode value remains:

- `javana`

Answer Validation UI stays hidden in:

- `asfalto`
- `hover`
- `javana` with Study Mode off

## Validation commands and results

Commands executed:

```bash
node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `navigator.js` syntax check: passed
- `navigator-store.js` syntax check: passed

Functional verification target:

- open `TL.JJ.008`
- `Kulla Mode` -> no Answer Validation UI
- `Orbit Mode` -> no Answer Validation UI
- `BeYond Mode` + `Study Mode OFF` -> no Answer Validation UI
- `BeYond Mode` + `Study Mode ON` -> Answer Validation appears
- status shows `NOT_APPLICABLE_NO_LLM_CALL`
- `Display allowed` is visibly `false`
- checklist renders
- no answer text is shown
- existing Quick Find / Outline / Related Pages / NANA Study / Council / Provider Runs remain functional

## Safety guarantees

- local-only read-only implementation
- no API calls
- no real LLM calls
- no backend
- no deploy changes
- no `build.py` changes
- no CSL or canonical layer mutation
- no source ZIP changes
- no SG/SP/SA/SD pipeline changes
- no new localStorage schema break
- Navigator remains progressive enhancement
- failure mode is safe:
  - if answer validation JSON is missing, UI shows `No Answer Validation data available`
  - if `display_allowed == false`, no answer text is shown

## What remains intentionally unimplemented

- no rendering of validated real answer text
- no UI for escalation/review workflow
- no semantic confidence scoring
- no combined provider-vs-validator diffing
- no backend sync
- no publication-pipeline integration

## Rollback instructions

Revert only the BeYond Answer Validation UI integration files:

```bash
rm -f AXIS_NAVIGATOR_BEYOND_ANSWER_VALIDATION_UI_CHECKPOINT.md
git diff -- pipeline/13-ssg/static/js/navigator.js pipeline/13-ssg/static/css/navigator.css
```

Manual rollback scope:

- remove Answer Validation fetch/cache/render logic from `pipeline/13-ssg/static/js/navigator.js`
- remove Answer Validation presentation styles from `pipeline/13-ssg/static/css/navigator.css`

If desired, the broader `NANA Study`, `Council Simulation`, and `Provider Runs` integrations can remain while only the Answer Validation block is removed.

## Relationship to BeYond Provider Runs UI, NANA Answer Validator, and the full BeYond safety chain

This layer sits on top of two earlier foundations:

- `AXIS Navigator BeYond Provider Runs UI`
  - exposed provider-run artifacts inside BeYond Mode
  - established the provider visibility layer in `NANA Study`
- `AXIS NANA Answer Validator`
  - created local answer-validation artifacts
  - introduced structural display-eligibility checks for provider answers

Practical relationship:

- `BeYond Provider Runs UI` shows what provider artifacts exist
- `NANA Answer Validator` decides whether any provider answer is display-safe
- `BeYond Answer Validation UI` is the read-only viewer for those safety decisions

This extends the visible BeYond safety chain to:

```text
Retrieval -> Prompt -> Gate -> Execution -> Council -> Provider -> Answer Validation
```

In short:

- `BeYond Provider Runs UI` = provider artifact visibility
- `NANA Answer Validator` = structural answer safety check
- `BeYond Answer Validation UI` = read-only safety verdict layer inside Navigator
