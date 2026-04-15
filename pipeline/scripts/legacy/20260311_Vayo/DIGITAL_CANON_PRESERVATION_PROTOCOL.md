# DIGITAL CANON PRESERVATION PROTOCOL
**A Formal Protocol for Long-Term Transmission of Knowledge Corpora**  
**Version:** 1.0  
**Date:** 2026-03-11  
**Status:** Locked

---

## 1. PREAMBLE

This protocol defines the conditions under which a digital knowledge corpus
can be considered durably preserved: readable, verifiable, and rebuildable
by any competent operator, without dependency on any specific infrastructure,
at any point in the future.

It is written to be understood by someone who has never encountered the system
that implements it. The protocol is not tied to any specific software version.
Software changes. The protocol describes properties that must survive those
changes.

A corpus preserved in compliance with this protocol satisfies three claims:

**Claim 1 — Integrity.** The preserved content is identical to the source
content at the moment of preservation. This claim can be verified by any
operator holding the preserved artifact, independently, without trusting any
intermediary.

**Claim 2 — Reproducibility.** Given the original source and the preservation
engine, any compliant operator can reconstruct the preserved corpus. The
reconstruction is not approximate. It is exact.

**Claim 3 — Independence.** The preserved corpus does not depend on any live
network service, any proprietary application, any cloud provider, any domain
name, or any institution. It requires only the preserved artifact, standard
computing hardware, and open-source tools that have been stable for decades.

These three claims together define what it means to have transmitted a corpus
faithfully. Each section of this protocol formalizes one aspect of satisfying
them.

---

## 2. CORPUS IDENTITY

A corpus has identity at three levels. This protocol preserves the first two.
The third is explicitly outside its scope.

### 2.1 Textual Identity

Textual identity is the content of the corpus: the specific sequence of words,
sentences, and structures that constitute each unit of knowledge in each
language.

Textual identity is represented by `content.html` files. One file per post
per language. The file contains the content exactly as extracted from the
source, with no transformation of meaning.

Textual identity is preserved when: for every post in the corpus, the
content file in the preservation artifact is identical to the content file
produced by a fresh extraction from the same source. This equivalence is
verified by SHA-256 hash.

### 2.2 Structural Identity

Structural identity is the organisation of the corpus: the permanent
identifiers assigned to each post, the language layers attached to each
post, the canonical ordering of posts within sections, and the relationships
among posts.

Structural identity is represented by the identity record (`identity.json`)
of each post. The identity record contains:

- **Corpus identifier** (`corpus_id`): the machine-readable name of the
  corpus this post belongs to. Stable across engine versions.

- **Post identifier** (PDPN): a code of the form `XX.YY.NNN` assigned at
  extraction and never changed. The PDPN is independent of the post's URL,
  title, publication date, and source system identifier. It is the permanent
  address of this unit of knowledge within this corpus.

- **Language layers**: the set of languages in which this post exists within
  the corpus, each with its own content file and SHA-256 hash. The source
  language and each translated language are distinct, equal-status layers.

- **Canonical ordering**: the `fin_dex` value that determines the post's
  position within its section. Canonical ordering is part of structural
  identity because the sequence in which a corpus is read is itself a
  property of the knowledge it encodes.

- **Corpus class** (`corpus_class`): optional classification of the corpus
  by knowledge domain (`dhamma`, `philosophy`, `historical`, `literary`,
  `other`). Advisory metadata. Does not affect rebuild or verification.

Structural identity is preserved when: for every post in the corpus, the
identity record in the preservation artifact contains the correct PDPN,
the correct language layers, and the correct ordering, and these values
match those produced by a fresh extraction from the same source.

### 2.3 Semantic Interpretation

Semantic interpretation is the meaning of the corpus: what the teachings
say, how they should be understood, which translations are doctrinally
accurate, and how the content should be applied.

Semantic interpretation is **explicitly outside the scope of this protocol.**

The protocol preserves what was said. It makes no claim about what it means.
Semantic authority belongs to the knowledge tradition that produced the corpus.
The protocol's role is to ensure that the tradition's own record of what was
said is preserved faithfully and verifiably, so that those with semantic
authority can work from a reliable foundation.

### 2.4 Corpus Descriptor

Every corpus compliant with this protocol is described by a `corpus.json`
descriptor. The descriptor contains at minimum:

