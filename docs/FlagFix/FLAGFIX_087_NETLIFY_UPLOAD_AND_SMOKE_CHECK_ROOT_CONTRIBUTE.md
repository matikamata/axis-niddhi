# FlagFix 087 - Netlify upload and smoke check for root/contribute CTA copy

Date: 2026-05-19

## Upload Status

Manual upload status:

- `COMPLETED` (manual upload confirmed by human)

Deployment was manually executed by the human using:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

## Upload Source Folder

Use exactly:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Validated local source:

- exists: `yes`
- file count: `3082`
- size: `807M`

## Local Pre-Upload Validation

Published local root `index.html` contains:

- `ENTER ARCHIVE`
- `CONTRIBUTE`
- `ACESSAR ACERVO`
- `COLABORAR`

Published local `contribute.html` contains:

- `AXIS-NIDDHI Collaboration Surface`

Published local `contribute.html` no longer contains:

- `AXIS-NIDDHI Cloudflare Staging`

Published repo status:

- `main...origin/main [ahead 2]`
- working tree clean

## Public Smoke Check Results

Manual browser/web verification after upload:

- `https://niddhi.netlify.app/`: `PASS`
  - `ENTER ARCHIVE` present
  - `CONTRIBUTE` present
  - `ACESSAR ACERVO` present
  - `COLABORAR` present

- `https://niddhi.netlify.app/welcome`: `PASS`
  - same CTA surface confirmed

- `https://niddhi.netlify.app/contribute`: `PASS`
  - `AXIS-NIDDHI Collaboration Surface` present
  - `AXIS-NIDDHI Cloudflare Staging` absent
  - neutral body copy visible

## LABZ Exclusion Confirmation

- No LABZ promotion performed.
- No LABZ/Bodhi/flower file modifications in this sprint.

## Explicit Non-Actions

- No build/pipeline run
- No DeepL call
- No translation
- No CSL changes
- No metadata CSV changes
- No TCC/SP10/SP11 changes
- No sync/copy actions
- No `.gitignore` changes
- No push

## Next Step

Upload and smoke checks are now complete for root/contribute CTA copy parity.

Proceed with normal release hygiene in follow-up checkpoints as needed.
