# CANONICAL SUCCESSION PROTOCOL
**Lineage Continuity for Knowledge Corpora**  
**Version:** 1.0  
**Date:** 2026-03-11  
**Status:** Locked  
**Companion:** Digital Canon Preservation Protocol V1.0

---

## 1. PREAMBLE

The Digital Canon Preservation Protocol guarantees that a corpus sealed at
a specific moment in time can be recovered, read, and verified at any future
point. It answers the question: *can this corpus survive?*

Survival is necessary. It is not sufficient.

A knowledge tradition does not end at a single canonical moment. It continues.
Errors in earlier translations are recognised and corrected. New scholarly
understanding refines the rendering of difficult terms. Sections that were
incomplete at the first preservation are completed in later cycles. The corpus
lives, and its living state must be able to become canonical again — without
destroying the authority of what was canonical before.

This requirement is **canonical succession**: the capacity of a corpus to
evolve across time while preserving the integrity of its complete historical
lineage. A successor canonical state does not supersede its predecessor. It
extends it. The predecessor remains, unmodified, permanently verifiable, a
fixed point in the lineage to which any future operator can return.

Without a succession protocol, preservation produces a static artifact.
With a succession protocol, preservation produces a living archive: a sequence
of canonical states, each independently verifiable, each referencing the one
before it, together forming an unbroken record of how the corpus has evolved
and who authorised each evolution.

AXIS-NIDDHI therefore separates two responsibilities:

**Preservation Protocol** — ensures that a canonical state is durable,
verifiable, and independent of infrastructure. Defined in the Digital Canon
Preservation Protocol.

**Succession Protocol** — ensures that the lineage connecting canonical states
across time is itself durable, verifiable, and tamper-evident. Defined in
this document.

The first ensures that each node survives. The second ensures that the chain
connecting nodes cannot be broken, forged, or silently reordered.

---

## 2. CANONICAL STATES

A **canonical state** is a corpus release produced in full compliance with
the Digital Canon Preservation Protocol, sealed with a SHA-256 manifest,
and archived in the archaeology archive under a read-only mount.

A canonical state is not a draft, a working corpus, or a release candidate.
It is a formally sealed, reviewed, authorised version of the corpus at a
specific point in time.

### 2.1 Properties

Every canonical state is:

**Immutable.** The content of a canonical state does not change after sealing.
The SHA-256 manifest enforces this: any modification to any file invalidates
the manifest verification. Immutability is not a policy that can be overridden —
it is a cryptographic property of the sealed artifact.

**Cryptographically sealed.** The manifest provides a verifiable fingerprint
of the entire state. The fingerprint is computed from the content itself,
not from external metadata. It does not expire and does not require a trusted
third party to verify.

**Historically permanent.** A canonical state, once archived, is never removed
from the archaeology archive. A successor state does not replace it. Both
coexist. The archive grows in one direction only.

**Independently verifiable.** Any operator holding the artifact and a SHA-256
implementation can verify the seal without contacting any service, any
organisation, or any other operator.

### 2.2 Required Identity Fields

Every canonical state must carry the following identity fields in its
release-sealed-at.txt and in the corpus lineage index:

```
corpus_id          — stable machine-readable identifier of the corpus
canonical_version  — version label (V1, V2, V3, ...)
release_date       — ISO 8601 date of sealing
release_manifest   — filename of the SHA-256 manifest
lineage_reference  — SHA-256 hash of the previous canonical state's manifest
                     (null for the first canonical state)
```

### 2.3 Example: PureDhamma Corpus Canonical States

```
PureDhamma Corpus  (corpus_id: puredhamma)

V1 — 2026-03-11
     748 posts · EN + PT-BR · first canonical preservation
     lineage_reference: null

V2 — 2031-06-02
     748 posts · EN + PT-BR + DE · German translation added
     lineage_reference: <sha256 of V1 manifest>

V3 — 2038-10-14
     751 posts · EN + PT-BR + DE · three posts added from recovered archive
     lineage_reference: <sha256 of V2 manifest>
```

Each version is a complete, independent canonical state. V3 does not replace
V1. A reader who holds V1 and a reader who holds V3 hold different canonical
states of the same corpus. Both are authentic. Both are verifiable. The
lineage chain connects them without collapsing them into one another.

