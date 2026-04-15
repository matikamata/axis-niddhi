a)
# AXIS-NIDDHI — POSITIONING
**Conceptual Position of the System**  
**Version:** 1.0  
**Date:** 2026-03-11  
**Status:** Locked — companion to AXIS_NIDDHI_ENGINE_MODEL.md

---

## WHAT AXIS-NIDDHI IS

AXIS-NIDDHI is a **corpus preservation engine**: a system designed to extract
a body of knowledge from its original publication infrastructure, structure it
into a durable canonical representation, and produce a self-contained artifact
that can be rebuilt and distributed indefinitely — without depending on anything
that may cease to exist.

The system was built to preserve the PureDhamma corpus. Its architecture is
general. Any bounded corpus with a definable source format can be processed
through the same engine.

The three properties that define what it means to have preserved a corpus are:

**Integrity.** The content is exactly what was published — nothing added,
nothing removed, nothing silently altered. Every file is verifiable by
SHA-256 hash. Every mutation is logged with its before-and-after state.

**Reproducibility.** Given the original source, the result can always be
reconstructed. Not approximately. Exactly. A rebuild ten years from now
produces the same canonical structure as a rebuild today.

**Independence.** The preserved corpus does not depend on any cloud service,
any live database, any domain name, or any institution. It runs on standard
hardware with standard open-source tools. It can be handed to a future operator
as a single directory.

---

## THE DETERMINISTIC REBUILD GUARANTEE

The central engineering commitment of AXIS-NIDDHI is that the pipeline is
deterministic: the same source always produces the same output.

This is not a performance claim. It is a preservation guarantee. It means that
the frozen release is not just a snapshot — it is a proof. Any operator who
holds a frozen release and the source ZIP holds everything needed to verify,
independently, that the corpus was preserved faithfully.

The mechanism is simple: the source is a sealed ZIP. The pipeline applies
defined transformations. The result is hashed and sealed. Nothing in this chain
depends on network state, time-varying configuration, or external services
beyond the one deliberate manual gate — translation — which is itself logged
and auditable.

Determinism converts preservation from a claim into a fact that can be checked.

---

## THE CSL AS CANONICAL STRUCTURED REPRESENTATION

Between the source and the publication, every piece of content passes through
the CSL — the Canonical Source Library.

The CSL is not a database. It is a directory tree. Every post is a folder.
Every folder contains the content in all processed languages and a machine-
readable identity record. The identity record contains the SHA-256 hashes of
the content, the titles, the publication metadata, and an append-only log
of every operation the pipeline has performed on that post.

The CSL has one property that makes it the right choice for long-term
preservation: it is human-readable without any tooling. A person with a
text editor can open any folder, read the content, read the identity record,
and understand exactly what the post contains and what was done to it. No
proprietary format, no database schema, no application layer required.

The CSL is the single source of truth. The static site is derived from it.
The WordPress injection is derived from it. If either publication form is
lost, the CSL is sufficient to regenerate it. If the CSL and any downstream
artifact disagree, the CSL is correct.

---

## FROZEN RELEASES AS PRESERVATION ARTIFACTS

A frozen release is not a build artifact in the software engineering sense.
It is a preservation artifact — a sealed, self-describing package designed
to be independently operable by a future operator who may have no context
about the original project.

A frozen release contains:

- The engine scripts needed to rebuild the corpus
- The source ZIP that is the origin of all content
- The control metadata (post index, glossary, section map)
- A SHA-256 manifest of every file, expressed in relative paths
- A README sufficient to onboard a new operator from zero

The manifest uses relative paths deliberately. A manifest with absolute paths
is coupled to a specific filesystem location. A manifest with relative paths
is valid wherever the release is stored — on the original machine, in an
archaeology archive, on a USB drive, on a server in a different country.

The archaeology layer stores frozen releases under a read-only, no-execute
mount. The physical mount enforces the conceptual property: archaeology is
a record, not an operational environment. Nothing in it is ever run.
Everything in it is available for reading and verification.

---

## ENGINE, CORPUS, AND RELEASE: THE SEPARATION

The most important conceptual boundary in the system is the separation between
three things that are easy to conflate:

The **engine** is the processing machinery. It is corpus-agnostic. It knows
how to extract, preprocess, translate, audit, and publish — but it contains
no content, no corpus-specific constants, no assumptions about what the corpus
says or how it is structured. The engine is a tool.

The **corpus** is the content and its description. The source ZIP, the post
index, the glossary, the section map — these belong to the corpus, not the
engine. A corpus has a persistent identity (`corpus_id`) that remains stable
across engine versions and rebuilds.

The **frozen release** is a point-in-time combination: this engine, configured
for this corpus, sealed on this date. It is neither the engine nor the corpus
in isolation. It is the proof that on a specific date, a specific engine
processed a specific corpus and produced a verified result.

This separation has practical consequences. The engine can be improved without
invalidating existing frozen releases. A corpus can be reprocessed with a newer
engine without touching the source. A frozen release from 2026 remains
independently verifiable in 2036 regardless of what has changed in the engine
or the corpus since.

---

## AN ANALOGY: GIT FOR KNOWLEDGE CORPORA

The architecture of AXIS-NIDDHI has structural parallels with Git. The analogy
is explanatory, not prescriptive — AXIS-NIDDHI is not built on Git and does
not behave like Git. But the conceptual mapping helps orient engineers and
archivists who are already familiar with version control.

```
Git concept          AXIS-NIDDHI equivalent
────────────────────────────────────────────────────────────────────────
Repository           Corpus
                     A bounded, identified body of knowledge with its
                     own source ZIP, metadata, and CSL workspace.

Commit history       Lineage
                     The append-only event log in each CSL entry.
                     Every transformation is a logged, hashed record.
                     The lineage cannot be rewritten.

Blob                 content.html
                     The raw content of a post at a specific version,
                     identified by its SHA-256 hash.

Tree                 CSL structure
                     The directory tree under 09-csl/ that organises
                     all posts and their associated metadata.

Tag                  Frozen release
                     A sealed, named snapshot of the engine + corpus
                     at a specific point in time. Cryptographically
                     sealed by the SHA-256 manifest.

Clone                Deterministic rebuild
                     Running axis pipeline --full on a frozen release
                     produces an identical CSL from the same source ZIP.
                     The rebuild is the clone. The source ZIP is the
                     remote origin.

.gitignore           Credentials exclusion
                     deepl_key.txt and wp_password.txt are never included
                     in frozen releases. They are operator-supplied,
                     analogous to secrets that are excluded from version
                     control.

git gc               CSL freeze (SA02)
                     The freeze manifest step seals the CSL state,
                     analogous to garbage collection stabilising a
                     repository's object store.
```

### Where the analogy holds

Both systems treat the historical record as append-only and authoritative.
Both derive working state from a fixed origin. Both make it possible to
verify the integrity of the current state against a known reference.
Both separate the stored representation (blob/CSL entry) from the rendered
output (working tree / static site).

### Where the analogy breaks

Git is designed for continuous change by multiple contributors. AXIS-NIDDHI
is designed for the deliberate, one-time preservation of a bounded corpus.
Git history can be rewritten (`rebase`, `force push`). AXIS-NIDDHI lineage
cannot — Invariant 3 is absolute. Git repositories are operational
environments. AXIS-NIDDHI frozen releases are archival artifacts; the
archaeology layer is explicitly non-operational.

The analogy is a map, not the territory. It is useful for orientation.
The invariants in the Engine Model are the authoritative description.

---

## CLOSING STATEMENT

AXIS-NIDDHI exists at the intersection of two disciplines that rarely share
vocabulary: software engineering and archival preservation.

From archival preservation it takes the commitment to completeness, provenance,
and permanence. From software engineering it takes the tools to make those
commitments verifiable and reproducible. The SHA-256 manifest is an archivist's
seal expressed in cryptography. The deterministic rebuild is a cataloguing
principle expressed in code.

The system is an answer to a question that archivists have always faced and
that software engineers rarely ask: not *how do we build this*, but *how do
we ensure this can still be read by someone we will never meet, on a day we
cannot predict*.

AXIS-NIDDHI is the engineering answer to that question for the PureDhamma
corpus — and, by design, for any corpus that follows.

---

*AXIS-NIDDHI Positioning V1.0 — locked 2026-03-11.*  
*Companion document to AXIS_NIDDHI_ENGINE_MODEL.md.*  
*The Git analogy in Section 5 is explanatory only — not an implementation direction.*

b)
# AXIS-NIDDHI ENGINE MODEL
**Conceptual Architecture Reference**  
**Version:** 1.1 (simplified diagram added)  
**Date:** 2026-03-11  
**Status:** Locked — authoritative conceptual reference for V5.4 and V6

---

## PREAMBLE

This document describes what AXIS-NIDDHI *is*, not how it is implemented.

Implementation details — script names, file paths, shell commands — belong in
the engineering documents. This document describes the conceptual model that
those details express. It should remain stable across engine versions.

A reader with no knowledge of the codebase should be able to read this document
and understand the purpose, structure, and guarantees of the system.

---

## SYSTEM AT A GLANCE

```
  ┌─────────────┐
  │   ENGINE    │  Scripts, templates, and tooling — corpus-agnostic
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │   ADAPTER   │  Reads the source format → yields normalized post records
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │     CSL     │  Canonical Source Library — the source of truth
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │  PIPELINE   │  Translation · migration · audit · integrity
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │ PUBLICATION │  Static site · WordPress · offline archive
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │   FREEZE    │  SHA-256 manifest · sealed release · operator README
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │ ARCHAEOLOGY │  Immutable · read-only mount · permanent record
  └─────────────┘
```

The detailed description of each layer follows in Section II.

---

## I. PURPOSE

AXIS-NIDDHI is a **corpus preservation engine**.

Its purpose is to take a body of knowledge that exists in a particular
publication system at a particular moment in time, extract it completely and
faithfully, transform it into a durable structured representation, and produce
from that representation a publishable artifact that can be rebuilt identically
at any future point — on any machine, without access to the original
publication infrastructure.

