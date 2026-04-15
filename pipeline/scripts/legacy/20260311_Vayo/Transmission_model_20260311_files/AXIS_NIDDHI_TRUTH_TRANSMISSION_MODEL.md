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
