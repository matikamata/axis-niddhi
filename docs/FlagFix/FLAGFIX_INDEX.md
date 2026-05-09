# AXIS-NIDDHI FlagFix Navigational Index

This document is the current navigational index for FlagFix policy, review scaffold, discussion, and checkpoint files in `docs/FlagFix/` and `review/`.

This index is navigational only. The current directory layout is maintained by Git history; this document does not authorize future moves, deletions, superseding, or implementation.

## Batch 01 — Print Review UX

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FlagFix/FLAGFIX_BATCH_01_PRINT_REVIEW_UX_PLAN.md` | Print Review UX batch plan | discussion | Existing Batch 01 planning record; included here for inventory completeness. |
| `docs/FlagFix/FLAGFIX_BATCH_01_CLOSURE_RECORD_2026-05-04.md` | Batch 01 closure record | checkpoint | Records final Print Review UX closure state, global decisions, and guardrails; no implementation is authorized here. |
| `docs/FlagFix/FLAGFIX_006_PRINT_NAV_LABEL_LOCALIZATION.md` | Print navigation label localization | review scaffold | Tracks English `From` / `To` labels appearing in printed/PDF review navigation. |
| `docs/FlagFix/FLAGFIX_016_PRINT_MARGIN_CONTENT_WIDTH_ALIGNMENT.md` | Print margins and optical centering | closed / no additional global patch recommended now | Current print margin/content-width behavior is acceptable after related fixes; PR #84 resolved the urgent image-driven overflow case. |
| `docs/FlagFix/FLAGFIX_017_PRINT_GREEN_LINE_DECORATION_STANDARDIZATION.md` | Print green line decoration standardization | review scaffold | Tracks inconsistent green line decoration in printed review output. |
| `docs/FlagFix/FLAGFIX_018_PRINT_DRAFT_BANNER_TYPOGRAPHY_GRAY_TONE.md` | Print draft banner typography and gray-tone design | closed / no implementation recommended now | Current banner behavior is acceptable for review workflow; future typography or print-menu polish may be handled separately. |
| `docs/FlagFix/FLAGFIX_019_PRINT_PREV_NEXT_NAV_COMPACTION_AND_BOX_DESIGN.md` | Print previous/next navigation compaction | review scaffold | Tracks compact boxed print navigation and label treatment near the final page of essays. |
| `docs/FlagFix/FLAGFIX_024_PRINT_INCONSISTENCIA_VISUAL_TITULO_H5.md` | Print H5 title visual inconsistency | implemented | Resolved by PR #86 / commit `d798a86`; checkpoint `checkpoint/flagfix-024-print-h5-standardization-20260504`. |
| `docs/FlagFix/FLAGFIX_025_PRINT_COMPACT_LAYOUT_BD_AA_007.md` | Compact print layout on BD.AA.007 | review scaffold | Tracks unusually narrow/compact print layout on the BD.AA.007 review page. |

## Batch 02 — Title and Metadata Integrity

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FlagFix/FLAGFIX_BATCH_02_TITLE_METADATA_INTEGRITY_PLAN.md` | Batch plan for title and metadata integrity | discussion | Groups title punctuation, slug/title divergence, protected title terms, capitalization, and date visibility review. |
| `docs/FlagFix/FLAGFIX_BATCH_02_PARTIAL_CHECKPOINT_2026-05-04.md` | Batch 02 partial checkpoint | checkpoint | Consolidates the current 020/021 review state, supporting policies, and Batch 02 guardrails while human decisions remain pending. |
| `docs/FlagFix/FLAGFIX_BATCH_02_CLOSURE_RECORD_2026-05-04.md` | Batch 02 closure record | checkpoint | Closes Batch 02 as a planning/review-control batch and records that 007/011/012/013 are covered by the 020 matrix workflow while 020/021 remain paused for human review. |
| `docs/FlagFix/FLAGFIX_011_TITLE_PUNCTUATION_PRESERVATION_POLICY.md` | Title punctuation preservation | policy | Protects semantic punctuation such as dashes, questions, ellipses, and source-title force. |
| `docs/FlagFix/FLAGFIX_012_SLUG_TITLE_DIVERGENCE_POLICY.md` | Slug/title divergence | policy | Prevents slug-derived titles from overriding source title semantics. |
| `docs/FlagFix/FLAGFIX_013_PT_TITLE_CAPITALIZATION_POLICY.md` | Portuguese title capitalization | policy | Defines conservative pt-BR title casing review rules. |
| `docs/FlagFix/FLAGFIX_020_TITLE_COMPARISON_MATRIX.md` | Human title comparison workflow | review scaffold | Defines the review matrix before any title correction is considered. |
| `docs/FlagFix/FLAGFIX_020_TITLE_MATRIX_EXPANSION_PLAN_2026-05-04.md` | Title comparison matrix expansion plan | discussion | Plans controlled pilot expansion of the human-review matrix; no title corrections, scripts, metadata changes, or rebuilds are authorized here. |
| `docs/FlagFix/FLAGFIX_020_TITLE_MATRIX_PILOT_CHECKPOINT_2026-05-04.md` | Title comparison matrix pilot checkpoint | checkpoint | Records matrix state after PR #98: header plus six rows, human review pending, and no title corrections applied. |
| `review/title-matrix/flagfix_020_title_comparison_matrix.csv` | Seed title comparison matrix | review scaffold | Contains initial human-review rows and decisions; no correction is authorized by the CSV alone. |
| `docs/FlagFix/FLAGFIX_021_MISSING_DATE_METADATA_REVIEW.md` | Missing or ambiguous date metadata | review scaffold | Documents date visibility review tasks before automated correction. |
| `docs/FlagFix/FLAGFIX_021_MISSING_DATE_REVIEW_BOX_POLICY.md` | Missing date review box behavior | policy | Sets conservative display policy for date review boxes and source-date uncertainty. |
| `docs/FlagFix/FLAGFIX_021_MISSING_DATE_METADATA_AUDIT_2026-05-04.md` | Missing date metadata audit | checkpoint | Records the current audit totals for visible top dates versus candidate missing-date pages; no date correction or inference is authorized here. |
| `docs/FlagFix/FLAGFIX_021_DATE_METADATA_AUDIT_CHECKPOINT_2026-05-04.md` | Missing date metadata audit checkpoint | checkpoint | Freezes the post-audit state: 748 pages scanned, 63 candidates, 25 CSV rows, review box absent, and human review still pending. |
| `review/date-metadata/flagfix_021_missing_date_metadata_audit.csv` | Missing date metadata audit CSV | review scaffold | Small reviewable subset from the current date-visibility audit, including control and comment-only cases; human review remains pending. |

