# FLAGFIX_033 - Remove stale Print Translation Control Center

Date: 2026-05-18
Workspace: `/home/sanghop/axis/axis-niddhi-production`
Scope: remove stale print-specific CSV plus documentation

## Decision

Remove:

```text
pipeline/metadata/Print_Translation_Control_Center.csv
```

This file was an old print-batch experiment. #FlagFix_032 showed it was stale/print-specific and contradicted current CSL state in multiple rows, including rows marked pending while PT content and PT titles already exist.

## Official translation selector

The official DeepL batch selector remains:

```text
pipeline/metadata/Translation_Control_Center.csv
```

That file was coherent with CSL during #FlagFix_032 and is the control file used by the active translation flow.

This sprint does not modify `Translation_Control_Center.csv`.

## Reference search

Command run:

```bash
grep -RIn "Print_Translation_Control_Center.csv\|Print_Translation_Control_Center" \
  pipeline/scripts pipeline/13-ssg docs review 2>/dev/null || true
```

References found:

```text
pipeline/scripts/tools/print_batch.py
pipeline/scripts/tools/create_bilingual_review_snapshot.sh
docs/FlagFix/FLAGFIX_020_TITLE_MATRIX_EXPANSION_PLAN_2026-05-04.md
docs/FlagFix/FLAGFIX_032_TRANSLATION_BATCH_PREFLIGHT.md
docs/MANUAL_OPERACOES_BATCH_PRINT.md
```

Assessment:

- No active `SP10`/`SP11` DeepL selector dependency was found.
- The script references are print/review-surface references, not active translation batch selection.
- Historical docs are intentionally left unchanged in this sprint.
- `print_batch.py` may need separate retirement or update if physical print batching is revived.

## Why deletion is appropriate

Keeping the stale CSV creates a risk that operators may confuse it with the official translation selector and use old `YES`/`PENDING` rows for a future batch.

Deleting the file makes that failure mode visible immediately instead of silently allowing stale print-batch data to steer work.

## Script behavior

No script behavior was modified.

Specifically unchanged:

```text
pipeline/scripts/core/SP10_translate_deepl.py
pipeline/scripts/core/SP11_translate_titles.py
```

## No-change confirmation

No DeepL call was made.
No translation was run.
No CSL content was modified.
No `Translation_Control_Center.csv` change was made.
No build was run.
No pipeline was run.
No deploy was run.
No Netlify/Vitrine update was made.
No Cloudflare configuration was touched.
`/home/sanghop/axis/axis-niddhi-published` was not touched.
