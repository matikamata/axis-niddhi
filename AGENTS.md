# AGENTS.md — AXIS-NIDDHI Local Agent Guardrails

## Mandatory preflight

Before editing any file, every local coding agent must report:

```bash
pwd
git branch --show-current
git status --branch --short
git remote -v
```

If the workspace role is unclear, stop and ask.

## Portable path convention

`AXIS_WORKSPACE` is the locally configured parent of the role-specific checkouts.
See [docs/PORTABLE_PATHS.md](docs/PORTABLE_PATHS.md) for POSIX and PowerShell setup.
Repository-relative paths start at the checkout root.

## Workspace roles

| Path | Role | Rule |
|---|---|---|
| `${AXIS_WORKSPACE}/axis-niddhi-production` | production | clean production branches only |
| `${AXIS_WORKSPACE}/bengyond-playground` | rescue quarantine | read/diff/cherry-pick archaeology only; no push |
| `${AXIS_WORKSPACE}/axis-niddhi-lab` | integration lab | controlled integration |
| `${AXIS_WORKSPACE}/axis-navigator-lab` | Navigator lab | UX experiments |
| `${AXIS_WORKSPACE}/axis-nana-lab` | NANA lab | retrieval/LLM/provider experiments |
| `${AXIS_WORKSPACE}/axis-print-review` | print review lab | print/PDF/CSS work |

## Absolute rules

- Do not use `git add .`.
- Do not push from rescue or playground clones.
- Do not commit secrets.
- Do not run `build.py` unless explicitly requested.
- Do not run pipeline stages unless explicitly requested.
- Do not modify generated static output unless explicitly approved.
- Do not treat `pipeline/13-static-site/` as source truth.
- The CSL/canon is upstream of publication artifacts.

## High-risk paths

Do not stage these accidentally:

```text
pipeline/13-static-site/
pipeline/13-static-site/pages/
pipeline/13-static-site/assets/
pipeline/13-ssg/cache/
outputs/
outputs/nana/
review/
```

Any commit touching generated static output requires the exact approval sentence:

```text
sim, queremos publicar exatamente este build
```

## Secret policy

Never print, stage, commit, or publish secret contents.

High-risk examples:

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

Secret-like paths may be reported by filename/path only.

## Production policy

Production branches must be small, reviewable, and intentional.

Allowed production change types:

```text
docs-only
hotfix-css
hotfix-js
template-hotfix
metadata-review
```

Generated mass output is forbidden unless explicitly approved.

## Rescue policy

The rescue workspace is archaeology.

Allowed:

```text
inspect
grep
diff
manual extraction of ideas
cherry-pick only after human architectural approval
```

Forbidden:

```text
push
deploy
clean
reset
mass commit
production build
```
