# FlagFix 068 - Netlify Vitrine Deployment Package

Date: 2026-05-19

## Context

Latest checkpoint:

- `checkpoint/flagfix-067-vitrine-deployment-decision-20260519`

#FlagFix_067 recommended creating an audit-ready package from the approved Netlify publish directory before any manual Netlify upload.

No upload or deployment was performed in this sprint.

## Source Payload

Approved source folder:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Published repo state:

- Path: `/home/sanghop/axis/axis-niddhi-published`
- Status: `main...origin/main [ahead 1]`
- Working tree: clean
- Current local commit: `92f4c29`
- Netlify publish directory: `pipeline/13-static-site`

Source payload checks:

- Source exists: `source_exists=yes`
- Source file count: `3082`
- Source size: `807M`

## Static Parity

Compared:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site`
- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Result:

- `diff -qr` output lines: `0`
- Production static and published static were identical before packaging.

## Package

Package directory:

- `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749`

Tarball:

- `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/niddhi-netlify-vitrine-static-site-flagfix-068.tar.gz`

Package details:

- Tarball size: `722M`
- Source file inventory: `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/source_file_inventory.txt`
- Source file count record: `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/source_file_count.txt`
- Source size record: `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/source_size.txt`
- Package listing record: `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/package_ls_lh.txt`

SHA256:

```text
36cb0f2ee4feff4f45590684390b70b016d9e0246aac215f4af6f491b4272589  /home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/niddhi-netlify-vitrine-static-site-flagfix-068.tar.gz
```

SHA256 file:

- `/home/sanghop/axis/vitrine-deployment-packages/flagfix_068_20260519_060749/niddhi-netlify-vitrine-static-site-flagfix-068.tar.gz.sha256`

## Tarball Readability

Readability check:

```bash
tar -tzf "$PKG_DIR/niddhi-netlify-vitrine-static-site-flagfix-068.tar.gz" >/tmp/flagfix_068_tar_list.txt
```

Result:

- Tar listing succeeded.
- Tar listing entries: `3846`
- The archive contains the contents of `pipeline/13-static-site`, not the parent folder.

First entries:

```text
./
./pronunciation_manifest.json
./sw.js
./index.json
./pipeline/
./pipeline/print_output/
./pipeline/print_output/lote_1/
./pipeline/print_output/lote_1/test_a4.pdf
./search_index.json
./pages/
```

## Repository Safety Check

After package creation:

- Published repo status: `main...origin/main [ahead 1]`
- Production repo status: `main...origin/main`
- No files inside `pipeline/13-static-site` were altered.
- No files in `axis-niddhi-published` were modified.
- Production changes are limited to this report.

## Recommendation

Next recommended sprint:

- `#FlagFix_069 - Manual Netlify upload decision/execution`

Suggested #FlagFix_069 scope:

- verify package SHA256 before use;
- confirm package path;
- decide whether to upload manually to Netlify;
- if approved, upload/deploy in that sprint only;
- record Netlify result and rollback notes.

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
- No files inside `pipeline/13-static-site` were altered.
