# FlagFix 056 — Commit Synced Vitrine Payload

Date: 2026-05-19

## Scope

This sprint committed the already-synced Vitrine static payload in:

- `/home/sanghop/axis/axis-niddhi-published`

Committed path scope:

- `pipeline/13-static-site/**`

No production static files were modified.

## Pre-Commit Review

Published repo before commit:

- branch: `main`
- status: `main...origin/main`
- modified paths: 758
- untracked files: 0
- outside expected area: 0
- expected area confirmed: `pipeline/13-static-site/**`

Diff stat before commit:

- `758 files changed`
- `14799 insertions(+)`
- `2977 deletions(-)`

## Parity Validation

Source:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site`

Target:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site`

Parity command:

```bash
diff -qr axis-niddhi-published/pipeline/13-static-site axis-niddhi-production/pipeline/13-static-site
```

Result:

- `/tmp/flagfix_056_parity_diff_qr.txt`
- line count: 0
- source and target static payloads matched before commit

## Published String Validation

Stale strings:

- `Vivendo il Dhamma`: 0 occurrences
- `Viparie1B987Ama Two Meanings`: 0 occurrences
- `pending translation / pendente de tradução`: 0 occurrences

Corrected strings:

- `Vivendo o Dhamma`: 8 occurrences in 8 files
- `Vipariṇāma Two Meanings`: 12 occurrences in 6 files
- `Awaiting translation / Aguardando tradução`: 439 occurrences in 1 file

## Bodhi Asset Hash

```text
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  axis-niddhi-production/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
```

The approved transparent/no-background Bodhi asset is now committed in the published payload.

## Published Commit

Commit command:

```bash
git add pipeline/13-static-site
git commit -m "build(vitrine): sync static payload after title corrections"
```

Published commit:

- short hash: `92f4c29`
- full hash: `92f4c298f17008f4022c0267f1e64af14a1742a1`
- message: `build(vitrine): sync static payload after title corrections`

Post-commit published status:

- `main...origin/main [ahead 1]`
- working tree clean

Remote:

```text
origin  https://github.com/matikamata/axis-niddhi.git (fetch)
origin  https://github.com/matikamata/axis-niddhi.git (push)
```

## Recommendation

Next step should be explicit operator review before any public update:

1. Perform visual review of representative Vitrine pages from the committed published workspace.
2. Decide whether to push `axis-niddhi-published` commit `92f4c29` to `origin/main`.
3. Confirm whether Netlify should update from Git or via manual drag/drop.

Do not deploy automatically from this sprint.

## Non-Actions

This sprint did not:

- deploy;
- push the published repo;
- run build or pipeline;
- call DeepL;
- translate anything;
- modify production repo files except this report;
- modify CSL;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11;
- change `.gitignore`;
- copy or sync again.
