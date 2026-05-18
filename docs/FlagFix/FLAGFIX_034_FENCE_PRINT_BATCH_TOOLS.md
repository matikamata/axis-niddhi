# FLAGFIX_034 - Fence print-batch tools referencing removed CSV

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Scope: fence/deprecate print-batch references to removed CSV

## Context

#FlagFix_033 removed:

```text
pipeline/metadata/Print_Translation_Control_Center.csv
```

That file was an old print-batch experiment and must not be confused with the official SP10/DeepL selector.

The official translation selector remains:

```text
pipeline/metadata/Translation_Control_Center.csv
```

## Tools inspected

```text
pipeline/scripts/tools/print_batch.py
pipeline/scripts/tools/create_bilingual_review_snapshot.sh
```

## Behavior after fencing

### `print_batch.py`

Status: fenced.

This tool's primary workflow depends on the removed print CSV. It now exits immediately with code `2` unless explicitly allowed for archaeology.

Override:

```bash
AXIS_ALLOW_RETIRED_PRINT_BATCH_TOOL=1
```

The error explains:

- the print-batch workflow was retired by #FlagFix_033;
- `Translation_Control_Center.csv` remains official for SP10/DeepL;
- `Print_Translation_Control_Center.csv` must not be recreated without explicit review.

### `create_bilingual_review_snapshot.sh`

Status: deprecation message updated, not hard-fenced.

This script's primary purpose is review snapshot creation, not print batching. It no longer points operators to `Print_Translation_Control_Center.csv` or `print_batch.py` as the next print path. Its summary now says the print-batch workflow was retired by #FlagFix_033 and that the removed CSV should not be recreated without explicit review.

## Why the CSV was not restored

Restoring `Print_Translation_Control_Center.csv` would reintroduce stale, contradictory print-batch state that #FlagFix_032 identified and #FlagFix_033 intentionally removed.

If physical print batching is revived later, it should receive a fresh control artifact or a redesigned workflow, not resurrect the removed CSV silently.

## Script behavior

No SP10/SP11 behavior was modified.

Unchanged:

```text
pipeline/scripts/core/SP10_translate_deepl.py
pipeline/scripts/core/SP11_translate_titles.py
pipeline/metadata/Translation_Control_Center.csv
```

## No-change confirmation

No DeepL call was made.
No translation was run.
No CSL content was modified.
No `Translation_Control_Center.csv` change was made.
No `Print_Translation_Control_Center.csv` restore was made.
No build was run.
No pipeline was run.
No deploy was run.
No Netlify/Vitrine update was made.
No Cloudflare configuration was touched.
`/home/sanghop/axis/axis-niddhi-published` was not touched.