The system is designed to answer one question, permanently:

> *If PureDhamma.net disappears tomorrow, is the corpus preserved in a form
> that can be rebuilt, read, and distributed without depending on anything
> that no longer exists?*

The answer, for every corpus processed by AXIS-NIDDHI, must be: yes.

---

## II. THE ENGINE MODEL

AXIS-NIDDHI is structured in four conceptual layers.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   LAYER 1 — SOURCE                                                       │
│                                                                          │
│   A corpus in its original form.                                         │
│   A WordPress backup. A Ghost export. A directory of Markdown files.    │
│   The system does not require the source to remain available.            │
│   It treats the source as a one-time input, not an ongoing dependency.  │
│                                                                          │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                   ADAPTER — thin translation layer
                   Converts source format → normalized extraction
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   LAYER 2 — CSL (Canonical Source Library)                              │
│                                                                          │
│   The corpus in its canonical structured form.                           │
│   Every post is a directory. Every directory contains a content file    │
│   and an identity record. Every mutation is logged. Every state is      │
│   verifiable by SHA-256. The CSL is the source of truth for everything  │
│   downstream.                                                            │
│                                                                          │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                   PIPELINE — deterministic transformations
                   Translation, migration, audit, freeze
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   LAYER 3 — PUBLICATION                                                  │
│                                                                          │
│   The corpus rendered for distribution.                                  │
│   A static HTML site. A WordPress installation. An offline archive.     │
│   The publication layer is derived from the CSL and can always be       │
│   regenerated from it. It is never the primary record.                  │
│                                                                          │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                   ARCHIVAL FREEZE — cryptographic seal + immutable storage
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   LAYER 4 — ARCHAEOLOGY                                                  │
│                                                                          │
│   Frozen releases stored immutably.                                      │
│   A record of the corpus and the engine at a specific point in time.   │
│   Read-only. Never executed. Verified by manifest. Preserved            │
│   indefinitely.                                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

These four layers are not pipeline stages. They are conceptual zones with
different preservation properties:

| Layer | Mutability | Dependency | Purpose |
|---|---|---|---|
| Source | External, may disappear | One-time input | Origin |
| CSL | Append-only mutations, audit-logged | Self-contained | Truth |
| Publication | Regenerable from CSL | Derived | Distribution |
| Archaeology | Immutable | None | Permanence |

The CSL is the only layer that must be preserved for the corpus to survive.
Everything else can be regenerated from it.

---

## III. THE ADAPTER

The adapter is the translation layer between a source format and the CSL.

Its function is narrow and precisely bounded: given a corpus in its native
format, yield a stream of normalized post records that the engine can write
into the CSL. The adapter knows about the source. It knows nothing about
the CSL, the pipeline, or the publication layer.

```
Source format                    Normalized record
─────────────────────────────────────────────────────────
WordPress MySQL database    →    ExtractedPost
Ghost JSON export           →    ExtractedPost
Markdown directory tree     →    ExtractedPost
Any future format           →    ExtractedPost
```

The adapter contract has one rule: produce faithful representations of the
source content. Nothing is interpreted, summarized, or transformed. The adapter
is a reader, not an editor.

This design means the engine is independent of the source format. A corpus
that begins as a WordPress site can be migrated to a Ghost platform and
re-ingested using a different adapter without changing any downstream process.
The CSL entries are identical. The publication output is identical.

---

## IV. THE CSL — CANONICAL SOURCE LIBRARY

The CSL is the heart of the system.

Every post in a corpus is represented in the CSL as a directory:

```
09-csl/
└── PD.AA.001/
    ├── source/
    │   ├── en-US/
    │   │   └── content.html    ← source language content
    │   └── pt-BR/
    │       └── content.html    ← translated content
    └── meta/
        ├── identity.json       ← canonical post record
        └── lineage.json        ← immutable event log
```

The CSL has four properties that make it the canonical representation:

**1. Completeness.** Every piece of content the corpus contains is represented
in the CSL. Nothing exists only in the source system or only in the publication
layer. The CSL is the complete record.

**2. Immutability of origin.** The source content, once extracted, is never
modified. Translations are stored separately. Transformations are logged.
The original extraction is preserved as received.

**3. Auditability.** Every mutation to a CSL entry is recorded in the lineage
log with a timestamp, the responsible pipeline step, and SHA-256 hashes of
the content before and after. A human can reconstruct the complete history
of any post by reading its lineage.

**4. Verifiability.** Every content file has a SHA-256 hash stored in the
identity record. The current content can be verified against the stored hash
at any time. Any corruption or unauthorized modification is detectable.

### The identity record

The identity record (`identity.json`) is the canonical descriptor of a post.
It contains the post's identifier, its titles in all languages, its artifact
references, and its lineage. It is the single authoritative record for
everything the pipeline knows about that post.

The identity record is written once at extraction and updated through
controlled pipeline mutations. It is never rewritten from scratch after
creation.

### The lineage

The lineage is an append-only event log. Events are never deleted or modified.
The log records: where the content came from, what transformations were applied
to it, what translations were produced, and when the post was published.

The lineage is the audit trail that makes the system's behavior human-readable
long after the pipeline has run.

---

## V. THE DETERMINISTIC REBUILD PHILOSOPHY

The central claim of AXIS-NIDDHI is:

> *Given the same source corpus ZIP, the engine will always produce the
> same CSL, the same translated content, and the same static site.*

This is determinism. It is not a performance target. It is a preservation
guarantee.

Determinism is achieved through three practices:

**1. Source integrity.** The source is a sealed ZIP archive. It does not
change. Every rebuild reads from the same bytes. The engine does not depend on
a live source system.

**2. Controlled mutations.** Every transformation applied to the CSL is
explicit, logged, and reproducible. The pipeline does not make inferences or
assumptions. It applies defined transformations to defined inputs and produces
defined outputs.

**3. Sealed releases.** A frozen release contains everything needed to rebuild
the corpus from the ZIP: the engine scripts, the control metadata, and the
source ZIP itself. The SHA-256 manifest seals the release state. A future
operator can verify that the release they received is identical to the one
that was sealed.

### What determinism means in practice

A corpus preserved with AXIS-NIDDHI can be rebuilt:

- Ten years from now, on different hardware
- After the original publication domain has expired
- By an operator who was not involved in the original preservation
- Without access to any cloud service, API, or live system
- Using only the frozen release and standard open-source tools

This is the operational meaning of determinism. It is not a technical property.
It is a commitment to the people who will need this corpus in the future.

---

## VI. THE ARCHIVAL FREEZE MODEL

A frozen release is a cryptographically sealed snapshot of the engine in a
state sufficient to rebuild the corpus from source.

### What a frozen release contains

```
/frozen-release/
├── axis                      CLI entry point
├── README.md                 Operator onboarding
├── release-manifest.sha256   SHA-256 of every file (relative paths)
├── release-sealed-at.txt     Engine version, corpus, seal timestamp
├── sources/
│   └── corpus.zip            The original corpus ZIP (sealed)
└── pipeline/
    ├── scripts/              Engine scripts
    ├── 13-ssg/               Static site generator (full subtree)
    └── metadata/             Control files (post index, glossary, sections)
```

### What a frozen release does NOT contain

- Generated content (`09-csl/`, `13-static-site/`) — rebuilt from the ZIP
- Credentials (`deepl_key.txt`, `wp_password.txt`) — supplied by the operator
- Operator-specific paths — all paths derived from the release root

### The manifest

The release manifest (`release-manifest.sha256`) contains a SHA-256 hash of
every file in the release, expressed as relative paths. Relative paths make
the manifest location-independent: the release can be copied to any directory,
any machine, or any storage medium, and the manifest remains valid.

```bash
cd /path/to/any-copy-of-the-release
sha256sum --check release-manifest.sha256
# All files: OK
```

This verification works whether the release is on the original machine, in an
archaeology archive, or on a USB drive handed to a future operator.

### The archaeology layer

The archaeology layer is permanent, immutable storage for frozen releases and
historical artifacts. It is mounted read-only with `noexec` to prevent both
accidental writes and accidental execution.

The archaeology layer is not a backup. It is a historical record. The
distinction matters: a backup is expected to be restored and run. An
archaeology entry is expected to be read and referenced. Nothing in archaeology
is ever executed. Its purpose is to make the past recoverable, not operational.

```
/mnt/archaeology/
├── frozen-releases/          Sealed engine + corpus snapshots
├── corpus-raw/               Original source ZIPs before processing
├── engine-history/           Engine versions at each major release
└── pipeline-experiments/     Approaches considered and superseded
```

The archaeology layer grows in one direction only.

---

## VII. THE SEPARATION OF ENGINE, CORPUS, AND RELEASE

Three things that must never be conflated:

**The engine** is the set of scripts, templates, and tools that process a
corpus. It is independent of any particular corpus. It knows about corpus
structure — how to extract, preprocess, translate, and publish — but not
about corpus content: which posts exist, what they say, what language they
were written in.

**The corpus** is the content and its metadata. It includes the source ZIP,
the post index, the glossary, the section structure, and the CSL entries
produced from them. A corpus has an identity (`corpus_id`) that is separate
from the engine version that processed it.

**The frozen release** is a specific combination of engine + corpus source at
a specific point in time, sealed into a self-contained, independently
verifiable artifact. A frozen release is neither the engine nor the corpus —
it is the engine in a state configured to rebuild a specific corpus.

```
Engine (V5.4)  +  Corpus source (PureDhamma 2026-02)
        └─────────────────────────┘
                    │
                    ▼
          Frozen release
          2026-03-11_v5.4
          (sealed, immutable)
```

This separation means:

- The engine can be updated without invalidating existing frozen releases
- A corpus can be reprocessed with a newer engine without modifying the source
- A frozen release remains verifiable even after both the engine and the corpus
  source have been superseded

### The three-layer physical model

