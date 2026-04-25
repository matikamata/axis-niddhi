# AXIS Cognitive Layer Bootstrap

## Purpose

This bootstrap introduces a safe derivative layer that points forward to:

- AXIS ÑĀṆA
- AXIS Academy
- PitiPath

It does so without mutating canon, without external services, and without changing the preservation pipeline.

## Core principle

Canon first, magic later.

Generated lesson, quiz, and audio-script artifacts are:

- derivative
- cited
- local
- disposable
- non-canonical

## Current bootstrap outputs

- one lesson sample for `dukkha`
- one quiz sample for `anicca`
- one audio script sample for `nibbana`

## Artifact contract

Every generated artifact includes:

```json
{
  "artifact_id": "...",
  "artifact_type": "...",
  "concept_id": "...",
  "source_csl_refs": [],
  "generated_from": "...",
  "input_context_hash": "...",
  "validation_status": "..."
}
```

## Validation policy

No generated artifact should pass validation if:

- JSON is invalid
- `artifact_id` is missing
- `concept_id` is missing
- `source_csl_refs` is empty
- `generated_from` is missing
- `input_context_hash` and `prompt_hash` are both missing
- `validation_status` is missing

## Explicit non-scope

- no backend
- no auth
- no cloud dependency
- no deployment integration
- no CSL edits
- no source ZIP edits
- no SG/SP/SA/SD pipeline edits
- no Navigator UI edits
- no semantic engine yet
- no AI orchestration beyond deterministic local samples

## Next safe step

The next layer can replace static sample generation with richer local orchestration while keeping the same artifact contract and validation rules.
