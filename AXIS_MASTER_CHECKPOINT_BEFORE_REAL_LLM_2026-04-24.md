# AXIS Master Checkpoint Before Real LLM — 2026-04-24

## 1. Current branch

- current branch: `feat-axis-navigator-v1-1`
- no work was performed on `main`
- all development remained in feature-branch mode

## 2. Navigator state

### Kulla Mode

- internal mode value: `asfalto`
- UI label: `Kulla Mode`
- minimal reading mode
- panel stays quiet and low-contrast
- no Study Mode panels shown

### Orbit Mode

- internal mode value: `hover`
- UI label: `Orbit Mode`
- practical study/navigation mode
- keeps Quick Find, This Page, outline, related pages, history, resume, and paths accessible
- no BeYond-only NANA workspace shown

### BeYond Mode

- internal mode value: `javana`
- UI label: `BeYond Mode`
- wider advanced cockpit panel
- exposes the Javana/BeYond workspace
- acts as the host surface for read-only ÑĀṆA visibility

### Study Mode

- persisted in local preferences as `axis.navigator.v1.preferences.study_mode`
- default is off
- when enabled together with `javana`, reveals `NANA Study`
- read-only UI layer only

### NANA Study UI

- visible only in `BeYond Mode + Study Mode ON`
- displays local ÑĀṆA artifacts for the resolved concept
- shows:
  - concept
  - canonical refs
  - related concepts
  - gate status
  - execution state
  - prompt preview when execution is ready

### Council UI

- visible only in `BeYond Mode + Study Mode ON`
- displays local Council Simulation artifacts
- shows:
  - `council_id`
  - `concept_id`
  - `consensus_status`
  - `citation_agreement_score`
  - `hallucination_risk`
  - candidate count
  - `llm_called`
  - compact candidate cards

### Provider Runs UI

- visible only in `BeYond Mode + Study Mode ON`
- displays local Provider Adapter dry-run artifacts
- shows:
  - `provider_run_id`
  - `concept_id`
  - `provider`
  - `provider_status`
  - `provider_decision`
  - `llm_called`
  - `answer_generated`
- mock preview is collapsed and explicitly labeled as simulated
- unsafe preview suppression is active if any loaded run reports `llm_called != false`

## 3. ÑĀṆA chain state

Current safe local chain:

```text
Concept Registry
-> Context Pack
-> Source-Bound Prompt
-> Insufficient Context Gate
-> Safe Execution Wrapper
-> Council Simulation
-> Provider Adapter Dry Run
```

Chain meaning:

- `Concept Registry`
  - deterministic concept-to-canonical-ref seed map
- `Context Pack`
  - canonical retrieval pack with refs and related concepts
- `Source-Bound Prompt`
  - future-LLM prompt package constrained to provided refs only
- `Insufficient Context Gate`
  - deterministic sufficiency filter
- `Safe Execution Wrapper`
  - simulated pre-LLM execution with gate enforcement
- `Council Simulation`
  - simulated multi-candidate comparison with citation agreement structure
- `Provider Adapter Dry Run`
  - provider abstraction layer with safe default behavior

## 4. Files created/modified by module

### Navigator

Created:

- `pipeline/13-ssg/static/js/navigator-store.js`
- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

Modified:

- `pipeline/13-ssg/templates/base.html`
- `pipeline/13-ssg/templates/welcome.html`
- `pipeline/13-ssg/build.py`

Navigator capabilities added across v1 -> v1.2:

- floating navigator button
- side panel shell
- Quick Find
- This Page
- resume reading
- recent history
- study paths
- cockpit mode toggle
- related pages
- page outline
- improved Quick Find UX/ranking
- Javana/BeYond workspace foundation
- Study Mode toggle
- NANA Study UI
- Council UI
- Provider Runs UI

### Cognitive Layer Bootstrap

Created:

- `scripts/orchestration/generate_lesson.py`
- `scripts/orchestration/generate_quiz.py`
- `scripts/orchestration/generate_audio_script.py`
- `scripts/orchestration/validate_generated_artifact.py`
- `scripts/orchestration/README.md`
- `docs/AXIS_COGNITIVE_LAYER_BOOTSTRAP.md`
- `outputs/.gitkeep`
- `outputs/lesson-dukkha-bootstrap-v1.json`
- `outputs/quiz-anicca-bootstrap-v1.json`
- `outputs/audio-script-nibbana-bootstrap-v1.json`

