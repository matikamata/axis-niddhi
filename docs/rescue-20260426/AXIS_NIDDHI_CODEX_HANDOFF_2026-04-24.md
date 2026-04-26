# AXIS-NIDDHI — CODEX HANDOFF DOCUMENT

**Technical handoff for CodeX / VS Code implementation**  
**Generated:** 2026-04-24  
**Project:** PureDhamma Preservation Project / AXIS-NIDDHI  
**Mode:** Safe continuation after Preservation + Canon stabilization  
**Primary audience:** CodeX inside VS Code / local development agents  
**Language:** PT-BR with technical English retained where useful

---

## 0. Purpose of this document

This document is a compact but detailed operational handoff for any local coding assistant, especially **CodeX inside VS Code**, before continuing AXIS-NIDDHI implementation.

It consolidates:

- the canonical AXIS-NIDDHI preservation architecture,
- the current implementation state reported in the project sessions,
- the non-negotiable invariants,
- the expected filesystem structure,
- the safe next implementation layer,
- the boundaries between preservation, cognition, UX/UI, and future apps.

This document is meant to be copied into the project folder and read before any code changes.

> **Important:** Some state below is based on successful terminal reports produced in the project chat, not a live filesystem scan by this assistant. CodeX must revalidate paths and run integrity checks before editing.

---

## 1. Executive summary for CodeX

AXIS-NIDDHI is not a normal website, CMS, or static-site project.

It is a **deterministic corpus preservation engine** for the PureDhamma corpus, designed to preserve, verify, rebuild, and distribute a knowledge corpus independently of the original infrastructure.

The preservation baseline is already operational.

Current architectural separation:

```text
AXIS ENGINE      → Infrastructure / deterministic rebuild pipeline
AXIS CANON       → Knowledge / CSL + hashes + ledger + seeds
AXIS ÑĀṆA        → Understanding / canonical Q&A and citation engine
AXIS COSMOS      → Navigation / concept graph and knowledge visualization
AXIS ACADEMY     → Learning / structured Brilliant-Duolingo style layer
sKullApp         → End-user experiential interface
PitiPath         → Future audio / movement / micro-learning companion
```

The current goal is **not** to destabilize the preservation engine.

The near-term goal is to continue implementation safely in the cognitive/UX layer:

1. preserve the working AXIS-NIDDHI pipeline,
2. keep the vitrines already deployed safe,
3. build local orchestration around ÑĀṆA → Cosmos → Academy → sKullApp,
4. use APIs such as Vertex AI only as optional processors, never as the source of truth.

---

## 2. Canonical identity of AXIS-NIDDHI

AXIS-NIDDHI is a **corpus preservation engine**.

Its purpose is to:

1. ingest a bounded corpus from an original source archive,
2. extract the content faithfully,
3. transform it into a durable structured representation,
4. preserve translation artifacts,
5. produce static distribution artifacts,
6. seal releases cryptographically,
7. allow future rebuilds without depending on the original website, domain, CMS, or cloud infrastructure.

The system is organized around three core preservation claims:

| Claim | Meaning |
|---|---|
| **Integrity** | Content is preserved exactly and every mutation is auditable. |
| **Reproducibility** | Given the same source ZIP and engine state, the corpus can be rebuilt. |
| **Independence** | Reading, verifying, and rebuilding do not depend on the original web infrastructure. |

The CSL, not the static site, is the primary record.

---

## 3. Non-negotiable invariants

CodeX must treat these as hard safety rails.

### I1 — Source immutability

The source ZIP is never modified after acquisition.

Do not edit or regenerate the original backup ZIP in place.

### I2 — CSL primacy

`09-csl/` is the canonical structured representation.

If a static page disagrees with CSL, CSL wins.

### I3 — Lineage append-only

Lineage records are never rewritten silently.

A pipeline step may add a lineage entry. It may not delete or rewrite prior events.

### I4 — Deterministic rebuild

Given the same source ZIP and the same engine version, a full rebuild should produce the same corpus structure, modulo explicitly acknowledged runtime timestamps or run-specific IDs.

