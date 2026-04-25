# AXIS ÑĀṆA Answer Validator

## Purpose

The Answer Validator is a local-only structural validation step for provider outputs.

It does not call any model.
It does not interpret doctrine.
It decides whether a provider answer is eligible to be displayed as a derivative, non-canonical artifact.

## Core rule

A provider answer is never trusted by default.

Display eligibility must be earned through validation.

## Inputs

The validator consumes:

- one provider run
- one source-bound prompt package
- one gate result

These artifacts define:

- what the provider claimed
- which canonical refs were allowed
- whether answering was allowed at all

## Decision model

### No real provider call

If `llm_called == false`:

- `answer_validation_status = NOT_APPLICABLE_NO_LLM_CALL`
- `display_allowed = false`

### Gate blocked

If the gate says `allowed_to_answer == false`:

- `answer_validation_status = REJECTED_GATE_BLOCKED`
- `display_allowed = false`

### Real answer validation

If `llm_called == true`, the validator checks:

- raw answer exists
- answer contains `Sources:`
- at least one approved canonical ref appears
- no unknown canonical-looking refs appear
- answer does not claim canonical authority
- provider output is marked derivative / non-canonical
- answer quality remains `UNVERIFIED`

## Unknown ref policy

Refs matching the pattern below are treated as canonical-looking refs:

```text
[A-Z]{2}\.[A-Z]{2}\.[0-9]{3}
```

If a ref appears in the answer but is not in the prompt package allowed refs, the answer is rejected.

## Output role

The validator produces an `answer_validation` artifact.

That artifact is still local and derivative.
It is not Canon.
It is not CSL.
It is a safety checkpoint before any UI display of a real answer.

## Relationship in the chain

The effective chain becomes:

```text
Gate -> Provider -> Answer Validator
```

Meaning:

- Gate decides whether answering may proceed
- Provider generates or simulates output
- Answer Validator decides whether display is allowed

## Safety posture

- local only
- no API calls
- no LLM calls
- no canonical mutation
- no publication-side mutation
- no trust by default
