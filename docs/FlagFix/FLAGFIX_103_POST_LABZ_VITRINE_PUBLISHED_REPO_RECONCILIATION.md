# #FlagFix_103 — Post-LABZ Vitrine/Published Repo Reconciliation

## Purpose
Run a read-only audit of `axis-niddhi-published` Git state (`main...origin/main [ahead 2]`) and recommend the safest reconciliation path.

Source checkpoint:
`checkpoint/flagfix-102-labz-netlify-promotion-closure-20260519`

## Production status
- Repo: `/home/sanghop/axis/axis-niddhi-production`
- Branch: `main...origin/main`
- Working tree: clean
- Recent state includes checkpoint/tag chain through `#102`.

## Published status
- Repo: `/home/sanghop/axis/axis-niddhi-published`
- Branch: `main`
- Status: `main...origin/main [ahead 2]`
- Working tree: clean
- Remote: `origin https://github.com/matikamata/axis-niddhi.git`

## Published ahead count
`2`

## Local-ahead commits in published
1. `92f4c298f17008f4022c0267f1e64af14a1742a1`
   - Message: `build(vitrine): sync static payload after title corrections`
   - Scope: broad static payload update under `pipeline/13-static-site/**` (hundreds of generated/static files).
2. `5da4e599abb0acc7d561eb8b788c489c63238296`
   - Message: `fix(vitrine): align root landing CTA`
   - Scope: `pipeline/13-static-site/index.html`.

## Changed paths in ahead commits
- Both ahead commits are confined to `pipeline/13-static-site/**`.
- No working-tree uncommitted changes were present during this audit.

## Static payload comparison (production vs published)
- Command result file: `/tmp/flagfix_103_production_vs_published_static.diff`
- Diff line count: `752`
- Result: payloads are **not** currently identical.
- Difference pattern is wide across archive/index/CSS and many page HTML files, consistent with separate promotion tracks and published-local payload history.

## Are ahead commits already represented in production history?
- `92f4c298...` is known in refs as `origin/flagfix-062-approved-vitrine-payload`, but is not part of production `main` history.
- `5da4e599...` is not present in production repo object history.
- Operationally, equivalent outcomes were later handled via production-side FlagFix chain and manual Netlify flow, but Git commit identity is not shared between repos.

## PR context (read-only)
- GitHub PR listings for the recent LABZ and Vitrine sequence show merged PRs up through `#102`.
- No additional reconciliation PR from `axis-niddhi-published` local `main` ahead commits is currently open from this audit context.

## Risk assessment
- Immediate risk is moderate if the ahead state is misunderstood as “ready to push main” in published.
- The repo is clean and operationally usable for manual payload uploads, but Git divergence can cause future operator confusion.
- Direct push from published `main` remains high risk and should be avoided.

## Recommended reconciliation strategy
`RECOMMEND_KEEP_AS_LOCAL_HISTORY_ONLY`

Rationale:
- The ahead commits are historically meaningful local Vitrine payload checkpoints used during the promotion workflow.
- There is no urgent safety requirement to mutate published history now.
- Forcing reset/rewrite now adds avoidable risk unless done with explicit rollback controls.
- Keep published local history as-is for now, and formalize handling in a follow-up governance sprint.

## Next sprint recommendation
`#FlagFix_104 — published repo local history preservation plan`

Suggested #104 focus:
- decide retention window for local-only published commits;
- define explicit “when to branch/PR vs keep local-only” policy;
- document conditions for any future reset (snapshot + approval gate).

## Explicit no-change confirmations
- Read-only audit only.
- No push.
- No deploy.
- No Netlify upload.
- No commit.
- No reset/rebase/merge.
- No branch deletion.
- No sync/copy.
- No `axis-niddhi-published` modifications.
- No production website file edits.
- No build/pipeline run.
- No DeepL/translation.
- No CSL/metadata/TCC/SP10/SP11 changes.
- No `.gitignore` changes.
