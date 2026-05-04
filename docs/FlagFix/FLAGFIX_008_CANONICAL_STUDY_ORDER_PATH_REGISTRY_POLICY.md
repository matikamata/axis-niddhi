# FlagFix 008 — Canonical Study Order and Path Registry Policy

## Status

Planning / review policy only.

No renderer, CSL, HTML, CSS, JavaScript, navigation, metadata, pipeline, deployment, graph, study-order, path registry, or static-site output changes are authorized by this document.

## Purpose

Define guardrails for any future canonical study order, pathway registry, curriculum map, or guided navigation layer in AXIS-NIDDHI.

This policy exists before implementation so that future study-order work does not silently alter canonical identity, page routes, source evidence, or doctrinal sequence.

## Problem

AXIS-NIDDHI currently preserves and publishes a corpus of Dhamma essays as stable static artifacts.

Future UX layers may want to introduce:

- canonical reading order;
- beginner/intermediate/advanced paths;
- topic-based study paths;
- prerequisite chains;
- pathway navigation;
- related-page registries;
- graph-based knowledge navigation;
- AXIS-Navigator integration;
- AXIS-Ñāṇa retrieval context;
- AXIS-COSMOS order graph experiments.

These layers are useful, but risky if they become confused with canonical source structure.

## Core Principle

Study order is an interpretive layer, not canonical source truth.

A path registry may guide study, but must not overwrite:

- PD#PN identity;
- source title;
- source URL;
- canonical CSL content;
- publication route;
- archive order;
- source-bound metadata;
- human review boundaries.

## Layer Separation

Future study-order work must distinguish clearly between:

1. Canonical Source Layer
   - PureDhamma.net source content;
   - PD#PN identity;
   - CSL content;
   - source metadata.

2. Publication Layer
   - generated static pages;
   - archive pages;
   - language variants;
   - stable routes.

3. Study Guidance Layer
   - suggested order;
   - topic grouping;
   - learning paths;
   - related pages;
   - UX navigation aids.

4. Experimental Graph Layer
   - concept graph;
   - dependency graph;
   - semantic clusters;
   - AXIS-COSMOS order graph;
   - AI-assisted recommendations.

Only the first two layers are publication-critical. Study and graph layers must remain additive and reversible.

## Registry Requirements

Any future path registry must be:

- explicit;
- versioned;
- reviewable;
- source-bound;
- reversible;
- non-destructive;
- separate from CSL canonical content;
- safe to disable without breaking the site.

## Forbidden Actions

This policy does not authorize:

1. changing page routes;
2. renumbering PD#PN identifiers;
3. rewriting titles;
4. modifying CSL content;
5. changing archive sort order as canonical truth;
6. inserting automatic recommendations into canonical content;
7. treating AI-generated paths as authoritative;
8. deploying graph navigation without human review;
9. changing renderer behavior;
10. changing static-site output.

## Allowed Future Planning Work

Future planning documents may define:

- registry schema proposals;
- review matrix format;
- path naming conventions;
- beginner/intermediate/advanced labels;
- dependency notation;
- topic cluster rules;
- relationship types;
- AXIS-Navigator integration boundaries;
- AXIS-COSMOS discussion boundaries.

## Human Review Gate

Before implementation, any study-order registry must answer:

1. Is this order sourced, inferred, or editorial?
2. Who approved the ordering?
3. Is the path optional or canonical?
4. Does it preserve PD#PN identity?
5. Does it preserve source URL traceability?
6. Can it be disabled without changing content?
7. Does it affect search, archive, or related-page UI?
8. Does it introduce doctrinal interpretation?

## Acceptance Criteria

This FlagFix is complete when:

- the policy exists;
- canonical vs study guidance boundaries are documented;
- registry guardrails are documented;
- implementation remains blocked;
- no renderer, CSL, HTML, CSS, JavaScript, navigation, metadata, pipeline, deployment, graph, study-order, path registry, or static-site output is changed.
