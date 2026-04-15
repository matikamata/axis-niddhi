# AXIS-NIDDHI — V5.4 ARCHITECTURAL REFINEMENT RESPONSE
**From:** Vayo (Technical Architect)  
**To:** Aloka  
**Date:** 2026-03-11  
**Re:** Final architectural clarifications and V5.4 seal request

---

## ITEM 1 — ARCHITECTURE VALIDATION

### 1.1 Archaeology physical immutability

**Confirmed and endorsed.**

The three-layer invariant is only enforceable if `/mnt/archaeology` is physically
read-only. The recommended mount option is:

```bash
# /etc/fstab entry for permanent enforcement
/dev/nvme0n1p9  /mnt/archaeology  ext4  ro,noatime,noexec  0 2

# One-time manual mount
sudo mount -o ro /dev/nvme0n1p9 /mnt/archaeology

# Verify
mount | grep archaeology
# Expected: /dev/nvme0n1p9 on /mnt/archaeology type ext4 (ro,noatime,noexec)
```

**Additional safeguard:** use `noexec` in the mount options. This prevents any
accidental execution of scripts retrieved from archaeology, not only writes.

The pipeline tooling (build_release_snapshot.sh, run_full_pipeline.sh,
verify_pipeline_integrity.sh) references only `/beng-fut` and `/beng-release`.
No path in any CORE script points to `/mnt/archaeology`. The physical read-only
mount is a belt-and-suspenders addition to a constraint that already holds in code.

**Formal rule for the architectural record:**

```
INVARIANT A-01:
  /mnt/archaeology MUST be mounted read-only at all times.
  No automated tooling may reference /mnt/archaeology as input or output.
  Human read access for reference is the only permitted operation.
```

### 1.2 Release builder never references archaeology

**Confirmed.** Code-verified.

`build_release_snapshot.sh` references exactly four paths:

| Variable | Value | Role |
|---|---|---|
| `SRC_ROOT` | `/beng-fut` | Source — read only |
| `RELEASE_ROOT` | `/beng-release` | Destination — written |
| `SRC_PIPELINE` | `/beng-fut/pipeline` | Source subtree |
| `SRC_SOURCES` | `/beng-fut/sources` | ZIP location |

`/mnt/archaeology` appears nowhere in the builder. The execution graph is:

```
sources/corpus.zip  →  /beng-fut/pipeline/  →  /beng-release/
     [input]               [processing]           [output]
```

Archaeology sits entirely outside this graph. It is a temporal record, not
a data dependency.

**Formal rule for the architectural record:**

```
INVARIANT A-02:
  /mnt/archaeology is NEVER an input to any pipeline script.
  /mnt/archaeology is NEVER an output of any pipeline script.
  Data flow is strictly: sources → pipeline → release.
```

---

## ITEM 2 — RELEASE SNAPSHOT HARDENING

### 2.1 SHA-256 freeze manifest — decision

**Recommendation: integrate directly into `build_release_snapshot.sh`.**

Rationale for option A (integrated) over option B (separate script):

| Factor | Integrated (A) | Separate script (B) |
|---|---|---|
| Operator friction | Zero — runs automatically | Requires a second command |
| Risk of omission | Impossible — always generated | Operator may forget |
| Atomicity | Manifest describes exactly what was just built | May describe stale state |
| Philosophical fit | A release without a manifest is not sealed | Correct |

A separate `freeze_release.sh` would be appropriate only if releases are built
incrementally over multiple sessions. That is not the current model: one execution
of `build_release_snapshot.sh` produces a complete release.

**Patch to add to `build_release_snapshot.sh`** (insert as Section 14b, between
final verification and the summary banner):

