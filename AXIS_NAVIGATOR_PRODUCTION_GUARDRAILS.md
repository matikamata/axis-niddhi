# AXIS-NAVIGATOR / AXIS-NIDDHI — Production Guardrails for AI Agents

**Status:** Active Operating Policy  
**Audience:** Codex, Gemini, Claude, VSCode agents, local operators  
**Purpose:** Prevent any assistant, script, or human from breaking what is already working in production.

---

## 1. Current reality to preserve

The following is considered **live and stable**:

- GitHub account: `matikamata`
- Production repository: `matikamata/axis-niddhi`
- Public production site: `https://niddhi.pages.dev`

This stack is already functioning.

**Prime directive:**

> Do not break production in order to accelerate development.

Any new module — including **AXIS-NAVIGATOR** — must be developed in a way that is **isolated, reversible, and non-destructive**.

---

## 2. Golden rule

### Production is read-mostly

The repository and deployment that are already working must be treated as:

- stable
- protected
- minimally touched
- changed only with explicit intention

No assistant should assume that “cleaning up,” “modernizing,” “refactoring,” or “reorganizing” production is helpful.

If the system is working, the burden of proof is on the proposed change.

---

## 3. Repository roles

### A. `axis-niddhi` = production canon / stable delivery

This repo is the **working production engine/site layer**.

Rules:
- do not perform broad refactors there
- do not rename folders casually
- do not move core files just for aesthetics
- do not upgrade toolchains unless explicitly requested
- do not change deployment assumptions unless explicitly requested
- do not “simplify” by deleting files that seem unused

### B. `axis-navigator` = experimental module / safe development zone

This repo should be treated as:
- sandbox
- prototype layer
- isolated development zone
- safe place for iteration

Navigator should mature **outside production first**.

Only after validation should anything be proposed for controlled integration into the production surface.

---

## 4. Mandatory branching policy

No AI agent should work directly on the production branch.

### Required policy

- never commit directly to `main` in production repos
- never push directly to production without explicit user approval
- always work in a feature branch

### Branch naming recommendation

- `feat/axis-navigator-v1`
- `feat/navigator-overlay`
- `fix/print-css-safe`
- `chore/nonprod-audit-notes`

### Forbidden behavior

- direct edits on `main`
- force-push on production branch
- rebase/rewrite of production history
- mass formatting commits touching unrelated files

---

## 5. Deployment safety rules

The live site at `niddhi.pages.dev` must be treated as a fragile success state.

### Therefore:

No assistant may:
- alter deployment config casually
- change build output paths without explicit instruction
- change Cloudflare Pages settings assumptions blindly
- change GitHub Pages assumptions blindly
- replace the current deployment model with a new one “for convenience”

### Before any deployment-related change

The agent must explicitly answer:
1. What exact file controls the deployment?
2. Is this production or a preview path?
3. Is the change reversible in one commit?
4. Can the same result be tested outside production first?

If the answer is not clear, the change must not be made.

---

## 6. Safe integration strategy for AXIS-NAVIGATOR

Navigator must be integrated using **progressive enhancement**.

### Required integration model

- keep the current site fully readable without Navigator
- Navigator must be additive, not structural
- if Navigator JS fails, the page must still work normally
- no dependency on backend
- no dependency on external APIs for core reading UX
- no rewrite into SPA

### Practical meaning

Allowed:
- add a small JS overlay
- add a small CSS file
- inject a button/panel shell into templates
- read from existing JSON artifacts like `search_index.json` and `index.json`
- persist personal state in `localStorage`

Not allowed:
- rewrite site architecture
- replace rendering pipeline just to support Navigator
- modify canonical content files for UI convenience
- create hard dependency on dynamic runtime services

---

## 7. File-touch discipline

When working near production, assistants must minimize blast radius.

### Rule

Touch the fewest files possible.

### Preferred order

1. add new files
2. inject minimal template hooks
3. add minimal CSS
4. add minimal JS
5. only then consider modifying shared logic

### Avoid

- sweeping rename operations
- broad “cleanup” diffs
- unrelated lint/format churn
- changing multiple subsystems in one patch

---

## 8. Change classification

Every proposed change must be labeled by the agent as one of these:

### Class A — Safe additive
Examples:
- add `navigator.js`
- add `navigator.css`
- add localStorage helpers
- add hidden feature flag

Usually acceptable in a feature branch.

### Class B — Controlled integration
Examples:
- modify base template to load Navigator assets
- update build to copy new static assets
- expose existing JSON to front-end

Allowed only with narrow scope and explicit review.

### Class C — Production-risk change
Examples:
- deployment config changes
- route changes
- path/layout changes
- template refactors affecting all pages
- build pipeline changes

These require explicit user approval before implementation.

---

## 9. Mandatory pre-change checklist for AI agents

Before changing anything that may affect production, the agent must verify:

- which repo is being changed
- which branch is being changed
- whether the target is production or experimental
- whether the change is additive or destructive
- whether rollback is trivial
- whether the current behavior is already working

If current behavior is already working, default posture is:

> preserve first, improve second.

---

## 10. Mandatory output format for assistants

When Codex, Gemini, Claude, or any VSCode agent proposes a patch that touches production-adjacent files, it should report:

1. **Scope** — what exact files will be touched
2. **Risk level** — A / B / C
3. **Why this does not break production**
4. **Rollback plan** — exact revert path
5. **What remains untouched**

If the agent cannot explain those five points clearly, it should not proceed.

---

## 11. Forbidden assumptions

AI agents must not assume:

- that production should be “cleaned up” right now
- that newer tooling is automatically better
- that all duplicate-looking files are safe to delete
- that deployment infra can be inferred safely
- that repo reorganization is harmless
- that “I tested locally” means Cloudflare/GitHub Pages will behave identically

---

## 12. Recommended workflow

### Phase 1 — Build outside production
Develop AXIS-NAVIGATOR in its own safe branch/repo first.

### Phase 2 — Validate in preview/local
Test locally or in preview.

### Phase 3 — Integrate minimally
Port only the smallest proven pieces into production.

### Phase 4 — Deploy deliberately
Only after explicit approval.

---

## 13. Minimal integration doctrine

For AXIS-NAVIGATOR specifically, the correct doctrine is:

> Prototype wide, integrate narrow.

Meaning:
- explore freely in `axis-navigator`
- merge surgically into `axis-niddhi`
- keep production boring

That is the desired outcome.

---

## 14. One-sentence policy for assistants

> Never use the live AXIS-NIDDHI production stack as a playground.

---

## 15. Operator commandment

When in doubt:

- do not deploy
- do not refactor production
- do not touch `main`
- create a branch
- isolate the patch
- make rollback trivial

---

## 16. Copy-paste instruction block for VSCode agents

Use this block at the top of any future prompt:

```text
PRODUCTION GUARDRAIL MODE = ON

You are working in an ecosystem where the live production stack is already functioning.
Do not break production.
Do not refactor broadly.
Do not touch main.
Do not change deployment behavior unless explicitly asked.
Work only in a feature branch.
Prefer additive patches over structural rewrites.
If JS fails, the site must still read normally.
Navigator is progressive enhancement, not a rewrite.
Before proposing changes, state:
1) files touched
2) risk level
3) why production remains safe
4) rollback plan
5) what is intentionally left untouched
```

---

## 17. Final operational stance

The current system already proved something very important:

**it works.**

That is now an asset to defend.

AXIS-NAVIGATOR should evolve with discipline:
- experimental in the lab
- conservative in production
- reversible at every step

Any modification to pipeline/ MUST be:

- minimal
- reversible
- justified explicitly
- reviewed before merge to main

