# FLAGFIX_031 - Fence retired translation scripts before next batch

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Scope: minimal execution guards plus documentation

## Purpose

Fence retired, legacy, hardcoded, or emergency translation/title scripts so they cannot be run accidentally before the next translation batch.

This follows:

- #FlagFix_028: corrected `LD.AA.000` PT title contamination.
- #FlagFix_029: identified old DeepL/title paths and scripts needing retirement/formalization.
- #FlagFix_030: added a read-only PT title language contamination QA gate.

## Inspection and decisions

| Script | Status | Fenced | Override |
|---|---|---:|---|
| `pipeline/scripts/legacy/05_translate_pilot_v5_surgeon.py` | Retired DeepL pilot with hardcoded old base path and legacy DeepL credential handling risk. Still executable and risky. | Yes | `AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1` |
| `pipeline/scripts/legacy/05a_upload_glossary_deepl.py` | Retired glossary upload path with hardcoded old base path and legacy DeepL credential handling risk. Can call DeepL and write glossary ID. | Yes | `AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1` |
| `pipeline/scripts/legacy/07b_execute_menu_v3_guardian.py` | Retired DeepL translation executor with hardcoded old base path, glossary ID, and legacy DeepL credential handling risk. Can translate title/body and write metadata. | Yes | `AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1` |
| `pipeline/scripts/legacy/14_sync_titles_from_ledger.py` | Retired title sync from old ledger path. Can rewrite EN titles and reset `titles.pt`/`pt_source` to null. | Yes | `AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1` |
| `pipeline/scripts/legacy/S10_execute_translation_deepl.py` | Retired SP10 predecessor. Superseded by core `SP10_translate_deepl.py`; still executable and can translate/write. | Yes | `AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1` |
| `pipeline/scripts/tools/run_sp11_and_report.sh` | Useful concept but hardcoded to `/beng-fut`; runs `SP11 --apply` directly. Not safe as-is in this workspace. | Yes | `AXIS_ALLOW_HARDCODED_LEGACY_TOOL=1` |
| `pipeline/scripts/core/SP13_remediate_buda.py` | Emergency one-shot remediation script that can rewrite PT bodies and PT titles when `--apply` is used. | Yes | `AXIS_ALLOW_EMERGENCY_REMEDIATION=1` |

## Guard behavior

Retired Python translation scripts now stop at startup unless explicitly allowed:

```text
AXIS_ALLOW_RETIRED_TRANSLATION_SCRIPT=1
```

The hardcoded shell wrapper now stops unless explicitly allowed:

```text
AXIS_ALLOW_HARDCODED_LEGACY_TOOL=1
```

The emergency remediation script now stops unless explicitly allowed:

```text
AXIS_ALLOW_EMERGENCY_REMEDIATION=1
```

All guard failures exit with code `2`.

## Why not delete scripts

Deletion was intentionally avoided because these files may still be useful for:

- archaeology of previous translation behavior;
- recovery/debugging under supervision;
- comparing old and current pipeline behavior;
- preserving provenance while the batch pipeline is stabilized.

Fencing gives operators a clear stop sign without erasing historical context.

## SP10/SP11 status

No changes were made to:

```text
pipeline/scripts/core/SP10_translate_deepl.py
pipeline/scripts/core/SP11_translate_titles.py
```

The current production translation/title paths are unchanged by this sprint.

## No-change confirmation

No DeepL call was made.
No translation was run.
No CSL content was modified.
No build was run.
No pipeline was run.
No deploy was run.
No Netlify/Vitrine update was made.
No Cloudflare configuration was touched.
`/home/sanghop/axis/axis-niddhi-published` was not touched.