```bash
# ==============================================================================
# 14b. SHA-256 FREEZE MANIFEST
# ==============================================================================

info "Generating cryptographic seal"

MANIFEST="$RELEASE_ROOT/release-manifest.sha256"
MANIFEST_META="$RELEASE_ROOT/release-sealed-at.txt"

if $DRY_RUN; then
    dryrun "generate $MANIFEST"
else
    # Generate SHA-256 for every file in the release
    find "$RELEASE_ROOT" -type f \
        ! -name "release-manifest.sha256" \
        ! -name "release-sealed-at.txt" \
        | sort \
        | while read -r f; do
            sha256sum "$f"
        done > "$MANIFEST"

    # Seal metadata
    cat > "$MANIFEST_META" << SEALEOF
engine:    AXIS-NIDDHI V5.4
corpus:    PureDhamma (748 posts)
sealed_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
builder:   build_release_snapshot.sh
files:     $(wc -l < "$MANIFEST")
SEALEOF

    ok "Cryptographic seal: $MANIFEST ($(wc -l < "$MANIFEST") files)"
    ok "Seal metadata: $MANIFEST_META"
fi
```

The manifest excludes itself and the seal metadata file to avoid circular
dependency. Every other file in `/beng-release/` is checksummed.

**Verification by a future operator:**

```bash
# Verify release integrity at any future date
cd /beng-release
sha256sum --check release-manifest.sha256
# All files: OK  →  release is bit-identical to when it was sealed
```

### 2.2 Integrity check target — confirmation

**Confirmed. The guard already targets `/beng-release/pipeline`.**

Code evidence from `build_release_snapshot.sh` line 605:

```bash
if BENG_BASE="$REL_PIPELINE" bash "$REL_SCRIPTS/verify_pipeline_integrity.sh" --quiet; then
```

Where `REL_PIPELINE="/beng-release/pipeline"`.

The guard runs against the release workspace, not the lab. This is the correct
behaviour: the manifest confirms the source build, the integrity guard confirms
the release is independently operational.

**The two checks serve different purposes:**

| Check | Target | Purpose |
|---|---|---|
| `verify_pipeline_integrity.sh` | `/beng-release/pipeline` | Confirms the release can run the pipeline |
| `release-manifest.sha256` | All files in `/beng-release/` | Confirms the release is bit-identical over time |

Both are required for an archival-grade release. Neither substitutes for the other.

---

## ITEM 3 — AXIS CLI OPERATOR EXPERIENCE

### axis doctor recommendation

**Endorse. Implement now. Zero pipeline risk.**

`axis doctor` is a pure UX wrapper. It calls `verify_pipeline_integrity.sh`
with no additional logic. It does not touch any CORE script.

**Recommended CLI expansion:**

```bash
# In /beng-release/axis — add these cases to the existing case statement:

    doctor)
        echo -e "${BOLD}▶ axis doctor${NC}"
        bash "$SCRIPTS/verify_pipeline_integrity.sh"
        ;;

    build-release)
        echo -e "${BOLD}▶ axis build-release${NC}"
        echo -e "${YELLOW}  This command must be run from the Lab (/beng-fut), not the release.${NC}"
        echo -e "${YELLOW}  Run: sudo bash /beng-fut/pipeline/scripts/build_release_snapshot.sh${NC}"
        echo ""
        echo "  Options:"
        echo "    --dry-run    Simulate without copying files"
        echo "    --force      Rebuild from scratch (removes existing release)"
        ;;
```

**Note on `axis build-release`:** the release builder must always run from the
Lab context, not from within a release. The CLI wrapper correctly redirects the
operator with the precise command — it does not attempt to self-build.

**Complete CLI surface after this addition:**

```
axis build-site     Generate static site (748 pages)
axis preview        Local server on port 8080
axis status         Pipeline status
axis doctor         Pre-flight integrity check         ← NEW
axis pipeline       Full pipeline menu / flags
axis build-release  Redirect to Lab build command      ← NEW (informational)
```

**Decision on CLI expansion scope:** implement `axis doctor` and `axis build-release`
now. Defer any further expansion (e.g., `axis corpus`, `axis archive`) to V6.
The current CLI surface maps 1:1 to the operations an operator actually performs
on a sealed release.

---

## ITEM 4 — CORPUS GENERALIZATION STATUS

