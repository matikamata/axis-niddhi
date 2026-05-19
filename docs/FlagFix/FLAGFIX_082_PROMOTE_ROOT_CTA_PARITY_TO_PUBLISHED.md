# FlagFix 082 - Promote Vitrine root CTA parity to published payload

Date: 2026-05-19

## Reason for Promotion

FlagFix #081 aligned the approved Vitrine landing so root CTA visibility does not depend on host-specific root redirect behavior.

Before this promotion:

- Production `index.html` had `CONTRIBUTE` / `COLABORAR`.
- Published `index.html` did not.

This sprint promotes only the approved root CTA parity fix to published payload, without promoting LABZ.

## Exact Copied File

Copied file:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/index.html`
- to `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/index.html`

No other files were copied.

## CTA Before/After

Production source (`index.html`) CTA check:

- `ENTER ARCHIVE`
- `CONTRIBUTE`
- `ACESSAR ACERVO`
- `COLABORAR`

Published target before copy:

- `ENTER ARCHIVE`
- `ACESSAR ACERVO`
- no `CONTRIBUTE`/`COLABORAR`

Published target after copy:

- `ENTER ARCHIVE`
- `CONTRIBUTE`
- `ACESSAR ACERVO`
- `COLABORAR`

## Index Parity Check

Diff command:

- `diff -u production/index.html published/index.html`

Result:

- `/tmp/flagfix_082_index_parity.diff`
- line count: `0`

Meaning:

- Published root `index.html` now matches production root `index.html` exactly.

## Published Repo Status After Patch

Published repo status:

- `main...origin/main [ahead 1]`
- changed path:
  - `pipeline/13-static-site/index.html`

No additional changed paths were detected.

## LABZ Exclusion Check

Checked published changed filenames for:

- `labz`
- `flower` / `flores`
- `bodhi`

Result:

- no matches
- LABZ/Bodhi/flower files were not modified in this sprint

## Safety / Non-Actions

- No deploy
- No Netlify upload
- No build/pipeline run
- No DeepL call
- No translation
- No CSL changes
- No metadata CSV changes
- No `Translation_Control_Center.csv` changes
- No SP10/SP11 changes
- No `.gitignore` changes
- No broad static sync/copy
- No changes outside the single published root file

## Recommendation

Commit the published payload update separately in `axis-niddhi-published`, then perform Netlify upload and smoke check in a later dedicated sprint.