### ÑĀṆA Retrieval

Created:

- `metadata/nana/concept_registry.json`
- `scripts/nana/retrieve_concept.py`
- `scripts/nana/validate_context_pack.py`
- `scripts/nana/README.md`
- `docs/AXIS_NANA_RETRIEVAL_SKELETON.md`
- `outputs/nana/.gitkeep`
- `outputs/nana/context-pack-dukkha-bootstrap-v1.json`
- `outputs/nana/context-pack-anicca-bootstrap-v1.json`
- `outputs/nana/context-pack-nibbana-bootstrap-v1.json`

### Source-Bound Prompt Builder

Created:

- `scripts/nana/build_source_bound_prompt.py`
- `scripts/nana/validate_prompt_package.py`
- `docs/AXIS_NANA_SOURCE_BOUND_PROMPT_BUILDER.md`
- `outputs/nana/prompts/.gitkeep`
- `outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json`
- `outputs/nana/prompts/prompt-anicca-bootstrap-v1.json`
- `outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json`

Modified:

- `scripts/nana/README.md`

### Context Gate

Created:

- `scripts/nana/evaluate_context_sufficiency.py`
- `scripts/nana/validate_gate_result.py`
- `docs/AXIS_NANA_INSUFFICIENT_CONTEXT_GATE.md`
- `outputs/nana/gates/.gitkeep`
- `outputs/nana/gates/gate-dukkha-bootstrap-v1.json`
- `outputs/nana/gates/gate-anicca-bootstrap-v1.json`
- `outputs/nana/gates/gate-nibbana-bootstrap-v1.json`

### Safe Execution Wrapper

Created:

- `scripts/nana/execute_llm_safe_mode.py`
- `scripts/nana/validate_execution_result.py`
- `docs/AXIS_NANA_LLM_EXECUTION_WRAPPER.md`
- `outputs/nana/execution/.gitkeep`
- `outputs/nana/execution/execution-dukkha-bootstrap-v1.json`
- `outputs/nana/execution/execution-anicca-bootstrap-v1.json`
- `outputs/nana/execution/execution-nibbana-bootstrap-v1.json`

### Council Simulation

Created:

- `scripts/nana/simulate_council.py`
- `scripts/nana/validate_council_result.py`
- `docs/AXIS_NANA_COUNCIL_SIMULATION.md`
- `outputs/nana/council/.gitkeep`
- `outputs/nana/council/council-dukkha-bootstrap-v1.json`
- `outputs/nana/council/council-anicca-bootstrap-v1.json`
- `outputs/nana/council/council-nibbana-bootstrap-v1.json`

### Provider Adapter

Created:

- `scripts/nana/providers/__init__.py`
- `scripts/nana/providers/base_provider.py`
- `scripts/nana/providers/none_provider.py`
- `scripts/nana/providers/mock_provider.py`
- `scripts/nana/run_provider_adapter.py`
- `scripts/nana/validate_provider_result.py`
- `docs/AXIS_NANA_PROVIDER_ADAPTER_DRY_RUN.md`
- `outputs/nana/provider_runs/.gitkeep`
- `outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-anicca-none-bootstrap-v1.json`
- `outputs/nana/provider_runs/provider-nibbana-none-bootstrap-v1.json`

Modified:

- `scripts/nana/README.md`

### BeYond UI integrations

