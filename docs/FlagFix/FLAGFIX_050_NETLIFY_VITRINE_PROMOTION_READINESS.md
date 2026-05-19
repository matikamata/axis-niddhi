# FlagFix 050 — Netlify/Vitrine Promotion Readiness

Date: 2026-05-18

## Scope

This read-only audit compares the regenerated Cloudflare/dev static output with the currently published Netlify/Vitrine workspace before any promotion.

- Production/dev repo: `/home/sanghop/axis/axis-niddhi-production`
- Regenerated static source: `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site`
- Published Vitrine workspace: `/home/sanghop/axis/axis-niddhi-published`
- Comparable published static payload found at: `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Checkpoint reference:

- `checkpoint/flagfix-049-static-regeneration-after-title-corrections-20260518`

## Repository State

Initial state on branch `flagfix-050-netlify-vitrine-promotion-readiness` showed one pre-existing modified tracked static asset:

- `pipeline/13-static-site/assets/BodhiCircuitLeaf.png`

This audit did not modify or revert that file.

Operator note: `pipeline/13-static-site/assets/BodhiCircuitLeaf.png` appears as a pre-existing modified static asset because the background was intentionally removed in prior visual work, and the operator confirmed that context. #FlagFix_050 remains readiness/report-only: do not stage or commit the PNG in this PR, and leave asset handling or promotion to a separate explicitly approved sprint.

## Validator Results

Pre-promotion validators were run in `/home/sanghop/axis/axis-niddhi-production`.

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

## File Count Comparison

Raw workspace comparison:

- production static files: 3082
- published workspace files: 4135

The raw root-to-root comparison is not semantically equivalent because `/home/sanghop/axis/axis-niddhi-published` is a wider repository/workspace containing `.git`, docs, source folders, and other project files.

Comparable static payload comparison:

- production static files: 3082
- published static payload files: 3072

## Diff Summary

Root-level `diff -qr` between published workspace and production static produced 45 lines, mostly because the published root is not only the static payload.

Comparable static payload diff:

- diff lines: 762
- files differing: 758
- only in production static: 4
- only in published static: 0

Examples from the comparable payload diff:

- `_redirects` differs
- `archive.html` differs
- `assets/BodhiCircuitLeaf.png` differs
- `build_meta.json` differs
- `css/style.css` differs
- `css/typography-pro.css` differs
- `index.html` differs
- `index.json` differs
- `js/main.js` differs
- many `pages/*/index.html` files differ

Production-only static paths reported:

- `assets/BodhiCircuitLeaf_original.png`
- `assets/nana`
- `contribute.html`
- `pipeline/print_output`

## String Checks

Production static stale strings:

- `Vivendo il Dhamma`: 0 occurrences
- `Viparie1B987Ama Two Meanings`: 0 occurrences
- `pending translation / pendente de tradução`: 0 occurrences

Production static corrected strings:

- `Vivendo o Dhamma`: 8 occurrences in 8 files
- `Vipariṇāma Two Meanings`: 12 occurrences in 6 files
- `Awaiting translation / Aguardando tradução`: 439 occurrences in 1 file

Published static stale strings:

- `Vivendo il Dhamma`: 6 occurrences in 6 files
- `Viparie1B987Ama Two Meanings`: 12 occurrences in 6 files
- `pending translation / pendente de tradução`: 0 occurrences

Published static corrected strings:

- `Vivendo o Dhamma`: 2 occurrences in 2 files
- `Vipariṇāma Two Meanings`: 0 occurrences
- `Awaiting translation / Aguardando tradução`: 0 occurrences

Interpretation:

- Production static reflects the #028 and #037-#043 metadata corrections.
- Published Vitrine static still contains the stale LD.AA.000 and BA.AA.004 title artifacts.
- Published Vitrine does not yet contain the #036 archive/list copy improvement.

## Key Page Presence

All key files exist in both production static and the comparable published static payload:

- `archive.html`
- `index.json`
- `search_index.json`
- `pages/LD.AA.000/index.html`
- `pages/BA.AA.004/index.html`

The same files were not present directly at the published workspace root, confirming that the comparable payload is nested under `pipeline/13-static-site`.

## Risk Assessment

Promotion appears technically plausible because:

- pre-promotion validators pass;
- corrected strings are present in production static;
- stale strings are absent from production static;
- key pages exist in both payloads.

Promotion still needs review because:

- the comparable static payload diff is broad: 762 diff lines and 758 differing files;
- production has 10 more static files than the currently published static payload;
- there is a pre-existing modified tracked asset in production static: `pipeline/13-static-site/assets/BodhiCircuitLeaf.png`; the operator confirmed it comes from prior intentional visual work, but it should not be staged or committed in #FlagFix_050;
- the published workspace is not a bare static root, so any promotion command must target the nested static payload deliberately.

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
- modify static artifacts intentionally;
- stage or commit `pipeline/13-static-site/assets/BodhiCircuitLeaf.png`;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11 behavior;
- create an apply script;
- change `.gitignore`.

## Recommendation

Readiness status: conditionally ready for a separate promotion sprint after visual and diff review.

Recommended next step:

1. Review the broad static payload diff, especially `archive.html`, `index.json`, `search_index.json`, `css/*`, `js/main.js`, `assets/BodhiCircuitLeaf.png`, and representative corrected pages.
2. Confirm whether the production-only paths should be promoted.
3. Handle `BodhiCircuitLeaf.png` only in a separate visual asset/promotion sprint, even though its prior context is confirmed.
4. Perform Vitrine promotion only in a separate explicitly approved sprint.

Suggested future promotion command proposal only, not executed:

```bash
cd /home/sanghop/axis
rsync -av --delete \
  axis-niddhi-production/pipeline/13-static-site/ \
  axis-niddhi-published/pipeline/13-static-site/
```

Before any real sync, run the same command with `--dry-run` and review the output.