## Batch 03 — Pāli Protection

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FlagFix/FLAGFIX_BATCH_03_PALI_PROTECTION_PLAN.md` | Batch plan for Pāli and protected terminology | discussion | Groups protected terms, diacritics, Pāli quotes, glossary behavior, and title protection. |
| `docs/FlagFix/FLAGFIX_BATCH_03_PALI_PROTECTION_AUDIT_2026-05-04.md` | Batch 03 Pāli protection audit | checkpoint | Pilot read-only inventory of glossary/audio term markers, quote preservation, diacritic drift, and Miccha/Micchā title/body evidence; no implementation is authorized here. |
| `docs/FlagFix/FLAGFIX_BATCH_03_CLOSURE_RECORD_2026-05-04.md` | Batch 03 closure record | checkpoint | Closes Batch 03 as an inventory/review-control batch, records the audit artifacts, and keeps 002/003/004/009 in human-review-first posture with no new patches authorized. |
| `docs/FlagFix/FLAGFIX_002_PALI_TERM_COLOR_AUDIO_TAXONOMY_POLICY.md` | Pāli term color and audio taxonomy | policy | Preserves visible distinctions between glossary-only, audio-linked, and uncertain Pāli terms. |
| `docs/FlagFix/FLAGFIX_003_PALI_GRAMMAR_DIACRITICS_ORTHOGRAPHY_POLICY.md` | Pāli grammar, diacritics, and orthography | policy | Requires human review for spelling, macrons, grammar, and source-convention questions. |
| `docs/FlagFix/FLAGFIX_004_PALI_QUOTE_PROTECTION_POLICY.md` | Pāli quote protection | policy | Protects Pāli quotes and canonical phrases from translation-stage mutation. |
| `docs/FlagFix/FLAGFIX_007_TITLE_TRANSLATION_GLOSSARY_PROTECTION_POLICY.md` | Title translation glossary protection | policy | Protects doctrinal title terms during translation and title handling. |
| `docs/FlagFix/FLAGFIX_009_MICCHA_DITTHI_GLOSSARY_PROTECTION_POLICY.md` | Miccha Ditthi glossary protection | policy | Records a specific protected-term risk for Miccha Ditthi / Miccha Ditthi-like title handling. |
| `review/pali-protection/flagfix_batch03_pali_protection_audit.csv` | Batch 03 Pāli protection audit CSV | review scaffold | Small reviewable evidence set for glossary/audio markers, Pāli quotes, diacritic preservation, and Miccha/Micchā divergence; human review remains pending. |

## Batch 04 — Media and Assets

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FlagFix/FLAGFIX_BATCH_04_MEDIA_ASSETS_PLAN.md` | Batch plan for media and assets | discussion | Groups image, audio, YouTube, and asset traceability issues. |
| `docs/FlagFix/FLAGFIX_BATCH_04_MEDIA_ASSETS_AUDIT_2026-05-04.md` | Batch 04 media and assets audit | checkpoint | Pilot read-only inventory of text-bearing images, diagrams, YouTube/embed variants, audio traceability, and media-evidence cross-references; no implementation is authorized here. |
| `docs/FlagFix/FLAGFIX_BATCH_04_CLOSURE_RECORD_2026-05-04.md` | Batch 04 closure record | checkpoint | Closes Batch 04 as an audit/inventory/review-control batch, keeps 014 split-friendly, and records that 022 remains in its own dedicated hardening package. |
| `docs/FlagFix/FLAGFIX_027_AUDIO_PLAYBACK_APPLE_DEVICES.md` | Apple/Safari local audio playback on Cloudflare | deferred | Records this as a known deployment-surface limitation: Netlify full-folder deploy remains the audio-complete showcase path; Cloudflare GitHub-linked deploy may remain audio-incomplete until a future asset-publish strategy is approved. |
| `docs/FlagFix/FLAGFIX_005_TRANSLATABLE_IMAGE_FLOWCHART_ASSETS_POLICY.md` | Translatable image and flowchart assets | policy | Preserves original media as evidence before any human redraw or translation. |
| `docs/FlagFix/FLAGFIX_010_AUDIO_OFFLINE_PLACEHOLDER_POLICY.md` | Audio placeholders and external resolution | policy | Requires language-aware, traceable audio fallback states. |
| `docs/FlagFix/FLAGFIX_014_IMAGE_RENDERING_SIZE_CENTERING_ZOOM_POLICY.md` | Image rendering size, centering, and zoom | policy | Frames future image readability work without authorizing renderer or CSS changes. |
| `docs/FlagFix/FLAGFIX_015_YOUTUBE_PRINT_MARKER_POLICY.md` | YouTube print markers | policy | Preserves video evidence in print review even when embeds do not render. |
| `review/media-assets/flagfix_batch04_media_assets_audit.csv` | Batch 04 media and assets audit CSV | review scaffold | Small reviewable evidence set for image/diagram context, embed variants, audio traceability, and cross-reference rows related to media evidence blocks. |
| `docs/FlagFix/FLAGFIX_022_SHORTCODE_WORDPRESS_EASY_MEDIA_DOWNLOAD.md` | WordPress `easy_media_download` shortcode leakage | partially implemented / hardening pending | Original reader-facing leak is operationally resolved via media evidence blocks; corpus-wide hardening remains. |
| `docs/FlagFix/FLAGFIX_022_MEDIA_EVIDENCE_AUDIT_2026-05-04.md` | Media evidence block audit | checkpoint | Read-only audit of `axis-media-evidence`, corrupted shortcode evidence, affected pages, and future hardening sub-issues. |
| `docs/FlagFix/FLAGFIX_022_HARDENING_ROADMAP_2026-05-04.md` | FLAGFIX_022 hardening roadmap | discussion | Coordinates the umbrella record, audit, 022A URL hardening plan, and 022B markup normalization plan; no implementation is authorized here. |
| `docs/FlagFix/FLAGFIX_022A_CORRUPTED_URL_HARDENING_PLAN_2026-05-04.md` | Corrupted URL hardening for legacy media shortcodes | discussion | Plans future protection of legacy media shortcode URLs before glossary/Pāli marginalia; no implementation is authorized here. |
| `docs/FlagFix/FLAGFIX_022B_MEDIA_EVIDENCE_MARKUP_PLAN_2026-05-04.md` | Media evidence block markup normalization | discussion | Plans future normalization of `axis-media-evidence` blocks outside invalid parent contexts; no implementation is authorized here. |
| `docs/FlagFix/FLAGFIX_MEDIA_SHORTCODE_PRESERVATION_PLAN.md` | Media shortcode preservation layer | discussion | Plans preservation blocks for legacy media/download shortcodes; no production behavior is authorized here. |

