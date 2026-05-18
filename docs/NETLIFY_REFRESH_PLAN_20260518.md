# NETLIFY_REFRESH_PLAN_20260518

## 1. Purpose

This document is a future plan for deciding how and when to refresh the official Netlify surface after Cloudflare staging changes are stable, visually reviewed, and approved by a human.

It does not approve a Netlify refresh. It preserves the decision points, risks, and safe migration steps before any official public payload is changed.

## 2. Surface roles

| Surface | URL | Local path | Role |
|---|---|---|---|
| Cloudflare staging | https://niddhi.pages.dev/ | `<AXIS_ROOT>/axis-niddhi-production` | development/staging preview |
| Official Netlify | https://niddhi.netlify.app/ | `<AXIS_ROOT>/axis-niddhi-published/pipeline/13-static-site` | public surface shared by Prof. Lal |
| GitHub repo | https://github.com/matikamata/axis-niddhi | `<AXIS_ROOT>/axis-niddhi-production` | canonical tracked source |

`<AXIS_ROOT>` refers to the local operator workspace root. On the current maintainer machine this is `/home/sanghop/axis`, but public docs should avoid relying on one machine-specific path.

## 3. Changes currently proven on Cloudflare

These changes are candidates for review because they have been tested or prepared on the Cloudflare staging surface:

- Welcome gateway for clearer first entry.
- Contributor gateway for developers, reviewers, translators, and careful readers.
- Bee onboarding flow for small, verifiable first contributions.
- GitHub issue templates for translation review, visual QA, and broken-link reports.
- Archive guided navigation refinements.
- pt-BR translation status wording for pages without Portuguese translations.
- Final dedication section on the contributor gateway.

## 4. What must NOT be rushed into Netlify

Do not rush these into the official Netlify payload:

- Unreviewed UI experiments.
- Source-only changes that require build parity before static publication.
- Incomplete NANA, Navigator, or Cosmos prototypes.
- Anything that changes translation or corpus identity.
- Anything not visually reviewed on Cloudflare first.

## 5. Candidate files for future migration

The following are candidates only. They are not approved for migration by this document:

- `pipeline/13-static-site/welcome.html`
- `pipeline/13-static-site/contribute.html`
- `pipeline/13-static-site/_redirects`
- `pipeline/13-static-site/archive.html`
- `pipeline/13-static-site/css/style.css`
- `pipeline/13-static-site/js/main.js`
- Any specific post pages touched for translation status wording.

## 6. Pre-migration checklist

Before any Netlify refresh is approved:

- Cloudflare links verified.
- `/` route verified.
- `/welcome` and `/welcome.html` behavior understood.
- `/contribute` and `/contribute.html` behavior understood.
- Archive navigation reviewed.
- Issue templates verified.
- No browser redirect loops.
- No broken internal links.
- No accidental local-only links.
- No `127.0.0.1`, `localhost`, or absolute local paths.
- Screenshots saved if useful.

## 7. Safe migration method

Future proposal only:

1. Freeze production state with a tag.
2. Make a backup copy of the current `axis-niddhi-published`.
3. Copy only approved static payload files.
4. Test locally with `python3 -m http.server`.
5. Drag-and-drop to Netlify only after human approval.
6. Verify Netlify URLs.
7. Tag a checkpoint after successful publication.

## 8. Rollback plan

- Keep the previous Netlify payload backup.
- Re-upload the previous static folder if needed.
- Do not delete the old payload until the new one is verified.
- Preserve timestamped evidence for the refresh and any rollback.

## 9. Decision required before action

No Netlify refresh is approved by this document.

This document only prepares the decision.
