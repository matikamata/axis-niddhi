# AXIS NANA Retrieval Skeleton

## What this layer is

AXIS NANA Retrieval is a deterministic local lookup layer that maps a concept id to a small pack of canonical references and registry metadata.

Its job in this bootstrap phase is narrow:

- load a local registry
- retrieve cited canonical references
- emit a context pack
- stop before interpretation

## What this layer is not

This layer is not:

- an AI answer engine
- semantic search
- an embeddings system
- a graph engine
- a backend service
- a replacement for Canon

## Why it is local-only

Local-only retrieval preserves the core AXIS rule:

Canon first, retrieval second, interpretation later.

By staying local and deterministic, this layer can be audited, reproduced, and discarded without introducing cloud dependencies or hallucination surface area.

## Why it does not answer yet

Answering is intentionally deferred.

The bootstrap retrieval layer must only collect cited canonical context. If a future answer layer exists, it should consume context packs that are already constrained by canonical references and explicit safety flags.

## How it differs from the Cognitive Layer Bootstrap

The Cognitive Layer Bootstrap creates derivative study artifacts such as lessons, quizzes, and audio-script seeds.

The NANA Retrieval Skeleton does something earlier and narrower:

- concept lookup
- canonical reference packaging
- zero interpretation

In short:

- Cognitive Bootstrap = derivative learning artifacts
- NANA Retrieval Skeleton = source-bound context packaging

## Future safe use with LLM prompts

Future prompt layers may consume these context packs safely if they preserve the following discipline:

- use only the supplied context pack
- cite canonical refs for every claim
- refuse unsupported interpretation
- surface uncertainty explicitly
- keep Canon as authority

Until that later layer exists, the retrieval pack should remain non-interpreted and local-only.
