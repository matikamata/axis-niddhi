# AXIS NANA Source-Bound Prompt Builder Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files created

- `scripts/nana/build_source_bound_prompt.py`
- `scripts/nana/validate_prompt_package.py`
- `docs/AXIS_NANA_SOURCE_BOUND_PROMPT_BUILDER.md`
- `outputs/nana/prompts/.gitkeep`
- `outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json`
- `outputs/nana/prompts/prompt-anicca-bootstrap-v1.json`
- `outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json`

## Files modified

- `scripts/nana/README.md`

## Prompt packages generated

- `outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json`
  - concept: `dukkha`
  - question: `What causes suffering?`
  - context pack: `context-pack-dukkha-bootstrap-v1`
- `outputs/nana/prompts/prompt-anicca-bootstrap-v1.json`
  - concept: `anicca`
  - question: `What does anicca mean in this corpus?`
  - context pack: `context-pack-anicca-bootstrap-v1`
- `outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json`
  - concept: `nibbana`
  - question: `How should Nibbana be understood from this context?`
  - context pack: `context-pack-nibbana-bootstrap-v1`

All prompt packages are deterministic derivative artifacts with:

- `package_type: source_bound_prompt`
- cited `canonical_refs`
- `llm_call_status: not_called`
- `validation_status: pending`

## Validation commands and results

Commands executed:

```bash
python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --question "What causes suffering?" --dry-run

python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --question "What causes suffering?" --output outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json

python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-anicca-bootstrap-v1.json --question "What does anicca mean in this corpus?" --output outputs/nana/prompts/prompt-anicca-bootstrap-v1.json

python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-nibbana-bootstrap-v1.json --question "How should Nibbana be understood from this context?" --output outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json

python3 scripts/nana/validate_prompt_package.py outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json outputs/nana/prompts/prompt-anicca-bootstrap-v1.json outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json

node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `dukkha` dry-run prompt build: passed
- explicit prompt package generation for all 3 outputs: passed
- prompt package validation: all 3 outputs passed
- `navigator.js` syntax check: passed
- `navigator-store.js` syntax check: passed

## Safety guarantees

- local-only implementation
- no API calls
- no LLM calls
- no embeddings
- no backend
- no deploy changes
- no `build.py` changes
- no Navigator UI changes
- no CSL or canonical layer mutation
- no source ZIP changes
- no `03-translations/` changes
- no SG/SP/SA/SD pipeline changes
- prompt packages are derivative and disposable
- prompt packages are source-bound by explicit constraints

## What remains intentionally unimplemented

- no actual model invocation
- no answer generation
- no semantic retrieval
- no embeddings
- no graph engine
- no ranking or reasoning engine
- no backend service
- no cloud sync
- no ingestion into publication pipeline

## Relationship to AXIS NANA Retrieval Skeleton and Cognitive Layer Bootstrap

These three layers are adjacent, but they do different jobs.

- AXIS Cognitive Layer Bootstrap creates derivative study artifacts:
  - lesson
  - quiz
  - audio script
- AXIS NANA Retrieval Skeleton creates non-interpreted context packs:
  - concept id
  - canonical refs
  - related concepts
  - zero interpretation
- AXIS NANA Source-Bound Prompt Builder creates prompt packages for a future LLM:
  - question
  - bound context pack
  - canonical refs
  - source-only constraints
  - no model call

Practical sequence:

- Cognitive Layer Bootstrap = derivative learning outputs
- Retrieval Skeleton = canonical context packaging
- Source-Bound Prompt Builder = safe prompt packaging for future answer layers

This means the prompt builder sits downstream of retrieval and upstream of any future answer engine.

## Rollback instructions

Remove only the prompt-builder artifacts created for this layer:

```bash
rm -f AXIS_NANA_SOURCE_BOUND_PROMPT_BUILDER_CHECKPOINT.md
rm -f docs/AXIS_NANA_SOURCE_BOUND_PROMPT_BUILDER.md
rm -f outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json
rm -f outputs/nana/prompts/prompt-anicca-bootstrap-v1.json
rm -f outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json
rm -f outputs/nana/prompts/.gitkeep
rm -f scripts/nana/build_source_bound_prompt.py
rm -f scripts/nana/validate_prompt_package.py
```

If you also want to revert the documentation update in `scripts/nana/README.md`, restore that file to its previous state separately.