Unexpected non-determinism is a defect.

### I5 — Release self-containment

A frozen release must be operable without depending on `/beng-fut`, `/mnt/archaeology`, a live cloud service, or hidden system state.

Credentials are intentionally excluded and operator-supplied.

### I6 — Archaeology immutability

`/mnt/archaeology` is archival, not operational.

Expected mount discipline:

```bash
mount -o ro,noexec /dev/<device> /mnt/archaeology
```

No automated tooling should write to archaeology except during an explicit, short, human-supervised archive operation.

### I7 — Engine / corpus separation

Engine scripts must not embed corpus-specific content.

Corpus identity belongs in descriptors such as `corpus.json`, `source_format.json`, `pipeline_profile.json`, and registry files.

### I8 — Manifest portability

Release manifests must use relative paths.

Absolute-path manifests are preservation defects.

### I9 — No secret leakage

Never commit, copy into public release, or deploy:

```text
scripts/private/
deepl_key.txt
wp_password.txt
github_token.txt
.env
*.pem
*.key
```

### I10 — Preservation before UX

UX/UI work must consume canonical outputs; it must never mutate canonical content.

Cosmos, Navigator, Academy, ÑĀṆA, sKullApp, and PitiPath are downstream consumers.

---

## 4. Known workspaces and roles

The project has multiple workspaces. Revalidate before acting.

| Workspace | Role | Expected status |
|---|---|---|
| `/beng-fut/pipeline/` | LAB / long-term development base | Must remain stable; source of mature changes. |
| `/home/sanghop/bengyond/pipeline/` | Portable workspace / PenDrive precursor | Tested portable rebuild path. |
| `/home/sanghop/beng_prelaunch/pipeline/` | GOLDEN / distribution prelaunch workspace | Most recent full feature integration reports came from here. |
| `/beng-release/` | Self-contained release output | Rebuilt by release snapshot tooling. |
| `/mnt/archaeology/` | Immutable archive | Read-only/noexec; historical record. |

### Safety rule

Before editing, CodeX must identify which workspace it is in:

```bash
pwd
git branch --show-current 2>/dev/null || true
find . -maxdepth 2 -type d | sort | sed -n '1,80p'
```

Never assume paths.

---

## 5. Current implementation state from project reports

### 5.1 Preservation phase

Reported complete.

Core preservation properties:

- full rebuild from PureDhamma backup ZIP,
- 748 CSL entries,
- PT-BR translation preservation layer with 93 frozen translations,
- static site output operational,
- SHA-256 canon and release manifests,
- ledger, seed, mirror, and capsule layers operational,
- Sojourner and Steward distributions generated,
- remote mirror live via Netlify.

### 5.2 Verified reported metrics

| Component | Reported state |
|---|---|
| Corpus | PureDhamma |
| CSL entries | 748 |
| PT-BR frozen translations | 93 |
| Glossary terms | ~986 |
| Semantic concepts | 11/11 verified |
| Navigator nodes | 11 |
| Navigator edges | 55 |
| Sojourner distribution | static viewer + Navigator pages |
| Steward distribution | full rebuild package with ZIP + ledger + translations |
| Remote mirror | Netlify mirror endpoint operational |
| Capsule | sealed 200K / 28 files in one report |

### 5.3 Current live public surfaces mentioned by operator

The operator reported:

- GitHub repositories under `https://github.com/matikamata`
- GitHub Pages static archive: `https://matikamata.github.io/axis-niddhi/archive.html`
- Cloudflare Pages static archive: `https://niddhi.pages.dev/archive`
- Netlify AXIS-NIDDHI / AXIS-Navigator deployments
- AXIS Navigator: `https://axis-navigator.netlify.app/`
- AXIS-NIDDHI archive integration: `https://niddhi.netlify.app/archive`

These URLs should be treated as **deployment targets / vitrines**, not as canonical sources.

Canonical truth remains local: CSL + canon manifest + ledger + seed.

---

## 6. Pipeline architecture

The full rebuild pipeline is organized into four major phases:

```text
SG → SP → SA → SD
```