## Batch 05 — Architecture and Study Order

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FlagFix/FLAGFIX_BATCH_05_ARCHITECTURE_STUDY_ORDER_PLAN.md` | Batch plan for architecture and study order | discussion | Separates corpus order, archive order, review order, and future study paths. |
| `docs/FlagFix/FLAGFIX_BATCH_05_ARCHITECTURE_CHECKPOINT_2026-05-04.md` | Batch 05 architecture checkpoint | checkpoint | Records Batch 05 as architecture/planning boundary only, confirms AXIS-Cosmos is still discussion-stage, and authorizes no registry, graph, UI, or production implementation. |
| `docs/FlagFix/FLAGFIX_000_AXIS_PRESERVATION_STRATEGY_POLICY.md` | AXIS preservation strategy | policy | Defines source traceability, canonical identity, reproducibility, and review boundaries. |
| `docs/FlagFix/FLAGFIX_001_FUTURE_PRESERVATION_LAYERS_POLICY.md` | Future preservation layers | policy | Describes future layers without authorizing implementation in production. |
| `docs/FlagFix/FLAGFIX_008_CANONICAL_STUDY_ORDER_PATH_REGISTRY_POLICY.md` | Canonical study order and path registry | policy | Requires explicit, auditable path registries instead of overwriting source order. |
| `docs/FlagFix/FLAGFIX_008B_AXIS_COSMOS_ORDER_GRAPH_DISCUSSION.md` | AXIS Cosmos order graph | discussion | Explores future graph/order concepts as discussion only. |

## Other FlagFix Records

| Path | Theme | Status | Observation |
|---|---|---|---|
| `docs/FlagFix/FLAGFIX_023_PRODUCTION_BUILD_INPUT_CONTRACT.md` | Production build input contract | policy | Architecture guardrail for rebuild assumptions, CSL presence, and publication-repo boundaries. |
| `docs/FlagFix/FLAGFIX_GLOBAL_SANITY_CHECKPOINT_2026-05-04.md` | Global sanity checkpoint after Batch 04 | checkpoint | Sprint-wide checkpoint through Batch 04 closure, summarizing implemented fixes versus docs/review-control work and authorizing no new implementation. |
| `docs/FlagFix/FLAGFIX_SPRINT_FINAL_CLOSURE_RECORD_2026-05-04.md` | Final FlagFix sprint closure record | checkpoint | Summarizes the completed sprint through Batch 05 checkpoint, records implemented fixes and review-control artifacts, and authorizes no new implementation. |
| `docs/FlagFix/PRINT_REVIEW_LINKS_V1_LEGACY_REVIEW_2026-05-04.md` | Legacy print review links branch assessment | review scaffold | Reviews `print-review-links-v1` as reference only; does not authorize merge, cherry-pick, or implementation. |
| `docs/FlagFix/FLAGFIX_STATUS_CHECKPOINT_2026-05-02.md` | FlagFix status snapshot | checkpoint | Captures repository state and open issue groups after issue migration and early batch planning. |
| `docs/FlagFix/AXIS_HANDOFF_FLAGFIX_SPRINT_2026-05-03.md` | Post-sprint handoff | checkpoint | Records the final state of the policy/review-scaffold sprint completed around 2026-05-03 / 2026-05-04 UTC. |

## Guardrails

This index is navigational only.

It does not authorize implementation and does not authorize changes to renderer, CSL, HTML, CSS, JavaScript, pipeline, metadata, navigation, deployment config, Cloudflare config, or static-site output.

It does not authorize further moving, renaming, deleting, editing, or superseding existing policy documents.

Generated static output remains out of scope unless separately approved with the required publication approval language.

## Next Review Gate

Any future implementation requires its own issue, branch, and PR.

Future implementation PRs must restate their exact scope, expected changed files, review risks, and affected production surfaces before any code, metadata, pipeline, renderer, CSL, navigation, deployment, Cloudflare, or static-site changes are made.
