# AXIS Handoff — FlagFix Policy Sprint — 2026-05-03

## Status

This document records the final state of the FlagFix policy/review-scaffold sprint completed on 2026-05-03 / 2026-05-04 UTC.

This is a handoff document for future AI-assisted work.

## Final Git State

Repository:

- `matikamata/axis-niddhi`

Final production branch state at sprint closure:

- branch: `main`
- latest confirmed commit: `9b83377`
- latest confirmed PR: `#76`
- latest confirmed merge: `docs: close FlagFix batch 05 checkpoint`

Cloudflare Pages:

- automatic deployments are enabled;
- production deployment succeeded for `main`;
- this sprint created many deployments because each docs-only PR triggered Cloudflare.

## What This Sprint Did

This sprint converted FlagFix issues into explicit policy, review, and architecture guardrail documents.

The sprint was intentionally documentation-first.

The work closed the current FlagFix planning surface without authorizing implementation.

## What This Sprint Did Not Do

This sprint did not intentionally change:

- renderer behavior;
- CSL content;
- HTML output;
- CSS output;
- JavaScript output;
- static-site generated content;
- asset maps;
- media files;
- image files;
- audio files;
- glossary behavior;
- translation behavior;
- navigation behavior;
- deployment configuration;
- pipeline behavior.

No functional implementation is authorized merely because these policy documents exist.

## Batch Summary

### Batch 02 — Title and Metadata Integrity

Closed as policy/review-scaffold scope.

Final artifacts:

- `docs/FLAGFIX_011_TITLE_PUNCTUATION_PRESERVATION_POLICY.md`
- `docs/FLAGFIX_012_SLUG_TITLE_DIVERGENCE_POLICY.md`
- `docs/FLAGFIX_013_PT_TITLE_CAPITALIZATION_POLICY.md`
- `docs/FLAGFIX_020_TITLE_COMPARISON_MATRIX.md`
- `review/title-matrix/flagfix_020_title_comparison_matrix.csv`
- `docs/FLAGFIX_021_MISSING_DATE_REVIEW_BOX_POLICY.md`

Guardrail:

No automatic title, slug, route, metadata, CSL, renderer, or static-site correction is authorized from Batch 02 alone.

### Batch 03 — Pāli Protection

Closed as policy/review-scaffold scope.

Final artifacts:

- `docs/FLAGFIX_002_PALI_TERM_COLOR_AUDIO_TAXONOMY_POLICY.md`
- `docs/FLAGFIX_003_PALI_GRAMMAR_DIACRITICS_ORTHOGRAPHY_POLICY.md`
- `docs/FLAGFIX_004_PALI_QUOTE_PROTECTION_POLICY.md`
- `docs/FLAGFIX_007_TITLE_TRANSLATION_GLOSSARY_PROTECTION_POLICY.md`
- `docs/FLAGFIX_009_MICCHA_DITTHI_GLOSSARY_PROTECTION_POLICY.md`

Guardrail:

No automatic Pāli, Dhamma term, quote, title, glossary, translation, CSL, renderer, HTML, CSS, JavaScript, or static-site output changes are authorized from Batch 03 alone.

### Batch 04 — Media and Assets

Closed as policy/review-scaffold scope.

Final artifacts:

- `docs/FLAGFIX_005_TRANSLATABLE_IMAGE_FLOWCHART_ASSETS_POLICY.md`
- `docs/FLAGFIX_010_AUDIO_OFFLINE_PLACEHOLDER_POLICY.md`
- `docs/FLAGFIX_014_IMAGE_RENDERING_SIZE_CENTERING_ZOOM_POLICY.md`
- `docs/FLAGFIX_015_YOUTUBE_PRINT_MARKER_POLICY.md`

Guardrail:

No renderer, CSL, HTML, CSS, JavaScript, asset map, image, audio, YouTube, print, OCR, translation, external URL, or static-site output changes are authorized from Batch 04 alone.

### Batch 05 — Architecture and Study Order

Closed as policy/review-scaffold scope.

Final artifacts:

- `docs/FLAGFIX_000_AXIS_PRESERVATION_STRATEGY_POLICY.md`
- `docs/FLAGFIX_001_FUTURE_PRESERVATION_LAYERS_POLICY.md`
- `docs/FLAGFIX_008_CANONICAL_STUDY_ORDER_PATH_REGISTRY_POLICY.md`
- `docs/FLAGFIX_008B_AXIS_COSMOS_ORDER_GRAPH_DISCUSSION.md`

Guardrail:

No architecture, preservation-layer, study-order, graph, retrieval, AI, metadata, navigation, pipeline, deployment, or static-site output implementation is authorized from Batch 05 alone.

## Final Issue State

At the end of the sprint, the FlagFix list returned no remaining open FlagFix issues.

All active FlagFix issues in the reviewed sprint scope were closed after their corresponding policy/review documents were merged.

## Important Operational Lesson

Each small docs-only PR triggered a Cloudflare Pages deployment because automatic deployments are enabled for `main`.

This caused a large number of deployments even though no static-site functional content was intentionally changed.

Future docs-only policy work should consider one of these approaches:

1. batch several docs into one branch and one PR;
2. temporarily disable production auto-deploys for pure documentation sprints, if safe and desired;
3. move internal planning docs to a non-deploying repository or workspace;
4. configure Cloudflare ignore/build rules only after explicit review.

No Cloudflare configuration change has been authorized by this sprint.

## Current Concern

The top-level `docs/` directory is becoming crowded.

Observed issue:

- many FlagFix policy files now sit flat in `docs/`;
- this is traceable but visually noisy;
- future maintainability may improve by moving FlagFix docs into a subdirectory.

Recommended future docs reorganization:

- `docs/flagfix/policies/`
- `docs/flagfix/checkpoints/`
- `docs/flagfix/plans/`
- `docs/flagfix/reviews/`
- `docs/flagfix/handoffs/`

This reorganization should be docs-only and should not modify code, site generation, static output, Cloudflare config, or pipeline behavior.

## Recommended Next Step

Open a new branch for a docs-only reorganization proposal.

Suggested branch:

- `docs-flagfix-archive-reorg-plan`

Suggested first document:

- `docs/FLAGFIX_DOCS_REORGANIZATION_PLAN_2026-05-04.md`

Do not move files immediately unless a separate review approves the path changes.

First document should define:

- current docs sprawl;
- proposed target folder layout;
- redirect/reference implications;
- whether GitHub issue links will remain readable;
- whether internal references need updates;
- whether the static site includes docs files;
- whether Cloudflare deploy behavior should be changed later.

## Future Implementation Rule

Any future implementation must start from a new issue and branch.

Implementation must state explicitly which prior policy document it follows.

Implementation must prove that it does not silently change canonical content.

Implementation must include a minimal diff, review checklist, and rollback path.

## Handoff Prompt For New Chat

Use this prompt when opening a new chat:

Read `docs/AXIS_HANDOFF_FLAGFIX_SPRINT_2026-05-03.md` as the canonical handoff for the completed FlagFix policy sprint.

Do not infer implementation authorization from the existence of policy documents.

Current goal: continue safely from the final sprint state.

Default next step: plan a docs-only FlagFix documentation reorganization without changing renderer, CSL, HTML, CSS, JavaScript, pipeline, Cloudflare config, asset maps, metadata, navigation, or static-site output.

Main is sacred.
No deployment or functional behavior change unless explicitly requested.