### 6.1 SG — Genesis

Purpose: rebuild from the original source environment into extracted and canonical files.

Typical flow:

```text
SG00_reset_workspace.sh
  → reset local WP / DB / workspace

SG01_extract_html.py
  → MySQL / WordPress extraction
  → 01-extracted-htmls/{lang}/

SG02_preprocess_html.py
  → clean / normalize extracted HTML
  → 02-preprocessed/{lang}/

SG03_build_csl.py
  → build CSL
  → 09-csl/{PDPN}/source/{lang}/content.html
  → 09-csl/{PDPN}/meta/identity.json

SG04_harvest_assets.py
  → harvest image/audio assets
```

### 6.2 SP — Preservation

Purpose: preserve translations, migrate identity records, normalize structure, and optionally translate.

Current important addition:

```text
SP00_freeze_translations.py
  → exports current PT-BR translations from CSL to 03-translations/

SP01b_restore_translations.py
  → restores translations from 03-translations/ into a fresh CSL
```

The critical integration point is:

```text
SP01 → SP01b_restore_translations.py → SP02
```

This allows a fresh SQL/ZIP extraction to rebuild `09-csl/` without losing existing PT-BR work.

Expected guarantee:

```text
New dump → SG resets CSL → SP01b restores 93 translations
→ SP10 skips already-restored posts
→ zero DeepL spend on already-translated posts
```

### 6.3 SA — Audit

Purpose: verify structural integrity, translation progress, canon manifest, and build seal.

Current reported sequence:

```text
SA01_final_audit.py
SA02_freeze_manifest.py
SA03_translation_progress.py
SA04_generate_canon_manifest.py
SA06_build_seal.py
SA05_verify_canon.py
```

Important operational invariant:

> After any script/core change, regenerate SA04 canon manifest before SA05/SA06 verification.

### 6.4 SD — Distribution

Purpose: generate static site, asset maps, optional WP output.

Important outputs:

```text
13-static-site/
releases/sojourner/
releases/steward/
mirror_endpoint/
```

---

## 7. Script structure normalization

The script tree was normalized from a crowded `scripts/` folder into role-based folders.

Expected structure:

```text
scripts/
├── core/       # canonical pipeline scripts
├── legacy/     # preserved superseded scripts, not deleted
├── tools/      # utilities, packaging, mirror, seed, ledger, semantic, navigator, capsule
├── private/    # credentials, gitignored
└── .gitignore
```

Reported successful propagation:

- `beng_prelaunch`
- `bengyond`
- `beng-fut`

All three reported matching core state after propagation.

### Important

If a script expects old flat paths, patch the pathing cleanly rather than flattening the tree again.

Preferred resolution pattern:

```python
from pathlib import Path
import sys

_SCRIPT_DIR = Path(__file__).resolve().parent
# adjust parent depth only after verifying local tree
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
```

But prefer importing path constants from `config.py`.

---

## 8. CLI surface

The AXIS CLI evolved through multiple reports.

Reported current surface around V1.9:

```text
axis build
axis verify pipeline
axis verify canon
axis report
axis manifest
axis serve [port]
axis package sojourner
axis package steward
axis corpus list
axis corpus info <id>
axis tag
axis seed generate
axis seed verify
axis ledger add
axis ledger list
axis ledger verify
axis mirror endpoint
axis mirror add
axis mirror list
axis mirror sync
axis semantic list
axis semantic add
axis semantic verify
axis navigator build
axis navigator map
axis navigator paths
axis navigator query
axis capsule build
axis capsule verify
axis capsule info
axis version
```

Before adding a new CLI command:

1. Check existing `axis_cli.sh` or equivalent dispatcher.
2. Preserve backward compatibility.
3. Add dry-run where risk exists.
4. Print clear status and paths.
5. Never hide failed verification.

---

## 9. Distribution tiers

The distribution system now uses renamed tiers to avoid conflicts with older folders.

### 9.1 SOJOURNER

Purpose: offline viewer / user-facing archive.

Expected contents:

