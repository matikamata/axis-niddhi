# FlagFix 079 - Netlify/Cloudflare surface parity audit

Date: 2026-05-19

## Why This Audit Was Opened

The public Netlify Vitrine is online at:

- `https://niddhi.netlify.app/`

The public Cloudflare experimental surface is online at:

- `https://niddhi.pages.dev/`

Concern: the Netlify public root appeared to lack the `CONTRIBUTE` CTA that exists in the approved static payload and on Cloudflare.

Policy context:

- Cloudflare is the test/homologation/experimental surface.
- Netlify is the stable approved Vitrine.
- Once a payload is approved, Netlify should be an exact copy of the approved static payload, not a reduced or older surface.

## Repository State

Production repo:

- Path: `/home/sanghop/axis/axis-niddhi-production`
- Status: `main...origin/main`
- Current head includes `checkpoint/flagfix-078-labz-preview-closure-bodhi-asset-20260519`.

Published repo:

- Path: `/home/sanghop/axis/axis-niddhi-published`
- Status: `main...origin/main [ahead 1]`
- Head: `92f4c29 build(vitrine): sync static payload after title corrections`
- `netlify.toml` publish directory: `pipeline/13-static-site`

No repository files were changed during inspection except this report.

## Local Static Parity

Compared:

- `axis-niddhi-production/pipeline/13-static-site`
- `axis-niddhi-published/pipeline/13-static-site`

Result:

- Diff count: `753` lines from `diff -qr`

Interpretation:

- Current production static has moved past the last published local payload because #FlagFix_077 and #FlagFix_078 added LABZ preview/static changes and restored the corrected Bodhi asset in production.
- The published local payload remains the previously approved Vitrine payload from the title/static correction block.
- This means current production and local published are not expected to be byte-identical after #077/#078.

First diff examples:

- `archive.html` differs
- `assets/labz` exists only in production
- `build_meta.json` differs
- `css/style.css` differs
- generated page HTML differs across many pages

## Local CONTRIBUTE Search

Focused local surface files:

- `index.html`
- `welcome.html`
- `archive.html`
- `contribute.html`

Local production static:

- `welcome.html` contains:
  - `CONTRIBUTE`
  - `COLABORAR`
- `contribute.html` exists and contains `Contribute / Colaborar`.
- `index.html` does not contain the CTA.
- `archive.html` does not contain the CTA.

Local published static:

- `welcome.html` contains:
  - `CONTRIBUTE`
  - `COLABORAR`
- `contribute.html` exists and contains `Contribute / Colaborar`.
- `index.html` does not contain the CTA.
- `archive.html` does not contain the CTA.

Local redirect rule in both production and published payloads:

```text
/ /welcome 302
```

## Public HTTP Status Summary

Cloudflare:

- `https://niddhi.pages.dev/`
  - `302` to `/welcome`
  - final `200`
- `https://niddhi.pages.dev/archive.html`
  - `308` to `/archive`
  - final `200`

Netlify:

- `https://niddhi.netlify.app/`
  - `200`
  - no observed redirect to `/welcome`
- `https://niddhi.netlify.app/archive.html`
  - `200`

## Public CONTRIBUTE Search

Public root/archive files fetched into:

- `/tmp/flagfix_079_public_surface/`

Counts:

| Public file | CONTRIBUTE/COLABORAR hits | ENTER ARCHIVE hits | Corrected title/status hits | Stale string hits |
| --- | ---: | ---: | ---: | ---: |
| `cloudflare_root.html` | 2 | 2 | 0 | 0 |
| `cloudflare_archive.html` | 0 | 0 | 442 | 0 |
| `netlify_root.html` | 0 | 2 | 0 | 0 |
| `netlify_archive.html` | 0 | 0 | 442 | 0 |

Additional direct checks:

- `https://niddhi.netlify.app/welcome` contains `CONTRIBUTE` and `COLABORAR`.
- `https://niddhi.netlify.app/welcome.html` contains `CONTRIBUTE` and `COLABORAR`.
- `https://niddhi.netlify.app/contribute.html` exists and contains `Contribute / Colaborar`.
- `https://niddhi.pages.dev/welcome` contains `CONTRIBUTE` and `COLABORAR`.
- `https://niddhi.pages.dev/contribute.html` exists and contains `Contribute / Colaborar`.