```
/mnt/archaeology/    ← permanent, immutable, read-only
                          historical record; never executed
                          ↑
                          ↑  freeze procedure (cp + seal)
                          ↑
/beng-release/       ← portable, self-contained, reproducible
                          current operational release
                          built from the Lab by the release builder
                          ↑
                          ↑  build_release_snapshot.sh (cp only, never mv/patch)
                          ↑
/beng-fut/           ← mutable, development
                          active scripts, working CSL, live SSG output
                          the Lab — origin of all releases
```

Data flows in one direction: Lab → Release → Archaeology.
No layer ever writes to a layer above it in this diagram.

---

## VIII. THE TRANSLATION LAYER

Translation is a first-class concern of the preservation model, not an
optional feature.

A teaching expressed only in its source language is accessible only to readers
of that language. Preservation of meaning requires preservation across
languages. AXIS-NIDDHI treats translated content as a first-class artifact with
the same integrity guarantees as the source: SHA-256 hashing, lineage logging,
and CSL storage.

The translation workflow is the one deliberate manual gate in the pipeline.
An operator reviews the translation control index and marks posts for
translation. The engine then calls the translation API and stores the result.
The manual gate is intentional: translation quality affects the meaning of the
teaching, and no automated system should translate religious content without
human review of at least the control parameters.

The translated CSL entry carries the same identity record as the source. It
records the translation engine used, the character count, the glossary applied,
and the SHA-256 hashes of the source and result. Every translation decision
is auditable.

---

## IX. DESIGN INVARIANTS

These invariants, if violated, would compromise the preservation guarantees
of the system. They are binding across all versions.

```
INVARIANT 1 — SOURCE IMMUTABILITY
  The source ZIP is never modified after acquisition.
  The extracted source content is read-only after extraction.
  It is the Treasure. It is never edited manually.

INVARIANT 2 — CSL PRIMACY
  The CSL is the source of truth for all downstream processes.
  The publication layer is derived from the CSL.
  If the CSL and the publication layer disagree, the CSL is correct.

INVARIANT 3 — LINEAGE APPEND-ONLY
  Lineage entries are never deleted or modified.
  A pipeline step may add entries. It may never remove or alter existing ones.

INVARIANT 4 — DETERMINISTIC REBUILD
  Given the same source ZIP and the same engine version, the full pipeline
  must produce the same CSL content, modulo timestamps and run-specific IDs.
  Any non-determinism is a defect.

INVARIANT 5 — RELEASE SELF-CONTAINMENT
  A frozen release must be independently operable.
  It must not depend on the Lab, the archaeology mount, any cloud service,
  or any system state not included in the release itself (except credentials,
  which are operator-supplied by design).

INVARIANT 6 — ARCHAEOLOGY IMMUTABILITY
  /mnt/archaeology is mounted read-only at all times (ro,noexec).
  No automated tooling writes to it.
  Human read access is the only permitted operation.
  The physical mount enforces this invariant.

INVARIANT 7 — ENGINE / CORPUS SEPARATION
  Engine scripts carry no corpus-specific content.
  Corpus identity is described by corpus.json and injected via the
  AXIS_CORPUS environment variable.
  An engine script that embeds corpus-specific constants carries
  technical debt, not a design feature.

INVARIANT 8 — MANIFEST PORTABILITY
  The SHA-256 release manifest uses relative paths.
  It must remain valid regardless of where the release is stored.
  An absolute-path manifest is a preservation defect.
```

---

## X. WHAT AXIS-NIDDHI IS NOT

Understanding what the system does not do clarifies what it is.

**It is not a CMS.** The system does not manage content in the sense of
providing an interface for creating or editing posts. It manages the
preservation and transformation of content that already exists.

**It is not a static site generator.** The SSG component produces a static
site, but the static site is one output of the system, not its purpose. The
purpose is preservation. The static site is a distribution artifact.

**It is not a backup system.** A backup is designed to restore a system to
its previous operational state. AXIS-NIDDHI is designed to preserve content
independent of the system that produced it. A backup depends on the original
system architecture remaining valid. A preservation system does not.

**It is not a content pipeline in the software engineering sense.** It does
not process a stream of incoming content. It processes a corpus — a bounded,
complete body of knowledge — once, with care, and produces a permanent record.

**It is not cloud-dependent.** Every component runs locally. No step requires
a live service except the translation API, which is a deliberate manual gate.
The offline-first architecture is a preservation requirement: cloud services
have terms of service, pricing, and lifetimes. The teachings do not.

---

## XI. THE PRESERVATION COMMITMENT

The system exists because the teachings it preserves have value that outlasts
any particular publication infrastructure.

The technical architecture — deterministic builds, SHA-256 integrity,
append-only lineage, immutable archaeology — is in service of a human
commitment: that these teachings will be available to future readers
regardless of what happens to the systems and institutions that currently
host them.

Every design decision in AXIS-NIDDHI traces back to this commitment.
Determinism exists so a future operator can trust the rebuild.
The manifest exists so a future operator can verify the release.
The archaeology layer exists so no version is ever truly lost.
The adapter interface exists so the engine can serve corpora that do not yet
exist, in formats that have not yet been designed.

The system is an act of long-term care expressed in engineering.

---

*AXIS-NIDDHI Engine Model V1.1 — locked 2026-03-11.*  
*This document describes the conceptual architecture.*  
*Implementation details are in the engineering documents.*  
*The invariants in Section IX are binding across all versions.*

c)
# AXIS-NIDDHI V6 — ARCHITECTURAL OUTLINE
**Multi-Corpus Preservation Engine**  
**Status:** Design document — pre-implementation  
**Baseline:** V5.4 (frozen 2026-03-11, single-corpus, stable)  
**Author:** Vayo (Technical Architect)  
**Date:** 2026-03-11

---

## DESIGN PRINCIPLES

V6 introduces zero breaking changes to V5.4.  
Every change is additive or a controlled substitution in exactly three files.  
The CSL, the SSG, and all SP/SA/SD scripts remain untouched.  
A V5.4 operator who does not activate multi-corpus features notices nothing different.

---

## SECTION 1 — CORPUS COUPLING AUDIT (V5.4 baseline)

Before designing V6, the exact coupling points in the live codebase must be named.
The following is derived from code inspection, not documentation.

```
COUPLING MAP — files that know the corpus identity

FILE                    COUPLING                            HOW COUPLED
────────────────────────────────────────────────────────────────────────────────
config.py               DB_CONFIG['database'] = 'beng_wp_21'   hardcoded
                        WP_BASE_URL = '.../beng_feb2026'        hardcoded
                        WP_ADMIN_USER = 'axis_niddhi'           hardcoded
                        PDPN_CSV = metadata/PDPN_01_...csv      hardcoded name
                        SOURCE_LANG = (derived, ok)             env-aware
                        SCHEMA_VERSION = (derived, ok)          constant

SG00_reset_workspace.sh DB_NAME = 'beng_wp_21'                  hardcoded
                        WP_ALIAS = 'beng_feb2026'               hardcoded
                        ZIP detection: find *.zip | head -1     first-found

SG01_extract_html.py    row["id_10WEB.io"]                      column name
                        row["Fin-dex"]                          column name
                        row["PD#PN"]                            column name
                        row["Slug_Derived"]                     column name
                        filename = f"{findex}__{pdpn}__{slug}"  naming scheme

────────────────────────────────────────────────────────────────────────────────
ALL OTHER SCRIPTS       Zero corpus coupling                    operate on CSL
                        SG02, SG03, SG04, all SP, SA, SD        corpus-agnostic
────────────────────────────────────────────────────────────────────────────────
```

**Key finding:** the corpus coupling is contained in exactly 3 files.  
SG01's column-name coupling is the most fragile because it is inline in the
extraction loop — 4 hardcoded string literals that would silently produce empty
output for any corpus with different column headers.

---

## SECTION 2 — CORPUS.JSON SCHEMA PROPOSAL

Every corpus is described by a single `corpus.json` file.  
The pipeline reads this file at startup instead of hardcoded constants.

### Full schema with annotations

```json
{
  "$schema": "https://axis-niddhi.local/corpus-schema/v1.0.json",
  "$comment": "Corpus descriptor for AXIS-NIDDHI V6. One file per corpus.",

  "corpus_id":   "puredhamma",
  "corpus_name": "Pure Dhamma",
  "corpus_version": "2026-02",
  "description": "Teachings originally published at PureDhamma.net",
  "archived_at": "2026-03-11",

  "source": {
    "type": "wordpress_zip",
    "zip_filename": "corpus-puredhamma.zip",
    "$comment_type": "One of: wordpress_zip | ghost_export | markdown_tree"
  },

  "database": {
    "name":     "corpus_puredhamma",
    "user":     "wp_user",
    "password": "wp_pass123",
    "$comment": "Credentials may also be supplied via env vars (preferred)."
  },

  "wordpress": {
    "alias":      "puredhamma_local",
    "admin_user": "axis_niddhi"
  },

  "languages": {
    "source": "en",
    "targets": ["pt"]
  },

  "post_index": {
    "filename":   "PDPN_01_Operational.csv",
    "delimiter":  ";",
    "encoding":   "utf-8",
    "columns": {
      "fin_dex":  "Fin-dex",
      "post_id":  "id_10WEB.io",
      "pdpn":     "PD#PN",
      "slug":     "Slug_Derived"
    },
    "$comment_columns": "Maps canonical field names to actual CSV column headers."
  },

  "identifier": {
    "pattern":    "{fin_dex}__{pdpn}__{slug}",
    "pdpn_regex": "^[A-Z]{2}\\.[A-Z]{2}\\.[0-9]{3}$",
    "$comment":   "Pattern for canonical filename. pdpn_regex validates entries."
  },

  "sections_file":  "MasterPDPN_Sections.csv",
  "glossary_file":  "Glossario_v5.csv",
  "menu_file":      "Translation_Control_Center.csv",

  "corpus_class":   "dhamma",
  "$comment_class": "Optional. Classifies the corpus by knowledge domain.
                     Known values: dhamma | philosophy | historical | literary | other.
                     Not used by the engine. Available for cataloguing, UI filtering,
                     and future multi-corpus index generation. V5.4 compatible: if absent,
                     defaults to null and the engine proceeds without it."
}
```