**Confirmed deferred to V6.**

The corpus.json descriptor model is architecturally sound and documented.
It will not be implemented in V5.4.

**Formal status entry:**

```
AXIS-NIDDHI V5.4 — DEFERRED FEATURES
══════════════════════════════════════
Feature:   Multi-corpus support (corpus.json descriptor)
Status:    DEFERRED — V6
Scope:     config.py, SG00_reset_workspace.sh, SG01_extract_html.py
Risk if implemented now: breaks single-corpus stability
Design:    Documented in ARCHITECTURAL_CONSOLIDATION_20260311.md §3
Trigger:   Second corpus acquisition or operator request
```

V5.4 is single-corpus, single-source, stable. The generalization path is
documented and ready. The decision to activate it is operational, not architectural.

---

## ITEM 5 — FINAL CONFIRMATION

**All five points confirmed.**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   AXIS-NIDDHI V5.4 — ARCHITECTURAL SEAL                                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  1. PRODUCTION PIPELINE                                          CONFIRMED   ║
║     build_release_snapshot.sh + verify_pipeline_integrity.sh                 ║
║     constitute the final production pipeline infrastructure.                 ║
║     SHA-256 freeze manifest to be integrated into builder.                  ║
║                                                                              ║
║  2. ARCHAEOLOGY LAYER                                            CONFIRMED   ║
║     Documentation + read-only archival storage only.                        ║
║     Physical enforcement: mount -o ro,noexec /mnt/archaeology               ║
║     Zero data-flow dependency with pipeline or release.                     ║
║                                                                              ║
║  3. V5.4 STABLE BASELINE                                         CONFIRMED   ║
║     30 CORE scripts. SHA-256 integrity at every mutation.                   ║
║     Deterministic rebuild from PureDhamma ZIP.                              ║
║     No unresolved critical fragilities.                                     ║
║                                                                              ║
║  4. CORPUS GENERALIZATION                                        DEFERRED    ║
║     corpus.json model documented. Not implemented.                          ║
║     Target: V6 — Multi-Corpus Engine.                                       ║
║                                                                              ║
║  5. CLI EXPANSION                                                CONFIRMED   ║
║     axis doctor → verify_pipeline_integrity.sh                              ║
║     axis build-release → informational redirect to Lab                      ║
║     No further CLI expansion in V5.4.                                       ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   READY FOR FIRST FROZEN RELEASE SNAPSHOT                                    ║
║                                                                              ║
║   Corpus:   PureDhamma (748 posts · EN + PT-BR · 25 sections)               ║
║   Engine:   AXIS-NIDDHI V5.4                                                 ║
║   Date:     2026-03-11                                                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## PENDING ACTIONS BEFORE FREEZE

Three items require code changes before the frozen release snapshot is generated.
All are small, surgical, and non-breaking.

| # | Item | File | Change |
|---|---|---|---|
| P1 | SHA-256 manifest generation | `build_release_snapshot.sh` | Add Section 14b (code above) |
| P2 | `axis doctor` command | `build_release_snapshot.sh` § axis CLI block | Add `doctor)` and `build-release)` cases |
| P3 | Archaeology mount note | Operator documentation | Add to README and consolidation doc |

**After P1–P3 are applied:**

```bash
# Operator sequence for first frozen release
sudo bash /beng-fut/pipeline/scripts/build_release_snapshot.sh --force
# → /beng-release/ built and sealed with SHA-256 manifest

axis doctor
# → INTEGRITY: PASS ✔

# Archive the sealed release
sudo cp -r /beng-release /mnt/archaeology/frozen-releases/2026-03-11_v5.4/
# → archaeology sealed, read-only mount prevents any future modification

# Verify the archaeology copy
sha256sum --check /mnt/archaeology/frozen-releases/2026-03-11_v5.4/release/release-manifest.sha256
# All files: OK
```

This is the complete V5.4 seal procedure.

---

*V5.4 seal confirmed by Vayo. Awaiting P1–P3 application before first frozen release.*
