# AXIS-NIDDHI

### A framework for careful translation and crystallization of Dhamma content

This system does **not** attempt to reinterpret or redefine Dhamma.
It supports faithful transmission across languages with minimal distortion.

---

## 🧭 New here?

Before exploring the code, please read:

👉 `/docs/VISION.md`

This document explains the intention, scope, and guiding principles behind this project.

---

## 📜 License

> License: MIT (see `LICENSE.md`)

---

## Canonical Corpus Publishing Engine

> Deterministic pipeline for publishing knowledge corpora as reproducible, static artifacts.

---

## 🧭 Quick Overview

AXIS-NIDDHI takes a source corpus (e.g., a WordPress backup) and produces:

* Static, database-free HTML output
* Multi-language support via controlled translation pipeline
* Bit-for-bit reproducible builds
* Cryptographically verifiable integrity (SHA-256)

This is not a backup system.

It is a **deterministic publishing and verification pipeline**.

---

## ⚙️ What It Does

Given a source archive:

* Extracts content into a canonical structure (CSL)
* Applies controlled transformations (translation, normalization)
* Verifies integrity at every stage
* Produces a fully static, portable site

Output characteristics:

* No runtime dependencies
* No database required
* Fully offline-readable
* Rebuildable on any compatible system

---

## 🌍 Language Expansion

AXIS-NIDDHI supports any DeepL-compatible language.

Each new language requires a **human validation layer**, including:

* glossary validation
* translation review
* consistency checks

Technology assists — it does not replace discernment.

See `CONTRIBUTING.md`.

---

## 📚 Context

This engine was built in the context of a specific corpus:

A body of work published at PureDhamma.net — a large collection of essays aimed at explaining Dhamma with technical precision.

The current situation:

* Deep material is primarily available in English
* Many readers rely on translations
* Literal translation can introduce distortion

AXIS-NIDDHI exists to support:

> **careful, traceable, and verifiable transmission across languages**

---

## 🧱 Architecture

```
pipeline/
├── scripts/core/
├── scripts/tools/
├── metadata/
├── 09-csl/              ← Canonical Source Library (source of truth)
├── 13-ssg/              ← Static site generator
└── release/             ← Reproducible builds
```

### Pipeline Stages

| Stage        | Code | Description                      |
| ------------ | ---- | -------------------------------- |
| Genesis      | SG   | Extract → structured corpus      |
| Processing   | SP   | Translation + normalization      |
| Audit        | SA   | Integrity verification (SHA-256) |
| Distribution | SD   | Static site generation           |

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
```

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

*AXIS-NIDDHI — Enable continuity without altering meaning.*

