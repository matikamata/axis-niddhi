# FlagFix 055 — Vitrine Promotion Real Sync

Date: 2026-05-19

## Scope

This sprint performed the approved real Vitrine static payload sync after the #053 dry run and #054 rollback snapshot.

Source:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/`

Target:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/`

Only the target static payload directory was synced.

## Rollback Snapshot Verification

#054 rollback snapshot base:

- `/home/sanghop/axis/vitrine-safety-snapshots/flagfix_054_published_dirty_state_20260519_020609`

Verified SHA256:

```text
e9dad6d238b561230351d141e1aba619636279abb64a890789be525bd01dd782  /home/sanghop/axis/vitrine-safety-snapshots/flagfix_054_published_dirty_state_20260519_020609.patch
9d1523a308bd44fb28783c5df1c7f49a97e919ee31005bd9c5f4ee3569ae45a7  /home/sanghop/axis/vitrine-safety-snapshots/flagfix_054_published_dirty_state_20260519_020609_pipeline_13_static_site_snapshot.tar.gz
```

Both values matched the expected #054 report values before real sync.

## Validators

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

## Final Dry Run

Command:

```bash
rsync -avnc --delete \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/ \
  > /tmp/flagfix_055_vitrine_rsync_final_dry_run.txt
```

Counts:

- dry-run line count: 1527
- delete preview count: 0
- transfer/update item count: 1523

## Real Sync

Command executed:

```bash
rsync -avc --delete \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/ \
  > /tmp/flagfix_055_vitrine_rsync_real_sync.txt
```

Real sync output:

- `/tmp/flagfix_055_vitrine_rsync_real_sync.txt`
- line count: 1527

No deploy was run.

## Post-Sync String Validation

Published stale strings after sync:

- `Vivendo il Dhamma`: 0 occurrences
- `Viparie1B987Ama Two Meanings`: 0 occurrences
- `pending translation / pendente de tradução`: 0 occurrences

Published corrected strings after sync:

- `Vivendo o Dhamma`: 8 occurrences in 8 files
- `Vipariṇāma Two Meanings`: 12 occurrences in 6 files
- `Awaiting translation / Aguardando tradução`: 439 occurrences in 1 file

Representative corrected files:

- `pipeline/13-static-site/index.json`
- `pipeline/13-static-site/search_index.json`
- `pipeline/13-static-site/pages/LD.AA.000/index.html`
- `pipeline/13-static-site/pages/BA.AA.004/index.html`
- `pipeline/13-static-site/archive.html`

## Bodhi Asset Hash Comparison

```text
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  axis-niddhi-production/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7  axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
```

The published Vitrine payload now has the approved transparent/no-background Bodhi leaf asset.

## Source/Target Diff

Post-sync comparison:

```bash
diff -qr axis-niddhi-published/pipeline/13-static-site axis-niddhi-production/pipeline/13-static-site
```

Result:

- diff line count: 0
- source and target static payloads match

## Published Repo Status

After sync, `/home/sanghop/axis/axis-niddhi-published` shows:

- branch/status: `main...origin/main`
- porcelain changed paths: 758
- status counts: `M:758`
- untracked files: 0
- diff stat summary: `758 files changed, 14799 insertions(+), 2977 deletions(-)`

All observed changed paths are under:

- `pipeline/13-static-site/**`

## Recommendation

Next step should be a separate explicit review/publish sprint:

1. Review representative pages visually from the published workspace before any Netlify action.
2. Commit the `axis-niddhi-published` static payload changes if the review is approved.
3. Then decide whether Netlify uses Git-based update or manual drag/drop for the approved payload.

Do not treat this sync as a deployment. It only updated the local published/Vitrine payload workspace.

## Non-Actions

This sprint did not:

- deploy;
- run build or pipeline;
- call DeepL;
- translate anything;
- modify CSL;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11;
- create an apply script;
- change `.gitignore`;
- modify production static other than creating this #055 report.