---

## 3. LINEAGE CHAIN

The **lineage chain** is the cryptographic link connecting canonical states
across time. It is constructed by including, in each canonical state, the
SHA-256 hash of the previous canonical state's manifest.

### 3.1 Structure

```
V1  ─────────────────────────────────────────────────────────────
    manifest: release-manifest.sha256
    sha256(manifest): A1B2C3...
    lineage_reference: null

              │
              │  sha256(V1.manifest) = A1B2C3...
              ▼

V2  ─────────────────────────────────────────────────────────────
    manifest: release-manifest.sha256
    sha256(manifest): D4E5F6...
    lineage_reference: A1B2C3...    ← hash of V1 manifest

              │
              │  sha256(V2.manifest) = D4E5F6...
              ▼

V3  ─────────────────────────────────────────────────────────────
    manifest: release-manifest.sha256
    sha256(manifest): G7H8I9...
    lineage_reference: D4E5F6...    ← hash of V2 manifest
```

### 3.2 Properties of the Lineage Chain

**No canonical state can be silently replaced.** Replacing V2 with a modified
version would change sha256(V2.manifest). V3's lineage_reference would no
longer match the hash of the replacement V2. The substitution is immediately
detectable by any operator who holds V3.

**The complete historical lineage remains verifiable.** Starting from the most
recent canonical state, an operator can walk backward through the chain,
verifying each link, until reaching V1 with lineage_reference: null. A
complete walk constitutes a proof that every canonical state in the lineage
is authentic and unmodified.

**The corpus history is tamper-evident.** Any attempt to insert, remove, or
reorder a canonical state breaks the chain at the point of interference. The
break is detectable without knowledge of when or how it occurred — the hash
mismatch is the evidence.

### 3.3 The Chain as Historical Record

The lineage chain is more than a technical integrity mechanism. It is a
structured record of the decisions made by each generation of custodians.
Each canonical state represents a moment at which a group of people reviewed
the corpus, found it ready, and authorised its sealing. The chain connects
those moments into a continuous historical record.

A future researcher examining the lineage chain does not see a sequence of
file versions. They see a sequence of custodial acts: this corpus, at this
moment, was reviewed and sealed by these people, with these findings, and the
result was this state — which led, in time, to the next state, reviewed and
sealed by the next generation of custodians.

---

## 4. COUNCIL MODEL

Knowledge traditions have historically produced canonical collections through
a structured process: gathering, recitation, structuring, and sealing. The
collected texts are recited to confirm fidelity to the tradition, organised
into a stable structure, and sealed as the authoritative canon by the
authority of the assembled community.

This process is not a metaphor for AXIS-NIDDHI. It is a structural equivalent.
The acts are the same. The medium is different.

### 4.1 Structural Equivalence

```
Historical council act          AXIS-NIDDHI equivalent
──────────────────────────────────────────────────────────────────────
RECITATION                      EXTRACTION
Texts are gathered and          SG01 extracts content from the source
recited to verify fidelity      system verbatim, with provenance headers
to the source tradition.        confirming origin. The extraction log
                                is the recitation record.

STRUCTURING                     IDENTITY ASSIGNMENT
Texts are organised into        PDPN identifiers are assigned.
sections, ordered, and          Section structure is established.
related to each other.          Identity records are written.
The structure itself            Canonical ordering (fin_dex) is fixed.
becomes canonical.              The structure is sealed with the content.

SEALING                         CANONICAL FREEZE
The assembled authority         The release authority, after review,
seals the canon. No             executes the freeze procedure.
subsequent change               The SHA-256 manifest seals the state.
alters the sealed texts.        The archaeology archive makes it
The seal is the act             permanent. The review log records
of the council.                 the act of authorisation.
```

### 4.2 Digital Canonical Councils

Each canonical release constitutes a **digital canonical council**: a formal,
documented act of review and sealing that produces an authoritative version
of the corpus for its moment in history.

The council is not a meeting. It is a protocol. Its acts are:

1. The corpus is prepared in working state by the maintainer.
2. The reviewer examines the corpus and confirms its readiness.
3. The release authority executes the freeze.
4. The archivist seals the archaeology record.
5. The lineage is updated to reference the new canonical state.

