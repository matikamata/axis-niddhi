# FlagFix 078 - LABZ preview closure and Bodhi asset preservation

Date: 2026-05-19

## Summary

#FlagFix_077 opened the LABZ ambient side-layer path technically and made it available for Cloudflare preview.

After visual review, the operator decision is:

- The LABZ side-layer technical path is useful as future infrastructure.
- The current two flower visuals are not approved as final.
- LABZ visual iteration is paused here.
- Future work may revisit better ambient assets from a new design brief.
- The current LABZ preview state should not be promoted to Netlify/Vitrine.

## Visual Decision

LABZ flower preview:

`TECHNICAL PASS / VISUAL NOT FINAL`

Operational implications:

- Do not treat the current flower assets as approved final design.
- Do not promote this LABZ state to Netlify/Vitrine.
- Do not continue visual iteration in this sprint block.

## Bodhi Asset Finding

The latest static build restored the older Bodhi asset because the old file still existed in the SSG source path:

- `pipeline/13-ssg/static/assets/BodhiCircuitLeaf.png`

The operator manually replaced the Bodhi leaf asset in both source and generated static:

- `pipeline/13-ssg/static/assets/BodhiCircuitLeaf.png`
- `pipeline/13-static-site/assets/BodhiCircuitLeaf.png`

This sprint preserves that correction so future builds use the corrected SSG source asset.

## Files Preserved

| File | Type | Dimensions | Size | SHA256 |
| --- | --- | ---: | ---: | --- |
| `pipeline/13-ssg/static/assets/BodhiCircuitLeaf.png` | PNG RGBA | 2048 x 2048 | 3136828 bytes | `92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7` |
| `pipeline/13-static-site/assets/BodhiCircuitLeaf.png` | PNG RGBA | 2048 x 2048 | 3136828 bytes | `92437a1aba75f9b6fb0d16f8598e1b0902a08c6c513d9014ac295d29848e49c7` |

Hash parity:

`MATCH`

## Checks

- Published repo was inspected read-only.
- LABZ CSS/HTML/JS were not changed in this sprint.
- Result: `NO_LABZ_CODE_CHANGE_IN_078`
- Path scope result: `PATH_SCOPE_OK`

## No-Change Confirmations

- No build/pipeline run.
- No deploy.
- No Netlify/Vitrine update.
- No `/home/sanghop/axis/axis-niddhi-published` changes.
- No CSL changes.
- No metadata CSV changes.
- No `Translation_Control_Center.csv` changes.
- No SP10/SP11 changes.
- No DeepL call.
- No translation.
- No LABZ CSS/HTML/JS changes.
- No bee assets added.

## Recommendation

Merge this preservation/closure PR, then checkpoint.

After that:

- Stop LABZ visual iteration for now.
- Keep the technical side-layer infrastructure available for future review.
- Start any future LABZ visual work from a new design brief rather than from these two flower candidates.