```text
releases/sojourner/
├── dist/          # static site
├── navigator/     # Navigator HTML layer
└── data/          # concept_map, query_index, paths JSON
```

Reported properties:

- ~33MB
- 749 pages counted, where 1 is root `index.html`
- no rebuild required

### 9.2 STEWARD

Purpose: full rebuild capability.

Expected contents:

```text
releases/steward/
├── pipeline/
│   ├── scripts/core/
│   ├── scripts/tools/
│   ├── metadata/
│   ├── 03-translations/
│   └── sources/   # includes source ZIP
└── ledger/
```

Reported properties:

- ~2.2GB
- includes source ZIP
- includes 93 frozen PT-BR translations
- credentials excluded
- ledger verified

### 9.3 NINUNK

Purpose: future bootable ISO / bare-metal archival environment.

Current state: structure only / future phase.

Do not attempt ISO build unless explicitly requested.

---

## 10. Canon seed, ledger, mirror, capsule

### 10.1 Seed

The seed is not a rebuild package.

It is a cryptographic declaration:

```text
This canon was built, with these hashes,
from this source, by this engine.
```

Reported seed package:

```text
seeds/puredhamma_seed/
├── corpus.json
├── pipeline_profile.json
├── canon_manifest.json
├── build_seal.json
└── seed_manifest.json
```

### 10.2 Ledger

Append-only registry of canon states.

Reported structure:

```text
ledger/
├── ledger.json
└── entries/
    └── puredhamma-v1.json
```

Rules:

- existing entries are never modified,
- duplicate tags are rejected,
- `entry_hash` mismatch is structural failure,
- canon hash divergence is informational unless the declared canon is supposed to match live current state.

### 10.3 Mirror protocol

Mirror endpoint is transport-agnostic:

```text
HTTP / HTTPS / file://
```

Reported endpoint structure:

```text
mirror_endpoint/
├── ledger.json
├── endpoint_manifest.json
├── entries/puredhamma-v1.json
├── seeds/puredhamma-v1/
└── tags/puredhamma-v1/
```

Reported invariant fixed:

```text
axis mirror endpoint copies mirror_endpoint/ to 13-static-site/
```

This keeps Netlify deploy and mirror endpoint synchronized.

### 10.4 Capsule

Time capsule aggregates seed, ledger, semantic, navigator, mirror endpoint, and human/machine documentation.

Reported structure:

```text
capsule/
├── README_HUMANS.md
├── README_MACHINES.json
├── AXIS_PROTOCOL.md
├── capsule_manifest.json
├── seeds/
├── ledger/
├── semantic/
├── navigator/
└── mirror_endpoint/
```

---

## 11. Semantic and Navigator layers

### 11.1 Semantic layer

Purpose: concept registry that references the canon without mutating it.

Reported current status:

- 11 concepts,
- 0 warnings,
- all Navigator nodes formalized.

Concepts:

```text
anicca
anatta
avijja
dukkha
magga
nibbana
paticca_samuppada
phala
sankhara
tanha
tilakkhana
```

Invariant:

> Semantic layer is additive. It never modifies canon text, CSL, or `identity.json`. Concepts reference CSL entries; CSL never references back.

### 11.2 Navigator layer

Purpose: knowledge navigation over concepts and study paths.

Reported current status:

- 11 nodes,
- 55 edges,
- 3 study paths,
- 14 Navigator HTML pages in Sojourner.

Study paths:

```text
BEGINNER_PATH
DEPENDENT_ORIGINATION_PATH
LIBERATION_PATH
```

Navigator is non-canonical.

It is rebuilt from semantic data:

```bash
axis navigator build
```

---

## 12. AXIS ÑĀṆA

The former “AXIS Oracle” is now **AXIS ÑĀṆA**.

Rationale:

- avoids confusion with Oracle Corporation and generic “oracle” tooling,
- better expresses correct understanding / direct knowledge,
- reduces internet-noise associations.

### 12.1 Purpose

ÑĀṆA is the controlled understanding layer.

It should retrieve canonical context, cite CSL IDs, and return structured outputs for downstream modalities.

### 12.2 Invariant

