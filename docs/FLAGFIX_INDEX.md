# AXIS-NIDDHI FlagFix Navigational Index

This document is a navigational index for existing FlagFix policy, review scaffold, discussion, and checkpoint files in `docs/` and `review/`.

It does not move, rename, delete, supersede, or implement any existing FlagFix document.

## Batch 02 — Title and Metadata Integrity

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FLAGFIX_BATCH_02_TITLE_METADATA_INTEGRITY_PLAN.md` | Batch plan for title and metadata integrity | discussion | Groups title punctuation, slug/title divergence, protected title terms, capitalization, and date visibility review. |
| `docs/FLAGFIX_011_TITLE_PUNCTUATION_PRESERVATION_POLICY.md` | Title punctuation preservation | policy | Protects semantic punctuation such as dashes, questions, ellipses, and source-title force. |
| `docs/FLAGFIX_012_SLUG_TITLE_DIVERGENCE_POLICY.md` | Slug/title divergence | policy | Prevents slug-derived titles from overriding source title semantics. |
| `docs/FLAGFIX_013_PT_TITLE_CAPITALIZATION_POLICY.md` | Portuguese title capitalization | policy | Defines conservative pt-BR title casing review rules. |
| `docs/FLAGFIX_020_TITLE_COMPARISON_MATRIX.md` | Human title comparison workflow | review scaffold | Defines the review matrix before any title correction is considered. |
| `review/title-matrix/flagfix_020_title_comparison_matrix.csv` | Seed title comparison matrix | review scaffold | Contains initial human-review rows and decisions; no correction is authorized by the CSV alone. |
| `docs/FLAGFIX_021_MISSING_DATE_METADATA_REVIEW.md` | Missing or ambiguous date metadata | review scaffold | Documents date visibility review tasks before automated correction. |
| `docs/FLAGFIX_021_MISSING_DATE_REVIEW_BOX_POLICY.md` | Missing date review box behavior | policy | Sets conservative display policy for date review boxes and source-date uncertainty. |

## Batch 03 — Pāli Protection

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FLAGFIX_BATCH_03_PALI_PROTECTION_PLAN.md` | Batch plan for Pāli and protected terminology | discussion | Groups protected terms, diacritics, Pāli quotes, glossary behavior, and title protection. |
| `docs/FLAGFIX_002_PALI_TERM_COLOR_AUDIO_TAXONOMY_POLICY.md` | Pāli term color and audio taxonomy | policy | Preserves visible distinctions between glossary-only, audio-linked, and uncertain Pāli terms. |
| `docs/FLAGFIX_003_PALI_GRAMMAR_DIACRITICS_ORTHOGRAPHY_POLICY.md` | Pāli grammar, diacritics, and orthography | policy | Requires human review for spelling, macrons, grammar, and source-convention questions. |
| `docs/FLAGFIX_004_PALI_QUOTE_PROTECTION_POLICY.md` | Pāli quote protection | policy | Protects Pāli quotes and canonical phrases from translation-stage mutation. |
| `docs/FLAGFIX_007_TITLE_TRANSLATION_GLOSSARY_PROTECTION_POLICY.md` | Title translation glossary protection | policy | Protects doctrinal title terms during translation and title handling. |
| `docs/FLAGFIX_009_MICCHA_DITTHI_GLOSSARY_PROTECTION_POLICY.md` | Miccha Ditthi glossary protection | policy | Records a specific protected-term risk for Miccha Ditthi / Miccha Ditthi-like title handling. |

## Batch 04 — Media and Assets

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FLAGFIX_BATCH_04_MEDIA_ASSETS_PLAN.md` | Batch plan for media and assets | discussion | Groups image, audio, YouTube, and asset traceability issues. |
| `docs/FLAGFIX_005_TRANSLATABLE_IMAGE_FLOWCHART_ASSETS_POLICY.md` | Translatable image and flowchart assets | policy | Preserves original media as evidence before any human redraw or translation. |
| `docs/FLAGFIX_010_AUDIO_OFFLINE_PLACEHOLDER_POLICY.md` | Audio placeholders and external resolution | policy | Requires language-aware, traceable audio fallback states. |
| `docs/FLAGFIX_014_IMAGE_RENDERING_SIZE_CENTERING_ZOOM_POLICY.md` | Image rendering size, centering, and zoom | policy | Frames future image readability work without authorizing renderer or CSS changes. |
| `docs/FLAGFIX_015_YOUTUBE_PRINT_MARKER_POLICY.md` | YouTube print markers | policy | Preserves video evidence in print review even when embeds do not render. |
| `docs/FLAGFIX_MEDIA_SHORTCODE_PRESERVATION_PLAN.md` | Media shortcode preservation layer | discussion | Plans preservation blocks for legacy media/download shortcodes; no production behavior is authorized here. |

## Batch 05 — Architecture and Study Order

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FLAGFIX_BATCH_05_ARCHITECTURE_STUDY_ORDER_PLAN.md` | Batch plan for architecture and study order | discussion | Separates corpus order, archive order, review order, and future study paths. |
| `docs/FLAGFIX_000_AXIS_PRESERVATION_STRATEGY_POLICY.md` | AXIS preservation strategy | policy | Defines source traceability, canonical identity, reproducibility, and review boundaries. |
| `docs/FLAGFIX_001_FUTURE_PRESERVATION_LAYERS_POLICY.md` | Future preservation layers | policy | Describes future layers without authorizing implementation in production. |
| `docs/FLAGFIX_008_CANONICAL_STUDY_ORDER_PATH_REGISTRY_POLICY.md` | Canonical study order and path registry | policy | Requires explicit, auditable path registries instead of overwriting source order. |
| `docs/FLAGFIX_008B_AXIS_COSMOS_ORDER_GRAPH_DISCUSSION.md` | AXIS Cosmos order graph | discussion | Explores future graph/order concepts as discussion only. |

## Other FlagFix Records

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FLAGFIX_BATCH_01_PRINT_REVIEW_UX_PLAN.md` | Print Review UX batch plan | discussion | Existing Batch 01 planning record; included here for inventory completeness. |
| `docs/FLAGFIX_023_PRODUCTION_BUILD_INPUT_CONTRACT.md` | Production build input contract | policy | Architecture guardrail for rebuild assumptions, CSL presence, and publication-repo boundaries. |
| `docs/FLAGFIX_STATUS_CHECKPOINT_2026-05-02.md` | FlagFix status snapshot | checkpoint | Captures repository state and open issue groups after issue migration and early batch planning. |
| `docs/AXIS_HANDOFF_FLAGFIX_SPRINT_2026-05-03.md` | Post-sprint handoff | checkpoint | Records the final state of the policy/review-scaffold sprint completed around 2026-05-03 / 2026-05-04 UTC. |

## Guardrails

This index is navigational only.

It does not authorize implementation and does not authorize changes to renderer, CSL, HTML, CSS, JavaScript, pipeline, metadata, navigation, deployment config, Cloudflare config, or static-site output.

It does not authorize moving, renaming, deleting, editing, or superseding existing policy documents.

Generated static output remains out of scope unless separately approved with the required publication approval language.

## Next Review Gate

Any future implementation requires its own issue, branch, and PR.

Future implementation PRs must restate their exact scope, expected changed files, review risks, and affected production surfaces before any code, metadata, pipeline, renderer, CSL, navigation, deployment, Cloudflare, or static-site changes are made.