```json
{
  "corpus_id":    "<unique identifier>",
  "corpus_name":  "<human-readable name>",
  "corpus_class": "<domain classification, optional>",
  "source": {
    "type":         "<source format>",
    "zip_filename": "<source archive filename>"
  },
  "languages": {
    "source":  "<source language code>",
    "targets": ["<target language codes>"]
  },
  "post_index": {
    "filename":  "<post index filename>",
    "delimiter": "<CSV delimiter>",
    "columns": {
      "fin_dex": "<ordering column>",
      "post_id": "<source system ID column>",
      "pdpn":    "<post identifier column>",
      "slug":    "<URL slug column>"
    }
  }
}
```

The corpus descriptor is the machine-readable identity card of the corpus.
It is included in every canonical release and archival record.

---

## 3. CANONICAL BUILD

### 3.1 The Deterministic Reconstruction Rule

Given:
- a source archive (the corpus ZIP)
- a compliant preservation engine
- the corpus descriptor

any compliant operator must produce output that is structurally identical
to any other compliant operator's output from the same inputs.

This is the Deterministic Reconstruction Rule. It is the technical
foundation of Claim 2 (Reproducibility). It means that the canonical
corpus is not the artifact produced by one specific operator — it is the
artifact that any operator would produce from the same inputs. The
preservation is in the rule, not in the artifact.

### 3.2 The Canonical Build Sequence

The canonical build proceeds through defined phases. Each phase takes
well-specified input and produces well-specified output.

**Phase SG — Genesis**

Input: source archive ZIP + corpus descriptor  
Output: `09-csl/` — the Canonical Source Library

```
source.zip
    │
    ▼  SG00: Reset and deploy source to local environment
    │
    ▼  SG01: Extract content from source system
    │        → 01-extracted-htmls/{lang}/*.html
    │        Each file carries a provenance header (tattoo) identifying
    │        corpus, PDPN, source ID, extraction timestamp.
    │
    ▼  SG02: Preprocess extracted content
    │        → 02-preprocessed/{lang}/*.html
    │        Structural normalisation. No content modification.
    │
    ▼  SG03: Build CSL
    │        → 09-csl/{PDPN}/source/{lang}/content.html
    │           09-csl/{PDPN}/meta/identity.json
    │        PDPN identifiers assigned. Identity records initialised.
    │        SHA-256 hashes computed and stored.
    │
    ▼  SG04: Harvest assets
             → asset_map.json
             Maps content asset references to canonical locations.
```

**Phase SP — Preservation**

Input: `09-csl/` from SG phase  
Output: `09-csl/` with translations and structural upgrades

The SP phase applies controlled transformations to the CSL:
schema migration, structural header normalisation, translation via
external API, glossary application, and title translation. Every
transformation is logged in the lineage of each affected post.

The translation step (SP10) is the one deliberate manual gate in the
canonical build. An operator must mark posts for translation in the
translation control index. This gate is intentional: automated systems
must not translate knowledge-bearing content without human authorisation
of the translation parameters.

**Phase SA — Audit**

Input: `09-csl/` from SP phase  
Output: integrity report + frozen manifest

The SA phase verifies that the CSL is complete and consistent. It checks
that every expected post is present, that every identity record is valid,
that translation coverage meets the configured threshold, and that SHA-256
hashes in identity records match the current content files. The SA phase
produces a freeze manifest of the CSL state.

**Phase SD — Distribution**

Input: `09-csl/` from SA phase  
Output: `13-static-site/` — static HTML site

```
09-csl/
    │
    ▼  SD01: Generate asset map
    │
    ▼  SD03: Static site generator (SSG)
    │        → 13-static-site/pages/{PDPN}/index.html
    │           13-static-site/index.html
    │        Renders each CSL entry as a standalone HTML page.
    │        Navigation derived from structural identity.
    │        No database required at read time.
    │
    ▼  SD04: (Optional) WordPress injection
             Publishes to a local WordPress instance for operator review.
```

### 3.3 Compliance Requirements

A build is compliant with this protocol if and only if:

1. Every post in the corpus descriptor's post index appears in the CSL
   output with a valid identity record.
2. Every identity record contains a SHA-256 hash that matches the
   corresponding content file.
3. The lineage of each modified post contains a logged entry for every
   transformation applied.
4. The static site output contains one rendered page per CSL entry per
   language.

A build that satisfies these requirements from the same source inputs as
another compliant build will produce structurally identical output.

---

## 4. VERIFICATION LAYER

### 4.1 The Two Verification Scopes

