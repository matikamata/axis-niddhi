# FlagFix 052 — Vitrine Promotion Plan

Date: 2026-05-19

## Scope

This sprint creates a read-only plan for a future Netlify/Vitrine promotion. No files were copied or synced.

Current production static source:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site`

Current published/Vitrine workspace:

- `/home/sanghop/axis/axis-niddhi-published`

Comparable published static payload:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Checkpoint reference:

- `checkpoint/flagfix-051-transparent-bodhi-leaf-asset-20260518`

## Target Structure

Future promotion should target:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/`

Static files should not be copied to:

- `/home/sanghop/axis/axis-niddhi-published/`

Reason:

- the published root is a wider repository/workspace containing `.git`, docs, project files, `netlify.toml`, and source/support directories;
- both production and published `netlify.toml` files set `publish = "pipeline/13-static-site"`;
- the current Vitrine static payload already lives under `pipeline/13-static-site`;
- key static files such as `archive.html`, `index.json`, `search_index.json`, and `pages/*/index.html` are present in the nested static payload, not at the published root.

This structure matches the current Netlify/Vitrine use.

## Validator Results

Validators were run in `/home/sanghop/axis/axis-niddhi-production`.

CSL correction manifest validator:

- total: 25
- match: 25
- mismatch: 0
- missing_file: 0
- missing_path: 0
- exit code: 0

PT title language contamination audit:

- checked: 748
- null PT titles: 439
- hits: 0
- exit code: 0

## Static Diff Summary

Read-only comparison:

```bash
diff -qr \
  axis-niddhi-published/pipeline/13-static-site \
  axis-niddhi-production/pipeline/13-static-site
```

Summary:

- diff lines: 762
- files differing: 758
- only in production static: 4
- only in published static: 0

Representative differences:

- `_redirects`
- `archive.html`
- `assets/BodhiCircuitLeaf.png`
- `build_meta.json`
- `css/style.css`
- `css/typography-pro.css`
- `index.html`
- `index.json`
- `js/main.js`
- many `pages/*/index.html` files

Production-only paths observed in the diff include:

- `assets/BodhiCircuitLeaf_original.png`
- `assets/nana`
- `contribute.html`
- `pipeline/print_output`

## String Status

Production static corrected strings:

- `Vivendo o Dhamma`: 8 occurrences in 8 files
- `Vipariṇāma Two Meanings`: 12 occurrences in 6 files
- `Awaiting translation / Aguardando tradução`: 439 occurrences in 1 file

Production static stale strings:

- `Vivendo il Dhamma`: 0 occurrences
- `Viparie1B987Ama Two Meanings`: 0 occurrences
- `pending translation / pendente de tradução`: 0 occurrences

Published static corrected strings:

- `Vivendo o Dhamma`: 2 occurrences in 2 files
- `Vipariṇāma Two Meanings`: 0 occurrences
- `Awaiting translation / Aguardando tradução`: 0 occurrences

Published static stale strings:

- `Vivendo il Dhamma`: 6 occurrences in 6 files
- `Viparie1B987Ama Two Meanings`: 12 occurrences in 6 files
- `pending translation / pendente de tradução`: 0 occurrences

Interpretation:

- production static contains the #028, #036, and #037-#043 corrections;
- published/Vitrine static is still stale for the LD.AA.000 and BA.AA.004 title fixes;
- published/Vitrine static does not yet contain the improved awaiting-translation copy.

## BodhiCircuitLeaf Asset Status

Production asset:

- path: `axis-niddhi-production/pipeline/13-static-site/assets/BodhiCircuitLeaf.png`
- file type: PNG image data, 2048 x 2048, 8-bit/color RGBA, non-interlaced
- sha256: `92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7`

Published asset:

- path: `axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png`
- file type: PNG image data, 1024 x 1024, 8-bit/color RGBA, non-interlaced
- sha256: `de326fede79eca1b87237bbbb6274b74fd3a86191d15683d9b6521d2395c8545`

Interpretation:

- the approved transparent/no-background production asset differs from the currently published asset;
- the approved production asset should be included in the future promotion package.

## Proposed Future Commands

Dry run first, in a future approved sprint:

```bash
cd /home/sanghop/axis
rsync -avnc --delete \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/
```

Only after explicit review and approval, real sync:

```bash
cd /home/sanghop/axis
rsync -avc --delete \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/
```

Do not target the published root.

## Pre-Promotion Checklist

- Confirm production repo is on the approved checkpoint or merge commit.
- Run `validate_csl_correction_manifest.py` and confirm exit code 0.
- Run `audit_pt_titles_language_contamination.py` and confirm exit code 0.
- Run the proposed `rsync -avnc --delete` dry run.
- Review delete/add/update lines from the dry run.
- Confirm production-only paths are intended for Vitrine.
- Confirm `BodhiCircuitLeaf.png` transparent/no-background asset is included.
- Spot-check `LD.AA.000`, `BA.AA.004`, `archive.html`, `index.json`, and `search_index.json`.
- Confirm no source, CSL, metadata CSV, SP10/SP11, or deployment config changes are part of the promotion.

## Post-Promotion Validation Checklist

After a future approved sync, still before deploy/publish confirmation:

- Re-run string checks in `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`.
- Confirm stale strings are absent:
  - `Vivendo il Dhamma`
  - `Viparie1B987Ama Two Meanings`
  - `pending translation / pendente de tradução`
- Confirm corrected strings are present:
  - `Vivendo o Dhamma`
  - `Vipariṇāma Two Meanings`
  - `Awaiting translation / Aguardando tradução`
- Confirm `BodhiCircuitLeaf.png` hash matches production.
- Run a targeted `diff -qr` after sync and inspect any remaining differences.
- Perform visual smoke review of key pages before considering public promotion complete.

## Rollback Idea

Before real sync in a future sprint, capture the current published static payload state by branch, tag, or archive. If rollback is needed, restore `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/` from that captured state and re-run the post-promotion validation checks.

## Non-Actions

This sprint did not:

- copy files;
- sync files;
- modify `/home/sanghop/axis/axis-niddhi-published`;
- update Netlify/Vitrine;
- deploy;
- run build or pipeline;
- call DeepL;
- translate anything;
- modify CSL content;
- modify static artifacts;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11 behavior;
- create an apply script;
- change `.gitignore`.

## Recommendation

Ready for `#FlagFix_053` dry-run sync planning/execution, provided it remains dry-run first and targets only:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/`

Not ready for direct real sync or public promotion without:

- reviewing the dry-run output;
- confirming the production-only paths;
- performing visual review after the dry run plan is accepted.
