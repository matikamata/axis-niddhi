# AXIS-NIDDHI — Cloudflare Docs-Only Deploy Policy

**Date:** 2026-05-04  
**Status:** Policy / Operational Guidance  
**Scope:** Docs-only deployment noise management  
**Implementation:** Not authorized by this document

---

## Purpose

This document defines how AXIS-NIDDHI handles Cloudflare Pages deployments triggered by documentation-only pull requests.

It exists because Cloudflare automatic deployments are currently enabled for `main`, and documentation-only PRs also trigger deployments.

The goal is to reduce operational confusion and avoid misreading documentation deploys as functional publication events.

---

## Current Decision

Docs-only Cloudflare deployments are currently accepted as expected behavior.

A docs-only PR may trigger a Cloudflare production deployment if all of the following are true:

- the PR changes only documentation or review-scaffold files;
- the PR explicitly declares `docs-only`;
- the PR explicitly declares `no functional changes`;
- the changed files are listed in the PR body;
- no renderer, CSL, HTML, CSS, JavaScript, pipeline, metadata, navigation, deployment config, Cloudflare config, or static-site output files are changed.

---

## Why No Cloudflare Config Change Yet

This policy does not change Cloudflare configuration.

Cloudflare ignore rules, build skip rules, or deployment filtering may be considered later, but only in a dedicated operational PR with explicit approval.

The current priority is clarity and traceability, not automation.

---

## Docs-Only PR Rules

Every docs-only PR should include:

```text
Scope:
- docs-only
- no functional changes
- Cloudflare deploy expected if merged
```

Every docs-only PR should include an expected changed-files list.

If the changed-files list contains anything outside the approved documentation scope, the PR must stop for review.

---

## Batch Guidance

Small documentation changes should be batched when practical.

Batching is recommended when:

- several related policy files are being created;
- multiple review-scaffold files belong to the same sprint;
- the work is internal planning and does not need immediate merge;
- reducing Cloudflare deployment noise is more important than incremental PR history.

Separate PRs remain acceptable when:

- the document is a checkpoint or handoff;
- the document closes a specific issue;
- the document needs independent review;
- delaying the document would increase operational confusion.

---

## Cloudflare Deploy Labeling

When a docs-only PR is expected to trigger Cloudflare, the PR body should state:

```text
Cloudflare:
- automatic production deploy may be triggered
- deploy is expected
- no functional/static-site change is intended
```

This prevents a successful Cloudflare deploy from being misread as evidence of a publication change.

---

## Guardrails

This document does not authorize changes to:

- Cloudflare configuration;
- GitHub Actions;
- deployment configuration;
- renderer behavior;
- CSL content;
- HTML output;
- CSS output;
- JavaScript output;
- pipeline behavior;
- metadata behavior;
- navigation behavior;
- generated static-site output.

This document does not authorize implementation of any FlagFix item.

This document does not authorize any functional change.

---

## PR Checklist for Docs-Only Changes

Before commit:

```bash
git diff --name-only
```

Expected result:

```text
docs/<approved-document>.md
```

Before merge, confirm:

- only approved docs/review files changed;
- PR body declares docs-only;
- PR body declares no functional changes;
- PR body states Cloudflare deploy may occur;
- no generated output changed;
- no deployment configuration changed.

---

## Next Review Gate

Any future change to Cloudflare deployment behavior requires a separate issue, branch, PR, and explicit approval.

Examples requiring a separate review gate:

- adding Cloudflare ignore rules;
- changing build commands;
- changing Pages project settings;
- adding GitHub Actions deployment filters;
- moving internal planning docs to a non-deploying repository;
- excluding docs paths from production builds.

Until such a review gate is approved, docs-only deploys remain expected operational noise, not a functional publication event.