> ÑĀṆA never answers from itself as an authority. It retrieves canonical context and cites CSL entries.

LLMs may help render, summarize, teach, or transform, but only from provided canonical context.

### 12.3 Reported modes

```text
qa
explain
quiz
study_path
cite
concept_map
```

### 12.4 Modality outputs

Expected response struct should support:

```text
to_dict()        → text / sKullApp
to_audio_hint()  → PitiPath / TTS
to_graph_hint()  → Cosmos graph layer
```

### 12.5 Implementation naming

Preferred names:

```text
axis_nana/
nana_engine.py
NanaResponse or ÑāṇaResponse in docs
```

For Python identifiers, avoid diacritics:

```python
class NanaResponse:
    pass
```

---

## 13. AXIS COSMOS

AXIS COSMOS is the navigation/visualization layer.

Purpose:

- render interactive concept graphs,
- consume `to_graph_hint()` from ÑĀṆA,
- visualize concept dependency, study paths, and eventually concept evolution.

### 13.1 Astronomy of Knowledge

Cosmos should treat the canon as a navigable “astronomy of knowledge”:

| Metaphor | Technical meaning |
|---|---|
| Stars | Canonical concepts |
| Constellations | Linked concept clusters |
| Orbits | Repeated study paths |
| Gravity | Citation density / dependency strength |
| Telescope | Query lens / focus mode |
| Time-lapse sky | Concept Evolution Tracking |

### 13.2 Concept Evolution Tracking

Future mechanism:

```text
concept_id
canonical_state
first_registered_at
related_edges_at_state
csl_refs_at_state
semantic_hash
navigator_hash
notes
```

Goal:

- show how understanding of a concept grows across canon versions,
- distinguish canonical text evolution from semantic/navigation layer evolution,
- support future Council Consensus or multi-operator reviews.

Do not mutate CSL for this. Store separately under something like:

```text
cosmos/evolution/
semantic/evolution/
```

---

## 14. AXIS ACADEMY

Academy is the structured learning layer.

Benchmark inspiration:

- Brilliant: conceptual interactive progression,
- Duolingo: streaks, micro-lessons, feedback loops,
- Obsidian graph: exploratory knowledge graph.

### 14.1 Design principle

Academy must be generated from canonical citations.

No free-floating lessons.

Every lesson, quiz, hint, or correction must resolve to:

```text
concept_id
CSL references
study_path
source evidence
```

### 14.2 Suggested data structure

```text
academy/
├── lessons/
│   └── <concept_id>_<level>.json
├── quizzes/
│   └── <concept_id>_<quiz_id>.json
├── paths/
│   └── beginner_path.json
└── progress_schema.json
```

### 14.3 Suggested lesson JSON

```json
{
  "lesson_id": "dukkha_beginner_001",
  "concept_id": "dukkha",
  "level": "beginner",
  "source_csl_refs": ["BD.AA.009", "TL.BB.006", "DS.FF.002"],
  "nana_query": "What is dukkha?",
  "learning_objective": "Understand dukkha as structural unsatisfactoriness, not merely ordinary pain.",
  "cards": [],
  "quiz": [],
  "next": ["anicca", "tanha"]
}
```

---

## 15. sKullApp

sKullApp is the end-user experiential interface.

Meaning stack:

```text
School + Kulla + Skull + Cool
```

Working interpretation:

- **School:** learning system,
- **Kulla:** raft / crossing tool,
- **Skull:** maranasati / technical seeing-through identity,
- **Cool:** usable, accessible, memorable.

Core UX principle:

> The app is a raft. It is useful until the user no longer needs it.

sKullApp should consume:

```text
ÑĀṆA responses
Academy lessons
Cosmos graph hints
Navigator paths
PitiPath audio scripts
```

It must not become the canonical store.

---

## 16. PitiPath / Mpiti-Pat

PitiPath is the future audio/movement layer.

Purpose:

- convert canon-grounded learning paths into audio experiences,
- serve busy users during walking, gym, cleaning, commuting,
- use generated audio scripts grounded in CSL citations,
- optionally integrate TTS, music bed, spatial audio, ANC-aware modes.

