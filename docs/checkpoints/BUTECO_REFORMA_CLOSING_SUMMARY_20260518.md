# BUTECO_REFORMA_CLOSING_SUMMARY_20260518

## 1. Purpose

This document closes the Cloudflare staging, Bee onboarding, and contributor gateway reform cycle known as “Fechamento de Buteco / Reforma da Vitrine.”

It records the final state, completed work, guardrails, and recommended next steps so future maintainers and IDE agents can resume with less ambiguity.

## 2. Final state

- GitHub repo: `https://github.com/matikamata/axis-niddhi`
- Cloudflare staging: `https://niddhi.pages.dev/`
- Official Netlify remains protected: `https://niddhi.netlify.app/`
- `axis-niddhi-production` is the GitHub/Cloudflare staging workspace.
- `axis-niddhi-published` remains the manual Netlify payload and was not touched in this cycle.

## 3. What was completed

- Welcome gateway stabilized.
- Contributor gateway created and polished.
- Bee onboarding flow documented.
- Bee First Task issue created.
- GitHub issue templates added.
- Netlify refresh plan documented.
- Production-to-published Netlify refresh SOP documented.
- Cloudflare routing note documented.
- Static payload `.gitignore` hygiene improved.
- PR discipline guide added.
- Post 309 publication handoff preserved.

## 4. Important URLs

- `https://niddhi.pages.dev/`
- `https://niddhi.pages.dev/contribute`
- `https://niddhi.pages.dev/archive`
- `https://github.com/matikamata/axis-niddhi/issues/120`
- `https://github.com/matikamata/axis-niddhi/issues/new/choose`
- `https://niddhi.netlify.app/`

## 5. Important docs created or updated

- `docs/BEE_FIRST_TASK.md`
- `docs/DEPLOYMENT_SURFACES.md`
- `docs/NETLIFY_REFRESH_PLAN_20260518.md`
- `docs/PR_DISCIPLINE.md`
- `docs/TRANSLATION_REVIEW_GUIDE.md`
- `docs/sops/PRODUCTION_TO_PUBLISHED_NETLIFY_REFRESH_SOP_20260518.md`
- `docs/checkpoints/AXIS_NIDDHI_POST_309_PTBR_PUBLICATION_HANDOFF_2026-05-12.md`
- `.github/ISSUE_TEMPLATE/*`

## 6. Checkpoints/tags

- `checkpoint/vitrine-dev-abelhas-20260517`
- `checkpoint/bee-gateway-published-20260517`
- `checkpoint/bee-issue-templates-20260517`
- `checkpoint/bee-contributor-gateway-polished-20260517`
- `checkpoint/bee-onboarding-flow-complete-20260517`
- `checkpoint/contributor-gateway-grand-finale-20260518`
- `checkpoint/netlify-refresh-plan-20260518`
- `checkpoint/static-payload-gitignore-hygiene-20260518`
- `checkpoint/cloudflare-routing-note-20260518`
- `checkpoint/bee-first-task-issue-flow-20260518`
- `checkpoint/pr-discipline-guide-20260518`
- `checkpoint/netlify-refresh-sop-20260518`

## 7. What was intentionally not done

- No Netlify refresh was approved.
- `axis-niddhi-published` was not touched.
- No full pipeline rebuild was performed as part of this closing summary.
- No CSL or corpus identity change was made.
- No NANA, Navigator, or Cosmos feature work was done.
- No translation batch was started.

## 8. Known guardrails going forward

- Use branch and PR by default.
- Treat Cloudflare as the staging/review surface.
- Treat Netlify as the official public surface.
- Do not blindly sync production to published.
- Use issue templates for Bee reports.
- Keep Portuguese translations marked as study/review support, not official, final, or certified.
- PureDhamma.net remains the primary source.

## 9. Recommended next steps

1. Pause UI changes.
2. Use the Bee flow with first collaborators.
3. Collect small issues.
4. Do not refresh Netlify until the `NETLIFY_REFRESH_PLAN_20260518.md` checklist is approved.
5. Return to Dhamma translation/review work when ready.

## 10. Closing note

The reform cycle is complete enough to stop. The next useful work is not more decoration, but careful review, small reports, and preservation of meaning.
