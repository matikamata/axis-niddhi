# AXIS NANA Source-Bound Prompt Builder

## What this layer does

This layer consumes a `canonical_context_pack` and produces a deterministic prompt package for a future LLM call.

Its purpose is narrow:

- bind a user question to a cited context pack
- carry forward canonical references
- embed strict source-bound instructions
- stop before any model call

## What this layer does not do

This layer does not:

- call an LLM
- generate an answer
- add external knowledge
- perform retrieval beyond the input context pack
- change Canon

## Why it is source-bound

The prompt package exists to reduce hallucination risk before any future answer step.

It constrains the future model to:

- use only the supplied canonical context
- cite every claim with canonical refs
- avoid outside interpretation
- include a dedicated final `Sources:` section
- list only provided canonical refs under `Sources:`
- say the context is insufficient when needed

## Why it is local-only

Local-only prompt construction keeps this stage auditable, deterministic, and disposable.

It also preserves the AXIS principle that Canon remains the authority and derivative artifacts remain downstream helpers.

## Relationship to the retrieval skeleton

The retrieval skeleton stops at non-interpreted context packs.

The source-bound prompt builder is the next derivative layer:

- Retrieval Skeleton = canonical context packaging
- Prompt Builder = safe prompt packaging for a future LLM

## Future safe use

If a future answer layer is added, it should consume these prompt packages exactly as constrained:

- no external knowledge
- explicit citation per claim
- dedicated final `Sources:` section required
- inline citations alone are not sufficient
- no speculation
- explicit insufficiency when context does not support an answer
