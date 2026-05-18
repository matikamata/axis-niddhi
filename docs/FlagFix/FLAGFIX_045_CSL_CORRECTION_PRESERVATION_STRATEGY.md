# FlagFix 045 - CSL Correction Preservation Strategy

Date: 2026-05-18

## Problem Statement

Recent FlagFix batches corrected title metadata on disk under:

- `pipeline/09-csl/*/meta/identity.json`

Those corrections fixed known local CSL metadata problems, but `pipeline/09-csl` is ignored by Git in this workspace. The tracked PRs preserve documentation and review CSV evidence, not the actual `identity.json` diffs.

Before any static regeneration, rebuild, migration, or Vitrine promotion, AXIS needs a safe way to preserve and verify those local CSL metadata corrections.

## Known Correction Batches

- #FlagFix_028: corrected `LD.AA.000` `titles.pt` from `Vivendo il Dhamma` to `Vivendo o Dhamma`.
- #FlagFix_037: corrected `BA.AA.004` `titles.en` from `Viparie1B987Ama Two Meanings` to `Vipariṇāma Two Meanings`.
- #FlagFix_039: corrected EN batch 1: `BA.AA.001`, `BA.AA.005`, `BM.CC.006`, `DS.DD.005`, `IS.BB.004`.
- #FlagFix_040: corrected EN batch 2: `CH.AA.005`, `DS.DD.003`, `DS.DD.007`, `ER.FF.004`, `KD.DD.005`.
- #FlagFix_041: corrected EN batch 3: `KD.II.010`, `KD.JJ.010`, `KD.JJ.011`, `PS.DD.004`, `PS.GG.004`.
- #FlagFix_042: corrected final EN batch: `PS.II.011`, `TL.II.008`, `TL.II.013`.
- #FlagFix_043: corrected PT cleanup batch: `KD.DD.005`, `KD.II.010`, `KD.JJ.010`, `TL.II.008`, `TL.II.013`.

Current known audit result:

- checked: 748 identity files
- EN hits: 0
- PT hits: 0
- total suspicious title hits: 0

## Risk Analysis

- A future full pipeline rebuild may overwrite local CSL metadata corrections.
- Git does not track `pipeline/09-csl`, so normal PR review cannot see the corrected metadata values directly.
- Static regeneration may or may not pick up corrected local CSL depending on which workspace state is used.
- Existing docs and CSVs prove operator intent and evidence, but they are not executable correction manifests.
- If a workspace refresh restores older CSL metadata, the static site could regenerate with stale corrupted titles even though the tracked docs say the cleanup is closed.
- Changing `.gitignore` quickly could create noisy or overly broad tracking of generated/intermediate CSL content.

## Preservation Options

### Option A - Tracked Correction Manifest

Create a tracked JSON or CSV manifest outside the ignored CSL tree. Each row/object records:

- PD#PN
- file path
- JSON field path, such as `titles.en` or `titles.pt`
- old value when known
- expected corrected value
- evidence source
- originating FlagFix

Pros:

- Reviewable in Git.
- Small and explicit.
- Can be validated read-only before any apply step exists.
- Can later be consumed by an apply script after review.

Cons:

- Requires a new manifest format and validator.
- Does not by itself modify CSL unless paired with a later apply script.

### Option B - Track Selected CSL Patches Outside Ignored Tree

Store patch files or before/after snippets under a tracked review or metadata-preservation directory.

Pros:

- Preserves exact diffs without changing `.gitignore`.
- Human-readable and PR-reviewable.

Cons:

- Harder to apply deterministically than structured JSON/CSV.
- Patch drift is likely if surrounding JSON changes.

### Option C - Change `.gitignore` to Track Selected `identity.json` Files

Adjust ignore rules so selected CSL metadata files become tracked.

Pros:

- Git would preserve exact corrected files.
- Simple mental model once configured.

Cons:

- Risk of accidentally tracking broader generated CSL material.
- May blur source/generated boundaries.
- Should not be done until the team agrees which CSL metadata is canonical.

### Option D - Formal Post-CSL-Build Remediation Step

Add a pipeline step that applies approved metadata corrections after CSL generation and before static generation.

Pros:

- Fits deterministic pipeline execution.
- Protects future rebuilds if the upstream source still contains bad metadata.

Cons:

- Requires pipeline behavior changes.
- Needs tests/validation and a careful rollout.
- Too much for a docs-only sprint.

### Option E - Regenerate Canonical Source, Then Apply Manifest

Treat the ignored CSL tree as rebuildable. On refresh, regenerate or restore CSL, then apply a tracked manifest deterministically and validate.

Pros:

- Clean separation between generated CSL and durable corrections.
- Works well with Option A.
- Good long-term path if CSL remains ignored.

Cons:

- Requires the regeneration/apply order to be documented and enforced.
- Needs tooling before it is safe for operators.

## Preferred Recommendation

Preferred path:

1. Create a tracked correction manifest in the next sprint.
2. Add a read-only validator that compares the manifest against current `pipeline/09-csl/*/meta/identity.json`.
3. Keep the validator non-mutating at first.
4. Add an apply script only after manifest format and validator output are reviewed.
5. Do not change `.gitignore` until the canonical CSL ownership strategy is approved.

This gives us a durable, reviewable record without rushing into pipeline behavior changes or broad Git tracking changes.

## Proposed Next Sprint

Suggested next sprint:

`#FlagFix_046 - CSL title correction manifest and read-only validator`

Proposed scope:

- Create a tracked manifest for #028 and #037-#043 title metadata corrections.
- Add a read-only validator that reports match/mismatch/missing file cases.
- Do not write to CSL.
- Do not run build/pipeline/deploy.
- Do not change `.gitignore`.
- Do not create an apply script yet.

## Explicit Non-Actions

This sprint did not:

- create a manifest;
- create a validator;
- create an apply script;
- modify `.gitignore`;
- modify CSL content;
- modify static artifacts;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11 behavior;
- run build, pipeline, deploy, DeepL, translation, Netlify, or Vitrine promotion.

## Operational Note

Static artifacts remain stale until an approved regeneration batch. Before that regeneration, the team should preserve the CSL corrections through a tracked manifest and validator so the regenerated static site reflects the corrected metadata.