These five acts, taken together, constitute the digital canonical council
for that release. The review log is the minutes. The sealed manifest is the
council's seal. The archaeology archive is the library in which the sealed
canon is preserved.

The lineage chain connects successive councils. A future operator examining
the lineage does not merely see file hashes. They see the record of every
council that has sealed this corpus since its first preservation — who
authorised each state, when, and on what basis.

---

## 5. SUCCESSION RULES

The following rules are binding. They admit no exceptions. A canonical
succession that violates any of these rules is not compliant with this
protocol.

**Rule 1 — Canonical releases are immutable.**

A sealed canonical release is never modified. The content, the manifest,
the identity records, the review log, and the lineage reference are fixed
at the moment of sealing. The ro,noexec mount on the archaeology archive
is the technical enforcement of this rule. The rule has no override.

**Rule 2 — A new canonical release must reference the previous release.**

The lineage_reference field in every canonical state except the first must
contain the SHA-256 hash of the previous canonical state's manifest. A release
without a valid lineage_reference is not a compliant successor canonical
state — it is an orphan release, and its place in the lineage is undefined.

**Rule 3 — The previous release must remain preserved.**

A successor canonical state does not justify removing its predecessor from
the archaeology archive. Both must coexist permanently. The successor extends
the lineage; it does not replace any node in it.

**Rule 4 — Corrections create new canonical states, not patches.**

An error discovered in a sealed canonical release is addressed by creating
a new working corpus cycle, applying the correction, passing the correction
through review, and sealing a new canonical state. A correction record may
be placed alongside the original release in the archaeology archive to
document what was found and when. The original release is not modified.

**Rule 5 — The lineage must remain cryptographically verifiable at all times.**

Any operator holding any two adjacent canonical states must be able to
confirm, independently, that the later state's lineage_reference matches
the SHA-256 hash of the earlier state's manifest. If this verification fails
for any link in the chain, the chain is broken at that point and must be
documented and investigated before any further canonical succession proceeds.

---

## 6. LINEAGE VERIFICATION

### 6.1 Single-Link Verification

To verify that canonical state Vn is a valid successor to canonical state Vn-1:

```
1. Locate Vn-1 in the archaeology archive
2. Compute: h = sha256(Vn-1/release-manifest.sha256)
3. Read:    ref = Vn/release-sealed-at.txt → lineage_reference
4. Assert:  h == ref
   PASS:  the link is valid
   FAIL:  the link is broken — investigate before proceeding
```

### 6.2 Full Chain Verification

To verify the complete canonical lineage from V1 to Vn:

```
verify_chain(corpus_id):

    Load lineage.json for corpus_id
    states = lineage.canonical_states  [ordered V1 → Vn]

    For i from 1 to len(states) - 1:
        current  = states[i]
        previous = states[i-1]

        # Step 1: verify previous release manifest is intact
        assert sha256sum --check archaeology/{previous.version}/release-manifest.sha256
               returns ALL_OK

        # Step 2: verify lineage reference
        previous_manifest_hash = sha256(
            archaeology/{previous.version}/release-manifest.sha256
        )
        assert current.lineage_reference == previous_manifest_hash

    # Step 3: verify current release manifest is intact
    assert sha256sum --check archaeology/{current.version}/release-manifest.sha256
           returns ALL_OK

    return CHAIN_VERIFIED
```

This procedure produces a **complete canonical lineage proof**: confirmation
that every canonical state in the corpus history is intact, that every link
between states is valid, and that the lineage chain is uninterrupted from V1
to the present canonical state.

### 6.3 Verification Frequency

Full chain verification should be performed:

- Before sealing any new canonical state
- On any occasion when the integrity of the corpus history is in question
- At any handover of custodial responsibility to a new maintainer or archivist
- Whenever an operator wishes to confirm the canonical lineage is intact

Single-link verification should be performed immediately after every canonical
release is archived, to confirm that the new link was written correctly before
the archaeology mount is returned to read-only.

---

## 7. THE LINEAGE INDEX

