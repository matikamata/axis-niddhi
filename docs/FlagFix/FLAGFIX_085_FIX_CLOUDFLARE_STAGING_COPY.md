# FlagFix 085 - Fix Cloudflare staging copy on public contribute surface

Date: 2026-05-19

## Reason for Fix

After root CTA parity was corrected, the public `contribute.html` still displayed host-specific wording:

- `AXIS-NIDDHI Cloudflare Staging`

That wording is not appropriate for stable Vitrine copy and should be host-neutral.

## Copy Change

Old wording:

- `AXIS-NIDDHI Cloudflare Staging`

New wording:

- `AXIS-NIDDHI Collaboration Surface`

Additional neutralization applied in body text:

- English section:
  - from `This Cloudflare site ... staging surface ...`
  - to `This site ... collaboration surface ...`
- Portuguese section:
  - from `Este site no Cloudflare ...`
  - to `Este site é ...`

## Files Changed

- `pipeline/13-static-site/contribute.html`

No template source file for contribute was found under:

- `pipeline/13-ssg/templates/contribute.html` (missing)
- `pipeline/13-ssg/static/contribute.html` (missing)

## Remaining `Cloudflare Staging` Hits

Checked:

- `pipeline/13-static-site/contribute.html`
- `pipeline/13-ssg/**`

Result:

- no remaining `Cloudflare Staging` / `cloudflare staging` hits in these contribute/source locations.

Neutral label presence check:

- `AXIS-NIDDHI Collaboration Surface` found in `pipeline/13-static-site/contribute.html`.

## LABZ Exclusion Confirmation

- No LABZ files changed.
- No Bodhi/flower files changed.
- No LABZ promotion action performed.

## Scope / Safety Confirmation

- Changed path scope is minimal:
  - only `pipeline/13-static-site/contribute.html`
- No deploy
- No Netlify upload
- No build/pipeline run
- No DeepL call
- No translation workflow change
- No CSL/metadata/TCC/SP10/SP11 changes
- No sync/copy to `axis-niddhi-published`

## Recommendation

After merge, promote this small copy patch to published/Netlify in a separate sprint and run a focused public smoke check for `contribute.html`.
