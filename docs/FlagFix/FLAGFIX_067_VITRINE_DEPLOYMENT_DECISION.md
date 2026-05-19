# FlagFix 067 - Vitrine Deployment Decision

Date: 2026-05-19

## Context

Latest checkpoint:

- `checkpoint/flagfix-066-vitrine-deployment-readiness-final-check-20260519`

#FlagFix_066 completed the final deployment readiness check:

- PR #155: `CLOSED`
- PR #158: `MERGED`
- Production vs published static diff: `0` lines
- Published repo: `main...origin/main [ahead 1]`
- Published working tree: clean
- Stale strings: absent
- Corrected strings: present
- Bodhi asset hash: matched between production and published
- Netlify publish directory: `pipeline/13-static-site`
- Readiness recommendation: `READY for deployment decision`

No deployment has been performed.

## Current Published State

Published repo:

- Path: `/home/sanghop/axis/axis-niddhi-published`
- Branch/status: `main...origin/main [ahead 1]`
- Working tree: clean
- Current local commit: `92f4c29`
- Commit message: `build(vitrine): sync static payload after title corrections`

Published `netlify.toml`:

```toml
[build]
  command = ""
  publish = "pipeline/13-static-site"
  ignore = "exit 0"

[build.environment]
  PYTHON_VERSION = "3.10"
```

## Payload Folder

Deployment payload folder:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Payload check:

- Publish directory exists: `publish_dir_exists=yes`
- File count: `3082`
- Size: `807M`

## Static Parity

Compared:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site`
- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Result:

- `diff -qr` output lines: `0`
- Production and published static payloads remain identical.

## Options

### Option A - Deploy Manually to Netlify Now

Use the folder `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site` directly for manual Netlify upload.

Pros:

- Fastest path to Vitrine update.
- Uses the exact reviewed payload.

Cons:

- No fresh immutable package artifact is recorded immediately before deployment.
- Harder to prove the exact upload payload later unless Netlify records are sufficient.

### Option B - Create a Deployment Package First

Create a `.zip` or tarball snapshot from exactly:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Record:

- package path;
- file count;
- size;
- SHA256;
- source commit/context.

Pros:

- Best audit trail.
- Gives the operator a stable package to upload manually later.
- Separates packaging from actual Netlify deployment.
- Keeps deployment as an explicit follow-up decision.

Cons:

- Adds one small sprint before upload.
- Requires storing a large package artifact outside Git.

### Option C - Postpone Vitrine Deployment

Leave the payload ready but do not package or deploy yet.

Pros:

- Lowest immediate operational risk.
- Cloudflare/dev already reflects the updated static payload.

Cons:

- Netlify/Vitrine remains behind the reviewed payload.
- The ready state may need to be revalidated later.

### Option D - Push/Merge Additional Published Repo State First

Attempt additional Git reconciliation in `axis-niddhi-published` before Netlify upload.

Pros:

- Could reduce local ahead-only ambiguity.

Cons:

- Not required for manual Netlify upload.
- Previous PR #155 showed that published repo history can introduce unsafe non-static scope.
- Adds risk without improving the deployment payload itself.

## Recommendation

Recommended next step: Option B.

Create a deployment package/snapshot in a later explicit sprint before any manual Netlify upload. The package should be created from exactly:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

The package sprint should record:

- file count: expected `3082`;
- payload size: expected around `807M`;
- package file path;
- package SHA256;
- source payload path;
- published local commit: `92f4c29`;
- static parity result at packaging time.

Do not deploy in #FlagFix_067.

## Proposed Next Sprint

`#FlagFix_068 - Create Netlify Vitrine deployment package`

Suggested scope:

- read-only preflight;
- create package from the approved publish directory;
- record SHA256 and file count;
- do not upload/deploy;
- produce package report.

## Explicit Non-Actions

- No deploy.
- No Netlify upload.
- No push.
- No build or pipeline run.
- No DeepL call.
- No translation.
- No CSL modification.
- No metadata CSV modification.
- No `Translation_Control_Center.csv` modification.
- No SP10/SP11 modification.
- No sync/copy.
- No `.gitignore` change.
- No `axis-niddhi-published` modification.
- No production static modification.
- No deployment package created in this sprint.