Verification operates at two scopes: **per-post** and **per-release**.

Per-post verification confirms that the content of a specific post is
identical to the content recorded in the identity record.

Per-release verification confirms that the entire release artifact is
identical to what was sealed at the moment of freezing.

These are independent operations. A release may pass per-release
verification (the manifest is intact) while a per-post verification
reveals that a content file was corrupt before sealing. The per-post
verification is the earlier check; the per-release verification is the
later seal.

### 4.2 Per-Post Verification

Every `content.html` file in the CSL has its SHA-256 hash stored in the
corresponding `identity.json` under `artifacts.{lang}.integrity_sha256`.

Verification:
```
hash = SHA-256(content.html)
expected = identity.json → artifacts.{lang}.integrity_sha256
result = (hash == expected) ? PASS : FAIL
```

A PASS confirms the file is identical to the state recorded when the
identity record was last written. A FAIL indicates either a logged
mutation (check the lineage for an entry with `output_hash == current hash`)
or an unlogged modification (a defect or corruption).

### 4.3 Per-Release Verification

Every frozen release contains a `release-manifest.sha256` file. This file
contains one line per file in the release, in the form:

```
<sha256hash>  ./<relative/path/to/file>
```

Paths are relative to the release root. This is not a formatting convention.
It is a functional requirement: relative paths make the manifest valid at
any location where the release is stored.

Verification:
```bash
cd /path/to/release-root
sha256sum --check release-manifest.sha256
```

Expected output: `<filename>: OK` for every file.
Any `FAILED` indicates the corresponding file has changed since sealing.

### 4.4 Pre-Flight Integrity Verification

Before a build or rebuild is executed, the operator should confirm that the
preservation engine is complete and correctly assembled. This is the
pre-flight check.

The pre-flight check verifies:
- All required engine scripts are present
- The configuration module (`config.py`) is importable and correct
- The CSL directory exists and contains expected entries
- Required workspace directories are present
- The Python environment contains required packages

The pre-flight check is executed by:
```bash
axis doctor
```

This command must pass before a canonical build is initiated.

### 4.5 Verification Procedures

**Procedure A — Fresh Rebuild Verification**

Used when: verifying a canonical build against the source.

1. Execute `axis doctor` — confirm PASS
2. Execute `axis pipeline --full` from a clean workspace
3. For each post, verify `SHA-256(content.html) == identity.json.integrity_sha256`
4. Execute `SA02_freeze_manifest.py` — confirm all hashes match
5. Compare post count against corpus descriptor post index — confirm equal

**Procedure B — Frozen Release Verification**

Used when: verifying a frozen release received from any source.

1. Navigate to the release root directory
2. Execute `sha256sum --check release-manifest.sha256`
3. Confirm all files return `OK`
4. Execute `axis doctor` from within the release
5. Confirm `release-sealed-at.txt` records the expected engine version
   and corpus identifier

**Procedure C — Archaeological Archive Verification**

Used when: verifying an archived release, potentially years after sealing.

1. Mount the archive storage (read-only mount is standard; a temporary
   read-only bind-mount of the archive directory suffices for verification)
2. Navigate to the archived release root
3. Execute `sha256sum --check release-manifest.sha256`
4. Confirm all files return `OK`

No network access is required. No application layer is required. No account,
certificate, or service is required. The verification requires only the
files and a SHA-256 implementation.

### 4.6 Why SHA-256 Is Sufficient

SHA-256 produces a 256-bit digest. The probability of two different files
producing the same SHA-256 hash (a collision) is sufficiently small that no
collision has ever been observed in practice for arbitrary input data, and
none is expected to be found through any feasible computational means for
the foreseeable future.

More relevant for this protocol: SHA-256 is not a proprietary algorithm.
It is defined in FIPS PUB 180-4, published by the United States National
Institute of Standards and Technology. Implementations exist in every major
programming language, every major operating system, and every major platform.
The algorithm has been stable since 2001. There is no credible technical
argument that SHA-256 implementations will become unavailable within the
timescale this protocol is designed to serve.

A SHA-256 hash of a file is therefore a verification that does not expire,
does not require a trusted party, does not depend on network availability,
and will remain computable on any standard computing platform for the
foreseeable future.

---

## 5. CANONICAL RELEASE GOVERNANCE

### 5.1 The Release Lifecycle

A corpus moves through four states. The transitions between states are
explicit, documented, and irreversible in the forward direction.