Conclusion:

- Netlify does include the contribute surface.
- Netlify public root does not show it because the root is serving an index-style page without the CTA rather than redirecting to `/welcome`.
- Cloudflare public root does show it because Cloudflare redirects `/` to `/welcome`.

## Public Cloudflare vs Netlify Diff Summary

Root comparison:

- `cloudflare_root.html` vs `netlify_root.html`
- Diff length: `140` lines

Archive comparison:

- `cloudflare_archive.html` vs `netlify_archive.html`
- Diff length: `12796` lines

Important root difference:

- Cloudflare root content is equivalent to the current `welcome.html` surface and includes `CONTRIBUTE`.
- Netlify root content is an older/index-style surface and omits `CONTRIBUTE`.

## Public Netlify vs Local Published

Local published surface files:

- `index.html`: exists, `7558` bytes
- `welcome.html`: exists, `7015` bytes
- `archive.html`: exists, `507209` bytes

Comparisons:

- Local published `welcome.html` vs public Netlify root: `140` diff lines
- Local published `index.html` vs public Netlify root: `20` diff lines
- Local published `archive.html` vs public Netlify archive: `12780` diff lines

Interpretation:

- Public Netlify root most closely resembles local `index.html`, not local `welcome.html`.
- Public Netlify archive is not byte-identical to local published archive.
- Public Netlify therefore does not currently match the local published payload exactly.

## Corrected/Stale String Checks

Public corrected strings:

- Cloudflare archive contains corrected title/status strings.
- Netlify archive contains corrected title/status strings.

Public stale strings:

- No hits for:
  - `Vivendo il Dhamma`
  - `Viparie1B987Ama Two Meanings`
  - `pending translation / pendente de tradução`

This suggests the title/static correction block has reached both public surfaces, even though root routing/surface parity is not aligned.

## Root Cause Hypothesis

Most likely:

1. The local approved payload contains `CONTRIBUTE` in `welcome.html` and contains `contribute.html`.
2. Cloudflare publicly redirects `/` to `/welcome`, so the CTA appears on the root URL.
3. Netlify publicly serves `/` as an index-style page that does not contain the CTA.
4. Netlify public is not an exact byte match for the local published payload; either:
   - the public Netlify deploy is not the exact local published package, or
   - Netlify routing is not applying the local `_redirects` rule as expected, or
   - the root `index.html`/`welcome.html` split is structurally fragile for Netlify.

Not supported by the evidence:

- The local approved payload lacks `CONTRIBUTE`.
- The `contribute.html` page is absent from Netlify.
- Cloudflare has a branch-only CTA that never reached local static.

## Recommendation

Open a follow-up FlagFix before any further upload/deploy:

`#FlagFix_080 — Netlify root routing and CONTRIBUTE CTA parity plan`

Recommended focus:

- Decide whether Netlify root should:
  - force redirect `/` to `/welcome`, or
  - make `index.html` the canonical welcome surface and include `CONTRIBUTE` there too.
- Verify why Netlify public root ignores or bypasses the local `_redirects` expectation.
- Verify whether the deployed Netlify payload is exactly the package expected from #FlagFix_068/#069.
- Do not upload another package until this root routing decision is explicit.

If the desired stable Vitrine behavior is "root must show the CTA," the lowest-risk product fix may be to make `index.html` and `welcome.html` intentionally aligned, rather than depending on host-specific root redirect behavior.

## Explicit Non-Actions

- No deploy.
- No Netlify upload.
- No push.
- No build/pipeline run.
- No DeepL call.
- No translation.
- No CSL changes.
- No metadata CSV changes.
- No `Translation_Control_Center.csv` changes.
- No SP10/SP11 changes.
- No sync/copy.
- No `.gitignore` changes.
- No `/home/sanghop/axis/axis-niddhi-published` changes.
- No production static changes.
