# FlagFix 023 — Production Build Input Contract

## Status

Planning-only / architecture guardrail.

## Context

During FlagFix 022, the production repository successfully published static artifacts through Cloudflare Pages, but a local attempt to run:

```bash
python3 pipeline/13-ssg/build.py
````

aborted because the production clone does not contain:

```text
pipeline/09-csl
```

The build script correctly reported:

```text
SOVEREIGN ABORT: CSL not found
```

This revealed an architectural ambiguity:

* `axis-niddhi-production` currently behaves as a static publication repository.
* `pipeline/13-static-site/` is committed and deployed by Cloudflare Pages.
* Cloudflare has no build command and simply publishes the existing static output.
* Full deterministic rebuilds require a Canonical Source Library (`09-csl`) that is not present in this production clone.

## Problem

Future agents may incorrectly assume that `axis-niddhi-production` is a full rebuild workspace.

That could cause unsafe behavior, such as:

* copying an arbitrary `09-csl` from another workspace;
* rebuilding `13-static-site` from stale or mismatched canonical input;
* mixing lab/review artifacts into production;
* treating generated static files as if they were source truth;
* silently changing hundreds or thousands of pages.

## Current Safe Interpretation

For now:

```text
axis-niddhi-production = publication repository
```

It contains deployable static artifacts and selected SSG code, but it should not be treated as a complete canonical rebuild workspace unless an approved `09-csl` source is explicitly provided.

## Required Guardrail

Before any future rebuild from `pipeline/13-ssg/build.py`, the operator or agent must answer:

1. Which `09-csl` is the canonical input?
2. Is it sealed, current, and approved for production?
3. Was it copied intentionally into this workspace?
4. Does the resulting diff match the intended FlagFix scope?
5. Are generated page changes expected, reviewed, and minimal?

If any answer is unclear, the rebuild must not proceed.

## Proposed Future Solutions

### Option A — Publication-only production repo

Keep `axis-niddhi-production` as a static deploy repository.

* `13-static-site/` remains the deploy artifact.
* Rebuilds happen elsewhere.
* Production receives only reviewed, explicit static diffs.

This is safest for Cloudflare deployment.

### Option B — Full rebuild production repo

Add a controlled mechanism for bringing in `09-csl`.

Requirements:

* explicit source path;
* checksum/manifest validation;
* no silent fallback;
* no automatic copy from random local paths;
* rebuild report before commit.

### Option C — Split repos by role

Maintain separate repositories or worktrees:

* canonical build lab;
* print review lab;
* production deploy repo;
* navigator/nana labs.

Production receives only reviewed output.

## Recommended Policy

Until a formal rebuild contract is implemented:

```text
Do not run full production rebuilds inside axis-niddhi-production unless 09-csl provenance is explicit and approved.
```

For small FlagFix patches, prefer surgical edits to:

```text
pipeline/13-ssg/
pipeline/13-static-site/
docs/
```

with clear validation and minimal diff.

## Related Incidents

* FlagFix 022: media shortcode preservation layer.
* Attempted local SSG rebuild aborted because `pipeline/09-csl` was absent.
* Static deploy still succeeded because Cloudflare publishes committed `13-static-site` artifacts.

## Human Review Notes

This issue is architectural, not urgent.

It does not block current publication, but it must be documented before future automation or agent-driven rebuilds.
