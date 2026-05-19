# #FlagFix_088 — LABZ Netlify Migration Structural Audit

## Why this audit was opened
After #FlagFix_087, Netlify root/contribute CTA parity is confirmed, but LABZ ambient flower visuals are still not visible on Netlify. This audit checks structural readiness for a later, controlled migration.

## Scope and non-actions
Read-only audit only.

No deploy, no Netlify upload, no build/pipeline run, no sync/copy, no translation/DeepL, no CSL/metadata/TCC/SP10/SP11 changes, no `.gitignore` change, no edits to LABZ/Bodhi/flower files.

## Production state
- `git status -sb`: `## main...origin/main`
- checkpoint found: `checkpoint/flagfix-087-netlify-root-contribute-smoke-check-20260519`

## Inventory results (LABZ/Bodhi/flower filename patterns)
- Production inventory count: `12`
- Published inventory count: `5`

### Only in production (summary)
Count: `7`

- `pipeline/13-ssg/static/assets/BodhiCircuitLeaf.png`
- `pipeline/13-ssg/static/assets/labz/`
- `pipeline/13-ssg/static/assets/labz/labz-lily-right-mvp-01.webp`
- `pipeline/13-ssg/static/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
- `pipeline/13-static-site/assets/labz/`
- `pipeline/13-static-site/assets/labz/labz-lily-right-mvp-01.webp`
- `pipeline/13-static-site/assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`

### Only in published (summary)
Count: `0`

## Reference and route findings
- Production contains LABZ activation and ambient-layer references in:
  - `pipeline/13-static-site/css/style.css`
  - `pipeline/13-static-site/js/main.js`
  - `pipeline/13-ssg/static/css/style.css`
  - `pipeline/13-ssg/static/js/main.js`
  - `pipeline/13-ssg/templates/base.html`
- Production CSS includes explicit flower asset references:
  - `../assets/labz/labz-ora-pro-nobis-left-mvp-01.webp`
  - `../assets/labz/labz-lily-right-mvp-01.webp`
- Published CSS has LABZ/stardust theme rules and `toggleLabz()` support, but does not include the FF-071 ambient side-layer block with the flower image URLs.
- Published static inventory has no `assets/labz/` files.

## Host-specific dependency findings
- Targeted grep found no direct LABZ host lock-in (`cloudflare/pages.dev/netlify` paired with `labz/stardust`): `0` hits.
- Structural interpretation: current LABZ ambient implementation is static-file/CSS/markup based, not host-API dependent.

## Public Cloudflare vs Netlify observations (read-only)
- Cloudflare:
  - `https://niddhi.pages.dev/` returns `302` to `/welcome`
  - `https://niddhi.pages.dev/welcome` returns `200`
- Netlify:
  - `https://niddhi.netlify.app/` returns `200`
  - `https://niddhi.netlify.app/welcome` returns `200`
- CTA smoke indicators present on both public surfaces (`CONTRIBUTE`, `COLABORAR`), but this does not imply LABZ ambient parity.

## Structural conclusion
LABZ is missing on Netlify primarily because the published payload currently lacks:
1. LABZ flower asset files under `pipeline/13-static-site/assets/labz/`
2. The ambient side-layer CSS/image-reference block present in production static.

This is a payload-content gap, not a host-platform limitation.

## Recommendation
`NEEDS_VISUAL_DESIGN_REVIEW`

Reason:
- Technically, migration path is straightforward and appears host-neutral.
- Product decision is still to keep LABZ visuals paused/not final.
- Therefore, do not migrate LABZ to Netlify yet; re-open only under an explicit future visual-approval sprint.

## Explicit no-change confirmations
- No deploy
- No Netlify upload
- No build/pipeline run
- No sync/copy to published
- No edits to LABZ/Bodhi/flower files
- No DeepL/translation
- No CSL/metadata/TCC/SP10/SP11 changes
- No `.gitignore` changes
