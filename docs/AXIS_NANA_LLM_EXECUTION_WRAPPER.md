# AXIS NANA LLM Execution Wrapper

## What this layer is

This layer simulates how AXIS NANA would prepare an LLM execution after prompt construction and gate evaluation.

It is a safe-mode wrapper only.

It does not call any model.
It does not generate any answer.
It only prepares or blocks execution.

## Core rule

Gate first. Execution second.

- if the gate blocks, execution is blocked
- if the gate allows, execution is marked ready
- in both cases, no LLM is called

## What it consumes

The wrapper takes:

- a source-bound prompt package
- a gate evaluation result

It validates compatibility between them before producing an execution artifact.

## What it produces

The wrapper emits a deterministic execution result that says:

- `BLOCKED` when the gate disallows answering
- `READY` when the gate allows answering

In the ready case it also assembles a `prepared_prompt`, but still does not execute it.

## Why this exists

This layer gives AXIS NANA a full pre-LLM control path:

- retrieval
- prompt construction
- context sufficiency gate
- execution wrapper
- only then any future model call

That keeps the system auditable and reduces hallucination risk before any external model is introduced.

## What this layer is not

This layer is not:

- an LLM client
- an answer generator
- a semantic reasoner
- a backend execution service

## Safe future use

If a future model connector is added, it should sit after this wrapper and only accept execution artifacts explicitly marked `READY`.
