# AXIS-NIDDHI is a framework for purification, translation, and crystallization of Dhamma content.

## 🧭 New here?

Before exploring the code, please read:

👉 /docs/VISION.md

This document explains the intention, philosophy, and scope of this project.

---

## 📜 License
> License: MIT (see `LICENSE.md`)

---

## Canonical Corpus Publishing Engine

> Deterministic pipeline for preserving and publishing knowledge corpora as reproducible static artifacts.

---

## 🧭 Quick Overview

AXIS-NIDDHI takes a source corpus (e.g., a WordPress backup) and produces:

- Static, database-free HTML output
- Multi-language support via controlled translation pipeline
- Bit-for-bit reproducible builds
- Cryptographically verifiable integrity (SHA-256)

This is not a backup system.

It is a **deterministic preservation engine**.

---

## ⚙️ What It Does

Given a source archive:

- Extracts content into a canonical structure (CSL)
- Applies controlled transformations (translation, normalization)
- Verifies integrity at every stage
- Produces a fully static, portable site

Output characteristics:

- No runtime dependencies
- No database required
- Fully offline-readable
- Rebuildable on any compatible system

---

## 🧱 Architecture

```

pipeline/
├── scripts/core/
├── scripts/tools/
├── metadata/
├── 09-csl/              ← Canonical Source Library (source of truth)
├── 13-ssg/              ← Static site generator
└── release/             ← Sealed reproducible builds

````

### Pipeline Stages

| Stage | Code | Description |
|------|------|-------------|
| Genesis | SG | Extract → structured corpus |
| Preservation | SP | Translation + normalization |
| Audit | SA | Integrity verification (SHA-256) |
| Distribution | SD | Static site generation |

---

> Status: Active — First public release (2026)

---

## 🚀 Quick Start

```bash
# Install CLI
echo "alias axis='bash $(pwd)/release/axis'" >> ~/.bashrc && source ~/.bashrc

# Add source
ls pipeline/sources/*.zip

# Add DeepL key
echo "DEEPL_API_KEY=your-key" > pipeline/scripts/private/deepl_key.txt

# Verify integrity
axis integrity

# Full pipeline
axis pipeline --full

# Preview
axis preview
````

---

## 🌍 Language Expansion

AXIS-NIDDHI supports any DeepL-compatible language.

Each new language requires a **human validation layer**:

* glossary validation
* translation review
* doctrinal consistency check

See `CONTRIBUTING.md`.

---

## 📚 Background (Optional Context)

This engine was built to preserve a specific corpus:

A body of work published at PureDhamma.net — a large collection of essays aiming to reconstruct early teachings with technical precision.

Regardless of philosophical alignment, the engineering problem remains:

> How do you preserve a knowledge corpus so it can be rebuilt, verified, and read independently of its original platform?

AXIS-NIDDHI is one answer.

---

## 🧠 Design Principles

* Determinism over convenience
* Structure over ambiguity
* Reproducibility over speed
* Independence over infrastructure

---

## 🐝 Start Here

👉 Read: `WELCOME.md`
👉 Then: `CONTRIBUTING.md`

---

*AXIS-NIDDHI — Preserve structure. Enable continuity.*

````

---