### Minimal required fields for a new corpus

```json
{
  "corpus_id":    "waharaka",
  "corpus_name":  "Waharaka Thero Teachings",
  "corpus_class": "dhamma",
  "source": { "type": "wordpress_zip", "zip_filename": "corpus-waharaka.zip" },
  "database": { "name": "corpus_waharaka" },
  "wordpress": { "alias": "waharaka_local" },
  "languages": { "source": "si", "targets": ["en"] },
  "post_index": {
    "filename": "WaharakaIndex.csv",
    "delimiter": ",",
    "columns": {
      "fin_dex": "Index",
      "post_id": "WP_ID",
      "pdpn":    "PostCode",
      "slug":    "Slug"
    }
  }
}
```

`corpus_class` is optional in both the full and minimal schemas. The engine
reads it only for logging and identification purposes. It has no effect on
pipeline execution. Omitting it does not cause any warning or fallback —
the field is classified as advisory metadata, not operational configuration.

Known values at V6 design time: `dhamma`, `philosophy`, `historical`,
`literary`, `other`. The list is not enforced by the schema — any string
is accepted. Standardisation of values is an operator convention, not an
engine constraint.

A corpus with only these fields can run the full SG phase without any
modification to the pipeline scripts.

---

## SECTION 3 — REQUIRED CHANGES TO CONFIG.PY

### What changes

`config.py` currently hardcodes corpus identity in the body of the file.  
In V6, it reads from a `corpus.json` descriptor and derives all corpus-specific
constants from that descriptor.

### What does NOT change

- `BASE_DIR` derivation from `BENG_BASE` env or `__file__` — unchanged
- `SCRIPTS_DIR`, `METADATA_DIR`, `LOG_DIR` — unchanged
- All `DIR_0N_*` path constants — unchanged
- `DIR_13_SSG_ENGINE`, `DIR_13_SSG_OUTPUT` — unchanged
- All credential functions (`get_deepl_key`, `get_wp_password`) — unchanged
- `SCHEMA_VERSION`, `SOURCE_LANG` — unchanged (SOURCE_LANG now from descriptor)

### Proposed config.py V6 diff (additive changes only)

```python
# ==============================================================================
# V6 ADDITION — corpus descriptor loader
# Place this block AFTER BASE_DIR/SCRIPTS_DIR declarations,
# BEFORE DB_CONFIG and WP_BASE_URL.
# ==============================================================================

import json as _json

# Active corpus is selected via env var AXIS_CORPUS (default: puredhamma)
# This allows: AXIS_CORPUS=waharaka axis pipeline --full
_CORPUS_ID    = os.environ.get("AXIS_CORPUS", "puredhamma")
_CORPUS_DIR   = BASE_DIR.parent / "corpora" / _CORPUS_ID
_CORPUS_JSON  = _CORPUS_DIR / "corpus.json"

# Graceful degradation: if corpus.json not found, fall back to V5.4 hardcoded values.
# This makes V6 config.py backward-compatible with V5.4 deployments.
_CORPUS = {}
if _CORPUS_JSON.exists():
    try:
        _CORPUS = _json.loads(_CORPUS_JSON.read_text(encoding="utf-8"))
    except Exception as _e:
        print(f"⚠️  corpus.json load failed ({_e}) — using V5.4 hardcoded defaults")

def _corpus_get(path: str, default):
    """Safely read a dotted path from _CORPUS dict. E.g. 'database.name'"""
    keys = path.split(".")
    node = _CORPUS
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            return default
        node = node[k]
    return node

# ==============================================================================
# CORPUS-DERIVED CONSTANTS (replace V5.4 hardcoded values)
# ==============================================================================

# V5.4:  DB_CONFIG = {"database": "beng_wp_21", ...}
# V6:    reads from corpus.json, falls back to V5.4 value if not present
DB_CONFIG = {
    "host":     "localhost",
    "user":     _corpus_get("database.user",     "wp_user"),
    "password": _corpus_get("database.password", "wp_pass123"),
    "database": _corpus_get("database.name",     "beng_wp_21"),
}

# V5.4:  WP_BASE_URL = "http://localhost/beng_feb2026"
# V6:    derived from corpus.json wordpress.alias
_WP_ALIAS   = _corpus_get("wordpress.alias", "beng_feb2026")
WP_BASE_URL = f"http://localhost/{_WP_ALIAS}"
WP_API_URL  = f"{WP_BASE_URL}/wp-json/wp/v2"
WP_API_POSTS = f"{WP_API_URL}/posts"
WP_API_PAGES = f"{WP_API_URL}/pages"
WP_ADMIN_USER = _corpus_get("wordpress.admin_user", "axis_niddhi")

# V5.4:  PDPN_CSV = METADATA_DIR / "PDPN_01_Operational.csv"
# V6:    filename from corpus.json post_index.filename
_INDEX_FILENAME = _corpus_get("post_index.filename", "PDPN_01_Operational.csv")
PDPN_CSV = METADATA_DIR / _INDEX_FILENAME

# V5.4:  SOURCE_LANG = "en" (was already env-aware)
# V6:    from corpus.json languages.source (same fallback)
SOURCE_LANG = os.environ.get(
    "BENG_SOURCE_LANG",
    _corpus_get("languages.source", "en")
)

# NEW in V6: column mapping (accessed by SG01)
# Scripts read this dict instead of hardcoding column names
CORPUS_COLUMNS = {
    "fin_dex": _corpus_get("post_index.columns.fin_dex", "Fin-dex"),
    "post_id": _corpus_get("post_index.columns.post_id", "id_10WEB.io"),
    "pdpn":    _corpus_get("post_index.columns.pdpn",    "PD#PN"),
    "slug":    _corpus_get("post_index.columns.slug",    "Slug_Derived"),
}

# NEW in V6: corpus identity (used in logs, tattoos, CLS entries)
CORPUS_ID   = _corpus_get("corpus_id",   "puredhamma")
CORPUS_NAME = _corpus_get("corpus_name", "Pure Dhamma")
```

### V6 config.py backward-compatibility guarantee

```
If corpus.json does NOT exist → _CORPUS = {} → all _corpus_get() return defaults
→ DB_CONFIG, WP_BASE_URL, PDPN_CSV, SOURCE_LANG are identical to V5.4 values
→ A V5.4 deployment with no corpus.json runs identically to V5.4
→ Zero breaking change
```

---

## SECTION 4 — IMPACT ON SG00 (reset_workspace.sh)

### Current coupling (3 hardcoded lines)

```bash
DB_NAME="beng_wp_21"
WP_ALIAS="beng_feb2026"
ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" | head -1)  # first-found only
```

### V6 change: read from corpus.json via shell helper

```bash
# ── V6 ADDITION — read corpus descriptor ─────────────────────────────────
CORPUS_ID="${AXIS_CORPUS:-puredhamma}"
CORPUS_DIR="$BENG_ROOT/corpora/$CORPUS_ID"
CORPUS_JSON="$CORPUS_DIR/corpus.json"

# Shell JSON reader (no jq dependency — pure bash + python3)
corpus_get() {
    # corpus_get <dotted.path> <default>
    local path="$1" default="$2"
    python3 -c "
import json, sys
try:
    data = json.load(open('$CORPUS_JSON'))
    keys = '$path'.split('.')
    node = data
    for k in keys:
        node = node[k]
    print(node)
except:
    print('$default')
" 2>/dev/null || echo "$default"
}

# Fallback to V5.4 values if corpus.json absent
if [[ -f "$CORPUS_JSON" ]]; then
    DB_NAME="${BENG_DB_NAME:-$(corpus_get database.name beng_wp_21)}"
    WP_ALIAS="${BENG_WP_ALIAS:-$(corpus_get wordpress.alias beng_feb2026)}"
    ZIP_FILENAME="$(corpus_get source.zip_filename '')"
    [[ -n "$ZIP_FILENAME" ]] \
        && ZIP_FILE="$CORPUS_DIR/sources/$ZIP_FILENAME" \
        || ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" | head -1)
else
    # V5.4 compatible fallback
    DB_NAME="${BENG_DB_NAME:-beng_wp_21}"
    WP_ALIAS="${BENG_WP_ALIAS:-beng_feb2026}"
    ZIP_FILE=$(find "$SOURCES_DIR" -maxdepth 1 -name "*.zip" | head -1)
fi
# ─────────────────────────────────────────────────────────────────────────
```

All other logic in SG00 is unchanged. The reset procedure, WP setup,
exorcism, and DB restore operate identically — they simply use corpus-derived
variable values instead of hardcoded ones.

**Change footprint:** replace 3 lines, add ~25 lines of boilerplate. Zero
functional change for the PureDhamma corpus.

---

## SECTION 5 — IMPACT ON SG01 (extract_html.py)

### Current coupling (4 inline column literals)

```python
wp_id  = int(row["id_10WEB.io"])   # ← corpus-specific column name
findex = str(row["Fin-dex"]).zfill(4)
pdpn   = str(row["PD#PN"]).strip()
slug   = clean_slug(str(row.get("Slug_Derived", "")))
```

### V6 change: read column names from CORPUS_COLUMNS

```python
# V6 addition — import CORPUS_COLUMNS from config
from config import (
    BASE_DIR, LOG_DIR, DIR_01_EXTRACTED, DIR_09_CSL,
    PDPN_CSV, DB_CONFIG, SOURCE_LANG,
    CORPUS_COLUMNS,   # ← V6 addition only
    CORPUS_ID,        # ← V6 addition only (for tattoo)
)

# V6 extraction loop — replace 4 hardcoded column references:
#   BEFORE: row["id_10WEB.io"], row["Fin-dex"], row["PD#PN"], row["Slug_Derived"]
#   AFTER:  row[CORPUS_COLUMNS["post_id"]], etc.

for _, row in df.iterrows():
    wp_id  = int(row[CORPUS_COLUMNS["post_id"]])
    findex = str(row[CORPUS_COLUMNS["fin_dex"]]).zfill(4)
    pdpn   = str(row[CORPUS_COLUMNS["pdpn"]]).strip()
    slug   = clean_slug(str(row.get(CORPUS_COLUMNS["slug"], "")))
    # ... rest of loop unchanged
```