```
WORKSPACE
   │
   │  Operator declares corpus ready for review.
   │  No further content changes are made during review.
   ▼
REVIEW
   │
   │  Reviewer confirms completeness, consistency, and integrity.
   │  Issues documented in review log. Outcome: APPROVED or RETURNED.
   │  If RETURNED: corpus goes back to WORKSPACE for correction.
   ▼
FREEZE
   │
   │  Release authority executes sealing procedure.
   │  build_release_snapshot generates sealed release.
   │  SHA-256 manifest seals every file.
   │  release-sealed-at.txt records corpus, engine, timestamp.
   ▼
ARCHAEOLOGY
      Frozen release copied to immutable archival storage.
      Manifest verified against archival copy.
      Mount returned to read-only.
      This state is permanent and irrevocable.
```

### 5.2 Roles and Responsibilities

**Operator.** Executes the canonical build, maintains the working corpus,
prepares the corpus for review, executes the freeze procedure when
authorised by the reviewer. In a single-operator context, the operator
holds all roles and observes the governance checkpoints as self-discipline.

**Reviewer.** Assesses the working corpus before sealing. Confirms that
the corpus is complete, that translations meet the required standard, that
structural integrity is intact, and that the lineage is consistent.
Records findings in a review log. Authorises or declines the freeze.
A reviewer does not modify content.

**Archivist.** Executes the archiving procedure after a frozen release
is produced. Copies the release to the archaeology archive, verifies
the manifest against the archive copy, and returns the mount to read-only.
The archivist is accountable for the integrity of the archival record.

**Future operator.** Any person who receives a frozen release or an
archival record at any future point. The protocol is designed so that the
future operator requires no context about the original project beyond
what is contained in the release itself. The `README.md` provides
onboarding. The manifest provides verification. The engine provides rebuild.

### 5.3 The Review Log

Every transition from REVIEW to FREEZE must be documented in a review log
entry. The review log is included in the frozen release.

Minimum content:
```
Corpus:              <corpus_id>
Release:             <YYYY-MM-DD_v{engine_version}>
Reviewer:            <identifier>
Date:                <ISO 8601>
Outcome:             APPROVED | RETURNED
Posts verified:      <count>
Translations:        <translated_count> / <total_count>
Lineage integrity:   PASS | issues noted
Structural checks:   PASS | issues noted
Issues:              <none> | <description>
```

### 5.4 Single-Operator Governance

When one person holds all roles, the governance model functions as a
structured self-review protocol. The stages still apply. The review log
is still written. The freeze is still a deliberate, documented act.

The reason is forward-looking: the person who seals a release is not the
person who will need to verify it in thirty years. The review log is the
message left for that future person. Its existence confirms that the corpus
was not sealed accidentally or impulsively — it was reviewed, found
complete, and deliberately preserved.

### 5.5 Immutability of Canonical Releases

A canonical release, once archived, is never modified. A discovered error
in a sealed release is addressed by:

1. Documenting the error in a correction record stored alongside the
   release in the archaeology archive.
2. Creating a new working corpus cycle that addresses the error.
3. Producing a new canonical release.

The original release remains in the archive, unchanged and verifiable,
with the correction record as its companion. This approach preserves the
complete canonical lineage: not only the correct state of the corpus, but
the history of how it arrived at that state.

---

## 6. ARCHAEOLOGICAL PRESERVATION

### 6.1 The Archaeology Archive

The archaeology archive is immutable long-term storage for canonical
releases and historical preservation artifacts.

Physical enforcement: the archive storage is mounted read-only with the
`noexec` flag (`ro,noexec`). This prevents both accidental writes and
accidental execution of archived scripts. The mount option is not a
recommendation. It is a protocol requirement.

```bash
# Required mount configuration
mount -o ro,noexec /dev/[device] /mnt/archaeology

# Verify
mount | grep archaeology
# Expected: type [fs] (ro,noexec,...)
```

The temporary remount to read-write (`remount,rw`) required during archiving
is the only permitted write operation on the archaeology storage. The window
in which the mount is writable must be kept as short as possible and must
be immediately followed by returning the mount to read-only.

### 6.2 Required Properties of an Archival Record

An archival record compliant with this protocol must satisfy all of the
following:

**Self-contained.** The archive record contains everything required to
verify and rebuild the corpus: the source ZIP, the engine scripts, the
control metadata, the SHA-256 manifest, and the operator README. No
external resource is required for verification. No external resource is
required for rebuild, beyond standard system dependencies (MySQL, PHP,
Python 3, standard Unix utilities) that have been stable for decades.

