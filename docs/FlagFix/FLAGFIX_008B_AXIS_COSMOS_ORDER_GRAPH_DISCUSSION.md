# FlagFix 008b — AXIS COSMOS Order Graph Discussion

## Status

Planning / architecture discussion only.

No renderer, CSL, HTML, CSS, JavaScript, navigation, metadata, pipeline, deployment, graph, study-order, path registry, AI, retrieval, or static-site output changes are authorized by this document.

## Purpose

Record the AXIS COSMOS order graph discussion before any graph, study-order, pathway, retrieval, or intelligence layer is implemented.

This document is a conceptual architecture checkpoint, not an implementation plan.

## Core Idea

AXIS COSMOS is a future architecture layer for representing the PureDhamma/AXIS-NIDDHI corpus as an ordered knowledge graph.

It may eventually support:

- concept relationships;
- prerequisite chains;
- canonical study sequences;
- topic constellations;
- pathway recommendations;
- review navigation;
- retrieval context packs;
- future AXIS ÑĀṆA / Navigator integration.

## Guardrail

AXIS COSMOS must not replace the canonical corpus.

It may only describe relationships between already preserved source-bound artifacts.

The canonical unit remains the preserved AXIS/CSL post identity.

## Non-Goals

This discussion does not authorize:

- changing page routes;
- changing titles;
- changing CSL metadata;
- changing rendered HTML;
- changing Navigator behavior;
- creating graph JSON artifacts;
- creating AI/retrieval outputs;
- publishing any new study-order UI;
- changing deployment behavior.

## Relationship to AXIS-NIDDHI

AXIS-NIDDHI remains the deterministic preservation and publication engine.

AXIS COSMOS, if implemented later, must be additive and reversible.

It should consume stable artifacts rather than mutate canonical content.

## Relationship to AXIS-Navigator

AXIS-Navigator may eventually display study paths, related pages, or graph-derived navigation.

However, any Navigator integration must remain progressive enhancement only.

The static corpus must remain readable without JavaScript, graph data, localStorage, AI calls, or external services.

## Relationship to AXIS ÑĀṆA

AXIS ÑĀṆA may eventually use graph relationships to build source-bound context packs.

However, graph-derived retrieval must remain evidence-bound.

No generated explanation may override, rewrite, or silently reinterpret source text.

## Future Review Questions

Before implementation, human review must answer:

1. What is the minimum safe graph schema?
2. Which relationships are source-evident versus editorial?
3. How should uncertainty be represented?
4. How should conflicting or multi-path study sequences be handled?
5. What artifacts are canonical, review-only, or experimental?
6. How can graph output be tested without changing published pages?
7. How can the graph remain useful offline?
8. How can AXIS COSMOS avoid becoming an opaque recommendation engine?

## Possible Relationship Types

Future discussion may consider relationship types such as:

- prerequisite;
- explains;
- expands;
- contrasts;
- depends-on;
- related-concept;
- pathway-next;
- pathway-previous;
- glossary-term;
- quote-source;
- translation-risk;
- needs-human-review.

These are discussion candidates only.

They are not approved schema fields.

## Required Future Gates

Before any implementation, create separate approved issues for:

1. graph schema proposal;
2. source-bound relationship taxonomy;
3. review matrix for initial graph edges;
4. offline static graph artifact policy;
5. Navigator integration policy;
6. ÑĀṆA retrieval integration policy.

## Acceptance Criteria

This discussion is complete when:

- AXIS COSMOS is defined as an additive, reversible architecture layer;
- canonical corpus boundaries are preserved;
- relationship between COSMOS, NIDDHI, Navigator, and ÑĀṆA is documented;
- future implementation gates are listed;
- no renderer, CSL, HTML, CSS, JavaScript, navigation, metadata, pipeline, deployment, graph, study-order, path registry, AI, retrieval, or static-site output is changed.