The tattoo generator also becomes corpus-aware:

```python
def generate_tattoo(row: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!--
💎 AXIS-NIDDHI — CANONICAL SOURCE ARTIFACT
===================================================
Corpus:       {CORPUS_ID}
Fin-dex:      {row[CORPUS_COLUMNS['fin_dex']]}
PD#PN:        {row[CORPUS_COLUMNS['pdpn']]}
Original-Slug:{row[CORPUS_COLUMNS['slug']]}
Source-ID:    {row[CORPUS_COLUMNS['post_id']]}
Language:     {SOURCE_LANG}
Extracted-At: {now}
Origin:       MySQL / {DB_CONFIG['database']}
===================================================
DO NOT EDIT THIS FILE MANUALLY. THIS IS THE TREASURE.
-->
"""
```

**Change footprint:** 4 line substitutions in the extraction loop, 2 additional
imports. Zero change to extraction logic, retry, CLS integration, or logging.

---

## SECTION 6 — MINIMAL ADAPTER INTERFACE

Adapters normalize different source formats into the existing pipeline intake
point: a directory of `.html` files at `01-extracted-htmls/{source_lang}/`
with the canonical tattoo header and filename pattern.

### Interface contract

Every adapter must implement one function:

```python
# adapters/base_adapter.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator
from dataclasses import dataclass

@dataclass
class ExtractedPost:
    """
    Normalized post as produced by any adapter.
    Adapters convert their native format to this structure.
    The SG01 loop writes this to disk.
    """
    fin_dex:  str    # zero-padded 4-digit index ("0001")
    pdpn:     str    # canonical identifier ("PD.AA.001")
    slug:     str    # sanitized slug ("meditation-and-mind")
    content:  str    # raw HTML content (no wrapper tags)
    source_id: str   # original ID in source system

class BaseAdapter(ABC):
    """
    Minimal interface all adapters must implement.
    Adapters are thin: they only parse the source and yield ExtractedPost.
    They do NOT write to disk. SG01 owns the write.
    """

    def __init__(self, corpus_descriptor: dict, source_path: Path):
        self.descriptor  = corpus_descriptor
        self.source_path = source_path
        self.columns     = corpus_descriptor.get("post_index", {}).get("columns", {})

    @abstractmethod
    def extract(self) -> Iterator[ExtractedPost]:
        """
        Yield one ExtractedPost per content item in the source.
        Must be lazy (generator) for large corpora.
        """
        ...

    @property
    def source_type(self) -> str:
        return self.descriptor.get("source", {}).get("type", "unknown")
```

### Adapter implementations

**Adapter A — wordpress_zip (existing corpus, V5.4 compatible)**

```python
# adapters/wordpress_zip.py

class WordPressZipAdapter(BaseAdapter):
    """
    Adapter for WordPress backup ZIPs.
    This is the existing SG00+SG01 behaviour, extracted into the adapter interface.
    Reads from MySQL (populated by SG00) via the post_index CSV.
    V5.4 pipeline = this adapter with corpus_descriptor = {"columns": {...V5.4 defaults...}}
    """

    def extract(self) -> Iterator[ExtractedPost]:
        import pandas as pd
        import pymysql

        col  = self.columns
        csv  = self.source_path / self.descriptor["post_index"]["filename"]
        sep  = self.descriptor.get("post_index", {}).get("delimiter", ";")
        db   = self.descriptor.get("database", {})

        df = pd.read_csv(csv, sep=sep, encoding="utf-8", dtype=str)
        df = df[df[col["post_id"]].notna()]

        conn = pymysql.connect(
            host="localhost",
            user=db.get("user", "wp_user"),
            password=db.get("password", "wp_pass123"),
            database=db.get("name"),
            cursorclass=pymysql.cursors.DictCursor
        )
        # ... table detection and extraction loop (same as SG01) ...
        # yields ExtractedPost for each row
        conn.close()
```

**Adapter B — ghost_export (future)**

```python
# adapters/ghost_export.py

class GhostExportAdapter(BaseAdapter):
    """
    Adapter for Ghost CMS JSON export files.
    Ghost exports contain posts as JSON with HTML content.
    No MySQL dependency — reads directly from the export JSON.
    """

    def extract(self) -> Iterator[ExtractedPost]:
        import json
        export = json.loads((self.source_path / "ghost-export.json").read_text())
        posts  = export.get("data", {}).get("posts", [])
        for i, post in enumerate(posts):
            yield ExtractedPost(
                fin_dex   = str(i + 1).zfill(4),
                pdpn      = post.get("slug", f"GH.XX.{i:03d}"),
                slug      = post.get("slug", "unknown"),
                content   = post.get("html", ""),
                source_id = str(post.get("id", ""))
            )
```

**Adapter C — markdown_tree (future)**

```python
# adapters/markdown_tree.py

class MarkdownTreeAdapter(BaseAdapter):
    """
    Adapter for a directory tree of Markdown files.
    No external system dependency — reads .md files directly.
    Converts Markdown → HTML using python-markdown.
    """

    def extract(self) -> Iterator[ExtractedPost]:
        import markdown
        md_files = sorted(self.source_path.glob("**/*.md"))
        for i, md_file in enumerate(md_files):
            html = markdown.markdown(md_file.read_text(encoding="utf-8"))
            yield ExtractedPost(
                fin_dex   = str(i + 1).zfill(4),
                pdpn      = md_file.stem,
                slug      = md_file.stem,
                content   = html,
                source_id = str(md_file)
            )
```

### Adapter registry

```python
# adapters/__init__.py

from .wordpress_zip import WordPressZipAdapter
from .ghost_export  import GhostExportAdapter
from .markdown_tree import MarkdownTreeAdapter

ADAPTERS = {
    "wordpress_zip":  WordPressZipAdapter,
    "ghost_export":   GhostExportAdapter,
    "markdown_tree":  MarkdownTreeAdapter,
}

def get_adapter(corpus_descriptor: dict, source_path) -> BaseAdapter:
    source_type = corpus_descriptor.get("source", {}).get("type", "wordpress_zip")
    cls = ADAPTERS.get(source_type)
    if cls is None:
        raise ValueError(f"Unknown source type: {source_type}. Known: {list(ADAPTERS)}")
    return cls(corpus_descriptor, source_path)
```

The critical design property: `SG01_extract_html.py` only needs to change its
extraction loop to call `adapter.extract()` instead of inline MySQL queries.
The rest of SG01 — tattoo generation, CLS integration, idempotency checks,
logging — is unchanged.

---

## SECTION 7 — CSL AS CANONICAL INTERMEDIATE MODEL

### Formal declaration

The CSL (Canonical Source Library) is the corpus-agnostic intermediate
representation of any corpus processed by AXIS-NIDDHI.

```
[ANY SOURCE FORMAT]
       │
       ▼  adapter.extract() → ExtractedPost
[01-extracted-htmls/{lang}/]
       │
       ▼  SG02_preprocess_html.py (unchanged)
[02-preprocessed/{lang}/]
       │
       ▼  SG03_build_csl.py (unchanged)
[09-csl/{PDPN}/]              ← CSL entry point
       │                         identity.json + content.html per language
       │
       ├──▶  SP phase (translation, migration)   — corpus-agnostic ✔
       ├──▶  SA phase (audit, freeze manifest)   — corpus-agnostic ✔
       └──▶  SD phase (SSG, static site, WP)     — corpus-agnostic ✔
```

Everything downstream of `09-csl/` is already V6-ready.  
The adapters are the only new layer. Everything else is unchanged.

### CSL identity.json remains the canonical post record

The `identity.json` schema (V3.1) already supports multi-corpus operation:

```json
{
  "pdpn": "PD.AA.001",
  "schema_version": "3.1",
  "titles": { "en": "...", "pt": "..." },
  "artifacts": {
    "en-US": { "status": "canonical", "integrity_sha256": "..." },
    "pt-BR": { "status": "derived",   "integrity_sha256": "..." }
  },
  "lineage": {
    "origin": {
      "corpus_id": "puredhamma",   ← V6 addition: one field in lineage.origin
      ...
    }
  }
}
```

V6 adds exactly one field to `lineage.origin`: `corpus_id`. This is written
by the adapter at extraction time and carried through the entire pipeline.
No schema migration required for existing V5.4 CSL entries — the field is
optional and defaults to `"puredhamma"` if absent.

---

## SECTION 8 — FILESYSTEM LAYOUT (V6)

```
/beng-engine/              ← engine (V6 rename of /beng-fut/pipeline)
├── scripts/               ← 28 CORE scripts (unchanged)
├── 13-ssg/                ← SSG engine (unchanged)
├── metadata/              ← engine-level metadata
└── logs/

/beng-corpora/             ← V6 addition: one directory per corpus
├── puredhamma/
│   ├── corpus.json        ← descriptor
│   ├── sources/
│   │   └── corpus-puredhamma.zip
│   ├── metadata/
│   │   ├── PDPN_01_Operational.csv
│   │   ├── MasterPDPN_Sections.csv
│   │   └── Glossario_v5.csv
│   ├── 01-extracted-htmls/
│   ├── 02-preprocessed/
│   ├── 09-csl/            ← corpus-specific CSL
│   ├── 13-static-site/    ← corpus-specific output
│   └── logs/
├── waharaka/
│   ├── corpus.json
│   ├── sources/
│   │   └── corpus-waharaka.zip
│   └── ...
└── other-teachings/
    └── ...
```

`BENG_BASE` in V6 would point to the corpus workspace, not the engine:

```bash
# V5.4 pattern (single corpus)
export BENG_BASE="/beng-fut/pipeline"

# V6 pattern (per corpus)
export BENG_BASE="/beng-corpora/puredhamma"
export AXIS_CORPUS="puredhamma"

# Or using the axis CLI
AXIS_CORPUS=waharaka axis pipeline --full
```

