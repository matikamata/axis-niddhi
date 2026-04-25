# AXIS Navigator BeYond Council UI Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files modified

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

## UI sections added

Inside the existing `NANA Study` area in BeYond Mode, the following Council UI was added:

- `Council Simulation` summary block
  - `council_id`
  - `concept_id`
  - `consensus_status`
  - `citation_agreement_score`
  - `hallucination_risk`
  - candidate count
  - `llm_called`
- compact candidate cards
  - `candidate_id`
  - `provider`
  - `answer_status`
  - `cited_refs`
  - `external_claims_detected`
  - `notes`

Visual status mapping:

- `NO_REAL_COUNCIL_YET` -> neutral / blue-gray
- `CITATION_CONSENSUS` -> green
- `DISSENT_REVIEW_REQUIRED` -> warn / yellow

## Data sources read

The UI reads local static JSON artifacts only:

- `outputs/nana/context-pack-*.json`
- `outputs/nana/prompts/prompt-*.json`
- `outputs/nana/gates/gate-*.json`
- `outputs/nana/execution/execution-*.json`
- `outputs/nana/council/council-*.json`

No backend calls are made.
No real model calls are made.
No data is mutated.

## Visibility rules

Council UI appears only when all conditions are true:

- internal cockpit mode is `javana`
- `study_mode == true`

UI label may show `BeYond Mode`, but internal mode value remains:

- `javana`

Council UI stays hidden in:

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
- `Kulla Mode` -> no Council UI
- `Orbit Mode` -> no Council UI
- `BeYond Mode` + `Study Mode OFF` -> no Council UI
- `BeYond Mode` + `Study Mode ON` -> Council Simulation appears
- candidate cards render
- `llm_called` is visibly `false`
- existing Quick Find / Outline / Related Pages remain functional

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
  - if council JSON is missing, UI shows `No Council data available`

## What remains intentionally unimplemented

- no real council execution
- no multi-model comparison engine
- no doctrinal answer generation
- no semantic dissent analysis
- no hallucination scoring beyond the static council artifact fields
- no backend sync
- no publication-pipeline integration

## Rollback instructions

Revert only the BeYond Council UI integration files:

```bash
rm -f AXIS_NAVIGATOR_BEYOND_COUNCIL_UI_CHECKPOINT.md
git diff -- pipeline/13-ssg/static/js/navigator.js pipeline/13-ssg/static/css/navigator.css
```

Manual rollback scope:

- remove Council fetch/cache/render logic from `pipeline/13-ssg/static/js/navigator.js`
- remove Council presentation styles from `pipeline/13-ssg/static/css/navigator.css`

If desired, the broader `NANA Study` integration can remain while only the Council block is removed.

## Relationship to Navigator v1.2 and NANA Council Simulation

This layer sits on top of two earlier foundations:

- `AXIS-NAVIGATOR v1.2`
  - introduced Javana / BeYond workspace structure
  - created the visual cockpit area where advanced study panels can live
- `AXIS NANA Council Simulation`
  - created deterministic local council artifacts
  - exposed candidate placeholders, citation agreement, and consensus fields

Practical relationship:

- Navigator v1.2 provides the BeYond workspace shell
- NANA Council Simulation provides the local JSON artifacts
- BeYond Council UI is the read-only viewer that makes those artifacts visible inside Navigator

In short:

- `Navigator v1.2` = advanced cockpit surface
- `NANA Council Simulation` = local council data
- `BeYond Council UI` = visual Council layer inside Navigator
