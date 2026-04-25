# AXIS NAVIGATOR — Validated Answer UI Checkpoint

## Current branch

- `feat-axis-nana-gemini-vertex`

## Files modified

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

## UI behavior added

The Navigator now renders a new `Validated Answer` section inside the existing
BeYond Mode study surface.

Visibility:

- visible only when internal cockpit mode is `javana`
- visible only when `study_mode == true`

Behavior:

- if a matching answer validation artifact has `display_allowed: true`
  - show the approved answer body
  - label it `Derived Answer — Canon-Constrained`
  - show a green approval badge
  - render simple markdown locally without adding dependencies
  - preserve the final `Sources:` section as a visible block
- if `display_allowed: false`
  - do not show answer text
  - keep only the validation metadata already shown in `Answer Validation`
- if approval metadata exists but the matching provider run has no local
  `raw_answer`
  - show a blocked explanatory note instead of partial content

## Data sources read

The UI reads local JSON only:

- `outputs/nana/answer_validation/answer-validation-<concept>-none-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-<concept>-mock-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-<concept>-openai-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-<concept>-gemini-bootstrap-v1.json`
- `outputs/nana/answer_validation/answer-validation-<concept>-gemini-vertex-real-v1.json`
- `outputs/nana/provider_runs/provider-<concept>-none-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-<concept>-mock-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-<concept>-openai-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-<concept>-gemini-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-<concept>-gemini-vertex-real-v1.json`

The rendered answer is resolved by matching:

- `answer_validation.provider_run_id`
- `provider_run.provider_run_id`

## Approval rule

The UI shows answer text only when both are true:

- `answer_validation.display_allowed == true`
- the matched provider run exists and contains non-empty `raw_answer`

When approved, the answer is still treated as:

- derivative
- non-canonical
- canon-constrained

## Blocked rule

The UI must not display answer text when:

- `display_allowed == false`
- no matching provider run is found
- matching provider run has no `raw_answer`

In blocked cases, the interface shows metadata only and keeps the current
safety-first behavior.

## Validation commands and results

Commands run:

```bash
node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `navigator.js`: passed
- `navigator-store.js`: passed

## Safety guarantees

- no Canon changes
- no CSL changes
- no source ZIP changes
- no pipeline script changes
- no `build.py` changes
- no template changes
- no deploy changes
- no backend changes
- no provider execution from the UI
- no API or LLM call performed by this UI patch
- progressive enhancement preserved
- existing BeYond study metadata remains visible even when answer display is blocked

## Rollback instructions

Rollback this UI layer by reverting only:

```bash
git checkout -- pipeline/13-ssg/static/js/navigator.js
git checkout -- pipeline/13-ssg/static/css/navigator.css
rm -f AXIS_NAVIGATOR_VALIDATED_ANSWER_UI_CHECKPOINT.md
```

If a narrower rollback is preferred, remove only the `Validated Answer`
rendering block and related styles while preserving the existing `Answer
Validation` panel.

## Relationship to other layers

### Answer Validator

This UI is downstream of the `Answer Validator`.
It does not decide whether an answer is safe.
It only renders answer text after `display_allowed == true`.

### Gemini Vertex real call

This UI can display answers produced by the guarded Gemini Vertex provider,
including the validated local artifact:

- `outputs/nana/provider_runs/provider-dukkha-gemini-vertex-real-v1.json`

The UI does not execute Gemini.
It only reads the stored derivative result.

### BeYond Mode Study UI

This checkpoint extends the BeYond study chain from:

`Retrieval -> Prompt -> Gate -> Execution -> Council -> Provider -> Answer Validation`

to a visible read-only end state:

`Retrieval -> Prompt -> Gate -> Execution -> Council -> Provider -> Answer Validation -> Validated Answer`