The engine (`scripts/`, `13-ssg/`) is shared. The workspace (`09-csl/`,
`01-extracted-htmls/`, etc.) is per-corpus.

---

## SECTION 9 — CLI EXTENSION (V6)

```bash
# Current V5.4 commands (unchanged)
axis build-site
axis preview
axis status
axis doctor
axis pipeline [--full | --genesis | --preservation | ...]
axis build-release

# V6 additions
axis corpus list                   # list all corpora in /beng-corpora/
axis corpus build <name>           # AXIS_CORPUS=<name> axis pipeline --full
axis corpus verify <name>          # run verify_pipeline_integrity against corpus
axis corpus status <name>          # CSL count, translation progress, last build
axis corpus release <name>         # build_release_snapshot for named corpus
```

Implementation: `axis corpus` is a dispatcher. Each subcommand sets
`AXIS_CORPUS=<name>` and `BENG_BASE=/beng-corpora/<name>`, then delegates
to the existing pipeline infrastructure. No pipeline script changes required.

---

## SECTION 10 — MIGRATION PATH FROM V5.4

### Phase 1 — V5.4 (current, frozen)
Single corpus. Hardcoded constants. Fully operational.
No changes required. No action needed.

### Phase 2 — V6.0: Descriptor layer (non-breaking)

**Step 1:** Create `corpus.json` for PureDhamma corpus.

```bash
mkdir -p /beng-corpora/puredhamma
cat > /beng-corpora/puredhamma/corpus.json << 'EOF'
{
  "corpus_id": "puredhamma",
  "corpus_name": "Pure Dhamma",
  "source": { "type": "wordpress_zip", "zip_filename": "corpus-puredhamma.zip" },
  "database": { "name": "beng_wp_21", "user": "wp_user", "password": "wp_pass123" },
  "wordpress": { "alias": "beng_feb2026", "admin_user": "axis_niddhi" },
  "languages": { "source": "en", "targets": ["pt"] },
  "post_index": {
    "filename": "PDPN_01_Operational.csv",
    "delimiter": ";",
    "columns": {
      "fin_dex": "Fin-dex",
      "post_id": "id_10WEB.io",
      "pdpn":    "PD#PN",
      "slug":    "Slug_Derived"
    }
  }
}
EOF
```

**Step 2:** Apply V6 patch to `config.py` (additive block, 45 lines).  
Backward-compatible: V5.4 deployments without `corpus.json` are unaffected.

**Step 3:** Apply V6 patch to `SG00_reset_workspace.sh` (replace 3 lines, add 25).  
Same behavior for PureDhamma. New corpora read their values from descriptor.

**Step 4:** Apply V6 patch to `SG01_extract_html.py` (4 line substitutions in loop).  
Column names now read from `CORPUS_COLUMNS` dict instead of string literals.

**Step 5:** Create `adapters/` directory with `base_adapter.py` and `wordpress_zip.py`.  
SG01 delegates extraction to adapter. All other logic unchanged.

**Step 6:** Run full rebuild verification.

```bash
AXIS_CORPUS=puredhamma axis pipeline --full
# Expected: identical output to V5.4 — same 748 posts, same CSL, same site
```

**Step 7:** Freeze V6.0 release with the same procedure as V5.4.

### Phase 3 — V6.1+: Second corpus onboarding

Once V6.0 is verified against PureDhamma:

```bash
# Create corpus descriptor for new corpus
mkdir -p /beng-corpora/waharaka
# ... write corpus.json ...

# Run genesis for new corpus
AXIS_CORPUS=waharaka axis pipeline --genesis

# Verify CSL
axis corpus verify waharaka
```

No engine changes required. The adapter handles source-format differences.
All SP, SA, SD scripts operate on the new corpus's `09-csl/` identically.

---

## SECTION 11 — CHANGE FOOTPRINT SUMMARY

```
FILE                        V6 CHANGE                    RISK
────────────────────────────────────────────────────────────────────────
config.py                   +45 lines (additive block)   LOW
                            Existing lines unchanged      Backward-compatible
                            via _corpus_get() fallbacks

SG00_reset_workspace.sh     3 lines replaced + 25 added  LOW
                            Behavior identical for        Env override preserved
                            PureDhamma (same defaults)

SG01_extract_html.py        4 line substitutions in loop  LOW
                            +2 imports (CORPUS_COLUMNS,   Fallback to V5.4 values
                            CORPUS_ID)                    if corpus.json absent

adapters/                   NEW directory (4 files)       ZERO
                            Not imported by any existing  Purely additive
                            V5.4 script

corpus.json (puredhamma)    NEW file                      ZERO
                            Describes existing corpus     No existing file touched

────────────────────────────────────────────────────────────────────────
ALL OTHER SCRIPTS           NO CHANGE                     —
SG02, SG03, SG04            Zero corpus coupling          Already V6-ready
All SP, SA, SD scripts      Operate on CSL               Already V6-ready
build.py (SSG)              Zero corpus coupling          Already V6-ready
verify_pipeline_integrity   +3 lines for corpus check     LOW
build_release_snapshot      +corpus-aware copy section    LOW
────────────────────────────────────────────────────────────────────────

TOTAL NEW CODE:     ~150 lines across 3 modified files + 4 new files
TOTAL RISK:         LOW — all changes are additive or backward-compatible
V5.4 IMPACT:        ZERO — V5.4 deployments without corpus.json unchanged
```

---

## SECTION 12 — WHAT V6 IS NOT

To prevent scope creep, the following are explicitly outside V6:

| Item | Status | Rationale |
|---|---|---|
| Multi-language SSG themes per corpus | Deferred V7 | Templates work for all corpora |
| Cloud deployment (S3, Netlify) | Out of scope | Offline-first principle |
| Database-backed corpus registry | Out of scope | Filesystem is the registry |
| Automated corpus ingestion pipeline | Deferred V7 | Manual ZIP provision is intentional |
| Git integration | Operator choice | Not an engine concern |
| Parallel multi-corpus builds | Deferred V7 | Sequential per-corpus is sufficient |

---

## APPENDIX — V5.4 → V6 TIMELINE RECOMMENDATION

V6 should not be implemented until a second corpus is acquired and ready for
onboarding. The V6 architecture is fully designed and the change footprint is
precisely quantified. Implementation is a controlled operation, not a research
problem.

```
Trigger for V6 implementation:
  A second corpus ZIP + post index is available for onboarding.

Estimated implementation time:
  Phase 2 (descriptor layer):  1–2 sessions
  Phase 3 (second corpus):     1 session

V5.4 remains the production baseline until V6.0 is verified against PureDhamma.
```

---

*AXIS-NIDDHI V6 — Architectural outline complete.*  
*Design finalized 2026-03-11. Implementation deferred pending second corpus.*

--*--

d)
# AXIS-NIDDHI — CORPUS GOVERNANCE MODEL
**Protocol for Canonical Corpus Releases**  
**Version:** 1.0  
**Date:** 2026-03-11  
**Status:** Locked — governance layer above the V5.4 preservation engine

---

## PURPOSE

This document defines the protocol by which a corpus moves from an editable
working state to a canonical sealed release.

The AXIS-NIDDHI engine already provides deterministic rebuild, cryptographic
integrity, and immutable archival storage. What it does not define is *who*
decides when a corpus is ready to be sealed, *how* changes are reviewed
before entering the canonical lineage, and *what* constitutes an authoritative
version of the corpus.

These are governance questions. The technical system cannot answer them.
This document answers them.

The goal is not to impose bureaucratic process. The goal is to ensure that
the corpus preserved by AXIS-NIDDHI represents the intended knowledge — not
an intermediate state, not an unchecked edit, not an accidental omission —
and that this can be verified by anyone who receives a frozen release.

---

## THE CANONICAL LINEAGE

The canonical lineage is the sequence of sealed releases that constitutes
the authoritative history of a corpus.

```
WORKING CORPUS
      │
      │  (review)
      ▼
REVIEWED CORPUS
      │
      │  (seal)
      ▼
CANONICAL RELEASE  ──────────────────────────────────────────────────┐
      │                                                                │
      │  (archive)                                                     │
      ▼                                                                │
ARCHIVAL RECORD                                               canonical lineage
      │                                                                │
      │  (next cycle)                                                  │
      ▼                                                                │
WORKING CORPUS                                                         │
      │                                                                │
      ▼                                                               ...
CANONICAL RELEASE  ──────────────────────────────────────────────────┘
```

Each canonical release is a node in the lineage. The lineage grows in one
direction only. No release is ever removed or superseded in the sense of
being invalidated — earlier releases remain in the archaeology archive and
remain verifiable indefinitely.

---

## THE FOUR STAGES

### Stage 1 — Working Corpus

The working corpus is the editable state of the corpus under active
development. In AXIS-NIDDHI terms, this is the Lab workspace: the `09-csl/`
directory under `/beng-fut/pipeline/`, the translation control index, and
the active static site output.

Properties of the working corpus:

- **Mutable.** Content may be added, corrected, retranslated, or restructured.
- **Not sealed.** No SHA-256 manifest covers the working state as a whole.
  Per-post hashes exist in identity records, but the corpus as a whole has
  no integrity seal.
- **Not archival.** The working corpus is a development workspace. It is
  not intended as a long-term record. Its contents may change.
- **Recoverable.** The CSL lineage records all mutations. If an erroneous
  change is made to the working corpus, the lineage provides the basis for
  identifying and reversing it.

The working corpus is where translation, correction, structural improvement,
and new content ingestion happen. It is the correct place for this work.
It is not the correct place for permanent preservation.

### Stage 2 — Review State

Before a corpus is sealed into a canonical release, it passes through a
review state in which designated reviewers confirm that the content meets
the standards required for canonical status.

The review state is not a separate technical workspace. It is a declared
checkpoint: the working corpus is frozen for review, changes are assessed,
and the decision is made to proceed to sealing or to return to working state.

**What review covers:**

- **Completeness.** Are all expected posts present? Are any missing?
- **Translation quality.** Are translated posts accurate and consistent
  with the glossary? Have all posts marked for translation been translated?