### 16.1 Safety principle

Do not overclaim medical, neurological, or guaranteed transformation effects.

If binaural, ANC, or Hemi-Sync-like ideas are explored, treat them as optional audio-design experiments, not scientific guarantees.

### 16.2 Suggested structure

```text
pitipath/
├── scripts/
│   └── <episode_id>.json
├── prompts/
│   └── audio_script_prompt.md
├── renders/
└── playlists/
```

### 16.3 Canon-to-audio flow

```text
User question / concept
  → ÑĀṆA retrieves CSL citations
  → Academy chooses lesson path
  → PitiPath generates audio script
  → TTS/music renderer produces optional output
```

---

## 17. API / Vertex / PRO mode architecture

Use cloud APIs only as processors.

Never make them source of truth.

### 17.1 Correct pattern

```text
Local canon data
  → ÑĀṆA retrieval
  → prompt constructed with canonical context only
  → Vertex/OpenAI/other API transforms into JSON/script/lesson
  → output saved locally
  → output verified for citation coverage
```

### 17.2 Recommended local orchestration structure

```text
scripts/
└── orchestration/
    ├── vertex_client.py
    ├── generate_quiz.py
    ├── generate_lesson.py
    ├── generate_audio_script.py
    ├── validate_generated_artifact.py
    └── prompts/
        ├── quiz_prompt.md
        ├── lesson_prompt.md
        └── audio_prompt.md

outputs/
├── quizzes/
├── lessons/
├── audio_scripts/
└── rejected/
```

### 17.3 Mandatory validation for generated outputs

Any generated quiz/lesson/audio script must include:

```text
source_csl_refs[]
concept_id
mode
model_used
created_at
prompt_hash
input_context_hash
validation_status
```

Reject generated artifacts if:

- they cite no CSL IDs,
- they introduce claims not supported by provided context,
- they overwrite canonical files,
- they require network access at read time,
- they include secrets or API keys.

---

## 18. Machine and OS recommendation

Recommended development topology:

### Primary dev

**MacBook Pro M2 / 24GB RAM / 1TB SSD**

Use for:

- VS Code / CodeX,
- API orchestration,
- rapid UX/UI iteration,
- Node/React prototypes,
- local scripts that call Vertex/OpenAI.

### Steward node

**ThinkPad X230** with Debian minimal or stable Ubuntu.

Use for:

- mirror node,
- long-running verification,
- cron-style rebuild checks,
- offline/portable distribution tests.

### Existing Linux workstation

**Dell XPS 9360 / Ubuntu / 16GB RAM / 1TB SSD**

Use for:

- current stable workspace continuity,
- staging,
- backup validation,
- compatibility tests.

Do not migrate everything at once. First establish a reproducible `README_LOCAL_SETUP.md`.

---

## 19. Current safe next implementation package

Recommended immediate package for CodeX:

```text
PHASE: AXIS Cognitive Layer Bootstrap
SCOPE: ÑĀṆA → Cosmos → Academy orchestration
RISK: Low if canonical files are read-only
```

### 19.1 Do first

1. Create `scripts/orchestration/` if absent.
2. Add local-only wrappers around ÑĀṆA.
3. Generate sample outputs into `outputs/`, not into canon folders.
4. Validate outputs for CSL citation coverage.
5. Add `README_COGNITIVE_LAYER.md`.

### 19.2 Do not do yet

- Do not modify SG/SP/SA/SD core unless required by a failing test.
- Do not rewrite `run_full_pipeline.sh`.
- Do not alter `09-csl/` manually.
- Do not change source ZIP.
- Do not build NINUNK ISO unless explicitly requested.
- Do not embed Vertex/OpenAI keys in code.
- Do not deploy automatically from CodeX without operator confirmation.

---

## 20. Pre-edit checklist for CodeX

Before any patch:

