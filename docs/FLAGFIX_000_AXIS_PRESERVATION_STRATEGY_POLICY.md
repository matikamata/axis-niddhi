# FlagFix 000 — AXIS Preservation Strategy Policy

## Status

Planning / review policy only.

No renderer, CSL, HTML, CSS, JavaScript, navigation, metadata, pipeline, deployment, archive, or static-site output changes are authorized by this document.

## Purpose

Define the preservation strategy guardrails for AXIS-NIDDHI before any future architecture or implementation work changes canonical content, publication flow, study order, or deployment behavior.

## Core Principle

AXIS-NIDDHI is a deterministic preservation and publishing framework.

It must preserve source traceability, canonical identity, reproducible static output, and human-review boundaries before adding new automation or intelligence layers.

## Preservation Priorities

AXIS-NIDDHI preservation work must prioritize:

1. source traceability;
2. canonical identity stability;
3. reproducible builds;
4. reviewable artifacts;
5. separation between source, transformation, review, and publication;
6. minimal and reversible changes;
7. no silent correction of doctrinal content;
8. no automatic publication behavior from experimental branches.

## Canonical Identity

The following must remain stable unless explicitly reviewed and approved:

- PD#PN identifiers;
- CSL identity metadata;
- source URL references;
- original title references;
- route identity;
- language identity;
- review status;
- release manifests.

## Source Integrity

Source material must not be silently rewritten.

Allowed preservation actions:

- document source provenance;
- record review decisions;
- compare source and output;
- identify divergence;
- create audit artifacts;
- propose future implementation issues.

Forbidden preservation actions:

- automatic doctrinal correction;
- unreviewed title normalization;
- unreviewed metadata invention;
- route rewriting without approval;
- source URL shortening where traceability matters;
- destructive cleanup of canonical artifacts;
- mixing lab experiments into production publication.

## Determinism Guardrail

Any future preservation implementation must be compatible with deterministic review.

Future implementation should avoid:

- uncontrolled timestamps;
- nondeterministic ordering;
- hidden network dependencies;
- machine-specific absolute paths;
- untracked generated outputs;
- implicit deployment side effects.

## Architecture Boundary

This policy does not authorize implementation.

It only defines the preservation strategy boundary for later work involving:

- AXIS-NIDDHI;
- AXIS-Navigator;
- AXIS-ÑĀṆA;
- AXIS-COSMOS;
- future multilingual preservation layers;
- future static/offline review packages.

## Acceptance Criteria

This FlagFix is complete when:

- preservation strategy guardrails are documented;
- no production output is changed;
- no pipeline behavior is changed;
- no deployment behavior is changed;
- future implementation remains blocked pending separate approved issues.
