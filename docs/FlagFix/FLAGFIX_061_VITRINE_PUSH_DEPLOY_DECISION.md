# FlagFix 061 — Vitrine Push/Deploy Decision

Date: 2026-05-19

## Scope

This sprint records the decision options for publishing the approved Vitrine payload.

No push, deploy, build, pipeline, sync, or copy was performed.

## Current Published Payload

Published repo:

- path: `/home/sanghop/axis/axis-niddhi-published`
- branch: `main`
- status: `main...origin/main [ahead 1]`
- working tree: clean
- remote: `https://github.com/matikamata/axis-niddhi.git`

Published local commit:

- short hash: `92f4c29`
- full hash: `92f4c298f17008f4022c0267f1e64af14a1742a1`
- message: `build(vitrine): sync static payload after title corrections`

Commit scope:

- `pipeline/13-static-site/**`
- `758 files changed`
- `14799 insertions(+)`
- `2977 deletions(-)`

## Review Status

Manual visual review:

- PASS

Reference:

- #FlagFix_060 recorded manual visual review PASS.

Automated review context:

- #FlagFix_059 HTTP checks: PASS
- #FlagFix_059 content checks: PASS
- #FlagFix_059 Bodhi technical check: PASS

## Static Parity

Comparison:

```bash
diff -qr \
  axis-niddhi-published/pipeline/13-static-site \
  axis-niddhi-production/pipeline/13-static-site
```

Result:

- output: `/tmp/flagfix_061_parity_diff_qr.txt`
- diff line count: 0
- published static payload still matches production static payload

## Publishing Options

### Option A — Push Published Local Commit Directly to `origin/main`

Pros:

- fastest path;
- preserves commit `92f4c29` exactly on remote main;
- may trigger Git-based Netlify update if configured that way.

Cons:

- bypasses PR review;
- broad 758-file static update lands directly on main;
- riskier operationally;
- contradicts prior recommendation to avoid direct push unless explicitly approved.

Assessment:

- Not recommended by default.

### Option B — Push Published Local Commit to Branch and Open PR

Pros:

- preserves review discipline;
- gives GitHub a visible review/merge point;
- avoids direct mutation of `origin/main`;
- keeps Netlify/GitHub state clearer before deployment decisions.

Cons:

- broad generated diff may be large in GitHub;
- if Vitrine is ultimately updated by manual drag/drop, PR may be a control-plane record rather than the deployment mechanism.

Assessment:

- Recommended first.

### Option C — Use Local Folder as Manual Netlify Drag/Drop Payload Without GitHub Push

Pros:

- keeps remote Git untouched;
- useful if Netlify update is explicitly manual;
- payload has passed automated and manual review.

Cons:

- GitHub remote does not record the payload commit;
- local ahead-one state remains a special operational condition;
- less auditable unless paired with external snapshot/report.

Assessment:

- Acceptable only if operator explicitly chooses manual Netlify handling.

### Option D — Keep Local Approved Vitrine Payload Ahead Locally and Wait

Pros:

- safest if deployment timing is not decided;
- no push or deploy risk;
- keeps reviewed payload available.

Cons:

- leaves `/home/sanghop/axis/axis-niddhi-published` ahead of remote;
- requires follow-up so the local commit is not forgotten.

Assessment:

- Safe short-term holding pattern.

## Recommendation

Recommended operational path:

1. Do not push directly to `origin/main`.
2. Push published commit `92f4c29` to a branch.
3. Open a PR from that branch to `main`.
4. Do not deploy until branch/PR state is clear.
5. If manual Netlify drag/drop is chosen later, use the exact reviewed local folder after the PR/deployment decision is explicitly recorded.

## Proposed Future Commands

Future branch push command, not executed:

```bash
cd /home/sanghop/axis/axis-niddhi-published
git push origin HEAD:flagfix-061-approved-vitrine-payload
```

Future PR command, not executed:

```bash
gh pr create \
  --base main \
  --head flagfix-061-approved-vitrine-payload \
  --title "build(vitrine): publish approved static payload after title corrections" \
  --body "## Summary

Publishes the approved Vitrine static payload after title corrections and visual review.

## Payload

- Source local repo: /home/sanghop/axis/axis-niddhi-published
- Commit: 92f4c298f17008f4022c0267f1e64af14a1742a1
- Scope: pipeline/13-static-site/**

## Validation

- Static parity with production: 0 diff lines
- Automated local HTTP/content checks: PASS
- Manual visual review: PASS
- BodhiCircuitLeaf transparent asset approved

## Safety

No build/pipeline run.
No DeepL call.
No translation.
No CSL changes.
No metadata CSV changes.
No TCC/SP10/SP11 changes.
No deploy performed by this PR."
```

## Next Sprint Recommendation

Suggested #FlagFix_062:

- either push `92f4c29` to branch `flagfix-061-approved-vitrine-payload` and open PR;
- or record an explicit operator decision to use manual Netlify drag/drop instead.

No Netlify deployment should occur until that decision is explicit.

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