The **lineage index** is a single plain-text JSON file, lineage.json,
maintained at the root of the corpus archive and updated at every canonical
succession. It provides an operator with a complete view of the canonical
history of the corpus without requiring navigation of the archaeology archive.

### 7.1 Format

```json
{
  "corpus_id":   "puredhamma",
  "corpus_name": "Pure Dhamma",
  "canonical_states": [
    {
      "version":           "V1",
      "date":              "2026-03-11",
      "engine":            "AXIS-NIDDHI V5.4",
      "post_count":        748,
      "languages":         ["en-US", "pt-BR"],
      "manifest_sha256":   "a1b2c3d4e5f6...",
      "lineage_reference": null,
      "review_authority":  "Aloka",
      "notes":             "First canonical preservation. PureDhamma corpus."
    },
    {
      "version":           "V2",
      "date":              "2031-06-02",
      "engine":            "AXIS-NIDDHI V6.1",
      "post_count":        748,
      "languages":         ["en-US", "pt-BR", "de-DE"],
      "manifest_sha256":   "d4e5f6g7h8i9...",
      "lineage_reference": "a1b2c3d4e5f6...",
      "review_authority":  "[reviewer]",
      "notes":             "German translation added. No content changes to EN/PT."
    }
  ]
}
```

### 7.2 Properties

The lineage.json file is the entry point for any future operator who wishes
to understand the canonical history of the corpus. It answers:

- How many canonical states exist?
- When was each one sealed?
- What engine produced it?
- How many posts does it contain, and in what languages?
- What was the reason or context for its creation?
- Who authorised it?

The manifest_sha256 field in each entry allows verification of the archive
record without opening the archive. The lineage_reference field allows
single-link verification without reading the release-sealed-at.txt inside
the archive.

### 7.3 Update Procedure

The lineage.json is updated as part of the canonical succession procedure,
after the new release has been archived and verified:

```
1. Compute sha256(new_release/release-manifest.sha256)
2. Add entry to lineage.json canonical_states array
3. Set lineage_reference = sha256 of previous release manifest
4. Verify the new entry is correct
5. Commit lineage.json to the corpus metadata directory
6. Include updated lineage.json in any future release
```

The lineage.json is not sealed inside the archaeology archive — it is a
living index maintained alongside the archive. Its own integrity can be
verified by comparing its manifest_sha256 values against the manifests
in the archive.

---

## 8. MINIMAL IMPLEMENTATION LAYER

The succession protocol requires a small, precisely defined addition to
the canonical freeze procedure. It does not modify the preservation
architecture. It extends it by three operations performed at seal time.

### 8.1 Changes to the Freeze Procedure

The existing freeze procedure is extended with the following steps, executed
after the SHA-256 manifest has been generated and before the release is
copied to the archaeology archive:

**Step A — Compute the lineage reference.**

```bash
# Locate the most recent sealed canonical state in the archaeology archive
PREVIOUS_MANIFEST=$(ls -t /mnt/archaeology/frozen-releases/*/release-manifest.sha256 \
                    | head -1)

# Compute its SHA-256 hash
LINEAGE_REF=$(sha256sum "$PREVIOUS_MANIFEST" | awk '{print $1}')

# For the very first canonical state: LINEAGE_REF="null"
```

**Step B — Write the lineage reference to release metadata.**

```bash
echo "canonical_version: ${CANONICAL_VERSION}"   >> "$RELEASE_ROOT/release-sealed-at.txt"
echo "lineage_reference: ${LINEAGE_REF}"          >> "$RELEASE_ROOT/release-sealed-at.txt"
```

**Step C — Update the lineage index.**

```bash
NEW_MANIFEST_HASH=$(sha256sum "$RELEASE_ROOT/release-manifest.sha256" | awk '{print $1}')

python3 - << PYEOF
import json
lineage_path = "${CORPUS_DIR}/lineage.json"
with open(lineage_path) as f:
    data = json.load(f)
data['canonical_states'].append({
    "version":           "${CANONICAL_VERSION}",
    "date":              "${RELEASE_DATE}",
    "engine":            "AXIS-NIDDHI ${ENGINE_VERSION}",
    "post_count":        ${POST_COUNT},
    "languages":         ${LANGUAGES_JSON},
    "manifest_sha256":   "${NEW_MANIFEST_HASH}",
    "lineage_reference": "${LINEAGE_REF}",
    "review_authority":  "${REVIEWER}",
    "notes":             "${RELEASE_NOTES}"
})
with open(lineage_path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("lineage.json updated.")
PYEOF
```