Modified:

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/css/navigator.css`

Integrated views:

- `NANA Study`
- `Council Simulation`
- `Provider Runs`

## 5. Safety guarantees

Confirmed state before any real LLM integration:

- Canon untouched
- CSL untouched
- source ZIP untouched
- SG/SP/SA/SD untouched
- `build.py` untouched after the initial Navigator integration
- deploy untouched
- no external API calls
- no real LLM calls
- no backend introduced
- no cloud dependency introduced
- all generated artifacts are derivative and disposable
- Navigator remains progressive enhancement
- failure mode remains safe:
  - reading pages still works without Navigator JS
  - missing ÑĀṆA artifacts degrade to read-only empty-state UI

## 6. Local artifact folders

Current local artifact folders:

```text
outputs/
outputs/nana/
outputs/nana/prompts/
outputs/nana/gates/
outputs/nana/execution/
outputs/nana/council/
outputs/nana/provider_runs/
```

Supporting source/metadata folders:

```text
metadata/nana/
scripts/orchestration/
scripts/nana/
scripts/nana/providers/
docs/
```

## 7. Validation commands

### Cognitive Layer Bootstrap

```bash
python3 scripts/orchestration/generate_lesson.py --concept dukkha --dry-run
python3 scripts/orchestration/generate_quiz.py --concept anicca --dry-run
python3 scripts/orchestration/generate_audio_script.py --concept nibbana --dry-run
python3 scripts/orchestration/validate_generated_artifact.py outputs/lesson-dukkha-bootstrap-v1.json outputs/quiz-anicca-bootstrap-v1.json outputs/audio-script-nibbana-bootstrap-v1.json
```

### ÑĀṆA Retrieval

```bash
python3 scripts/nana/retrieve_concept.py --concept dukkha --dry-run
python3 scripts/nana/retrieve_concept.py --concept anicca --dry-run
python3 scripts/nana/retrieve_concept.py --concept nibbana --dry-run
python3 scripts/nana/retrieve_concept.py --concept dukkha --output outputs/nana/context-pack-dukkha-bootstrap-v1.json
python3 scripts/nana/retrieve_concept.py --concept anicca --output outputs/nana/context-pack-anicca-bootstrap-v1.json
python3 scripts/nana/retrieve_concept.py --concept nibbana --output outputs/nana/context-pack-nibbana-bootstrap-v1.json
python3 scripts/nana/validate_context_pack.py outputs/nana/*.json
```

### Source-Bound Prompt Builder

```bash
python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --question "What causes suffering?" --dry-run
python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --question "What causes suffering?" --output outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json
python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-anicca-bootstrap-v1.json --question "What does anicca mean in this corpus?" --output outputs/nana/prompts/prompt-anicca-bootstrap-v1.json
python3 scripts/nana/build_source_bound_prompt.py --context-pack outputs/nana/context-pack-nibbana-bootstrap-v1.json --question "How should Nibbana be understood from this context?" --output outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json
python3 scripts/nana/validate_prompt_package.py outputs/nana/prompts/*.json
```

### Context Gate

```bash
python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --dry-run
python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-dukkha-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --output outputs/nana/gates/gate-dukkha-bootstrap-v1.json
python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-anicca-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-anicca-bootstrap-v1.json --output outputs/nana/gates/gate-anicca-bootstrap-v1.json
python3 scripts/nana/evaluate_context_sufficiency.py --context-pack outputs/nana/context-pack-nibbana-bootstrap-v1.json --prompt-package outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json --output outputs/nana/gates/gate-nibbana-bootstrap-v1.json
python3 scripts/nana/validate_gate_result.py outputs/nana/gates/*.json
```

### Safe Execution Wrapper

```bash
python3 scripts/nana/execute_llm_safe_mode.py --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --gate outputs/nana/gates/gate-dukkha-bootstrap-v1.json --dry-run
python3 scripts/nana/execute_llm_safe_mode.py --prompt-package outputs/nana/prompts/prompt-dukkha-bootstrap-v1.json --gate outputs/nana/gates/gate-dukkha-bootstrap-v1.json --output outputs/nana/execution/execution-dukkha-bootstrap-v1.json
python3 scripts/nana/execute_llm_safe_mode.py --prompt-package outputs/nana/prompts/prompt-anicca-bootstrap-v1.json --gate outputs/nana/gates/gate-anicca-bootstrap-v1.json --output outputs/nana/execution/execution-anicca-bootstrap-v1.json
python3 scripts/nana/execute_llm_safe_mode.py --prompt-package outputs/nana/prompts/prompt-nibbana-bootstrap-v1.json --gate outputs/nana/gates/gate-nibbana-bootstrap-v1.json --output outputs/nana/execution/execution-nibbana-bootstrap-v1.json
python3 scripts/nana/validate_execution_result.py outputs/nana/execution/*.json
```

### Council Simulation

```bash
python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --dry-run
python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --output outputs/nana/council/council-dukkha-bootstrap-v1.json
python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-anicca-bootstrap-v1.json --output outputs/nana/council/council-anicca-bootstrap-v1.json
python3 scripts/nana/simulate_council.py --execution outputs/nana/execution/execution-nibbana-bootstrap-v1.json --output outputs/nana/council/council-nibbana-bootstrap-v1.json
python3 scripts/nana/validate_council_result.py outputs/nana/council/*.json
```

### Provider Adapter

```bash
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider none --dry-run
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-dukkha-none-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-dukkha-bootstrap-v1.json --provider mock --output outputs/nana/provider_runs/provider-dukkha-mock-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-anicca-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-anicca-none-bootstrap-v1.json
python3 scripts/nana/run_provider_adapter.py --execution outputs/nana/execution/execution-nibbana-bootstrap-v1.json --provider none --output outputs/nana/provider_runs/provider-nibbana-none-bootstrap-v1.json
python3 scripts/nana/validate_provider_result.py outputs/nana/provider_runs/*.json
```

### Navigator syntax checks

```bash
node --check pipeline/13-ssg/static/js/navigator.js
node --check pipeline/13-ssg/static/js/navigator-store.js
```

## 8. Rollback strategy

### Rollback Navigator UI only

Scope:

- Navigator overlay
- Study Mode UI
- BeYond UI integrations

Relevant files:

- `pipeline/13-ssg/static/js/navigator.js`
- `pipeline/13-ssg/static/js/navigator-store.js`
- `pipeline/13-ssg/static/css/navigator.css`
- `pipeline/13-ssg/templates/base.html`
- `pipeline/13-ssg/templates/welcome.html`

Checkpoint docs to remove if desired:

- `AXIS_NAVIGATOR_V1_2_CHECKPOINT.md`
- `AXIS_NAVIGATOR_BEYOND_COUNCIL_UI_CHECKPOINT.md`
- `AXIS_NAVIGATOR_BEYOND_PROVIDER_RUNS_UI_CHECKPOINT.md`

### Rollback ÑĀṆA only

Scope:

- `metadata/nana/`
- `scripts/nana/`
- `outputs/nana/`
- ÑĀṆA docs/checkpoints

This removes:

- Retrieval
- Prompt Builder
- Gate
- Safe Execution
- Council
- Provider Adapter

### Rollback provider adapter only

Scope:

- `scripts/nana/providers/`
- `scripts/nana/run_provider_adapter.py`
- `scripts/nana/validate_provider_result.py`
- `outputs/nana/provider_runs/`
- `docs/AXIS_NANA_PROVIDER_ADAPTER_DRY_RUN.md`
- `AXIS_NANA_PROVIDER_ADAPTER_DRY_RUN_CHECKPOINT.md`

This preserves the earlier ÑĀṆA chain while removing provider abstraction.

### Full experimental rollback

Scope:

- Navigator additive UI layer
- Cognitive Layer Bootstrap
- all ÑĀṆA modules
- all derived outputs
- all related docs/checkpoints

This returns the repo to pre-experimental AXIS state while leaving Canon and production-preservation layers intact.

## 9. Ready-for-real-LLM criteria

Before plugging a real LLM provider, require all of the following:

- all checkpoints present and reviewed
- provider adapter default remains `none`
- real provider activation requires explicit opt-in flag
- no API key committed anywhere in the repo
- gate must allow execution before provider run
- prompt package must remain source-bound
- output must cite canonical refs
- raw LLM answer must be stored as derivative artifact only
- Canon must remain authoritative
- any real answer artifact must be validated before UI exposure

## 10. Next recommended steps

1. OpenAI / Vertex / local provider adapter in explicit opt-in mode
2. Real answer artifact schema
3. Answer validator
4. Council comparison with real providers
5. BeYond UI read-only view of real answer artifacts

## Reference checkpoints

Existing checkpoints in this workspace:

- `AXIS_COGNITIVE_LAYER_BOOTSTRAP_CHECKPOINT.md`
- `AXIS_NANA_RETRIEVAL_SKELETON_CHECKPOINT.md`
- `AXIS_NANA_SOURCE_BOUND_PROMPT_BUILDER_CHECKPOINT.md`
- `AXIS_NANA_INSUFFICIENT_CONTEXT_GATE_CHECKPOINT.md`
- `AXIS_NANA_LLM_EXECUTION_WRAPPER_CHECKPOINT.md`
- `AXIS_NANA_COUNCIL_SIMULATION_CHECKPOINT.md`
- `AXIS_NANA_PROVIDER_ADAPTER_DRY_RUN_CHECKPOINT.md`
- `AXIS_NAVIGATOR_V1_2_CHECKPOINT.md`
- `AXIS_NAVIGATOR_BEYOND_COUNCIL_UI_CHECKPOINT.md`
- `AXIS_NAVIGATOR_BEYOND_PROVIDER_RUNS_UI_CHECKPOINT.md`

This master checkpoint is the consolidation point immediately before any real LLM/provider integration.
