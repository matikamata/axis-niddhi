# FlagFix 053 — Vitrine Promotion Dry Run

Date: 2026-05-19

## Scope

This sprint ran the approved Vitrine promotion dry run only. No real sync was executed.

Source:

- `/home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/`

Target:

- `/home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/`

The target structure matches `netlify.toml`:

- `publish = "pipeline/13-static-site"`

Checkpoint reference:

- `checkpoint/flagfix-052-vitrine-promotion-plan-20260518`

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

## Dry-Run Command

Executed dry-run command:

```bash
rsync -avnc --delete \
  /home/sanghop/axis/axis-niddhi-production/pipeline/13-static-site/ \
  /home/sanghop/axis/axis-niddhi-published/pipeline/13-static-site/ \
  > /tmp/flagfix_053_vitrine_rsync_dry_run.txt
```

Output path:

- `/tmp/flagfix_053_vitrine_rsync_dry_run.txt`

## Dry-Run Summary

- dry-run line count: 1527
- delete preview count: 0
- transfer/update item count: 1523

First dry-run lines:

```text
sending incremental file list
./
_redirects
archive.html
build_meta.json
contribute.html
index.html
index.json
search_index.json
welcome.html
assets/
assets/BodhiCircuitLeaf.png
assets/BodhiCircuitLeaf_original.png
assets/nana/
assets/nana/manifest.json
assets/nana/answer_validation/
assets/nana/answer_validation/answer-validation-dukkha-bootstrap-v1.json
assets/nana/council/
assets/nana/council/council-dukkha-bootstrap-v1.json
assets/nana/execution/
assets/nana/execution/execution-dukkha-mock-bootstrap-v1.json
assets/nana/execution/execution-dukkha-none-bootstrap-v1.json
assets/nana/provider_runs/
assets/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json
assets/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json
css/style.css
css/typography-pro.css
js/main.js
pages/AB.AA.000/
pages/AB.AA.000/index.html
pages/AB.BB.001/
pages/AB.BB.001/index.html
pages/AB.BB.002/
pages/AB.BB.002/index.html
pages/AB.BB.003/
pages/AB.BB.003/index.html
pages/AB.BB.004/
pages/AB.BB.004/index.html
pages/AB.BB.005/
pages/AB.BB.005/index.html
```

Interpretation:

- the dry run previews a broad static payload refresh;
- no delete operations are previewed;
- the approved transparent `BodhiCircuitLeaf.png` is included in the preview;
- `contribute.html`, `welcome.html`, `BodhiCircuitLeaf_original.png`, and `assets/nana/**` are included in the preview.

## Published State Before Real Sync

Published/Vitrine still contains stale strings before any real sync:

```text
axis-niddhi-published/pipeline/13-static-site/index.json: "Viparie1B987Ama Two Meanings"
axis-niddhi-published/pipeline/13-static-site/index.json: "Vivendo il Dhamma"
axis-niddhi-published/pipeline/13-static-site/search_index.json: "Viparie1B987Ama Two Meanings"
axis-niddhi-published/pipeline/13-static-site/search_index.json: "Vivendo il Dhamma"
axis-niddhi-published/pipeline/13-static-site/pages/LD.AA.000/index.html: "Vivendo il Dhamma"
axis-niddhi-published/pipeline/13-static-site/pages/BA.AA.004/index.html: "Viparie1B987Ama Two Meanings"
axis-niddhi-published/pipeline/13-static-site/archive.html: "Vivendo il Dhamma"
```

Published Bodhi asset before real sync:

```text
de326fede79eca1b87237bbbb6274b74fd3a86191d15683d9b6521d2395c8545  axis-niddhi-published/pipeline/13-static-site/assets/BodhiCircuitLeaf.png
```

Read-only status check of `/home/sanghop/axis/axis-niddhi-published` showed existing modified files in its static subtree. Because this sprint ran only `rsync -n`, those target-workspace modifications were not caused by #FlagFix_053. Review the target workspace state before any future real sync.

## Real Sync Status

Real sync was not run.

No command without `--dry-run`/`-n` was executed.

## Recommendation

Proceed to real sync only after explicit operator approval of this dry-run summary.

Before approval, review:

- the broad 1523-item update preview;
- the zero-delete result;
- the included production-only files/directories;
- the already-dirty published workspace status;
- representative pages after a future sync, especially `LD.AA.000`, `BA.AA.004`, `archive.html`, `index.json`, and `search_index.json`.

## Non-Actions

This sprint did not:

- copy files;
- sync files for real;
- modify `/home/sanghop/axis/axis-niddhi-published`;
- deploy;
- run build or pipeline;
- call DeepL;
- translate anything;
- modify CSL content;
- modify metadata CSVs;
- modify `Translation_Control_Center.csv`;
- modify SP10/SP11 behavior;
- create an apply script;
- change `.gitignore`.
