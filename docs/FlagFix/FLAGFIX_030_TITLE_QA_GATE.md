# FLAGFIX_030 - Title QA gate before SP10/SP11 apply

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Scope: read-only QA tool plus documentation

## Purpose

Create a small reusable gate that audits `titles.pt` values in CSL identity metadata before any future `SP10` or `SP11` apply batch accepts DeepL-derived PT titles.

This responds to #FlagFix_028 and #FlagFix_029:

- `LD.AA.000` had `titles.pt = "Vivendo il Dhamma"`.
- The source marker was `pt_source = "deepl_v5"`, pointing more strongly to the `SP10_translate_deepl.py` initial translation path than to `SP11_translate_titles.py`.
- #FlagFix_029 found many `titles.pt = null` values, so the gate must be null-safe.

## Tool

Added:

```text
pipeline/scripts/tools/audit_pt_titles_language_contamination.py
```

Default audit root:

```text
pipeline/09-csl
```

Optional root:

```bash
python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py --csl-root pipeline/09-csl
```

## Markers

The first marker set targets suspicious Italian fragments in PT-BR titles:

```text
 il
 lo
 gli
 della
 del
 delle
 degli
 nell
 sull
 alla
 al
```

The audit pads and lowercases each title before matching, so short markers can be detected without crashing on `null`.

## Output

The tool prints:

```text
checked=<count>
null_pt_titles=<count>
hits=<count>
```

Each hit prints:

```text
PD#PN | file path | title | matched markers
```

Exit codes:

```text
0 = audit completed with no hits
1 = audit completed and found suspicious hits
2 = root/path/JSON read failure prevents audit
```

## Validation

Commands run:

```bash
python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py
python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py --csl-root pipeline/09-csl
```

Observed result for both commands:

```text
checked=748
null_pt_titles=439
hits=0
```

This matches the expected state after #FlagFix_028: no remaining Italian-marker `titles.pt` hits in current CSL metadata.

## Operational guidance

Run this audit before any future title-writing batch:

```bash
python3 pipeline/scripts/tools/audit_pt_titles_language_contamination.py
```

If it exits `1`, do not promote the batch blindly. Inspect each hit and route suspected false positives or true contamination through the title review workflow.

This tool is a guard, not a correction tool. It does not modify metadata, body content, renderer code, static output, or deployment surfaces.

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
