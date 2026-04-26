# Torre de Gits — Workspace Guardrails

**Date:** 2026-04-26  
**Status:** Active operational rule  
**Scope:** AXIS-NIDDHI production, rescue, lab, Navigator, NANA, print review

---

## 1. Purpose

This document records the official local workspace strategy for AXIS-NIDDHI after the Torre de Gits consolidation.

The project has a public production repository and live deployment surfaces. The Cloudflare deployment is connected to the GitHub repository `matikamata/axis-niddhi`, and the GitHub Pages archive is also public.

Therefore, local workspaces must be separated by operational role.

The goal is to prevent accidental deployment of experimental work, generated static output, local review artifacts, secrets, or large unreviewed diffs.

---

## 2. Official workspace roles

| Path | Role | Rule |
|---|---|---|
| `/home/sanghop/axis/axis-niddhi-production` | Production clone | Clean reference, main branch, Cloudflare-connected repo |
| `/home/sanghop/bengyond-playground` | Rescue quarantine | Read/diff/cherry-pick only; no push |
| `/home/sanghop/axis/axis-niddhi-lab` | Future integration lab | Controlled integration before production |
| `/home/sanghop/axis/axis-navigator-lab` | Navigator UX lab | UX experiments only |
| `/home/sanghop/axis/axis-nana-lab` | NANA/LLM lab | Retrieval, source-bound Q&A, provider experiments |
| `/home/sanghop/axis/axis-print-review` | Print review lab | CSS/print/PDF work before production |

---

## 3. Production rules

The production clone is the only local workspace allowed to prepare production branches for `matikamata/axis-niddhi`.

Hard rules:

- Do not run experimental builds in production.
- Do not run NANA experiments in production.
- Do not run Navigator experiments in production.
- Do not use `git add .`.
- Do not commit generated mass output without explicit human approval.
- Do not commit secrets.
- Do not push directly from rescue or playground clones.
- Do not use dirty worktrees for production commits.

---

## 4. Rescue quarantine rules

The rescue workspace exists only for archaeology and selective recovery.

Allowed:

- inspect
- diff
- grep
- copy specific ideas manually
- cherry-pick only after human architectural approval

Forbidden:

- push
- deploy
- clean
- reset
- mass commit
- run production build
- treat as current production truth

The rescue clone push URL must remain disabled.

Expected local config:

```bash
git remote -v
git config --local --get push.default
git config --local --get axis.role
git config --local --get axis.deploy
```

Expected values:

```text
origin push: DISABLED_RESCUE_QUARANTINE_DO_NOT_PUSH
push.default: nothing
axis.role: rescue-quarantine
axis.deploy: forbidden
```

---

## 5. Generated output policy

The following paths are high risk:

```text
pipeline/13-static-site/
pipeline/13-static-site/pages/
pipeline/13-static-site/assets/
pipeline/13-ssg/cache/
outputs/
outputs/nana/
review/
```

These paths may contain generated or review artifacts.

They must not be committed accidentally.

Any commit touching generated static output requires an explicit approval sentence from the human operator:

```text
sim, queremos publicar exatamente este build
```

Without that sentence, generated output must not be staged.

---

## 6. Secret policy

Never commit or publish:

```text
pipeline/scripts/private/
.env
deepl_key.txt
github_token.txt
wp_password.txt
*.pem
*.key
credentials
tokens
```

Secret-like filenames may be reported by path only. Contents must not be printed.

---

## 7. Agent policy

CodeX, Gemini Code Assist, Claude Code, or any other local coding assistant must obey the workspace role before editing.

Before any edit, the agent must report:

```bash
pwd
git branch --show-current
git status --branch --short
git remote -v
```

If the workspace role is unclear, the agent must stop and ask.

---

## 8. Canonical decision

The old castle is preserved as archaeology.

The new castle is built through separated workspaces:

```text
production
lab
navigator
nana
print-review
rescue
```

Production remains clean.

Labs may experiment.

Rescue preserves memory.

Only reviewed, minimal, intentional changes cross into production.
