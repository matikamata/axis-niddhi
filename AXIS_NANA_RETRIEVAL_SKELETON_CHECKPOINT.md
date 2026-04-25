# AXIS NANA Retrieval Skeleton Checkpoint

## Current branch

- `feat-axis-navigator-v1-1`

## Files created

- `metadata/nana/concept_registry.json`
- `scripts/nana/retrieve_concept.py`
- `scripts/nana/validate_context_pack.py`
- `scripts/nana/README.md`
- `docs/AXIS_NANA_RETRIEVAL_SKELETON.md`
- `outputs/nana/.gitkeep`
- `outputs/nana/context-pack-dukkha-bootstrap-v1.json`
- `outputs/nana/context-pack-anicca-bootstrap-v1.json`
- `outputs/nana/context-pack-nibbana-bootstrap-v1.json`

## Registry concepts available

- `dukkha`
  - refs: `DS.II.003`, `IS.BB.005`, `TL.KK.003`
  - related: `tanha`, `avijja`, `paticca_samuppada`
- `anicca`
  - refs: `KD.FF.005`, `KD.CC.006`, `KD.BB.004`
  - related: `dukkha`, `nibbana`, `paticca_samuppada`
- `nibbana`
  - refs: `BD.HH.007`, `KD.EE.004`, `TL.CC.006`
  - related: `anicca`, `tanha`, `avijja`
- `paticca_samuppada`
  - refs: `DS.FF.003`, `KD.BB.004`, `PS.II.004`
  - related: `avijja`, `tanha`, `dukkha`
- `tanha`
  - refs: `DS.FF.002`, `DS.FF.006`, `PS.II.009`
  - related: `dukkha`, `avijja`, `nibbana`
- `avijja`
  - refs: `KD.HH.006`, `KD.HH.005`, `DS.FF.007`
  - related: `paticca_samuppada`, `tanha`, `dukkha`

All entries are marked `bootstrap_seed` and explicitly non-exhaustive.

## Generated context packs

- `outputs/nana/context-pack-dukkha-bootstrap-v1.json`
  - pack type: `canonical_context_pack`
  - concept: `dukkha`
- `outputs/nana/context-pack-anicca-bootstrap-v1.json`
  - pack type: `canonical_context_pack`
  - concept: `anicca`
- `outputs/nana/context-pack-nibbana-bootstrap-v1.json`
  - pack type: `canonical_context_pack`
  - concept: `nibbana`

## Validation commands and results

Commands executed:

```bash
python3 scripts/nana/retrieve_concept.py --concept dukkha --dry-run
python3 scripts/nana/retrieve_concept.py --concept anicca --dry-run
python3 scripts/nana/retrieve_concept.py --concept nibbana --dry-run

python3 scripts/nana/retrieve_concept.py --concept dukkha --output outputs/nana/context-pack-dukkha-bootstrap-v1.json
python3 scripts/nana/retrieve_concept.py --concept anicca --output outputs/nana/context-pack-anicca-bootstrap-v1.json
python3 scripts/nana/retrieve_concept.py --concept nibbana --output outputs/nana/context-pack-nibbana-bootstrap-v1.json

python3 scripts/nana/validate_context_pack.py outputs/nana/context-pack-dukkha-bootstrap-v1.json outputs/nana/context-pack-anicca-bootstrap-v1.json outputs/nana/context-pack-nibbana-bootstrap-v1.json

node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

Results:

- `dukkha` dry-run: passed
- `anicca` dry-run: passed
- `nibbana` dry-run: passed
- explicit output generation for all 3 packs: passed
- context pack validation: all 3 outputs passed
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
- retrieval emits cited context only, not doctrinal answers

## What remains intentionally unimplemented

- no answer engine
- no semantic retrieval
- no embeddings
- no graph engine
- no ranking or inference layer
- no prompt orchestration
- no backend service
- no cloud sync
- no ingestion into publication pipeline

## Relationship to AXIS Cognitive Layer Bootstrap

The AXIS Cognitive Layer Bootstrap and the AXIS NANA Retrieval Skeleton are adjacent but different layers.

- Cognitive Layer Bootstrap creates derivative study artifacts:
  - lesson
  - quiz
  - audio script
- NANA Retrieval Skeleton creates source-bound context packs:
  - concept id
  - canonical refs
  - related concepts
  - zero interpretation

Practical relationship:

- Cognitive Bootstrap can use canonical refs as inputs for derivative study materials
- NANA Retrieval Skeleton prepares a stricter upstream retrieval layer that later systems may consume safely before any prompting or interpretation step

In short:

- Cognitive Bootstrap = derivative learning artifacts
- NANA Retrieval Skeleton = non-interpreted canonical context packaging

## Rollback instructions

Remove only the retrieval skeleton artifacts created for this layer:

```bash
rm -f AXIS_NANA_RETRIEVAL_SKELETON_CHECKPOINT.md
rm -f docs/AXIS_NANA_RETRIEVAL_SKELETON.md
rm -f metadata/nana/concept_registry.json
rm -f outputs/nana/context-pack-dukkha-bootstrap-v1.json
rm -f outputs/nana/context-pack-anicca-bootstrap-v1.json
rm -f outputs/nana/context-pack-nibbana-bootstrap-v1.json
rm -f outputs/nana/.gitkeep
rm -rf scripts/nana
```

If you want to keep the directory skeleton, remove only the generated JSON packs and keep `metadata/nana/`, `scripts/nana/`, and `outputs/nana/.gitkeep`.
