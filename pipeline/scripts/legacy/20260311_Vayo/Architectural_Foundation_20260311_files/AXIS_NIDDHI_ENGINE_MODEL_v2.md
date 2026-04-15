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
