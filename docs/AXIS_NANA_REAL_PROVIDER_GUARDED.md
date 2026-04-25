# AXIS ÑĀṆA Real Provider Guarded Mode

## Purpose

This document describes the first guarded real-provider path for AXIS ÑĀṆA.

The goal is not to make Canon dependent on an LLM.
The goal is to add an explicit, reversible, opt-in execution path for derivative answers.

## Activation model

The real provider is disabled by default.

It will only run when all of the following are true:

- `--provider openai`
- `--enable-real-llm true`
- `OPENAI_API_KEY` exists in the environment
- the execution artifact has `decision == READY`

If any condition fails, the adapter returns a blocked result and does not call the API.

## Safety model

The provider is gated by the existing ÑĀṆA chain:

```text
Concept Registry
-> Context Pack
-> Source-Bound Prompt
-> Context Gate
-> Safe Execution Wrapper
-> Provider Adapter
```

This means:

- Canon is retrieved before prompting
- prompts remain source-bound
- weak context should be stopped before provider execution
- provider output is derivative only

## Prompt discipline

The guarded provider must use the existing source-bound prompt package only.

Allowed:

- exact `system_instruction` from the prompt package
- exact `user_prompt` from the prompt package

Not allowed:

- extra context injection
- hidden augmentation
- replacing the source-bound prompt with a new one

## Hallucination containment

This provider reduces hallucination risk by construction, but does not eliminate it by authority.

Safety boundaries:

- gate must allow execution first
- prompt must remain source-bound
- answer is stored as derivative
- answer is marked non-canonical
- answer quality remains `UNVERIFIED` until downstream validation exists

## Non-canonical status

Even when a real provider call succeeds:

- the answer is not Canon
- the answer is not CSL
- the answer is not publication truth

It is a derivative artifact only.

## Storage expectations

Provider results should store:

- canonical refs
- raw answer text
- provider metadata
- derivative/non-canonical markers

This preserves traceability and keeps future validation possible.

## Operational note

If `OPENAI_API_KEY` is absent, guarded mode stays safely blocked.

If a real provider is later enabled in another environment, it must remain explicit opt-in and must not become the default path.
