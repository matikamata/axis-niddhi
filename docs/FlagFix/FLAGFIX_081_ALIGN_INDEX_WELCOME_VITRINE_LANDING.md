# FlagFix 081 - Align index and welcome Vitrine landing surface

Date: 2026-05-19

## Reason for Patch

FlagFix #079 and #080 confirmed root CTA parity drift:

- Cloudflare root (`/`) redirects to `/welcome`, so public root shows `CONTRIBUTE`.
- Netlify root (`/`) serves `index.html` directly, so the public root could miss `CONTRIBUTE` when `index.html` diverges.
- Approved CTA surface existed in `welcome.html`, but not in `index.html`.

To remove host-specific fragility, this patch aligns `index.html` and `welcome.html` to the same approved landing surface.

## Approved Landing Source

Approved CTA landing source used in this patch:

- `pipeline/13-static-site/welcome.html`

The same approved content was propagated to source templates and static root index.

## Files Changed

- `pipeline/13-ssg/templates/index.html`
- `pipeline/13-ssg/templates/welcome.html`
- `pipeline/13-static-site/index.html`

No other files were modified.

## CTA Parity Checks

All four target files now contain:

- `ENTER ARCHIVE`
- `CONTRIBUTE`
- `ACESSAR ACERVO`
- `COLABORAR`

## Index/Welcome Diff Results

Static:

- `diff -u pipeline/13-static-site/index.html pipeline/13-static-site/welcome.html`
- Result: `0` lines

Template:

- `diff -u pipeline/13-ssg/templates/index.html pipeline/13-ssg/templates/welcome.html`
- Result: `0` lines

Outcome:

- `index.html` now matches `welcome.html` in both static output and SSG source templates.

## Path Scope Result

Path scope validation returned:

- `PATH_SCOPE_OK`

Changed paths stayed within allowed scope.

## LABZ Exclusion Confirmation

- No LABZ CSS/HTML/JS/asset files were touched.
- No LABZ promotion action was performed.
- LABZ block remains excluded from Vitrine/Netlify in this sprint.

## No-Deploy / Safety Confirmation

- No deploy
- No Netlify upload
- No push
- No build/pipeline run
- No CSL changes
- No metadata CSV changes
- No `Translation_Control_Center.csv` changes
- No SP10/SP11 changes
- No DeepL call
- No translation
- No sync/copy to `axis-niddhi-published`
- No `.gitignore` changes

## Recommendation

Proceed with review of this surgical parity patch.

If approved, package/deploy to Netlify should happen in a separate sprint with standard Vitrine promotion controls.
