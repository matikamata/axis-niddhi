# #FlagFix_094 — LABZ Controlled Netlify Promotion Plan

## Purpose
Define a read-only, controlled promotion plan for LABZ from production static into Netlify/Vitrine payload, without performing any copy/sync/deploy in this sprint.

## Decision chain (#088–#093)
- `#088`: structurally migratable; gap is payload mismatch.
- `#089`: visual checklist defined.
- `#090`: visual hold for polish.
- `#091`: polish plan approved for Cloudflare-only patch.
- `#092`: minimal CSS-only polish applied (source + static CSS counterparts).
- `#093`: post-polish review result `POST_POLISH_VISUAL_PASS_WITH_MINOR_NOTES`.

## Inventory snapshot
- Production LABZ/Bodhi/flower inventory count: `12`
  - source: `/tmp/flagfix_094_production_labz_inventory.txt`
- Published LABZ/Bodhi/flower inventory count: `5`
  - source: `/tmp/flagfix_094_published_labz_inventory.txt`

## Comparison summary

### Missing from published (normalized list)
Count: `7`

From `/tmp/flagfix_094_labz_missing_from_published.txt`:
- `assets/labz`
- `assets/labz/labz-lily-right-mvp-01.webp`
- `assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
- `static/assets/BodhiCircuitLeaf.png`
- `static/assets/labz`
- `static/assets/labz/labz-lily-right-mvp-01.webp`
- `static/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`

Important interpretation:
- Entries prefixed with `static/...` come from `pipeline/13-ssg/static/...` and are source-side artifacts, not direct published payload paths.
- For Netlify/Vitrine promotion dry-run scope, target should be `pipeline/13-static-site/...` only.

### Common paths already present in published
Count: `5`

- `assets/BodhiCircuitLeaf.png`
- `assets/BodhiCircuitLeaf_White_Bakg.png`
- `assets/BodhiCircuitLeaf_original.png`
- `assets/images/Bhikkhu_Bodhi-Comprehensive_Manual_of_Abhidhamma-pdf.jpg`
- `assets/images/Bhikkhu_Bodhi-Comprehensive_Manual_of_Abhidhamma.pdf`

## Proposed future promotion scope (dry-run candidate)
Scope to evaluate in `#FlagFix_095` (no action now):

1. `pipeline/13-static-site/assets/labz/`
2. `pipeline/13-static-site/css/style.css` (contains post-polish LABZ ambient rules and asset URLs)

Optional verification-only context (no promotion action implied):
- `pipeline/13-static-site/index.html`
- `pipeline/13-static-site/welcome.html`
- `pipeline/13-static-site/contribute.html`

## Explicitly excluded from future LABZ promotion scope
- `pipeline/13-ssg/**` source tree (not published payload target for Netlify upload)
- CSL/metadata/TCC/SP10/SP11 and translation pipeline files
- `.gitignore`
- unrelated docs/scripts/review artifacts
- any broad full-static sync beyond controlled LABZ scope

## CSS/source/static parity guidance
- Authoritative deploy payload is `pipeline/13-static-site/**`.
- `pipeline/13-ssg/**` parity is engineering source parity, not a direct Netlify upload requirement.
- For controlled Netlify dry-run, compare production static vs published static only.

## Published repo state (read-only)
- `git status -sb`: `## main...origin/main [ahead 2]`
- top commits:
  - `5da4e59 fix(vitrine): align root landing CTA`
  - `92f4c29 build(vitrine): sync static payload after title corrections`

## Public baseline (read-only headers)
- Cloudflare:
  - `https://niddhi.pages.dev/` -> `302` to `/welcome`
  - `https://niddhi.pages.dev/welcome` -> `200`
- Netlify:
  - `https://niddhi.netlify.app/` -> `200`
  - `https://niddhi.netlify.app/welcome` -> `200`

## Rollback/snapshot requirement before any future promotion
Before any real sync/upload in a future sprint:
1. Capture published snapshot (status, `git diff --stat`, patch/tarball + SHA256).
2. Run promotion as dry-run first (`rsync -avnc --delete` style).
3. Review candidate path list and confirm LABZ-only scope.
4. Proceed to real sync/upload only after explicit approval.

## Recommendation
`READY_FOR_DRY_RUN_ONLY`

## Next sprint recommendation
`#FlagFix_095 — LABZ Netlify promotion dry-run`

## Explicit statement
No LABZ promotion was performed in #094.

## No-change confirmations
- No deploy
- No Netlify upload
- No sync/copy to published
- No edits in `axis-niddhi-published`
- No build/pipeline run
- No website/CSS/LABZ/Bodhi/flower edits
- No DeepL/translation
- No CSL/metadata/TCC/SP10/SP11 changes
- No `.gitignore` changes