**Manifest with relative paths.** The SHA-256 manifest uses file paths
relative to the release root. Absolute-path manifests are non-compliant
because they bind the verification to a specific filesystem location,
making the manifest invalid when the archive is copied or moved.

**Plain text content.** The knowledge content is stored as UTF-8 encoded
HTML files. HTML and UTF-8 are open, stable, widely implemented standards.
An HTML file can be rendered by any browser produced in the last three
decades and any browser that will be produced in the foreseeable future.
No proprietary format, no binary encoding, no application-specific
rendering layer is required.

**Human-readable structure.** The CSL directory structure — one folder per
post, with a `content.html` file and an `identity.json` file per language
— can be navigated and read by a person with a file manager and a text
editor. The knowledge is accessible even if no software in the release
executes correctly.

**Documented provenance.** Every archive record contains a `README.md`
sufficient to orient a future operator with no prior context, a
`release-sealed-at.txt` recording the corpus identity and seal timestamp,
and a review log confirming that the corpus was reviewed before sealing.

### 6.3 The Core Principle

A preserved corpus must remain readable and verifiable even if the original
preservation software no longer exists.

This principle has two implications:

First, the content layer (plain HTML files) must be readable without the
engine. A person who finds an archaeology archive decades from now and cannot
run the engine scripts must still be able to read every teaching in the corpus
by navigating the CSL directory tree with any file browser and opening
`content.html` files in any browser. The engine is a convenience for rebuilding.
The content is self-sufficient for reading.

Second, the verification layer (SHA-256 hashes) must be checkable without
the engine. SHA-256 is available as a standalone command-line utility on
every major operating system (`sha256sum` on Linux/macOS, `CertUtil` on
Windows, `openssl dgst -sha256` universally). Verifying the manifest does
not require the preservation engine to be functional.

The engine enables rebuild. The archive enables reading. These are two
different use cases that are both satisfied without requiring each other.

---

## 7. GIT FOR KNOWLEDGE CORPORA

### 7.1 The Analogy

AXIS-NIDDHI can be understood by technically literate readers through an
analogy with Git, the distributed version control system.

```
Git concept          Corpus preservation equivalent
────────────────────────────────────────────────────────────────────────
Repository           Corpus
                     A bounded, identified body of knowledge.

Commit history       Lineage
                     The append-only per-post event log.

Blob                 content.html
                     The content of a post at a specific state,
                     identified by its SHA-256 hash.

Tree                 CSL structure
                     The organised hierarchy of all post directories
                     and their associated identity records.

Tag                  Frozen release
                     A named, sealed point-in-time snapshot.
                     Cryptographically sealed by SHA-256 manifest.

Clone                Deterministic rebuild
                     Reconstructing the corpus from the source ZIP
                     using a compliant engine produces an identical CSL.

Remote origin        Source archive (corpus.zip)
                     The sealed source from which every rebuild starts.
```

The analogy helps orient engineers who already understand version control.
A frozen release is a tag. The source ZIP is the remote origin. The lineage
is the commit history.

### 7.2 Where the Analogy Holds

Both systems treat the historical record as append-only and authoritative.
Both derive the current state from a sequence of operations applied to a
known starting point. Both make it possible to verify the current state
against a known reference. Both separate the stored representation from
the rendered or compiled output.

### 7.3 Where the Analogy Breaks

The analogy must not be taken to imply that the two systems serve the same
purpose. They do not.

**Git tracks code evolution. AXIS-NIDDHI seals canonical knowledge states.**
Code is expected to change continuously. Knowledge corpora are preserved at
specific canonical moments. The system is not designed for continuous
iteration — it is designed for deliberate, reviewed, irreversible acts of
preservation.

**Git encourages branching and history rewriting. AXIS-NIDDHI forbids both.**
A `git rebase` or `git push --force` is a routine operation. In a corpus
preservation system, rewriting history would destroy the provenance record
that gives the canonical lineage its authority. Invariant 3 of this
protocol — lineage append-only — has no equivalent in Git because Git was
not designed with the requirement that the historical record be legally and
archivally authoritative.

**Git repositories are collaborative by design. Corpus archives are custodial.**
A Git repository is expected to have many contributors pushing changes
continuously. A corpus archive is held in custody by a small number of
maintainers who are accountable for its integrity. Collaboration happens
in the working corpus. The canonical release is not a collaborative product —
it is a reviewed, authorised, sealed record.

