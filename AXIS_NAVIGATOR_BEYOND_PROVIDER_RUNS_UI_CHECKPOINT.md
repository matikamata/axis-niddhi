# AXIS Navigator BeYond Provider Runs UI Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files modified

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

## UI sections added

Inside the existing `NANA Study` area in BeYond Mode, the following Provider UI was added after the Council block:

- `Provider Runs`
  - `provider_run_id`
  - `concept_id`
  - `provider`
  - `provider_status`
  - `provider_decision`
  - `llm_called`
  - `answer_generated`
- compact provider run cards
  - `provider=none` shown as safe neutral state
  - `provider=mock` shown as simulated placeholder state
- collapsed mock preview
  - label: `Simulated placeholder — no model was called`
  - preview only shown for mock runs with `simulated_answer`

Safety display behavior:

- `LLM called` is always shown visibly
- if any loaded provider run reports `llm_called != false`
  - a warning message is shown
  - simulated preview is hidden

Visual status mapping:

- `not_configured` -> neutral
- `mocked` -> blue-gray / info
- `BLOCKED_BY_GATE` -> warn / danger
- `DRY_RUN_ONLY` -> neutral
- `MOCK_ONLY` -> blue / info

## Data sources read

The UI reads local static JSON artifacts only:

- `outputs/nana/context-pack-*.json`
- `outputs/nana/prompts/prompt-*.json`
- `outputs/nana/gates/gate-*.json`
- `outputs/nana/execution/execution-*.json`
- `outputs/nana/council/council-*.json`
- `outputs/nana/provider_runs/provider-*.json`

More specifically for provider runs:

- `outputs/nana/provider_runs/provider-<concept>-none-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-<concept>-mock-bootstrap-v1.json`

No backend calls are made.
No provider execution occurs.
No real model calls are made.
No data is mutated.

## Visibility rules

Provider Runs UI appears only when all conditions are true:

- internal cockpit mode is `javana`
- `study_mode == true`

UI label may show `BeYond Mode`, but internal mode value remains:

- `javana`

Provider Runs UI stays hidden in:

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
- `Kulla Mode` -> no Provider Runs UI
- `Orbit Mode` -> no Provider Runs UI
- `BeYond Mode` + `Study Mode OFF` -> no Provider Runs UI
- `BeYond Mode` + `Study Mode ON` -> Provider Runs appears
- `provider=none` renders safely
- `provider=mock` renders placeholder only
- `LLM called` is visibly `false`
- existing Quick Find / Outline / Related Pages / NANA Study / Council remain functional

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
  - if provider JSON is missing, UI shows `No Provider Run data available`
  - if provider JSON is unsafe, simulated preview is suppressed

## What remains intentionally unimplemented

- no real provider execution from Navigator
- no OpenAI / Vertex / local model calls
- no provider configuration UI
- no credential handling
- no answer generation
- no semantic comparison between provider outputs
- no backend sync
- no publication-pipeline integration

## Rollback instructions

Revert only the BeYond Provider Runs UI integration files:

```bash
rm -f AXIS_NAVIGATOR_BEYOND_PROVIDER_RUNS_UI_CHECKPOINT.md
git diff -- pipeline/13-ssg/static/js/navigator.js pipeline/13-ssg/static/css/navigator.css
```

Manual rollback scope:

- remove Provider Runs fetch/cache/render logic from `pipeline/13-ssg/static/js/navigator.js`
- remove Provider Runs presentation styles from `pipeline/13-ssg/static/css/navigator.css`

If desired, the broader `NANA Study` and `Council Simulation` integration can remain while only the Provider Runs block is removed.

## Relationship to Navigator BeYond Council UI and NANA Provider Adapter Dry Run

This layer sits on top of two earlier foundations:

- `AXIS Navigator BeYond Council UI`
  - exposed the local study chain up through Council inside BeYond Mode
  - established the `NANA Study` workspace area and lazy artifact loading pattern
- `AXIS NANA Provider Adapter Dry Run`
  - created deterministic local provider run artifacts
  - introduced `none` and `mock` provider modes
  - enforced gate-respecting behavior before any future provider execution

Practical relationship:

- `BeYond Council UI` makes the study chain visible through Council
- `Provider Adapter Dry Run` produces safe provider-run artifacts
- `BeYond Provider Runs UI` is the read-only viewer that extends the visible chain inside Navigator

In short:

- `BeYond Council UI` = visible study/council layer
- `Provider Adapter Dry Run` = safe provider abstraction artifacts
- `BeYond Provider Runs UI` = local read-only provider visibility inside Navigator

This makes the visible BeYond chain:

```text
Retrieval -> Prompt -> Gate -> Execution -> Council -> Provider Adapter
```

without activating any real model or provider runtime.
