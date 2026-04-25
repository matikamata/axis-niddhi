# AXIS NANA Insufficient Context Gate

## What this layer is

This layer is a deterministic safety filter that evaluates whether a context pack plus prompt package provide enough canonical support for a future answer step.

It does not reason semantically.
It does not infer doctrine.
It does not answer.

## Core role

The gate exists to stop weak context from reaching any future answer engine.

It produces one of three explicit states:

- `NO_CANONICAL_SUPPORT`
- `ANSWER_PARTIAL`
- `ANSWER_CONFIDENT`

## How it works

The gate uses only local deterministic inputs:

- canonical reference count
- related concept count
- question length factor

These are combined into a bounded heuristic `coverage_score`.

No NLP, embeddings, semantic search, or model reasoning are used.

## Why this matters

The gate hardens AXIS NANA before any future model invocation by making uncertainty explicit.

If context is weak, the system should block.
If context is partial, the system should flag partial support.
If context is strong enough, the system may mark the package as answer-ready without invoking a model.

## What this layer is not

This layer is not:

- an LLM
- an answer engine
- a semantic retrieval system
- a graph reasoner
- a replacement for Canon

## Relationship to adjacent layers

- Retrieval Skeleton builds non-interpreted canonical context packs
- Source-Bound Prompt Builder binds a question to that context
- Insufficient Context Gate evaluates whether that bound package is strong enough to proceed safely

This keeps AXIS NANA ordered as:

- retrieval
- prompt constraint
- safety gate
- only then any future answer layer
