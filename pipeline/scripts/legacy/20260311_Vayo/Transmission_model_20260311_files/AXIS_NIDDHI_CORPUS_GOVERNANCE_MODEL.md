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
