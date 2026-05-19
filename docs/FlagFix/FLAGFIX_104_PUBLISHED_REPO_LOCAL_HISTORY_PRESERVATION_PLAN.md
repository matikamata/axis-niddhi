# #FlagFix_104 — Published Repo Local History Preservation Plan

Date: 2026-05-19
Workspace: `/home/sanghop/axis`

## Source checkpoint
`checkpoint/flagfix-103-published-repo-reconciliation-20260519`

## Problem statement
`axis-niddhi-published` is intentionally used as the local Netlify/Vitrine payload workspace, but it remains `ahead 2` on `main` relative to `origin/main`. We need a safe operational policy so this local-only history does not become an accidental direct push risk.

## Current known state
- Production `main` (`axis-niddhi-production`) is the canonical GitHub/Cloudflare baseline.
- Published workspace (`axis-niddhi-published`) is the manual Netlify payload workspace.
- Published status is clean and locally ahead by 2 commits:
  - `92f4c298f17008f4022c0267f1e64af14a1742a1` — `build(vitrine): sync static payload after title corrections`
  - `5da4e599abb0acc7d561eb8b788c489c63238296` — `fix(vitrine): align root landing CTA`
- These commits are operationally useful history for Vitrine handling and should not be pushed directly to `origin/main`.

## Final policy recommendation
`KEEP_PUBLISHED_LOCAL_HISTORY_UNPUSHED_UNTIL_NEXT_APPROVED_VITRINE_CYCLE`

## Explicit operating rules
1. Never push `axis-niddhi-published main` directly to `origin/main`.
2. If a published local commit must be preserved in GitHub, push to a named branch and open a PR.
3. If published must be reset later, first create snapshot/tarball + patch manifest + explicit approval.
4. Before any Vitrine upload, verify local payload state and scope, then do manual upload.
5. After upload, run public Netlify smoke checks and record result.
6. Keep Cloudflare as experimental surface and Netlify as stable Vitrine surface.
7. Treat LABZ future polish as non-blocking and separate from payload reconciliation work.

## Decision table
| Scenario | Action |
|---|---|
| Local ahead, clean, operationally useful | Keep as local history |
| Local ahead with reusable tracked change | Branch + PR (never direct main push) |
| Local dirty before sync/promotion | Snapshot first, then decide |
| Need exact parity with production | Dry-run diff first, then approved scoped sync |
| Need reset to origin/main | Snapshot + explicit approval only |

## Risk notes
- Direct push from published can reintroduce ancestry/path-scope failures (e.g., pattern seen around PR #155).
- Reset without snapshot can lose reviewed Vitrine payload history.
- Broad sync can accidentally promote experimental Cloudflare-only/LABZ changes.

## Recommended next sprint
`#FlagFix_105 — Vitrine Git hygiene closure index`

## Explicit no-change confirmations
- Documentation only.
- No push.
- No deploy.
- No Netlify upload.
- No commit in `axis-niddhi-published`.
- No reset/rebase/merge.
- No branch deletion.
- No sync/copy.
- No `axis-niddhi-published` modifications.
- No production website edits.
- No build/pipeline run.
- No DeepL/translation.
- No CSL/metadata/TCC/SP10/SP11 changes.
- No `.gitignore` changes.
