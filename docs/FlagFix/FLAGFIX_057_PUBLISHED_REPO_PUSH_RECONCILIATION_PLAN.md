# FlagFix 057 — Published Repo Push/Reconciliation Plan

Date: 2026-05-19

## Scope

This sprint creates a read-only reconciliation plan for the local Vitrine payload commit in `/home/sanghop/axis/axis-niddhi-published`.

No push, deploy, build, pipeline, copy, or sync was performed.

## Production Repo State

Production repo:

- path: `/home/sanghop/axis/axis-niddhi-production`
- branch/status: `main...origin/main`
- HEAD: `c4aef588373ba40727a4dc2b77dc6ac153d78eb1`
- checkpoint: `checkpoint/flagfix-056-commit-synced-vitrine-payload-20260519`

## Published Repo State

Published repo:

- path: `/home/sanghop/axis/axis-niddhi-published`
- branch: `main`
- status: `main...origin/main [ahead 1]`
- working tree: clean
- uncommitted/untracked paths: 0

Published local commit:

- short hash: `92f4c29`
- full hash: `92f4c298f17008f4022c0267f1e64af14a1742a1`
- message: `build(vitrine): sync static payload after title corrections`

Remote:

```text
origin  https://github.com/matikamata/axis-niddhi.git (fetch)
origin  https://github.com/matikamata/axis-niddhi.git (push)
```

Local commits ahead of `origin/main`:

```text
92f4c29 build(vitrine): sync static payload after title corrections
```

Commit scope from `git show --stat`:

- `pipeline/13-static-site/**`
- `758 files changed`
- `14799 insertions(+)`
- `2977 deletions(-)`

## Static Parity

Comparison:

```bash
diff -qr \
  axis-niddhi-published/pipeline/13-static-site \
  axis-niddhi-production/pipeline/13-static-site
```

Result:

- output path: `/tmp/flagfix_057_published_vs_production_static_diff_qr.txt`
- diff line count: 0
- published static payload matches production static payload

## Options

### Option A — Push Published Local Commit Directly to `origin/main`

Pros:

- fastest way to put the Vitrine payload commit on the remote main branch;
- preserves the local static payload commit exactly as created.

Cons:

- bypasses PR review;
- high-risk for a broad 758-file static update;
- could trigger remote/Netlify behavior depending on repository configuration;
- not recommended without explicit operator approval and visual review.

### Option B — Push Published Local Commit to a Branch and Open PR

Pros:

- preserves review discipline;
- allows GitHub diff/review before merging;
- avoids direct main mutation;
- gives a natural checkpoint for the Vitrine payload update.

Cons:

- broad generated/static diff may be large to review in GitHub;
- if Netlify is not Git-driven, this may be documentation/control-plane value rather than the actual deployment path.

### Option C — Do Not Push Published Repo; Use Folder as Netlify Drag/Drop Payload

Pros:

- avoids changing remote Git history;
- useful if Netlify/Vitrine promotion is manual drag/drop;
- current local folder is already committed and clean for local checkpointing.

Cons:

- remote Git will not record the payload commit;
- future operators must know the local published repo is ahead by one commit;
- local-only state is easier to lose unless backed up.

### Option D — Reset Published Repo to `origin/main` After Final Snapshot

Pros:

- returns published repo to remote-clean state;
- avoids accidental push/deploy of broad generated changes.

Cons:

- discards the local Vitrine payload commit unless preserved by branch/tag/archive;
- would undo the local committed sync in the working tree;
- not appropriate unless the operator decides not to use this payload.

### Option E — Keep Published Repo Ahead Locally Until Visual Review

Pros:

- safest immediate state;
- no remote mutation;
- no deploy;
- keeps a clean local commit available for review, branch push, or drag/drop.

Cons:

- requires explicit follow-up so the ahead-one state is not forgotten;
- does not complete GitHub/Netlify reconciliation by itself.

## Recommendation

Recommended path:

1. Do not push directly to `origin/main`.
2. Keep `/home/sanghop/axis/axis-niddhi-published` ahead locally until visual review is complete.
3. If GitHub history should contain the Vitrine payload update, push commit `92f4c29` to a branch and open a PR.
4. If Netlify promotion is manual drag/drop, use the committed local folder only after visual review and keep the commit as the local checkpoint.
5. Do not deploy until visual review is explicitly approved.

The safest next action is a dedicated visual review sprint before choosing PR push versus manual Netlify payload handling.

## Proposed Next Sprint

Suggested #FlagFix_058:

- visually review representative pages from `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`;
- confirm corrected titles and awaiting-translation label in browser;
- confirm transparent Bodhi asset rendering;
- decide whether to push a branch/PR or proceed with manual Netlify/Vitrine handling.

## Non-Actions

This sprint did not:

- push from `axis-niddhi-published`;
- deploy;
- run build or pipeline;
- call DeepL;
- translate anything;
- modify CSL;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11;
- copy or sync files;
- change `.gitignore`;
- modify `axis-niddhi-published`;
- modify production static.
