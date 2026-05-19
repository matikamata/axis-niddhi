# FlagFix 084 - Netlify root CTA deployment decision/execution

Date: 2026-05-19

## Context

Published payload already contains the approved root CTA parity patch from #FlagFix_083:

- published commit: `5da4e59`
- changed path: `pipeline/13-static-site/index.html`

Local published root now includes:

- `ENTER ARCHIVE`
- `CONTRIBUTE`
- `ACESSAR ACERVO`
- `COLABORAR`

## Source Folder for Manual Upload

Exact upload source:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Local payload status at decision time:

- folder exists: `yes`
- file count: `3082`
- size: `807M`

## Local Verification

Published repo:

- `main...origin/main [ahead 2]`
- working tree clean

Root CTA verification on local published `index.html`:

- `ENTER ARCHIVE` present
- `CONTRIBUTE` present
- `ACESSAR ACERVO` present
- `COLABORAR` present

LABZ/Bodhi/flower pending changes check:

- no pending files
- no LABZ/Bodhi/flower changes in this sprint

## Deployment Execution Status

Status:

- `HOLD - awaiting manual Netlify upload confirmation`

This sprint did not execute upload/deploy automatically because deployment requires explicit human dashboard action unless a configured/approved CLI path exists.

## Manual Upload Steps (Human)

Target site:

- `niddhi.netlify.app`

Use exactly:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Steps:

1. Open Netlify dashboard for `niddhi.netlify.app`.
2. Start manual deploy (drag-and-drop/manual upload flow).
3. Upload the publish payload from `pipeline/13-static-site` (contents, or folder if Netlify accepts it as publish root).
4. Wait for deploy completion in Netlify UI.
5. Confirm the public URL is updated.

## Post-Upload Smoke Check (Pending)

After human confirmation of upload, run:

- root/welcome/contribute HTTP checks
- root CTA grep checks
- stale-string absence check

This step is pending confirmation and was intentionally not executed yet in #084.

## No-LABZ Promotion Confirmation

- No LABZ promotion performed.
- No LABZ/Bodhi/flower files modified.

## Explicit Non-Actions

- No build/pipeline run
- No DeepL call
- No translation
- No CSL changes
- No metadata CSV changes
- No `Translation_Control_Center.csv` changes
- No SP10/SP11 changes
- No sync/copy actions
- No `.gitignore` changes
- No website file modifications
- No push

## Recommendation

Proceed with manual upload now, then run a focused public smoke-check follow-up sprint:

- `#FlagFix_085 — Netlify post-upload smoke check for root CTA parity`