- **Structural integrity.** Do all identity records validate? Are section
  assignments correct? Are PDPN identifiers consistent?
- **Lineage integrity.** Does the CSL lineage show no unexpected gaps or
  unsigned mutations?

**What review does not cover:**

Review is not a theological or doctrinal assessment. The governance model
does not define the correct interpretation of a teaching. It defines the
correct state of the technical record: whether the content in the corpus
accurately represents what was intended to be preserved, and whether the
engineering record of how it was processed is complete and verifiable.

**Review output:**

Review produces one of two outcomes:

- **Approved for sealing.** The corpus proceeds to Stage 3. The reviewer
  records the approval in a brief review log (see Review Log format below).
- **Returned to working state.** Specific defects are documented. The corpus
  returns to Stage 1 for correction. The review log records what was found
  and why the corpus was not approved.

### Stage 3 — Canonical Release

A canonical release is a sealed, self-contained, cryptographically verified
snapshot of the corpus and engine, produced by the AXIS-NIDDHI release
builder.

The sealing procedure is defined in the engineering documents
(`AXIS_NIDDHI_FINAL_HARDENING_20260311.md`). From the governance perspective,
the canonical release is the moment at which the working corpus becomes a
permanent record.

Properties of a canonical release:

- **Sealed.** The SHA-256 manifest covers every file in the release.
  No file can be added, removed, or modified without invalidating the manifest.
- **Self-contained.** The release includes the source ZIP, engine scripts,
  and metadata sufficient to rebuild the corpus from scratch on any machine.
- **Versioned.** The release is named by date and engine version
  (`2026-03-11_v5.4`). The name is permanent. It is not reused.
- **Documented.** The release includes a `release-sealed-at.txt` record
  identifying the corpus, engine version, seal timestamp, and file count.

A corpus version that has been sealed into a canonical release is considered
the authoritative version of the corpus at that point in time. Subsequent
corrections and improvements are made in a new working corpus cycle and
sealed into a new canonical release. The previous release is not modified.

**Canonical release naming convention:**

```
YYYY-MM-DD_v{engine_version}[_{corpus_id}]

Examples:
  2026-03-11_v5.4                   (single corpus, implicit)
  2026-06-01_v5.4_puredhamma        (multi-corpus, explicit)
  2026-09-15_v6.0_waharaka
```

### Stage 4 — Archival Record

After a canonical release is produced, it is copied to the archaeology
archive under a read-only, no-execute mount. This is the final and permanent
state of that corpus version.

Properties of the archival record:

- **Immutable.** The archaeology mount is `ro,noexec`. No process writes to
  it during normal operation. The only write operation is the controlled
  remount procedure performed during archiving.
- **Permanent.** Archival records are never deleted. Disk space is not a
  valid reason to remove an archival record. If storage is constrained,
  additional storage is added before records are removed.
- **Independently verifiable.** The SHA-256 manifest in the archival record
  uses relative paths. Verification requires only the files and a SHA-256
  implementation — no network, no trusted server, no application layer.
- **Self-describing.** The `README.md` in each archival record provides
  sufficient context to understand what it contains and how to use it,
  without reference to any external system.

The archaeology archive constitutes the canonical lineage of the corpus:
a sequence of sealed releases that can be traversed, compared, and verified
by any future operator or researcher.

---

## ROLES

Governance requires defined roles. The following roles apply to any corpus
managed under the AXIS-NIDDHI governance model.

### Contributor

A contributor proposes changes to the working corpus. This includes:
adding new content, correcting translations, updating glossary entries,
fixing structural errors in identity records, or improving section
assignments.

Contributors work in the Lab workspace (`/beng-fut/`). They do not produce
canonical releases. Their changes become canonical only after review and
sealing.

**Access:** Write access to the working corpus. No access to the release
builder or the archaeology archive.

### Reviewer

A reviewer assesses proposed changes before they enter a canonical release.
A reviewer confirms that the corpus in its current state meets the standards
for canonical status and authorises the release authority to proceed with
sealing.

A reviewer does not modify content. A reviewer identifies problems and
records findings in the review log.

**Access:** Read access to the working corpus and the review log. No write
access to the working corpus. No access to the release builder.

### Maintainer

A maintainer oversees the working corpus over time. Maintainers coordinate
contributor activity, manage the translation control index, ensure that
glossary consistency is maintained across corpus cycles, and prepare the
working corpus for review.

A maintainer is responsible for the structural integrity of the working
corpus. They are the primary contact for questions about the state of the
corpus between releases.

**Access:** Full write access to the working corpus and the translation
control index. Read access to the release builder output. No write access
to the archaeology archive.

### Release Authority

The release authority executes the sealing procedure after a reviewer has
approved the corpus for canonical status. The release authority is
accountable for the integrity of the sealed release: that it was produced
by the correct version of the engine, that the manifest is valid, and that
the archival record has been correctly created and verified.

For small projects, a single person may hold both the maintainer and release
authority roles. The roles are separated in this document because their
responsibilities are distinct: maintaining a corpus is an ongoing operation;
sealing a release is a specific, accountable act.

**Access:** Full access to the release builder and the archaeology archive
(including the controlled remount procedure for archiving). Read access to
the working corpus.

---

## THE REVIEW LOG

Every review produces a brief log entry. The log is maintained as a plain
text or Markdown file in the corpus metadata directory.

Minimum required fields:

```
REVIEW LOG ENTRY
────────────────────────────────────────────────
Corpus:       puredhamma
Date:         2026-03-11
Reviewer:     [name or identifier]
Engine:       V5.4
Outcome:      APPROVED / RETURNED

Posts reviewed:    748
Translations verified:  748 / 748
Lineage integrity:      PASS
Structural integrity:   PASS

Issues found:
  [none] or [list of issues with resolution]

Notes:
  [optional]
────────────────────────────────────────────────
```

The review log is included in the canonical release and therefore in the
archival record. A future operator can read the review log to understand
who approved the corpus for sealing and what was verified.

---

## GOVERNANCE IN A SINGLE-OPERATOR CONTEXT

The PureDhamma corpus, as preserved in V5.4, is managed by a single
operator who holds all four roles simultaneously.

In this context, the governance model functions as a self-discipline
framework rather than a multi-party review process. The stages still apply:

- The operator works in the Lab workspace (Stage 1)
- The operator performs a structured self-review before sealing (Stage 2)
- The operator executes the release builder and verifies the manifest (Stage 3)
- The operator archives the release under the read-only mount (Stage 4)

The review log, even when written by the same person who will seal the
release, creates a documented checkpoint. It converts the sealing decision
from an implicit act into an explicit one: the operator has reviewed the
corpus, found it complete, and authorised the seal.

This matters for long-term preservation because the operator who seals
V5.4 may not be the person who needs to verify it in 2036. The review log
is the record left for that future person.

---

## CORPUS DRIFT AND HOW THE MODEL PREVENTS IT

Corpus drift is the gradual divergence of a preserved corpus from the
knowledge it was intended to represent. It occurs when changes accumulate
in a working corpus without structured review, when translations are updated
without glossary consistency checks, or when structural modifications alter
the organisation of the corpus without updating the identity records.

The governance model prevents corpus drift through four mechanisms:

**1. Explicit review checkpoints.** The transition from working to canonical
is not automatic. It requires a reviewer to confirm that the corpus is
complete and consistent. Drift that has accumulated in the working corpus
is caught at the review stage, not after sealing.

**2. Immutable canonical releases.** Once sealed, a canonical release cannot
be modified. A future change requires a new working corpus cycle and a new
review. There is no mechanism for silently patching a sealed release.

**3. Append-only lineage.** The lineage in each CSL entry records every
operation. A reviewer can compare the lineage against the expected pipeline
operations and identify any mutations that are not accounted for.

**4. SHA-256 per-post hashing.** The hash of each content file is stored in
the identity record. If a file is modified outside the pipeline — by a
manual edit, a corrupted write, or an unauthorised operation — the hash
mismatch is detectable at review time.

The governance model does not prevent contributors from making errors.
It ensures that errors in the working corpus are caught before they enter
the canonical lineage.

---

## THE THREE-LAYER ARCHITECTURE

With the governance model in place, the complete AXIS-NIDDHI architecture
consists of three layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1 — CORPUS GOVERNANCE                                             │
│                                                                          │
│  Contributors · Reviewers · Maintainers · Release Authority             │
│  Working corpus → Review → Canonical release → Archival record         │
│  Review logs · Canonical lineage                                        │
│                                                                          │
│  Ensures: the corpus represents the intended knowledge                  │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │  authorises sealing
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 2 — PRESERVATION ENGINE (AXIS-NIDDHI V5.4)                       │
│                                                                          │
│  Deterministic rebuild · CSL · SHA-256 per-post integrity               │
│  Translation pipeline · Static site generation · Release builder       │
│  Integrity guard · Archaeology archiving                                │
│                                                                          │
│  Ensures: the corpus can be rebuilt and verified by the build record   │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │  produces
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 3 — FROZEN ARCHIVAL RELEASES                                      │
│                                                                          │
│  SHA-256 manifests · Relative-path portability · ro,noexec mount       │
│  Self-contained rebuild packages · Permanent canonical lineage         │
│                                                                          │
│  Ensures: the corpus remains verifiable and rebuildable across time    │
└─────────────────────────────────────────────────────────────────────────┘
```

The governance layer (Layer 1) determines *what* is preserved and *when* a
corpus is ready for sealing. The preservation engine (Layer 2) determines
*how* it is preserved. The archival releases (Layer 3) ensure *that* it
remains preserved.

No layer substitutes for the others. A technically perfect engine preserving
an unreviewed corpus is not preservation — it is archiving noise with high
fidelity. A rigorous review process without a deterministic engine produces
no verifiable artifact. Archival records without a self-contained rebuild
capability become unreadable when the original infrastructure ages out.

The three layers together constitute a complete preservation architecture.

---

*AXIS-NIDDHI Corpus Governance Model V1.0 — locked 2026-03-11.*  
*Governance layer above the V5.4 preservation engine.*  
*No engine changes required. Protocol applies immediately to the PureDhamma corpus.*

--*--
e)
# AXIS-NIDDHI — TRUTH TRANSMISSION MODEL
**Long-Term Knowledge Integrity Architecture**  
**Version:** 1.0  
**Date:** 2026-03-11  
**Status:** Locked — conceptual capstone of V5.4 baseline

---

## STATEMENT OF PURPOSE

A build pipeline produces an artifact. A truth transmission architecture
ensures that the artifact faithfully represents a specific body of knowledge
and can be verified to do so — now, and at any point in the future.

AXIS-NIDDHI is the second kind of system.

The distinction matters because the question it must answer is not
*did the build succeed* but *is what was built identical to what was known*.
These are different questions with different answers, requiring different
architectural properties.

This document describes the three layers that together provide the answer.

---

## THE THREE LAYERS

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 3 — VERIFICATION                                                  │
│  SHA-256 integrity · deterministic rebuild · sealed manifests           │
│  "This is what was preserved, and it has not changed."                  │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 2 — STRUCTURE                                                     │
│  CSL · identity records · lineage · stable identifiers                  │
│  "Every unit of knowledge has a permanent, verifiable location."        │
├─────────────────────────────────────────────────────────────────────────┤
│  LAYER 1 — TEXT                                                          │
│  Source HTML · translations · canonical content files                   │
│  "This is what was said."                                               │
└─────────────────────────────────────────────────────────────────────────┘
```

