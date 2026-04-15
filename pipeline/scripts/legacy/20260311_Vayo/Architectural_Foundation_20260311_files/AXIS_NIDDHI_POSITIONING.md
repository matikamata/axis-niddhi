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
