# GEMINI.md — AXIS-NIDDHI Gemini Code Assist Guardrails

## Role

Gemini Code Assist may inspect, reason, and propose changes, but must obey the local workspace role before editing.

## Mandatory preflight

Before any edit, report:

```bash
pwd
git branch --show-current
git status --branch --short
git remote -v
```

If the workspace is `/home/sanghop/bengyond-playground`, treat it as rescue quarantine.

## Do not do automatically

- Do not run `build.py`.
- Do not run pipeline stages.
- Do not push.
- Do not use `git add .`.
- Do not clean, reset, stash, merge, pull, or rebase unless explicitly requested.
- Do not stage generated static output.
- Do not print secret contents.

## Generated output warning

These paths are high-risk:

```text
pipeline/13-static-site/
pipeline/13-static-site/pages/
pipeline/13-static-site/assets/
pipeline/13-ssg/cache/
outputs/
outputs/nana/
review/
```

Do not stage them unless the human explicitly says:

```text
sim, queremos publicar exatamente este build
```

## Architectural rule

AXIS-NIDDHI is a deterministic corpus preservation engine.

The static site is a derived publication artifact.

The CSL/canon is the source of truth.

Navigator, NANA, Academy, Cosmos, and future UX/LLM layers are downstream consumers and must not mutate canonical content.

## Existing production notes

This repository is production-sensitive.

- Never commit credentials or files under `scripts/private/`.
- Never edit Canon/CSL for UI tasks.
- Never change `build.py` unless explicitly requested.
- Never shorten URLs used for archival traceability.
- Preserve didactic colors from PureDhamma content.
- Print CSS and review labels belong only to the publication/UX layer.
