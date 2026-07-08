# Derived Media Companion V0 Audit - 2026-07-08

## Summary

Branch: `feature/derived-media-companion-v0`

Workspace: `/home/imac2014/projects/axis/axis-niddhi-production`

Scope: post-implementation audit for the downstream Derived Media Companion Layer V0. This layer remains auxiliary and does not become Canon.

## Files Changed

Feature files:

- `.gitignore`
- `docs/DERIVED_MEDIA_COMPANION_LAYER_V0.md`
- `docs/DERIVED_MEDIA_COMPANION_LAYER_V0_PLAN.md`
- `docs/DERIVED_MEDIA_COMPANION_V0_AUDIT_20260708.md`
- `docs/DERIVED_MEDIA_COMPANION_V0_GITHUB_ISSUE_BODY.md`
- `pipeline/13-ssg/build.py`
- `pipeline/13-ssg/src/renderers/post_renderer.py`
- `pipeline/13-ssg/src/transformers/__init__.py`
- `pipeline/13-ssg/templates/post.html`
- `pipeline/derived_media/README.md`
- `pipeline/derived_media/summaries/.gitkeep`
- `pipeline/metadata/derived_media_manifest.json`
- `pipeline/metadata/derived_media_registry.csv`
- `pipeline/scripts/tools/DM01_scan_derived_media.py`
- `pipeline/scripts/tools/DM02_generate_derived_media_manifest.py`

Pre-existing dirty files intentionally not included in this feature:

- `pipeline/metadata/Translation_Control_Center.csv`
- `pipeline/metadata/translation_status.json`

## Commands Run

Workspace/auth inspection:

```bash
pwd
git status -sb
git branch --show-current
git remote -v
gh auth status
```

Audit and validation:

```bash
git diff --name-only
git diff --stat
git status --porcelain | rg -i '\.(m4a|mp4|webm|wav|mp3)$'
git ls-files | rg -i '\.(m4a|mp4|webm|wav|mp3)$'
rg -n 'GOOGLE_APPLICATION_CREDENTIALS|PRIVATE KEY|SECRET|/home/|C:\\|file://' \
  pipeline/metadata/derived_media_manifest.json \
  pipeline/metadata/derived_media_registry.csv \
  pipeline/derived_media \
  pipeline/scripts/tools/DM01_scan_derived_media.py \
  pipeline/scripts/tools/DM02_generate_derived_media_manifest.py \
  docs/DERIVED_MEDIA_COMPANION_LAYER_V0.md \
  docs/DERIVED_MEDIA_COMPANION_LAYER_V0_PLAN.md
python3 -m py_compile pipeline/scripts/tools/DM01_scan_derived_media.py pipeline/scripts/tools/DM02_generate_derived_media_manifest.py
python3 pipeline/scripts/tools/DM01_scan_derived_media.py --source /home/imac2014/projects/axis/axis-derived-media-staging/raw --dry-run --verbose
python3 pipeline/scripts/tools/DM02_generate_derived_media_manifest.py
cat pipeline/metadata/derived_media_manifest.json
bash pipeline/scripts/tools/axis_cli.sh verify pipeline
python3 pipeline/13-ssg/build.py --clean
rg -n 'Auxiliary derived media|media.example.invalid|derived-media-companion' pipeline/13-static-site
```

Positive render validation:

```bash
python3 - <<'PY'
# Isolated Jinja render check for derived_media block.
PY
```

## Results

- Branch check: passed; current branch is `feature/derived-media-companion-v0`.
- GitHub auth: failed; `gh` reports the default token for `matikamata` is invalid.
- Canonical safety: passed for this feature.
- `pipeline/09-csl/` touched: no.
- `pipeline/03-translations/` touched: no.
- `pipeline/sources/` touched: no.
- `pipeline/ledger/` touched: no.
- `pipeline/seeds/` touched: no.
- Release manifests touched: no.
- Source ZIPs touched: no.
- Binary media added/tracked: no.
- Static payload forbidden-marker scan: no forbidden markers in registry or manifest. The scan reports the forbidden marker strings inside validator source code only, where they are expected guard literals.
- Python compile: passed.
- Scanner dry-run: passed. It found 18 PDPN groups and 35 recognized candidates.
- Manifest generation: passed. Current manifest is `{}` because no registry rows are approved.
- Pipeline integrity: passed with warnings for missing local `.venv` and missing `pymysql`.
- Static build no-op: passed. Build completed with 748 posts rebuilt and 0 errors. Logs confirmed the derived media manifest is empty and the companion layer is a no-op.
- Empty companion block check: passed. No `derived-media-companion` or `Auxiliary derived media` block appears in generated `pipeline/13-static-site` when the manifest is `{}`.

## Scanner Warnings

- `045V_TL.GG.08_Perigo das Visões Erradas.mp4` skipped because `TL.GG.08` does not match the required three-digit PDPN format.
- `045_TL.GG.08_Como a visão distorcida causa sofrimento.m4a` skipped for the same reason.
- `TL.BB.004` has multiple audio candidates; operator must choose manually.
- `TL.BB.007` has multiple audio candidates; operator must choose manually.

## Positive Render Test

Run as an isolated Jinja template render, not as a temporary registry/static build. Reason: a full positive registry build would rewrite hundreds of generated static files in this checkout. The isolated render safely confirmed:

- no block renders when `derived_media={}`;
- summary link renders when present;
- `<audio controls preload="metadata">` renders when an audio URL exists;
- `<video controls preload="metadata">` renders when a video URL exists;
- external links render only when present;
- no `media.example.invalid` URL remains in the working tree.

## Known Warnings

- `gh auth status` failed due invalid token, so no GitHub issue, branch push, or Draft PR was created from this audit pass.
- `git diff --check` over the full working tree reports trailing whitespace in the pre-existing dirty `pipeline/metadata/Translation_Control_Center.csv`. The feature-scoped diff check should exclude that unrelated file.
- Static build generated many expected `pipeline/13-static-site/` changes during validation; they were restored and are not part of the feature commit.

## Rollback Path

To roll back Derived Media Companion Layer V0:

1. Revert the derived media integration in `pipeline/13-ssg/build.py`.
2. Revert the derived media block in `pipeline/13-ssg/templates/post.html`.
3. Revert the `derived_media_manifest` plumbing in `pipeline/13-ssg/src/renderers/post_renderer.py`.
4. Remove `pipeline/13-ssg/src/transformers/__init__.py` if it is not needed after rollback.
5. Remove `pipeline/scripts/tools/DM01_scan_derived_media.py`.
6. Remove `pipeline/scripts/tools/DM02_generate_derived_media_manifest.py`.
7. Remove `pipeline/metadata/derived_media_registry.csv`.
8. Remove `pipeline/metadata/derived_media_manifest.json`.
9. Remove `pipeline/derived_media/` if no text summaries need preservation.
10. Remove the derived media docs if the policy/plan/audit docs are no longer needed.
11. Confirm no `.m4a`, `.mp4`, `.webm`, `.wav`, or `.mp3` files are tracked.

No CSL repair, source ZIP repair, release manifest repair, ledger edits, or seed edits are required because the feature does not modify canonical content.