Each layer depends on the one below it and extends its guarantees upward.
A failure at any layer propagates to all layers above it. The architecture
is designed so that failures are detectable at the layer where they occur,
not silently absorbed.

---

## LAYER 1 — TEXT

The text layer contains the raw knowledge content: articles, teachings,
translations, and canonical texts in all supported languages.

In AXIS-NIDDHI, the text layer is physically represented by `content.html`
files within the CSL. One file per post per language. The files contain
only content — no layout, no navigation, no publication-specific markup.

Three properties govern the text layer:

**Fidelity.** The content of each file is exactly what was published at the
source. The extraction process (SG01) reads from the original WordPress
database without interpretation or modification. The tattoo header identifies
the origin precisely: corpus, identifier, language, timestamp, source ID.
The content that follows is the source content verbatim.

**Separation.** Source language content and translated content are stored
separately. The English article and its Portuguese translation are different
files in different subdirectories of the same CSL entry. They are related
by identity — they describe the same post — but they are never merged,
never overwritten, and never compared automatically. Each is the authoritative
record for its language.

**Immutability of origin.** Once extracted, the source language content is
not modified by any downstream pipeline step. Transformations — header fixes,
structural migrations — are logged in the lineage and produce new file states
that are themselves hashed. The original extraction is preserved in the
lineage origin record. The chain from source database to current file state
is always reconstructible.

The text layer alone is sufficient to read the corpus. A person with a
browser can open any `content.html` file and read the teaching it contains.
No application layer is required. This is the baseline accessibility
guarantee: the corpus is readable by a human with no tooling at all.

---

## LAYER 2 — STRUCTURE

The structure layer provides stable identity, relationships, and metadata
for every unit of knowledge in the corpus. It is implemented by the CSL.

Without structure, a collection of HTML files is an archive. With structure,
it is a navigable, verifiable, machine-processable corpus.

The structure layer has four components:

**Stable identifiers.** Every post in the corpus has a PDPN identifier
(`PD.AA.001`, `TL.BB.003`) that is assigned at extraction and never changes.
The identifier is independent of the URL, the title, the publication date,
and the source system. A post whose title changes, whose URL is redirected,
or whose WordPress ID is reassigned retains its PDPN across all rebuilds.
The identifier is the permanent address of the knowledge unit.

**Identity records.** The `identity.json` file for each CSL entry contains
the complete descriptor of that post: its identifier, titles in all
languages, SHA-256 hashes of each content file, publication metadata, and
lineage reference. The identity record is the machine-readable contract
for that post. Any system — the SSG, the translation pipeline, an audit
tool, a future application — reads from the identity record rather than
inferring properties from the file system.

**Lineage.** The lineage is the append-only history of every operation
performed on a post. It records the origin (which database, which source
ID, which extraction timestamp), every transformation (preprocessing,
schema migration, header fixes), every translation event (engine, character
count, glossary version, before/after hashes), and every publication event
(WordPress injection, static site build). The lineage converts the corpus
from a static archive into a traceable record of decisions and operations.

**Relationships.** The CSL section structure (`MasterPDPN_Sections.csv`,
section codes in identifiers) maps posts into a navigable hierarchy. A post
is not just a file — it is a member of a section, ordered within that section,
with a canonical position in the corpus that is stable across builds. The
navigation tree generated by the SSG is derived from this structure, not
computed heuristically from filenames or dates.

The structure layer is the layer that makes the corpus a corpus rather than
a collection of files. It is what allows a rebuild to produce not just the
same files but the same organised, navigable knowledge structure.

---

## LAYER 3 — VERIFICATION

The verification layer provides cryptographic guarantees that the text and
structure layers are intact and have not been altered since they were sealed.

It operates at two scopes: per-post and per-release.

**Per-post verification.** Every `content.html` file has its SHA-256 hash
stored in the corresponding `identity.json`. At any point, the current file
can be hashed and compared to the stored value. A match confirms the file
is unchanged. A mismatch indicates either intentional modification (logged
in the lineage) or corruption (not logged, therefore a defect). The hash
is computed and stored at every pipeline step that produces or modifies a
content file: extraction, preprocessing, translation, migration.

**Per-release verification.** Every frozen release is sealed with a
`release-manifest.sha256` file containing the SHA-256 hash of every file
in the release, expressed as relative paths. The manifest covers the engine
scripts, the metadata, the source ZIP, and all static assets. Verification
requires only standard tools:

```bash
cd /path/to/release
sha256sum --check release-manifest.sha256
# All files: OK
```

This command works from any location where the release has been copied —
the original machine, an archaeology archive, a USB drive, a server in a
different country — because the paths are relative.

**Deterministic rebuild as verification.** The deepest verification
property of the system is not a hash check but a rebuild. Because the
pipeline is deterministic, a rebuild from the same source ZIP should
produce the same CSL content. If a rebuild produces different content
from the same source, the difference is evidence of either a change in
the engine (which should be version-controlled) or a change in the source
(which should be impossible, because the source is a sealed ZIP). The
rebuild is the verification. The manifest is the seal.

**What verification does not cover.** The verification layer confirms that
the preserved content is identical to what was sealed. It does not confirm
that the original source was authoritative. That question — whether the
WordPress database at the moment of extraction contained the canonical
version of the teachings — is a human judgment that precedes the technical
process. The system preserves whatever was extracted. The governance model
(see `AXIS_NIDDHI_CORPUS_GOVERNANCE_MODEL.md`) addresses the question of
what should be extracted and when.

---

## HOW THE THREE LAYERS WORK TOGETHER

A corpus that has passed through all three layers has the following
properties:

```
PROPERTY                  PROVIDED BY           MECHANISM
──────────────────────────────────────────────────────────────────────────
Human-readable content    Text layer            content.html files
                                                No tooling required

Stable addressing         Structure layer       PDPN identifiers
                                                Survive title/URL changes

Navigable organisation    Structure layer       Section hierarchy
                                                Identity records

Traceable history         Structure layer       Append-only lineage
                                                Per-post event log

Content integrity         Verification layer    Per-post SHA-256
                                                Detects corruption/change

Release integrity         Verification layer    Manifest SHA-256
                                                Relative paths, portable

Rebuild independence      All three layers      Deterministic pipeline
                                                + sealed source ZIP
                                                + self-contained release
──────────────────────────────────────────────────────────────────────────
```

No single layer provides all of these properties. The text layer without
structure is an archive with no stable addressing. The structure layer
without verification can be silently corrupted. The verification layer
without reliable text and structure is a hash of noise. The three layers
are mutually dependent.

---

## TRANSMISSION ACROSS TIME

The phrase "transmission across time" names the specific requirement that
distinguishes a preservation architecture from a publication pipeline.

A publication pipeline is designed to produce output now. A preservation
architecture is designed to produce output now and to ensure that the same
output can be produced in ten years, by a different operator, with different
hardware, after the original publication infrastructure has been decommissioned.

The three-layer model addresses this requirement directly:

The **text layer** ensures that the content exists in a format that requires
no proprietary application to read. Plain HTML, UTF-8 encoded, with no
obfuscation or binary encoding. A browser from any decade can render it.

The **structure layer** ensures that the content retains its identity and
organisation independent of any database, any URL scheme, or any CMS.
The PDPN identifier is stable because it is assigned once and stored in
a plain JSON file, not computed from a live system.

The **verification layer** ensures that a future operator can confirm,
without trusting any intermediate party, that what they received is what
was sealed. The SHA-256 manifest is computed from the content itself.
It does not require a trusted server. It does not expire. It does not
depend on a certificate authority. It requires only the files and a
SHA-256 implementation, which has been part of every major operating
system for two decades and will remain so.

Together, these three layers allow a frozen release to function as a
**self-describing, self-verifying preservation artifact**: it contains
the content, the structure required to understand the content, and the
cryptographic proof that the content is intact.

---

## SUMMARY

AXIS-NIDDHI is a truth transmission architecture because it preserves
not only the content of a corpus but the conditions under which that
content can be verified as authentic, organised as knowledge, and rebuilt
as a complete, navigable corpus — independent of infrastructure, independent
of time, and independent of any specific operator.

The three layers are:

- **Text:** what was said, exactly as it was said
- **Structure:** where each unit of knowledge permanently resides
- **Verification:** proof that nothing has changed

These three properties, together, are what it means to have transmitted
a corpus faithfully. AXIS-NIDDHI is the engineering implementation of
that transmission.

---

*AXIS-NIDDHI Truth Transmission Model V1.0 — locked 2026-03-11.*  
*Conceptual capstone of the V5.4 baseline.*  
*Foundation for the multi-corpus architecture documented in V6 outline.*