These three steps are the complete implementation of the succession protocol
at the engine level. They add fewer than fifty lines to the freeze procedure,
require no new dependencies, and do not modify any preservation step. They
extend the seal with a backward reference and maintain the lineage index.

---

## 9. ARCHITECTURAL SIGNIFICANCE

### 9.1 What This Layer Completes

Prior to this protocol, AXIS-NIDDHI guaranteed two architectural properties:

**Preservation** — a canonical state, once sealed, can be recovered, read,
and verified at any future point, independently, without infrastructure.

**Verification** — any operator holding a sealed release can confirm that
its contents are identical to the state sealed by the original operator.

These two properties were sufficient for the preservation of a single
canonical state. They are not sufficient for a knowledge tradition that
produces multiple canonical states across time. Without succession, each
canonical state is an island: verifiable in itself, but with no formal
relationship to any other canonical state.

The succession protocol adds the third property:

**Succession** — the complete historical lineage of canonical states is
cryptographically linked, tamper-evident, and verifiable from the most
recent state back to the first, by any operator, without trusting any
intermediary.

### 9.2 The Complete Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SUCCESSION                                                              │
│                                                                          │
│  Lineage chain · lineage.json · canonical version identifiers           │
│  SHA-256 inter-release references · digital canonical councils          │
│                                                                          │
│  Guarantees: the corpus can evolve without losing its past              │
├─────────────────────────────────────────────────────────────────────────┤
│  PRESERVATION                                                            │
│                                                                          │
│  Deterministic rebuild · CSL · SHA-256 per-post integrity               │
│  Translation pipeline · Static site generation · Release builder        │
│                                                                          │
│  Guarantees: each canonical state survives independently                │
├─────────────────────────────────────────────────────────────────────────┤
│  VERIFICATION                                                            │
│                                                                          │
│  Release manifests · relative paths · ro,noexec archival mount          │
│  Pre-flight integrity check · per-post hash verification                │
│                                                                          │
│  Guarantees: each canonical state remains authentic                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.3 What the System Now Supports

A knowledge corpus governed by this architecture supports:

- **Preservation of canonical states.** Each sealed release survives
  indefinitely, readable and verifiable without infrastructure.

- **Verification of canonical states.** Any operator can confirm that any
  canonical state is intact, at any time, using only the files and a
  SHA-256 implementation.

- **Historical lineage of canonical states.** The complete succession of
  the corpus from first preservation to present is recorded in a
  cryptographically linked chain that any operator can traverse and verify.

- **Evolution without erasure.** The corpus can be corrected, expanded,
  and translated across successive generations of custodians, without any
  act of improvement requiring the destruction or modification of any
  earlier canonical state.

- **Custodial accountability.** Every canonical state records who reviewed
  it, when it was sealed, and what it contains. The record of custodianship
  is carried forward in the lineage.

---

## 10. FINAL SUMMARY

**Preservation** guarantees that knowledge survives.  
Each canonical state is sealed, self-contained, and independently verifiable,
requiring no infrastructure and no intermediary to confirm its authenticity.

**Verification** guarantees that knowledge remains authentic.  
SHA-256 hashes seal every file, every release, and every link in the lineage
chain. Tampering at any point is immediately detectable by any operator
holding the artifact.

**Succession** guarantees that knowledge can evolve without losing its past.  
Each canonical state references the one before it, forming a tamper-evident
chain from the first preservation to the present. No generation of custodians
can erase what previous generations sealed.

These three properties together define a durable transmission architecture
for knowledge corpora: one capable of carrying the integrity of a body of
knowledge not merely across infrastructure failures, but across the full
span of human generations.

---

*Canonical Succession Protocol V1.0 — locked 2026-03-11.*  
*Companion to the Digital Canon Preservation Protocol V1.0.*  
*This protocol is implementation-independent.*  
*Software changes. The lineage does not.*
