# GEMINI.md — AXIS-NIDDHI Production Rules

This repository is production-sensitive.

## Absolute rules

- Never run `git add .`.
- Never run `git reset`.
- Never run `git clean`.
- Never run `git stash`.
- Never push without explicit human approval.
- Never commit credentials or files under `scripts/private/`.
- Never edit Canon/CSL for UI tasks.
- Never change `build.py` unless explicitly requested.
- Never shorten URLs used for archival traceability.
- Preserve didactic colors from PureDhamma content.

## Architecture

CSL/Canon is the source of truth.
Static site is derived publication.
Print CSS and review labels belong only to publication/UX layer.

## Safe workflow

Before editing, always show:

git branch --show-current
git status --short
git diff --stat

After editing, always show:

git diff --stat
git diff --name-only
git status --short