**Git is infrastructure. The corpus archive is not.**
Git repositories depend on hosting services, network availability, and
organisational continuity. A corpus archive compliant with this protocol
depends on none of these. It is a directory of files on a physical medium.
Its survival does not require any organisation to continue operating.

The analogy is useful for introduction. The invariants in Section 8 are
authoritative.

---

## 8. TRANSMISSION ACROSS TIME

How does a corpus preserved under this protocol remain verifiable in ten,
twenty, or fifty years?

The answer has three parts, and each part references only things that will
remain available without any specific organisation continuing to exist.

**Part 1 — The content remains readable.**

The content of every post is a UTF-8 encoded HTML file. UTF-8 is the
dominant character encoding of the internet and has been so for two decades.
HTML is the document format of the web and has been stable in its fundamental
structure for three decades. Both are documented in freely available open
standards maintained by international bodies that are not dependent on any
single organisation.

A future reader who finds an archival record and cannot run any of the engine
scripts can navigate the `09-csl/` directory, open any `content.html` file
in any browser or text editor, and read the teaching it contains. No
installation, no account, no network connection, no proprietary application
is required.

**Part 2 — The integrity remains verifiable.**

Every content file has its SHA-256 hash stored in the adjacent `identity.json`.
Every release has its complete file inventory hashed in `release-manifest.sha256`.
Both files are plain text.

SHA-256 is defined in a published federal standard (FIPS 180-4). It is
implemented in every major programming language and every major operating
system. The algorithm is not patented. It does not require a license. An
implementation can be written from the published standard in under a day
by any competent programmer.

A future operator who cannot find `sha256sum` on their system can implement
SHA-256 from the published specification and verify the manifest using that
implementation. The verification procedure does not depend on any specific
tool — it depends only on the algorithm, which is public and stable.

**Part 3 — The corpus remains rebuildable.**

The frozen release contains the source ZIP, the engine scripts, and all
metadata required to rebuild the corpus from scratch. The engine depends on:

- Python 3 and standard libraries (stable since 2008; no end-of-life planned)
- MySQL or MariaDB (stable relational database systems, widely available)
- Apache or equivalent web server (decades of stability)
- Standard Unix utilities (`bash`, `find`, `sha256sum`, `cp`)

These dependencies are not cloud services. They are software that has been
continuously available, in one implementation or another, for between two
and four decades. They are maintained by open-source communities whose
continued operation does not depend on any single organisation's financial
health.

A future operator who receives a frozen release and wants to rebuild the
corpus needs to install these standard dependencies — the same dependencies
used to run any web server in the period 2000–2050 — and run one command:

```bash
axis pipeline --full
```

The deterministic reconstruction rule guarantees that the output will be
identical to the output produced by the original operator, because the
rule is defined by the algorithm, not by the person executing it.

**The complete transmission guarantee:**

```
50 years from now, a person holding a compliant frozen release can:

  1. Read the corpus
     → open any content.html in any browser
     → no software installation required

  2. Verify the corpus
     → sha256sum --check release-manifest.sha256
     → requires only: the files + any SHA-256 implementation

  3. Rebuild the corpus
     → install Python 3, MySQL, Apache
     → run: axis pipeline --full
     → produces: identical output to the original build

None of these three operations requires:
  → any network connection
  → any cloud service
  → any account or credential (beyond operator-supplied API keys for
    retranslation, which is not required for verification or reading)
  → any organisation to continue existing
  → any proprietary software
  → any specific hardware
```

This is the transmission guarantee. It is not a promise about the future.
It is a structural property of the present preservation architecture that
will remain true as long as open standards remain open and standard hardware
remains capable of running open-source software — conditions that have held
for half a century and show no sign of changing.

---

## 9. PROTOCOL SUMMARY

A knowledge corpus is durably preserved when three conditions hold simultaneously:

**The content can be read by a human with no tooling beyond a text viewer.**  
**The integrity can be verified by any operator with a SHA-256 implementation.**  
**The corpus can be rebuilt by any operator given the source archive and the engine.**

These three conditions are the protocol. Every section of this document is
an elaboration of how to satisfy them.

---

*Digital Canon Preservation Protocol V1.0 — locked 2026-03-11.*  
*This protocol is independent of any specific software version.*  
*It describes properties. Implementations may change. The properties must not.*
