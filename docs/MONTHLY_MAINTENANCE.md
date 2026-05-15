# Monthly Maintenance Routine

This checklist keeps AXIS-NIDDHI understandable and safe to operate.

Default rule: inspect first, preserve evidence, then decide. Do not build,
deploy, sync, clean, reset, or delete as part of routine maintenance unless a
human explicitly approves that action.

## 1. Workspace Check

Record:

- current branch;
- `git status -sb`;
- untracked files;
- modified generated output;
- which workspace is being inspected.

Current roles:

- `axis-niddhi-production`: canonical GitHub-connected staging/production source
  used for Cloudflare preview/testing.
- `axis-niddhi-published`: official Netlify drag-and-drop deploy payload.

Do not sync between them without a separate plan.

## 2. Public Entry Check

Verify the intended entry points:

- official Netlify vitrine: `https://niddhi.netlify.app/`
- Cloudflare preview/test surface: `https://niddhi.pages.dev/welcome.html`

Check that a new visitor can answer:

- What is this?
- What can I read?
- What is reviewed or still evolving?
- How do I report a translation issue?

## 3. Documentation Check

Review these files:

- `README.md`
- `docs/START_HERE.md`
- `docs/TRANSLATION_REVIEW_GUIDE.md`
- `docs/VISION.md`
- recent handoff notes

Keep public-facing docs short. Move operational details into handoffs or
maintenance notes.

## 4. Translation Review Check

Look for:

- unresolved `MEANING-RISK` or `PALI-RISK` notes;
- title review issues;
- glossary drift;
- accidental claims that machine output is final.

Do not edit translation data during monthly maintenance unless that is the
approved task.

## 5. Deploy Payload Check

Before touching the Netlify payload:

1. preserve current local state;
2. compare intended source and target;
3. identify generated files that would change;
4. write a minimal sync plan;
5. get visual approval from the Cloudflare candidate first.

## 6. What Not to Do by Default

- no full pipeline run;
- no CSL edits;
- no translation data edits;
- no dependency changes;
- no reset, pull, push, or commit;
- no cleanup of untracked files;
- no Netlify payload sync.

## Monthly Output

At the end, write a short note with:

- date;
- inspected workspace;
- public entry status;
- high-risk local changes;
- decisions needed;
- actions explicitly deferred.
