# Main Branch Protection Guardrail

## Purpose

This document defines the safety policy for protecting the `main` branch of `matikamata/axis-niddhi`.

The repository currently functions as the production static publication repository for AXIS-NIDDHI. Cloudflare Pages deploys from `main`, so any direct change to `main` can affect the public site.

## Current Production Model

- `main` is the publication branch.
- Cloudflare Pages deploys automatically from `main`.
- No Cloudflare build command is configured.
- The deployed site is based on committed static artifacts.
- The production clone does not currently contain approved full `09-csl` rebuild provenance.

## Required Policy

### 1. No direct pushes to `main`

All work should go through branches and pull requests.

Allowed branch patterns:

- `docs-*`
- `flagfix-*`
- `fix-*`
- `feat-*`
- `checkpoint-*`

### 2. Require pull request review before merge

At least one deliberate human review step should happen before merging.

For solo-maintainer operation, this may be a self-review checklist comment until collaborators are added.

### 3. Require status checks when available

Cloudflare Pages preview/deploy checks should be allowed to complete before merge when GitHub exposes them as checks.

### 4. Do not require linear history yet

Merge commits are currently useful for preserving FlagFix/PR history.

Recommended setting:

- Allow merge commits.
- Do not force squash-only yet.

### 5. Do not enable overly strict protection until workflow is stable

Do not enable settings that could lock the maintainer out or block urgent static publication fixes.

Avoid initially:

- requiring signed commits;
- requiring deployments before merge;
- requiring multiple reviewers;
- restricting who can push if emergency recovery is not tested.

## Initial GitHub Settings Recommendation

Recommended first protection layer for `main`:

- Require a pull request before merging: ON
- Require approvals: 1
- Dismiss stale approvals: OFF initially
- Require review from Code Owners: OFF initially
- Require status checks: ON only if stable checks are visible
- Require branches to be up to date: OFF initially
- Require conversation resolution: ON
- Require signed commits: OFF initially
- Require linear history: OFF
- Include administrators: OFF initially, then reconsider after testing
- Restrict who can push: OFF initially
- Allow force pushes: OFF
- Allow deletions: OFF

## Emergency Recovery Principle

If branch protection blocks urgent recovery, the maintainer may temporarily adjust protection rules, but every such event should be documented in a follow-up checkpoint.

## AXIS-NIDDHI Specific Rule

Never run or merge full production rebuild output unless the production build input contract is satisfied:

- approved `09-csl` provenance exists;
- build inputs are documented;
- output diffs are expected;
- Cloudflare deployment impact is intentional.

See:

- `docs/FLAGFIX_023_PRODUCTION_BUILD_INPUT_CONTRACT.md`
- `docs/FLAGFIX_STATUS_CHECKPOINT_2026-05-02.md`
