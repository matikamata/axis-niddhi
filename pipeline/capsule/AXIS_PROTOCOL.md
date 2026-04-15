# AXIS Canon Protocol — Technical Description

**Protocol:** AXIS-CANON  
**Engine:** AXIS-NIDDHI  
**Version:** 5.4  

---

## Architecture Overview

```
SOURCE ZIP (PureDhamma backup)
       │
       ▼
[SG] STAGE: EXTRACTION
  SG00 reset_workspace
  SG01 extract_html         → raw HTML per post
  SG02 preprocess_html      → cleaned HTML + iframes
  SG03 build_csl            → 09-csl/ (Canon Source Library)
  SG04 harvest_assets       → images, audio
       │
       ▼
[SP] STAGE: PROCESSING
  SP01 migrate_ptbr         → pt-BR stubs
  SP02 upgrade_identity     → lineage blocks (PDPN, findex, slug)
  SP03 mass_migration       → bulk identity upgrade
  SP04 phase5_migration     → phase 5 content normalization
  SP05 fix_headers          → h1/h2 normalization
  SP06 audio_converter      → MP3 assets
  SP07 compile_glossary     → Glossario_v5 (986 terms)
  SP08 glossary_gate        → DeepL glossary upload
  SP09 translation_menu     → translation control manifest
  SP10 translate_deepl      → DeepL API translation
  SP11 translate_titles     → title translation
       │
       ▼
[SA] STAGE: AUDIT
  SA01 final_audit          → completeness check
  SA02 freeze_manifest      → translation freeze
  SA03 translation_progress → progress report
  SA04 generate_canon_manifest → cryptographic manifest (5 components)
  SA05 verify_canon_integrity  → verify all hashes
  SA06 generate_build_seal     → reproducibility declaration
       │
       ▼
[SD] STAGE: DEPLOYMENT
  SD01 generate_asset_map   → asset_map.json
  SD02 generate_slug_map    → slug_map.json (748 entries)
  SD04 wordpress_inject     → static site generation
       │
       ▼
13-static-site/ (748 HTML pages, bilingual)
```

---

## Canon Source Library (CSL)

The CSL is the canonical representation of the corpus.

```
09-csl/
└── <PDPN>/                   e.g. TL.BB.001/
    ├── identity.json          lineage block (PDPN, findex, slug, titles)
    ├── source/
    │   ├── en-US/content.html canonical English content
    │   └── pt-BR/content.html derived Portuguese translation
    └── assets/                images, audio
```

**PDPN format:** `SS.CC.NNN`  
- `SS` = section code (TL, BD, AB, DS, ...)  
- `CC` = category code  
- `NNN` = zero-padded sequence  

**Invariant:** CSL entries are never deleted. Content is never modified
after audit freeze. New entries are appended only.

---

## Seed Protocol

A **seed** is the minimal corpus fingerprint sufficient to:
- Verify corpus integrity
- Bootstrap a new AXIS node
- Confirm reproducibility without the full corpus

```
seeds/puredhamma_seed/
├── corpus.json            748 entries, language status, engine version
├── pipeline_profile.json  full stage map with all 34 scripts
├── canon_manifest.json    5-component cryptographic manifest
├── build_seal.json        reproducibility declaration
└── seed_manifest.json     seed_integrity_hash (SHA-256 of above)
```

**Verification:** `axis seed verify`

---

## Ledger Protocol

The ledger is an append-only registry of canon versions.

```
ledger/
├── ledger.json            index of registered entries
└── entries/
    └── puredhamma-v1.json full entry with all hashes
```

**Invariants:**
- Existing entries are never modified
- Duplicate tags are rejected
- `entry_hash` mismatch = structural failure
- `canon_hash` change after rebuild = informational (expected)

**Commands:** `axis ledger add | list | verify`

---

## Mirror Protocol

The mirror protocol enables lightweight synchronization between AXIS nodes.

```
mirror_endpoint/
├── ledger.json            remote-accessible ledger
├── endpoint_manifest.json endpoint integrity hash
├── entries/               per-canon entry metadata
├── seeds/                 seed packages
└── tags/                  release tag snapshots
```

**Transport:** HTTP / HTTPS / file://  
**Discovery:** `GET /ledger.json` → compare entries → download new seeds  
**Integrity:** seed_integrity_hash verified before writing  

**Commands:** `axis mirror sync | list | endpoint | add`

---

## Semantic Layer

The semantic layer is a non-canonical concept index.

```
semantic/
├── index.json             concept registry
├── concept_schema.json    field definitions
└── concepts/
    └── <concept>.json     concept entry
```

**Concept fields:** concept, type, pali, translations, first_occurrence,
occurrences, related, glossary_refs

**Types:** dhamma_characteristic, attainment, practice, mental_factor,
doctrine, person, place, text, other

**Invariant:** Additive only — never modifies CSL or canon text.

**Commands:** `axis semantic list | add | verify`

---

## Navigator Layer

The navigator layer provides non-canonical study paths through the corpus.

```
navigator/
├── concept_map.json       concept graph (nodes + edges + CSL links)
├── learning_paths.json    structured study sequences
└── query_index.json       concept → CSL slug lookup
```

**Concept graph:** 10 nodes, 35 edges (initial)  
**Study paths:** tilakkhana_intro, paticca_samuppada_intro, nibbana_path  

**Invariant:** Non-canonical — never modifies CSL or semantic layer.  
**Rebuild:** `axis navigator build`

---

## Integrity Model

```
canon_hash          SHA-256 of source ZIP
csl_hash            SHA-256 of 09-csl/ directory tree
translations_hash   SHA-256 of all pt-BR translations
site_build_hash     SHA-256 of 13-static-site/
pipeline_hash       SHA-256 of scripts/core/ (34 scripts)
manifest_hash       SHA-256 of all five above
seed_integrity_hash SHA-256 of 4 seed component hashes
entry_hash          SHA-256 of ledger entry content
```

A full rebuild from the same source ZIP must produce the same
`seed_integrity_hash`. This is the reproducibility guarantee.

---

## Full CLI Reference

```
axis build                    Full pipeline SG→SP→SA→SD
axis verify pipeline          Integrity guard (30 checks)
axis verify canon             SA05 — verify all canon hashes
axis report                   MI99 mission report
axis manifest                 SA04 canon manifest
axis serve [port]             Serve static site
axis package sojourner        Sojourner distribution (33MB)
axis package steward          Steward distribution (full)
axis corpus list / info       Corpus registry
axis tag [corpus] [version]   Release tag
axis seed generate / verify   Canon seed
axis ledger add / list / verify  Canon ledger
axis mirror sync / list / endpoint / add  Mirror protocol
axis semantic list / add / verify  Semantic concepts
axis navigator build / map / paths / query  Concept graph
axis capsule build            Time capsule
axis help                     Full command reference
```
