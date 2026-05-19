# FlagFix 065 — Close Superseded PR #155

Date: 2026-05-19

## Scope

This sprint closed unsafe PR #155 as superseded by the safe replacement PR #158.

No merge, deploy, build, pipeline, copy, or sync was performed.

## PR Closed

PR #155:

- URL: `https://github.com/matikamata/axis-niddhi/pull/155`
- title: `build(vitrine): publish approved static payload after title corrections`
- head: `flagfix-062-approved-vitrine-payload`
- base: `main`
- initial state: `OPEN`
- final state: `CLOSED`

## Why PR #155 Was Unsafe

#FlagFix_063 reviewed PR #155 and found:

- the branch came from stale `axis-niddhi-published` history;
- path scope failed;
- the diff included non-static paths outside the approved Vitrine payload scope;
- observed unsafe paths included `.gitignore`, `docs/**`, `pipeline/scripts/**`, `pipeline/metadata/**`, and `review/**`.

Conclusion:

- PR #155 should not be merged.

## Replacement PR

Safe replacement:

- PR #158
- #FlagFix_064 created the replacement from current production `main`;
- #158 recorded that current production `main` already contains the approved static payload;
- checkpoint: `checkpoint/flagfix-064-static-payload-only-replacement-20260519`.

## Actions Taken

Comment added to PR #155:

```text
Superseded by #158.

This PR should not be merged.

Reason:
- #FlagFix_063 found unsafe path scope.
- The branch came from stale axis-niddhi-published history.
- The PR diff included non-static paths outside the approved Vitrine payload scope.

Safe replacement:
- #FlagFix_064 created and merged #158 from current production main.
- #158 records that the current production main already contains the approved static payload.
- The approved Vitrine payload remains preserved and reviewed.

No deploy is associated with this PR.
```

Closure action:

```text
Closing as superseded by #158. Branch retained for audit until explicit cleanup.
```

GitHub comment URL:

- `https://github.com/matikamata/axis-niddhi/pull/155#issuecomment-4485486285`

## Branch Handling

The PR branch was not deleted.

Retained branch:

- `flagfix-062-approved-vitrine-payload`

Reason:

- retained for audit until explicit cleanup is approved.

## Non-Actions

This sprint did not:

- merge PR #155;
- delete the PR branch;
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

## Recommendation

Treat PR #155 as closed/superseded.

Future cleanup may delete branch `flagfix-062-approved-vitrine-payload`, but only after explicit operator approval.