```bash
# Identify workspace
pwd

# Inspect branch if git exists
git status --short 2>/dev/null || true
git branch --show-current 2>/dev/null || true

# Confirm axis health
./axis_cli.sh version 2>/dev/null || ./axis version 2>/dev/null || true
./axis_cli.sh verify pipeline 2>/dev/null || ./axis verify pipeline 2>/dev/null || true

# List script structure
find scripts -maxdepth 2 -type f | sort | sed -n '1,160p'
```

If `axis verify pipeline` fails, stop and report.

---

## 21. Suggested first CodeX task

Use this exact task if beginning implementation:

```text
Task: Create a non-invasive AXIS Cognitive Layer Bootstrap.

Constraints:
- Do not modify SG/SP/SA/SD pipeline scripts.
- Do not modify 09-csl/, 03-translations/, sources/, ledger/, seeds/, or release manifests.
- Add only new files under scripts/orchestration/, outputs/, and docs/ unless a path fix is required.
- Use ÑĀṆA outputs as canonical context.
- Any generated artifact must cite CSL IDs.
- All API calls must be optional and disabled by default unless environment variables are present.
- Provide dry-run mode.

Deliverables:
1. scripts/orchestration/generate_lesson.py
2. scripts/orchestration/generate_quiz.py
3. scripts/orchestration/generate_audio_script.py
4. scripts/orchestration/validate_generated_artifact.py
5. scripts/orchestration/README.md
6. outputs/.gitkeep
7. docs/AXIS_COGNITIVE_LAYER_BOOTSTRAP.md

Validation:
- Run without API keys in local-only dry-run mode.
- Generate one sample lesson JSON for dukkha using existing semantic/navigator data.
- Generate one sample quiz JSON for anicca.
- Generate one sample audio-script JSON for nibbana or kulla.
- Validate that each output contains source_csl_refs[].
```

---

## 22. Suggested prompt for CodeX inside VS Code

```text
You are continuing AXIS-NIDDHI in local VS Code.

Before editing, read:
- AXIS_NIDDHI_CODEX_HANDOFF_2026-04-24.md
- AXIS_NIDDHI_ENGINE_MODEL_v2.md, if available
- AXIS_NIDDHI_CANONICAL_INDEX.md, if available

Mission:
Implement the AXIS Cognitive Layer Bootstrap without touching the preservation pipeline.

Safety constraints:
- Do NOT modify source ZIPs.
- Do NOT manually edit 09-csl/ or 03-translations/.
- Do NOT modify SG/SP/SA/SD core scripts unless a test proves it is required.
- Do NOT touch scripts/private/ or any credential file.
- Do NOT deploy.
- Do NOT rewrite the architecture.

Allowed changes:
- Add new orchestration scripts under scripts/orchestration/.
- Add generated samples under outputs/.
- Add documentation under docs/.
- Add dry-run only API client stubs that use environment variables if present.

Implementation target:
Create a local-only bridge from AXIS ÑĀṆA / semantic / navigator data to:
1. Academy lesson JSON
2. quiz JSON
3. PitiPath audio-script JSON

Every generated artifact must include:
- artifact_id
- concept_id
- source_csl_refs
- generated_from
- prompt_hash or input_context_hash
- validation_status

First run should work with no API keys, producing deterministic sample JSON from local data only.

After implementation:
- run axis verify pipeline if available,
- run semantic verify if available,
- run navigator build if available,
- show changed files only,
- explain whether any canonical files were touched.
```

---

## 23. Final architectural reminder

AXIS-NIDDHI has crossed the line from “site generator” to **canonical infrastructure**.

The correct mental model is:

```text
Preservation layer: ENGINE + CANON
Cognitive layer: ÑĀṆA + COSMOS + ACADEMY
Experience layer: sKullApp + PitiPath
Distribution layer: Sojourner + Steward + NINUNK
Survival layer: Seed + Ledger + Mirror + Capsule + Archaeology
```

Every future feature must declare which layer it belongs to.

If a feature cannot declare its layer, it is not ready for implementation.

---

## 24. Sync note

Session marker:

```text
#SyncSong = Kerala Dust - The Orb, TX
```

Meaning: this handoff was created at the transition from preservation/canon stabilization into disciplined PRO implementation mode.

---

*End of CodeX handoff.*
