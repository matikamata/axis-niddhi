# FlagFix 064 — Static-Payload-Only Replacement PR

Date: 2026-05-19

## Scope

This sprint attempted to create a replacement PR from current production `main`, constrained to:

- `pipeline/13-static-site/**`
- this #064 report

The goal was to replace unsafe PR #155, which was blocked by #FlagFix_063 because its branch came from stale published repo history and included unsafe non-static path changes.

## Reason PR #155 Is Replaced

Blocked PR:

- `https://github.com/matikamata/axis-niddhi/pull/155`
- head: `flagfix-062-approved-vitrine-payload`

#FlagFix_063 found:

- PR #155 was based on stale published repo history;
- changed path scope failed;
- it included non-static paths such as `.gitignore`, `docs/**`, `pipeline/scripts/**`, `pipeline/metadata/**`, and `review/**`;
- it is not safe to merge.

## Source and Target

Approved payload source:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/`

Production target:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/`

Replacement branch:

- `flagfix-064-static-payload-only-vitrine-update`

Base:

- current production `main`
- `296ef555420f700ca0311feb5ebe657fcd62d7f4`
- checkpoint: `checkpoint/flagfix-063-review-pr155-blocked-20260519`

## Copy Result

Command run:

```bash
rsync -avc --delete \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/
```

Result:

- no static file transfer was needed;
- production `main` already matched the approved published static payload;
- `git diff` after the copy showed no `pipeline/13-static-site/**` changes.

## Changed Path Scope

Path scope result:

- `PATH_SCOPE_OK`

Observed before this report:

- no static payload diff;
- no bad paths;
- no files outside the allowed static subtree.

After this report:

- only this report is expected to be changed in production.

## Static Parity

Comparison:

```bash
diff -qr \
  axis-niddhi-production/pipeline/13-static-site \
  axis-niddhi-published/pipeline/13-static-site
```

Result:

- output: `/tmp/flagfix_064_static_parity_diff_qr.txt`
- diff line count: 0
- production static matches approved published static

## String Checks

Stale strings in production static:

- `Vivendo il Dhamma`: not found
- `Viparie1B987Ama Two Meanings`: not found
- `pending translation / pendente de tradução`: not found

Corrected strings in production static:

- `Vivendo o Dhamma`: found
- `Vipariṇāma Two Meanings`: found
- `Awaiting translation / Aguardando tradução`: found

## Bodhi Asset Hash

```text
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
```

The approved transparent `BodhiCircuitLeaf.png` asset already matches between production and published.

## Conclusion

A replacement static-payload diff is not needed from current production `main` because production already contains the approved static payload.

PR #155 remains unsafe because of branch ancestry and out-of-scope paths. The safe replacement action is therefore documentation/decision cleanup, not another static payload patch.

## Recommendation

Use this #064 finding instead of PR #155:

- do not merge PR #155;
- close or supersede PR #155 explicitly in a follow-up;
- if a GitHub PR is still desired, it should document that production `main` already has the approved static payload and that no static diff is required;
- do not deploy from PR #155.

## Non-Actions

This sprint did not:

- merge PR #155;
- close PR #155;
- deploy;
- run build or pipeline;
- call DeepL;
- translate anything;
- modify CSL;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11;
- change `.gitignore`;
- modify anything outside `pipeline/13-static-site/**` plus this report;
- alter `/home/sanghop/axis/axis-niddhi-published`.
